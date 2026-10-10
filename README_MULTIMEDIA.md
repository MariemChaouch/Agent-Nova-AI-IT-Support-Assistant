# 📁 Guide — Base de Connaissances Multimédia (Agent Nova)

## Types de fichiers supportés

| Type | Extensions | Méthode |
|------|-----------|---------|
| Texte/Markdown | `.md` `.txt` `.rst` | Lecture directe |
| PDF | `.pdf` | Extraction texte page par page (pypdf) |
| Images | `.jpg` `.png` `.gif` `.webp` | OCR (pytesseract) + Description (Ollama llava) |
| Vidéos | `.mp4` `.avi` `.mov` `.mkv` | Transcription audio (Whisper) |
| Audio | `.mp3` `.wav` `.m4a` | Transcription (Whisper) |
| Word | `.docx` | Extraction paragraphes (python-docx) |
| PowerPoint | `.pptx` | Extraction slide par slide (python-pptx) |

---

## Structure recommandée de la KB

```
knowledge_base/
└── it_support/
    ├── acces_mots_de_passe.md       ← articles existants
    ├── logiciels.md
    ├── materiel.md
    ├── securite.md
    ├── vpn_reseau.md
    │
    ├── pdf/                          ← NOUVEAU
    │   ├── guide_vpn_cisco.pdf
    │   ├── politique_securite.pdf
    │   └── onboarding_izen.pdf
    │
    ├── images/                       ← NOUVEAU
    │   ├── erreur_vpn_screenshot.png
    │   ├── interface_outlook.jpg
    │   └── schema_reseau_izen.png
    │
    ├── videos/                       ← NOUVEAU
    │   ├── tuto_reinitialisation_mdp.mp4
    │   ├── connexion_vpn_pas_a_pas.mp4
    │   └── installation_office365.mp4
    │
    └── docs/                         ← NOUVEAU
        ├── procedure_onboarding.docx
        └── formation_securite.pptx
```

---

## Installation des dépendances

### 1. Packages Python
```bash
pip install -r requirements_multimedia.txt
```

### 2. FFmpeg (pour l'extraction audio des vidéos)
```bash
# Windows (via Chocolatey)
choco install ffmpeg

# Windows (via Winget)
winget install ffmpeg

# Ou télécharger : https://ffmpeg.org/download.html
```

### 3. Tesseract OCR (pour les images)
```bash
# Windows
# Télécharger : https://github.com/UB-Mannheim/tesseract/wiki
# Installer les langues : fra (français) + eng (anglais)

# Vérifier l'installation
tesseract --version
```

### 4. Modèle Ollama llava (description d'images, optionnel)
```bash
ollama pull llava
```
> ⚠️ llava requiert ~4GB RAM GPU. Si non disponible, l'OCR seul sera utilisé.

### 5. Modèle Whisper (transcription vidéo, optionnel)
Le modèle `base` (~150MB) est téléchargé automatiquement au premier usage.
Pour de meilleures performances, utilisez `small` ou `medium` :
```python
# Dans kb_loader.py, ligne load_video_file()
model = whisper.load_model("small")  # Meilleure précision
```

---

## Reconstruction de la base après ajout de fichiers

```bash
# Depuis le dossier src/
python -c "from agent import rebuild_knowledge_base; rebuild_knowledge_base()"
```

Ou via l'interface Streamlit → bouton **"Reconstruire la KB"** (à ajouter dans interface.py).

---

## Bonnes pratiques pour les fichiers

### PDFs
- Nommez les fichiers de façon descriptive : `guide_connexion_vpn_cisco.pdf`
- Préférez les PDFs avec texte natif (pas scannés) pour une meilleure extraction

### Images
- Captures d'écran : nommez selon le problème : `erreur_vpn_auth_failed.png`
- Schémas réseau : `schema_infrastructure_izen.png`
- Les images avec texte visible seront extraites par OCR

### Vidéos
- Tutoriels procéduraux → très efficaces pour Nova
- Durée recommandée : 2 à 10 minutes
- Langue : français de préférence (Whisper supporte aussi l'arabe)
- Format MP4 recommandé

### DOCX / PPTX
- Procédures d'onboarding, guides IT, formations sécurité
- Évitez les fichiers avec uniquement des images (sans texte)

---

## Débogage

L'index de la KB est généré automatiquement à chaque chargement :
```
data/kb_index.json
```

Il contient pour chaque document : type, chemin, aperçu du contenu, longueur.
