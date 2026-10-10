"""
avatar.py — Animation de l'avatar
Anime une photo de visage avec synchronisation labiale (SadTalker)
"""

import os
import subprocess
import shutil
from pathlib import Path
import base64


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).parent.parent
AVATAR_PHOTO = BASE_DIR / "data" / "avatar_photo.jpg"
OUTPUT_DIR = BASE_DIR / "data" / "avatar_videos"
SADTALKER_DIR = BASE_DIR / "SadTalker"   # Cloner ici

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# INSTALLATION SADTALKER (automatique)
# ============================================================

def install_sadtalker():
    """
    Clone et configure SadTalker automatiquement.
    À appeler une seule fois lors de la première utilisation.
    """
    if SADTALKER_DIR.exists():
        print("✅ SadTalker déjà installé")
        return
    
    print("📥 Clonage de SadTalker...")
    subprocess.run([
        "git", "clone",
        "https://github.com/OpenTalker/SadTalker.git",
        str(SADTALKER_DIR)
    ], check=True)
    
    print("📦 Installation des dépendances SadTalker...")
    subprocess.run([
        "pip", "install", "-r",
        str(SADTALKER_DIR / "requirements.txt")
    ], check=True)
    
    print("⬇️  Téléchargement des modèles SadTalker (peut prendre du temps)...")
    # Script de téléchargement des modèles
    download_script = SADTALKER_DIR / "scripts" / "download_models.sh"
    if download_script.exists():
        subprocess.run(["bash", str(download_script)], 
                      cwd=str(SADTALKER_DIR), check=True)
    
    print("✅ SadTalker installé et configuré !")


# ============================================================
# GÉNÉRATION VIDÉO AVEC SADTALKER
# ============================================================

def generate_talking_avatar(audio_path: str, output_name: str = "avatar_response.mp4") -> str:
    """
    Génère une vidéo de l'avatar qui parle en synchronisant les lèvres
    avec l'audio fourni.
    
    Args:
        audio_path: Chemin vers le fichier audio (.wav)
        output_name: Nom du fichier vidéo de sortie
    
    Returns:
        str: Chemin vers la vidéo générée
    """
    output_path = str(OUTPUT_DIR / output_name)
    
    # Si SadTalker n'est pas installé, utiliser l'avatar statique
    if not SADTALKER_DIR.exists():
        print("⚠️  SadTalker non installé, utilisation avatar statique")
        return generate_static_avatar_video(audio_path, output_path)
    
    print("🎬 Génération vidéo avatar...")
    
    cmd = [
        "python", str(SADTALKER_DIR / "inference.py"),
        "--driven_audio", audio_path,
        "--source_image", str(AVATAR_PHOTO),
        "--result_dir", str(OUTPUT_DIR),
        "--still",                  # Garder la tête moins mobile
        "--preprocess", "crop",     # Recadrer le visage automatiquement
        "--enhancer", "gfpgan"      # Améliorer la qualité du visage
    ]
    
    try:
        result = subprocess.run(
            cmd,
            cwd=str(SADTALKER_DIR),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Chercher la vidéo générée
        videos = sorted(OUTPUT_DIR.glob("*.mp4"), key=os.path.getmtime, reverse=True)
        if videos:
            latest_video = videos[0]
            shutil.move(str(latest_video), output_path)
            print(f"✅ Vidéo générée: {output_path}")
            return output_path
        else:
            print("⚠️  Aucune vidéo générée, utilisation avatar statique")
            return generate_static_avatar_video(audio_path, output_path)
            
    except subprocess.TimeoutExpired:
        print("⏱️  Timeout SadTalker, utilisation avatar statique")
        return generate_static_avatar_video(audio_path, output_path)
    except Exception as e:
        print(f"❌ Erreur SadTalker: {e}")
        return generate_static_avatar_video(audio_path, output_path)


# ============================================================
# AVATAR STATIQUE (fallback sans SadTalker)
# ============================================================

def generate_static_avatar_video(audio_path: str, output_path: str) -> str:
    """
    Crée une vidéo simple avec la photo de l'avatar et l'audio.
    Fallback quand SadTalker n'est pas disponible.
    
    Nécessite ffmpeg : sudo apt-get install ffmpeg
    """
    try:
        # Créer vidéo avec image fixe + audio
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", str(AVATAR_PHOTO),
            "-i", audio_path,
            "-c:v", "libx264",
            "-tune", "stillimage",
            "-c:a", "aac",
            "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-shortest",
            output_path
        ]
        
        subprocess.run(cmd, capture_output=True, timeout=30, check=True)
        print(f"✅ Vidéo statique générée: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"❌ Erreur génération vidéo: {e}")
        print("Installe ffmpeg: sudo apt-get install ffmpeg")
        return audio_path   # Retourner juste l'audio si vidéo impossible


# ============================================================
# CRÉER UN AVATAR PAR DÉFAUT (si pas de photo)
# ============================================================

def create_default_avatar():
    """
    Crée une image d'avatar simple si aucune photo n'est fournie.
    """
    from PIL import Image, ImageDraw, ImageFont
    
    # Créer une image 512x512 avec un visage simplifié
    img = Image.new('RGB', (512, 512), color='#E8D5C4')
    draw = ImageDraw.Draw(img)
    
    # Corps (fond)
    draw.ellipse([156, 280, 356, 480], fill='#4A90D9', outline='#2E6DA0', width=2)
    
    # Tête
    draw.ellipse([156, 80, 356, 280], fill='#F5C5A3', outline='#D4A484', width=2)
    
    # Yeux
    draw.ellipse([200, 155, 225, 180], fill='#2C2C2C')
    draw.ellipse([287, 155, 312, 180], fill='#2C2C2C')
    draw.ellipse([208, 160, 218, 170], fill='white')
    draw.ellipse([295, 160, 305, 170], fill='white')
    
    # Sourcils
    draw.arc([198, 140, 228, 160], start=200, end=340, fill='#5C4033', width=3)
    draw.arc([285, 140, 315, 160], start=200, end=340, fill='#5C4033', width=3)
    
    # Nez
    draw.ellipse([244, 195, 268, 215], fill='#D4A484')
    
    # Sourire
    draw.arc([210, 215, 302, 265], start=0, end=180, fill='#C0392B', width=3)
    
    # Nom "Nova"
    try:
        from PIL import ImageFont
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
    except:
        font = ImageFont.load_default()
    
    draw.text((180, 295), "NOVA", fill='white', font=font)
    draw.text((162, 335), "AI Assistant", fill='#B8D4F0', font=font)
    
    AVATAR_PHOTO.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(AVATAR_PHOTO))
    print(f"✅ Avatar par défaut créé: {AVATAR_PHOTO}")


def get_avatar_photo_base64() -> str:
    """Retourne la photo de l'avatar encodée en base64 pour l'affichage web."""
    if not AVATAR_PHOTO.exists():
        create_default_avatar()
    
    with open(AVATAR_PHOTO, "rb") as f:
        return base64.b64encode(f.read()).decode()


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    print("=== TEST AVATAR ===")
    
    # Créer l'avatar par défaut si besoin
    if not AVATAR_PHOTO.exists():
        print("Création de l'avatar par défaut...")
        create_default_avatar()
    
    print(f"✅ Photo avatar: {AVATAR_PHOTO}")
    print(f"✅ Dossier vidéos: {OUTPUT_DIR}")
    print("\nPour activer la synchronisation labiale, installe SadTalker:")
    print("  from src.avatar import install_sadtalker")
    print("  install_sadtalker()")
