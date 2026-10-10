"""
kb_loader.py — Chargeur Multimédia de la Base de Connaissances
Supporte : Markdown, PDF, Images, Vidéos (transcription), DOCX, PPTX, TXT
"""

import os
import json
import base64
import tempfile
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional

from langchain_core.documents import Document

# ============================================================
# CONFIGURATION
# ============================================================

# Extensions supportées par catégorie
SUPPORTED_EXTENSIONS = {
    "text":  [".md", ".txt", ".rst", ".csv"],
    "pdf":   [".pdf"],
    "image": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"],
    "video": [".mp4", ".avi", ".mov", ".mkv", ".webm", ".mp3", ".wav", ".m4a"],
    "office":[".docx", ".pptx", ".xlsx"],
}

# ============================================================
# LOADERS TEXTE (Markdown, TXT)
# ============================================================

def load_text_file(path: Path) -> Optional[Document]:
    """Charge un fichier texte ou Markdown."""
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
        return Document(
            page_content=text,
            metadata={
                "source": str(path),
                "type": "text",
                "filename": path.name,
                "category": path.parent.name,
            }
        )
    except Exception as e:
        print(f"⚠️  Erreur lecture {path.name}: {e}")
        return None


# ============================================================
# LOADER PDF
# ============================================================

def load_pdf_file(path: Path) -> list[Document]:
    """Extrait le texte d'un PDF avec pypdf."""
    docs = []
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(path))
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if text.strip():
                docs.append(Document(
                    page_content=text,
                    metadata={
                        "source": str(path),
                        "type": "pdf",
                        "filename": path.name,
                        "page": i + 1,
                        "category": path.parent.name,
                    }
                ))
        print(f"  📄 PDF {path.name} → {len(docs)} pages extraites")
    except ImportError:
        print("  ⚠️  pypdf non installé. Lancez : pip install pypdf")
    except Exception as e:
        print(f"  ⚠️  Erreur PDF {path.name}: {e}")
    return docs


# ============================================================
# LOADER IMAGES (OCR + Description via Ollama Vision)
# ============================================================

def load_image_file(path: Path, use_vision: bool = True) -> Optional[Document]:
    """
    Analyse une image :
    1. OCR avec pytesseract (texte visible)
    2. Description visuelle avec Ollama llava (optionnel)
    """
    content_parts = []

    # --- OCR ---
    try:
        import pytesseract
        from PIL import Image
        img = Image.open(str(path))
        ocr_text = pytesseract.image_to_string(img, lang="fra+eng").strip()
        if ocr_text:
            content_parts.append(f"[Texte OCR]\n{ocr_text}")
    except ImportError:
        pass  # pytesseract optionnel
    except Exception as e:
        print(f"  ⚠️  OCR {path.name}: {e}")

    # --- Description Vision (Ollama llava) ---
    if use_vision:
        try:
            import requests, base64
            with open(str(path), "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode()

            resp = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llava",
                    "prompt": (
                        "Décris cette image en français dans le contexte du support IT. "
                        "Identifie : captures d'écran, messages d'erreur, schémas réseau, "
                        "procédures, matériel informatique. Sois concis (max 150 mots)."
                    ),
                    "images": [img_b64],
                    "stream": False,
                },
                timeout=60
            )
            if resp.status_code == 200:
                description = resp.json().get("response", "")
                if description:
                    content_parts.append(f"[Description visuelle]\n{description}")
        except Exception as e:
            print(f"  ⚠️  Vision {path.name}: {e} (llava non disponible ?)")

    if not content_parts:
        content_parts.append(f"[Image IT : {path.stem}]")

    return Document(
        page_content="\n\n".join(content_parts),
        metadata={
            "source": str(path),
            "type": "image",
            "filename": path.name,
            "category": path.parent.name,
        }
    )


# ============================================================
# LOADER VIDÉO / AUDIO (Transcription Whisper)
# ============================================================

def load_video_file(path: Path) -> Optional[Document]:
    """
    Transcrit une vidéo ou un fichier audio avec Whisper (OpenAI).
    Extrait l'audio si nécessaire via ffmpeg.
    """
    try:
        import whisper
    except ImportError:
        print(f"  ⚠️  Whisper non installé. Lancez : pip install openai-whisper")
        return Document(
            page_content=f"[Vidéo/Audio IT : {path.stem} — transcription non disponible]",
            metadata={"source": str(path), "type": "video", "filename": path.name, "category": path.parent.name}
        )

    try:
        audio_path = str(path)

        # Extraire l'audio si c'est une vidéo
        if path.suffix.lower() in [".mp4", ".avi", ".mov", ".mkv", ".webm"]:
            tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            tmp.close()
            subprocess.run(
                ["ffmpeg", "-i", str(path), "-ac", "1", "-ar", "16000",
                 "-vn", tmp.name, "-y", "-loglevel", "error"],
                check=True
            )
            audio_path = tmp.name

        print(f"  🎬 Transcription de {path.name} (peut prendre du temps)...")
        model = whisper.load_model("base")
        result = model.transcribe(audio_path, language="fr")
        transcript = result.get("text", "").strip()

        # Nettoyage fichier temporaire
        if audio_path != str(path):
            os.unlink(audio_path)

        if not transcript:
            return None

        print(f"  ✅ Transcription OK : {len(transcript)} caractères")
        return Document(
            page_content=f"[Transcription vidéo/audio : {path.stem}]\n\n{transcript}",
            metadata={
                "source": str(path),
                "type": "video",
                "filename": path.name,
                "duration_hint": "voir fichier source",
                "category": path.parent.name,
            }
        )
    except FileNotFoundError:
        print(f"  ⚠️  ffmpeg non trouvé. Installez-le : https://ffmpeg.org/")
        return None
    except Exception as e:
        print(f"  ⚠️  Erreur transcription {path.name}: {e}")
        return None


# ============================================================
# LOADER OFFICE (DOCX, PPTX, XLSX)
# ============================================================

def load_docx_file(path: Path) -> Optional[Document]:
    """Extrait le texte d'un fichier Word."""
    try:
        from docx import Document as DocxDocument
        doc = DocxDocument(str(path))
        text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        return Document(
            page_content=text,
            metadata={"source": str(path), "type": "docx", "filename": path.name, "category": path.parent.name}
        )
    except ImportError:
        print("  ⚠️  python-docx non installé : pip install python-docx")
        return None
    except Exception as e:
        print(f"  ⚠️  Erreur DOCX {path.name}: {e}")
        return None


def load_pptx_file(path: Path) -> list[Document]:
    """Extrait le texte d'un PowerPoint slide par slide."""
    docs = []
    try:
        from pptx import Presentation
        prs = Presentation(str(path))
        for i, slide in enumerate(prs.slides):
            texts = []
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    texts.append(shape.text.strip())
            if texts:
                docs.append(Document(
                    page_content="\n".join(texts),
                    metadata={
                        "source": str(path), "type": "pptx",
                        "filename": path.name, "slide": i + 1, "category": path.parent.name
                    }
                ))
        print(f"  📊 PPTX {path.name} → {len(docs)} slides extraits")
    except ImportError:
        print("  ⚠️  python-pptx non installé : pip install python-pptx")
    except Exception as e:
        print(f"  ⚠️  Erreur PPTX {path.name}: {e}")
    return docs


# ============================================================
# CHARGEUR PRINCIPAL MULTIMÉDIA
# ============================================================

def load_all_documents(kb_dir: Path, use_vision: bool = True) -> list[Document]:
    """
    Parcourt récursivement le dossier kb_dir et charge tous les fichiers supportés.

    Args:
        kb_dir: Répertoire racine de la base de connaissances
        use_vision: Active/désactive la description d'images via Ollama llava

    Returns:
        Liste de Documents LangChain
    """
    all_docs = []
    stats = {ext_type: 0 for ext_type in SUPPORTED_EXTENSIONS}

    all_extensions = {
        ext: ext_type
        for ext_type, exts in SUPPORTED_EXTENSIONS.items()
        for ext in exts
    }

    for file_path in sorted(kb_dir.rglob("*")):
        if not file_path.is_file():
            continue

        suffix = file_path.suffix.lower()
        file_type = all_extensions.get(suffix)

        if file_type is None:
            continue  # Extension non supportée

        print(f"  📂 {file_type.upper()} → {file_path.relative_to(kb_dir)}")

        if file_type == "text":
            doc = load_text_file(file_path)
            if doc:
                all_docs.append(doc)
                stats[file_type] += 1

        elif file_type == "pdf":
            docs = load_pdf_file(file_path)
            all_docs.extend(docs)
            stats[file_type] += len(docs)

        elif file_type == "image":
            doc = load_image_file(file_path, use_vision=use_vision)
            if doc:
                all_docs.append(doc)
                stats[file_type] += 1

        elif file_type == "video":
            doc = load_video_file(file_path)
            if doc:
                all_docs.append(doc)
                stats[file_type] += 1

        elif file_type == "office":
            if suffix == ".docx":
                doc = load_docx_file(file_path)
                if doc:
                    all_docs.append(doc)
                    stats[file_type] += 1
            elif suffix == ".pptx":
                docs = load_pptx_file(file_path)
                all_docs.extend(docs)
                stats[file_type] += len(docs)

    # Résumé
    print("\n📊 Résumé du chargement :")
    for ext_type, count in stats.items():
        if count > 0:
            emoji = {"text": "📝", "pdf": "📄", "image": "🖼️", "video": "🎬", "office": "📊"}.get(ext_type, "📁")
            print(f"  {emoji} {ext_type.upper()} : {count} document(s)")
    print(f"  ✅ Total : {len(all_docs)} chunks documentaires\n")

    return all_docs


# ============================================================
# UTILITAIRES — INDEXATION DES MÉTADONNÉES
# ============================================================

def save_kb_index(docs: list[Document], index_path: Path):
    """Sauvegarde un index JSON des documents chargés."""
    index = []
    for doc in docs:
        meta = doc.metadata.copy()
        meta["preview"] = doc.page_content[:200]
        meta["length"] = len(doc.page_content)
        index.append(meta)

    index_path.parent.mkdir(parents=True, exist_ok=True)
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump({
            "generated_at": datetime.now().isoformat(),
            "total_docs": len(docs),
            "documents": index
        }, f, ensure_ascii=False, indent=2)

    print(f"📋 Index KB sauvegardé → {index_path}")


def get_kb_stats(kb_dir: Path) -> dict:
    """Retourne les statistiques de la KB (nombre de fichiers par type)."""
    stats = {}
    all_extensions = {
        ext: ext_type
        for ext_type, exts in SUPPORTED_EXTENSIONS.items()
        for ext in exts
    }
    for file_path in kb_dir.rglob("*"):
        if file_path.is_file():
            file_type = all_extensions.get(file_path.suffix.lower(), "unsupported")
            stats[file_type] = stats.get(file_type, 0) + 1
    return stats
