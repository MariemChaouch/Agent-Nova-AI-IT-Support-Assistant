"""
speech_to_text.py — Reconnaissance vocale
Micro → Texte avec faster-whisper
"""

from faster_whisper import WhisperModel
import numpy as np
import tempfile
import os

# ============================================================
# CONFIGURATION
# ============================================================

WHISPER_MODEL = "small"   # "tiny", "base", "small", "medium", "large"
LANGUAGE = "fr"

# ============================================================
# CHARGEMENT DU MODÈLE
# ============================================================

_model = None

def get_model():
    global _model
    if _model is None:
        print(f"🎙️ Chargement modèle faster-whisper ({WHISPER_MODEL})...")
        _model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
        print("✅ faster-whisper prêt")
    return _model

# ============================================================
# TRANSCRIPTION DEPUIS FICHIER AUDIO
# ============================================================

def transcribe_audio_file(audio_path: str) -> str:
    try:
        model = get_model()
        segments, info = model.transcribe(audio_path, language=LANGUAGE, beam_size=1)
        text = " ".join(segment.text for segment in segments).strip()
        print(f"📝 Transcription: '{text}'")
        return text
    except Exception as e:
        print(f"❌ Erreur transcription: {e}")
        return ""

# ============================================================
# TRANSCRIPTION DEPUIS NUMPY ARRAY
# ============================================================

def transcribe_audio_array(audio_array: np.ndarray, sample_rate: int = 16000) -> str:
    if audio_array.dtype != np.float32:
        audio_array = audio_array.astype(np.float32)
    if audio_array.ndim > 1:
        audio_array = audio_array.mean(axis=1)
    if np.max(np.abs(audio_array)) > 0:
        audio_array = audio_array / np.max(np.abs(audio_array))

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        import soundfile as sf
        sf.write(tmp.name, audio_array, sample_rate)
        text = transcribe_audio_file(tmp.name)
        os.unlink(tmp.name)

    return text

# ============================================================
# CAPTURE MICROPHONE (mode console / test)
# ============================================================

def listen_microphone(duration_seconds: int = 5) -> str:
    try:
        import speech_recognition as sr

        recognizer = sr.Recognizer()
        with sr.Microphone(sample_rate=16000) as source:
            print(f"🎤 Parle maintenant ({duration_seconds} secondes)...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=duration_seconds, phrase_time_limit=duration_seconds)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio.get_wav_data())
            tmp_path = tmp.name

        text = transcribe_audio_file(tmp_path)
        os.unlink(tmp_path)
        return text

    except Exception as e:
        print(f"❌ Erreur microphone: {e}")
        return ""

# ============================================================
# DÉTECTION DE SILENCE (VAD)
# ============================================================

def is_speech(audio_chunk: np.ndarray, threshold: float = 0.01) -> bool:
    energy = np.sqrt(np.mean(audio_chunk ** 2))
    return energy > threshold

# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    print("=== TEST SPEECH TO TEXT ===")
    text = listen_microphone(duration_seconds=5)
    if text:
        print(f"\n✅ Tu as dit: '{text}'")
    else:
        print("\n❌ Aucune parole détectée")