#!/bin/bash
# ============================================================
# SCRIPT D'INSTALLATION AUTOMATIQUE — PROJET KM AVATAR AI
# ============================================================

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   INSTALLATION PROJET KM — AVATAR AI    ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# 1. Vérifier Python
echo "▶ Vérification Python..."
python3 --version || { echo "❌ Python 3 non trouvé. Installe Python 3.10+"; exit 1; }

# 2. Créer environnement virtuel
echo ""
echo "▶ Création environnement virtuel..."
python3 -m venv venv
source venv/bin/activate

# 3. Mettre à jour pip
echo ""
echo "▶ Mise à jour pip..."
pip install --upgrade pip --quiet

# 4. Installer les dépendances Python
echo ""
echo "▶ Installation des dépendances Python..."
pip install -r requirements.txt

# 5. Installer Ollama
echo ""
echo "▶ Installation Ollama (LLM local)..."
if ! command -v ollama &> /dev/null; then
    curl -fsSL https://ollama.com/install.sh | sh
    echo "✅ Ollama installé"
else
    echo "✅ Ollama déjà installé"
fi

# 6. Télécharger le modèle Mistral
echo ""
echo "▶ Téléchargement modèle Mistral (peut prendre quelques minutes)..."
ollama pull mistral

# 7. Créer dossiers de données
echo ""
echo "▶ Création structure des dossiers..."
mkdir -p data/chroma_db


# 8. Vérifier pyaudio (micro)
echo ""
echo "▶ Vérification support audio..."
python3 -c "import pyaudio; print('✅ PyAudio OK')" 2>/dev/null || echo "⚠️  PyAudio: installe portaudio19-dev (sudo apt-get install portaudio19-dev)"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   ✅ INSTALLATION TERMINÉE !             ║"
echo "║                                          ║"
echo "║   Lance le projet :                      ║"
echo "║   source venv/bin/activate               ║"
echo "║   python run.py                          ║"
echo "╚══════════════════════════════════════════╝"
echo ""
