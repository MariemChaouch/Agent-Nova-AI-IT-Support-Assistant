"""
text_to_speech.py — Synthèse vocale
Texte → Voix avec Coqui TTS (open source)
"""

import os
import tempfile
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

# Dossier pour sauvegarder les fichiers audio générés
AUDIO_DIR = Path(__file__).parent.parent / "data" / "audio_cache"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# Modèle TTS (voix française)
# Modèles disponibles avec "tts --list_models" dans le terminal
TTS_MODEL = "tts_models/fr/mai/tacotron2-DDC"   # Voix française naturelle
# Alternative si celui-ci ne fonctionne pas :
# TTS_MODEL = "tts_models/multilingual/multi-dataset/xtts_v2"

# Paramètres voix
SPEAKING_RATE = 1.0     # Vitesse (1.0 = normal, 1.2 = plus rapide)


# ============================================================
# MOTEUR TTS PRINCIPAL (Coqui TTS)
# ============================================================

_tts_engine = None

def get_tts_engine():
    """Charge le moteur TTS (une seule fois en mémoire)."""
    global _tts_engine
    if _tts_engine is None:
        try:
            from TTS.api import TTS
            print(f"🔊 Chargement moteur TTS ({TTS_MODEL})...")
            _tts_engine = TTS(model_name=TTS_MODEL, progress_bar=False)
            print("✅ TTS Coqui prêt")
        except Exception as e:
            print(f"⚠️  Coqui TTS non disponible ({e}), utilisation de pyttsx3...")
            _tts_engine = "pyttsx3"
    return _tts_engine


def text_to_speech_coqui(text: str, output_path: str) -> str:
    """
    Génère un fichier audio depuis un texte avec Coqui TTS.
    
    Args:
        text: Le texte à synthétiser
        output_path: Chemin du fichier audio de sortie (.wav)
    
    Returns:
        str: Chemin du fichier audio généré
    """
    engine = get_tts_engine()
    
    if engine == "pyttsx3":
        return text_to_speech_pyttsx3(text, output_path)
    
    engine.tts_to_file(
        text=text,
        file_path=output_path
    )
    
    return output_path


# ============================================================
# MOTEUR TTS DE SECOURS (pyttsx3 — 100% offline, simple)
# ============================================================

def text_to_speech_pyttsx3(text: str, output_path: str) -> str:
    """
    Génère un fichier audio avec pyttsx3 (fallback simple).
    
    Args:
        text: Le texte à synthétiser
        output_path: Chemin du fichier audio de sortie
    
    Returns:
        str: Chemin du fichier audio généré
    """
    import pyttsx3
    
    engine = pyttsx3.init()
    
    # Configurer la voix française si disponible
    voices = engine.getProperty('voices')
    for voice in voices:
        if 'french' in voice.name.lower() or 'fr' in voice.id.lower():
            engine.setProperty('voice', voice.id)
            break
    
    engine.setProperty('rate', 150)     # Vitesse de parole
    engine.setProperty('volume', 0.9)   # Volume
    
    engine.save_to_file(text, output_path)
    engine.runAndWait()
    
    return output_path


# ============================================================
# LECTURE DIRECTE (sans sauvegarder)
# ============================================================

def speak_text(text: str):
    """
    Lit le texte directement sur les haut-parleurs.
    Utile pour les tests.
    
    Args:
        text: Le texte à lire
    """
    import pyttsx3
    
    engine = pyttsx3.init()
    
    # Configurer la voix française
    voices = engine.getProperty('voices')
    for voice in voices:
        if 'french' in voice.name.lower() or 'fr' in voice.id.lower():
            engine.setProperty('voice', voice.id)
            break
    
    engine.setProperty('rate', 150)
    engine.say(text)
    engine.runAndWait()


# ============================================================
# FONCTION PRINCIPALE (utilisée par l'interface)
# ============================================================

def generate_speech(text: str, filename: str = None) -> str:
    """
    Fonction principale : génère un fichier audio depuis un texte.
    
    Args:
        text: Texte à synthétiser
        filename: Nom du fichier (optionnel, auto-généré sinon)
    
    Returns:
        str: Chemin complet du fichier audio généré
    """
    if not filename:
        import hashlib
        hash_name = hashlib.md5(text.encode()).hexdigest()[:8]
        filename = f"response_{hash_name}.wav"
    
    output_path = str(AUDIO_DIR / filename)
    
    # Essayer Coqui TTS, fallback sur pyttsx3
    try:
        return text_to_speech_coqui(text, output_path)
    except Exception as e:
        print(f"⚠️  Erreur Coqui TTS: {e}, utilisation pyttsx3...")
        return text_to_speech_pyttsx3(text, output_path)


# ============================================================
# NETTOYAGE DU CACHE AUDIO
# ============================================================

def clear_audio_cache():
    """Supprime les anciens fichiers audio générés."""
    count = 0
    for f in AUDIO_DIR.glob("response_*.wav"):
        f.unlink()
        count += 1
    print(f"🗑️  {count} fichiers audio supprimés")


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    print("=== TEST TEXT TO SPEECH ===")
    
    texte_test = "Bonjour ! Je suis Nova, votre assistant de gestion des connaissances. Comment puis-je vous aider aujourd'hui ?"
    
    print(f"Synthèse de: '{texte_test}'")
    audio_path = generate_speech(texte_test, "test_tts.wav")
    
    print(f"✅ Audio généré: {audio_path}")
    print("Lecture en cours...")
    
    # Lire le fichier généré
    try:
        import subprocess
        subprocess.run(["aplay", audio_path], check=True)   # Linux
    except:
        try:
            import subprocess
            subprocess.run(["afplay", audio_path], check=True)  # Mac
        except:
            print("(Installe aplay ou afplay pour entendre l'audio)")
