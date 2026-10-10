# Agent Nova — IT Support IZEN

Agent IA actif de support IT pour IZEN (200 employés, Tunis).

## Architecture

```
Interface Streamlit  →  FastAPI Backend  →  LangChain + Ollama (Mistral)  →  ChromaDB
       ↓                                              ↓
  Whisper STT                                  KB IT (5 catégories)
  Coqui TTS                                    Système de tickets SMTP
```

## Base de Connaissances IT (5 catégories)

| Catégorie | Articles | Incidents couverts |
|-----------|----------|--------------------|
|  Accès & Mots de passe | 1 | ~15/jour |
|  VPN & Réseau | 1 | ~10/jour |
|  Logiciels | 1 | ~8/jour |
|  Matériel | 1 | ~7/jour |
| Sécurité | 1 | ~5/jour |

## Flux de traitement

1. **Employé** envoie un message (texte ou vocal)
2. **Nova** analyse l'intention (NLP/LLM)
3. **Recherche RAG** dans la KB IT
4. **Décision** :
   - Solution trouvée → Réponse étape par étape + audio
   -  Pas de solution → Ticket `IZN-XXXX` créé + email au dept IT

## Installation

```bash
# 1. Prérequis
pip install -r requirements.txt

# 2. Lancer Ollama avec Mistral
ollama serve
ollama pull mistral

# 3. Configurer SMTP (optionnel, pour les tickets email)
# Editer src/agent.py → SMTP_CONFIG → renseigner le mot de passe
# Ou via variable d'environnement : NOVA_SMTP_PASSWORD=...

# 4. Lancer l'interface
python run.py
# ou : streamlit run src/interface.py
```

## Configuration SMTP (tickets)

Editer `src/agent.py`, section `SMTP_CONFIG` :

```python
SMTP_CONFIG = {
    "host": "smtp.izen.tn",
    "port": 587,
    "user": "nova@izen.tn",
    "password": "MOT_DE_PASSE_ICI",   # ← À renseigner
    "it_email": "support@izen.tn",
}
```

## Étapes suivantes

Voir la présentation de l'équipe pour les prochaines fonctionnalités :
- Avatar animé SadTalker (75% → 100%)
- Enrichissement KB : vidéos + screenshots (30% → 100%)
- Communication vocale temps réel (40% → 100%)
- Extension SMTP complète (10% → 100%)

## Contact IT IZEN

- Email : support@izen.tn
- Téléphone : Poste 101
- Responsable : Mehdi Bouaziz — Dir. Support IT
