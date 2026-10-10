"""
media_enricher.py — Enrichissement multimédia pour Agent Nova (IZEN IT Support)
Recherche automatique de vidéos YouTube et génération d'images explicatives
selon le type de problème IT détecté.
"""

import os
import re
import requests
from pathlib import Path
from typing import Optional

# ============================================================
# CONFIGURATION
# ============================================================

# Clé API YouTube Data v3 (à mettre dans variable d'environnement)
# Créer une clé ici : https://console.developers.google.com/
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")

# Clé API Unsplash pour images (gratuit, 50 req/heure)
# Créer une clé ici : https://unsplash.com/developers
UNSPLASH_API_KEY = os.getenv("UNSPLASH_API_KEY", "")

# Répertoire de cache des images téléchargées
BASE_DIR   = Path(__file__).parent.parent
MEDIA_CACHE = BASE_DIR / "data" / "media_cache"
MEDIA_CACHE.mkdir(parents=True, exist_ok=True)

# ============================================================
# MAPPING : catégorie IT → requêtes de recherche
# ============================================================

CATEGORY_MEDIA_QUERIES = {
    "password": {
        "youtube_fr": "réinitialiser mot de passe windows tutoriel",
        "youtube_en": "windows password reset tutorial",
        "image_query": "windows password reset screen",
        "image_description": "Écran de réinitialisation de mot de passe Windows",
    },
    "vpn": {
        "youtube_fr": "configurer VPN Cisco AnyConnect tutoriel",
        "youtube_en": "Cisco AnyConnect VPN setup tutorial",
        "image_query": "VPN connection network diagram",
        "image_description": "Schéma de connexion VPN",
    },
    "software": {
        "youtube_fr": "réparer Microsoft Office tutoriel",
        "youtube_en": "Microsoft Office repair tutorial",
        "image_query": "microsoft office application interface",
        "image_description": "Interface Microsoft Office",
    },
    "hardware": {
        "youtube_fr": "réparer PC lent Windows tutoriel",
        "youtube_en": "fix slow PC Windows tutorial",
        "image_query": "computer hardware maintenance",
        "image_description": "Maintenance matériel PC",
    },
    "security": {
        "youtube_fr": "phishing email cybersécurité comment détecter",
        "youtube_en": "phishing email detection cybersecurity",
        "image_query": "cybersecurity phishing warning",
        "image_description": "Alerte phishing et cybersécurité",
    },
    "email": {
        "youtube_fr": "configurer Outlook email tutoriel",
        "youtube_en": "Outlook email setup troubleshooting tutorial",
        "image_query": "microsoft outlook email interface",
        "image_description": "Configuration Outlook",
    },
    "other": {
        "youtube_fr": "support informatique aide tutoriel",
        "youtube_en": "IT support help tutorial",
        "image_query": "IT support technology",
        "image_description": "Support IT",
    },
}


# ============================================================
# IMAGES EXPLICATIVES
# ============================================================

def get_explainer_image(category: str, question: str) -> Optional[dict]:
    """
    Retourne une image explicative pour le problème IT.
    
    Stratégie :
    1. Essaie Unsplash API (si clé configurée)
    2. Sinon retourne une image SVG générée localement (toujours disponible)
    """
    if UNSPLASH_API_KEY:
        result = _fetch_unsplash_image(category)
        if result:
            return result
    
    # Fallback : image SVG générée (toujours disponible, sans API)
    return _generate_svg_diagram(category, question)


def _fetch_unsplash_image(category: str) -> Optional[dict]:
    """Récupère une image depuis Unsplash (libre de droits)."""
    queries = CATEGORY_MEDIA_QUERIES.get(category, CATEGORY_MEDIA_QUERIES["other"])
    query   = queries.get("image_query", "IT support")
    
    try:
        resp = requests.get(
            "https://api.unsplash.com/search/photos",
            params={
                "query":       query,
                "per_page":    1,
                "orientation": "landscape",
                "content_filter": "high",
            },
            headers={"Authorization": f"Client-ID {UNSPLASH_API_KEY}"},
            timeout=5,
        )
        resp.raise_for_status()
        data    = resp.json()
        results = data.get("results", [])
        
        if not results:
            return None
        
        photo = results[0]
        return {
            "url":         photo["urls"]["regular"],
            "thumb":       photo["urls"]["thumb"],
            "description": photo.get("alt_description", queries["image_description"]),
            "author":      photo["user"]["name"],
            "source":      "unsplash",
        }
    
    except Exception as e:
        print(f"⚠️  Unsplash API error: {e}")
        return None


def _generate_svg_diagram(category: str, question: str) -> dict:
    """
    Génère un schéma SVG explicatif selon la catégorie du problème IT.
    Retourne un SVG inline (pas de dépendance externe).
    """
    diagrams = {
        "password": _svg_password_reset(),
        "vpn":      _svg_vpn_diagram(),
        "software": _svg_software_repair(),
        "hardware": _svg_hardware_check(),
        "security": _svg_security_alert(),
        "email":    _svg_email_config(),
        "other":    _svg_it_support(),
    }
    
    svg_content = diagrams.get(category, diagrams["other"])
    
    return {
        "svg":         svg_content,
        "description": CATEGORY_MEDIA_QUERIES.get(category, {}).get("image_description", "Schéma IT"),
        "source":      "generated_svg",
    }


# ============================================================
# GÉNÉRATEURS DE SCHÉMAS SVG
# ============================================================

def _svg_password_reset() -> str:
    return """<svg viewBox="0 0 500 280" xmlns="http://www.w3.org/2000/svg" font-family="Arial,sans-serif">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#1a1a2e"/>
      <stop offset="100%" style="stop-color:#16213e"/>
    </linearGradient>
    <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#7c6ff7"/>
    </marker>
  </defs>
  <rect width="500" height="280" fill="url(#bg)" rx="12"/>
  <text x="250" y="28" fill="#7c6ff7" font-size="15" font-weight="bold" text-anchor="middle">🔐 Réinitialisation du mot de passe Windows</text>
  <!-- Étape 1 -->
  <rect x="20" y="45" width="100" height="50" rx="8" fill="#2d2b55" stroke="#7c6ff7" stroke-width="1.5"/>
  <text x="70" y="66" fill="white" font-size="11" text-anchor="middle">① Écran</text>
  <text x="70" y="80" fill="white" font-size="11" text-anchor="middle">de connexion</text>
  <text x="70" y="93" fill="#7c6ff7" font-size="18" text-anchor="middle">🖥️</text>
  <!-- Flèche -->
  <line x1="122" y1="70" x2="148" y2="70" stroke="#7c6ff7" stroke-width="2" marker-end="url(#arrow)"/>
  <!-- Étape 2 -->
  <rect x="150" y="45" width="100" height="50" rx="8" fill="#2d2b55" stroke="#7c6ff7" stroke-width="1.5"/>
  <text x="200" y="66" fill="white" font-size="11" text-anchor="middle">② Mot de passe</text>
  <text x="200" y="80" fill="white" font-size="11" text-anchor="middle">oublié ?</text>
  <text x="200" y="93" fill="#f39c12" font-size="18" text-anchor="middle">❓</text>
  <!-- Flèche -->
  <line x1="252" y1="70" x2="278" y2="70" stroke="#7c6ff7" stroke-width="2" marker-end="url(#arrow)"/>
  <!-- Étape 3 -->
  <rect x="280" y="45" width="100" height="50" rx="8" fill="#2d2b55" stroke="#7c6ff7" stroke-width="1.5"/>
  <text x="330" y="66" fill="white" font-size="11" text-anchor="middle">③ Email de</text>
  <text x="330" y="80" fill="white" font-size="11" text-anchor="middle">récupération</text>
  <text x="330" y="93" fill="#3498db" font-size="18" text-anchor="middle">📧</text>
  <!-- Flèche -->
  <line x1="382" y1="70" x2="408" y2="70" stroke="#7c6ff7" stroke-width="2" marker-end="url(#arrow)"/>
  <!-- Étape 4 -->
  <rect x="410" y="45" width="70" height="50" rx="8" fill="#27ae60" stroke="#2ecc71" stroke-width="1.5"/>
  <text x="445" y="66" fill="white" font-size="11" text-anchor="middle">④ Nouveau</text>
  <text x="445" y="80" fill="white" font-size="11" text-anchor="middle">mot de passe</text>
  <text x="445" y="93" fill="white" font-size="18" text-anchor="middle">✅</text>
  <!-- Encadré Ctrl+Alt+Del -->
  <rect x="20" y="130" width="220" height="70" rx="8" fill="#1e1e3a" stroke="#e74c3c" stroke-width="1.5"/>
  <text x="130" y="148" fill="#e74c3c" font-size="12" font-weight="bold" text-anchor="middle">⌨️ Raccourci administrateur</text>
  <rect x="35" y="155" width="80" height="28" rx="5" fill="#2d2b55" stroke="#7c6ff7" stroke-width="1"/>
  <text x="75" y="173" fill="white" font-size="11" text-anchor="middle">Ctrl + Alt</text>
  <text x="130" y="173" fill="#7c6ff7" font-size="12" text-anchor="middle">+</text>
  <rect x="145" y="155" width="80" height="28" rx="5" fill="#2d2b55" stroke="#7c6ff7" stroke-width="1"/>
  <text x="185" y="173" fill="white" font-size="11" text-anchor="middle">Suppr</text>
  <text x="130" y="196" fill="rgba(255,255,255,0.5)" font-size="10" text-anchor="middle">→ Modifier le mot de passe</text>
  <!-- Encadré contact IT -->
  <rect x="260" y="130" width="220" height="70" rx="8" fill="#1e1e3a" stroke="#f39c12" stroke-width="1.5"/>
  <text x="370" y="148" fill="#f39c12" font-size="12" font-weight="bold" text-anchor="middle">📞 Contact IT IZEN</text>
  <text x="370" y="165" fill="white" font-size="11" text-anchor="middle">support@izen.tn</text>
  <text x="370" y="180" fill="white" font-size="11" text-anchor="middle">Poste 101 — Mehdi Bouaziz</text>
  <text x="370" y="195" fill="rgba(255,255,255,0.5)" font-size="10" text-anchor="middle">SLA : 2h</text>
  <!-- Footer -->
  <text x="250" y="240" fill="rgba(255,255,255,0.3)" font-size="10" text-anchor="middle">Schéma généré par Nova — Agent IT Support IZEN</text>
</svg>"""


def _svg_vpn_diagram() -> str:
    return """<svg viewBox="0 0 500 280" xmlns="http://www.w3.org/2000/svg" font-family="Arial,sans-serif">
  <defs>
    <linearGradient id="bg2" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#0d1b2a"/>
      <stop offset="100%" style="stop-color:#1b2838"/>
    </linearGradient>
  </defs>
  <rect width="500" height="280" fill="url(#bg2)" rx="12"/>
  <text x="250" y="28" fill="#3498db" font-size="15" font-weight="bold" text-anchor="middle">🔒 Architecture VPN — Connexion sécurisée</text>
  <!-- PC utilisateur -->
  <rect x="20" y="80" width="90" height="70" rx="8" fill="#1a2744" stroke="#3498db" stroke-width="2"/>
  <text x="65" y="105" fill="white" font-size="28" text-anchor="middle">💻</text>
  <text x="65" y="125" fill="white" font-size="11" text-anchor="middle">Votre PC</text>
  <text x="65" y="140" fill="#3498db" font-size="10" text-anchor="middle">Domicile/Externe</text>
  <!-- Tunnel chiffré -->
  <rect x="125" y="100" width="250" height="30" rx="15" fill="none" stroke="#27ae60" stroke-width="2" stroke-dasharray="8,4"/>
  <text x="250" y="120" fill="#27ae60" font-size="11" text-anchor="middle">🔐 Tunnel chiffré AES-256</text>
  <!-- Serveur VPN -->
  <rect x="200" y="155" width="100" height="60" rx="8" fill="#1a2744" stroke="#e74c3c" stroke-width="2"/>
  <text x="250" y="180" fill="white" font-size="22" text-anchor="middle">🛡️</text>
  <text x="250" y="200" fill="white" font-size="11" text-anchor="middle">Serveur VPN</text>
  <text x="250" y="213" fill="#e74c3c" font-size="10" text-anchor="middle">Cisco AnyConnect</text>
  <!-- Réseau IZEN -->
  <rect x="390" y="80" width="90" height="70" rx="8" fill="#1a2744" stroke="#27ae60" stroke-width="2"/>
  <text x="435" y="105" fill="white" font-size="28" text-anchor="middle">🏢</text>
  <text x="435" y="125" fill="white" font-size="11" text-anchor="middle">Réseau IZEN</text>
  <text x="435" y="140" fill="#27ae60" font-size="10" text-anchor="middle">Tunis HQ</text>
  <!-- Connexions -->
  <line x1="110" y1="115" x2="125" y2="115" stroke="#3498db" stroke-width="2"/>
  <line x1="375" y1="115" x2="390" y2="115" stroke="#3498db" stroke-width="2"/>
  <line x1="250" y1="130" x2="250" y2="155" stroke="#27ae60" stroke-width="2" stroke-dasharray="4,3"/>
  <!-- Étapes AnyConnect -->
  <rect x="20" y="230" width="460" height="35" rx="6" fill="#0d1b2a" stroke="#3498db" stroke-width="1"/>
  <text x="30" y="245" fill="#3498db" font-size="11" font-weight="bold">Étapes :</text>
  <text x="105" y="245" fill="white" font-size="10">① Ouvrir AnyConnect</text>
  <text x="240" y="245" fill="white" font-size="10">② Entrer l'IP du serveur</text>
  <text x="375" y="245" fill="white" font-size="10">③ Se connecter</text>
  <text x="105" y="258" fill="rgba(255,255,255,0.5)" font-size="9">Cisco AnyConnect Secure Mobility</text>
  <text x="250" y="258" fill="rgba(255,255,255,0.5)" font-size="9">vpn.izen.tn</text>
  <text x="375" y="258" fill="#27ae60" font-size="9">✅ Identifiants IZEN</text>
</svg>"""


def _svg_software_repair() -> str:
    return """<svg viewBox="0 0 500 280" xmlns="http://www.w3.org/2000/svg" font-family="Arial,sans-serif">
  <rect width="500" height="280" fill="#1a1a2e" rx="12"/>
  <text x="250" y="28" fill="#e67e22" font-size="15" font-weight="bold" text-anchor="middle">🔧 Réparation Logiciel — Étapes de diagnostic</text>
  <!-- Étape 1 -->
  <rect x="20" y="50" width="130" height="80" rx="8" fill="#2d1f0e" stroke="#e67e22" stroke-width="1.5"/>
  <text x="85" y="72" fill="#e67e22" font-size="11" font-weight="bold" text-anchor="middle">① Fermer & Relancer</text>
  <text x="85" y="90" fill="white" font-size="28" text-anchor="middle">🔄</text>
  <text x="85" y="115" fill="rgba(255,255,255,0.7)" font-size="10" text-anchor="middle">Fermer complètement</text>
  <text x="85" y="127" fill="rgba(255,255,255,0.7)" font-size="10" text-anchor="middle">via Gestionnaire des tâches</text>
  <!-- Flèche -->
  <line x1="152" y1="90" x2="172" y2="90" stroke="#e67e22" stroke-width="2" marker-end="url(#arrowO)"/>
  <defs><marker id="arrowO" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#e67e22"/></marker></defs>
  <!-- Étape 2 -->
  <rect x="175" y="50" width="130" height="80" rx="8" fill="#2d1f0e" stroke="#e67e22" stroke-width="1.5"/>
  <text x="240" y="72" fill="#e67e22" font-size="11" font-weight="bold" text-anchor="middle">② Réparation Office</text>
  <text x="240" y="90" fill="white" font-size="28" text-anchor="middle">⚙️</text>
  <text x="240" y="115" fill="rgba(255,255,255,0.7)" font-size="10" text-anchor="middle">Panneau de configuration</text>
  <text x="240" y="127" fill="rgba(255,255,255,0.7)" font-size="10" text-anchor="middle">→ Programmes → Réparer</text>
  <!-- Flèche -->
  <line x1="307" y1="90" x2="327" y2="90" stroke="#e67e22" stroke-width="2" marker-end="url(#arrowO)"/>
  <!-- Étape 3 -->
  <rect x="330" y="50" width="150" height="80" rx="8" fill="#2d1f0e" stroke="#e67e22" stroke-width="1.5"/>
  <text x="405" y="72" fill="#e67e22" font-size="11" font-weight="bold" text-anchor="middle">③ Réinstallation</text>
  <text x="405" y="90" fill="white" font-size="28" text-anchor="middle">📦</text>
  <text x="405" y="115" fill="rgba(255,255,255,0.7)" font-size="10" text-anchor="middle">Désinstaller puis</text>
  <text x="405" y="127" fill="rgba(255,255,255,0.7)" font-size="10" text-anchor="middle">réinstaller depuis portal.office.com</text>
  <!-- Commandes utiles -->
  <rect x="20" y="155" width="460" height="90" rx="8" fill="#0d0d1a" stroke="#7c6ff7" stroke-width="1.5"/>
  <text x="40" y="175" fill="#7c6ff7" font-size="12" font-weight="bold">💻 Commandes utiles (Win+R → cmd) :</text>
  <rect x="30" y="182" width="205" height="22" rx="4" fill="#1e1e3a"/>
  <text x="40" y="197" fill="#27ae60" font-size="11" font-family="Courier New">sfc /scannow</text>
  <text x="245" y="197" fill="rgba(255,255,255,0.5)" font-size="10">← Répare les fichiers système</text>
  <rect x="30" y="208" width="205" height="22" rx="4" fill="#1e1e3a"/>
  <text x="40" y="223" fill="#27ae60" font-size="11" font-family="Courier New">DISM /Online /Cleanup-Image</text>
  <text x="245" y="223" fill="rgba(255,255,255,0.5)" font-size="10">← Répare l'image Windows</text>
  <text x="250" y="240" fill="rgba(255,255,255,0.3)" font-size="10" text-anchor="middle">Nova — Agent IT Support IZEN</text>
</svg>"""


def _svg_hardware_check() -> str:
    return """<svg viewBox="0 0 500 280" xmlns="http://www.w3.org/2000/svg" font-family="Arial,sans-serif">
  <rect width="500" height="280" fill="#0d1f0d" rx="12"/>
  <text x="250" y="28" fill="#2ecc71" font-size="15" font-weight="bold" text-anchor="middle">🖥️ Diagnostic PC Lent — Checklist</text>
  <defs><marker id="arrowG" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#2ecc71"/></marker></defs>
  <!-- Checklist items -->
  <rect x="20" y="45" width="220" height="40" rx="6" fill="#1a3a1a" stroke="#2ecc71" stroke-width="1"/>
  <text x="40" y="60" fill="#2ecc71" font-size="13">☐</text>
  <text x="60" y="60" fill="white" font-size="11">RAM utilisée (Ctrl+Maj+Échap)</text>
  <text x="60" y="75" fill="rgba(255,255,255,0.5)" font-size="10">Gestionnaire des tâches → Performances</text>
  <rect x="260" y="45" width="220" height="40" rx="6" fill="#1a3a1a" stroke="#2ecc71" stroke-width="1"/>
  <text x="280" y="60" fill="#2ecc71" font-size="13">☐</text>
  <text x="300" y="60" fill="white" font-size="11">Espace disque libre</text>
  <text x="300" y="75" fill="rgba(255,255,255,0.5)" font-size="10">Ce PC → Disque C: → &gt;15% libre requis</text>
  <rect x="20" y="95" width="220" height="40" rx="6" fill="#1a3a1a" stroke="#f39c12" stroke-width="1"/>
  <text x="40" y="110" fill="#f39c12" font-size="13">☐</text>
  <text x="60" y="110" fill="white" font-size="11">Processus suspects</text>
  <text x="60" y="125" fill="rgba(255,255,255,0.5)" font-size="10">Gestionnaire des tâches → CPU élevé ?</text>
  <rect x="260" y="95" width="220" height="40" rx="6" fill="#1a3a1a" stroke="#f39c12" stroke-width="1"/>
  <text x="280" y="110" fill="#f39c12" font-size="13">☐</text>
  <text x="300" y="110" fill="white" font-size="11">Programmes au démarrage</text>
  <text x="300" y="125" fill="rgba(255,255,255,0.5)" font-size="10">Gestionnaire des tâches → Démarrage</text>
  <rect x="20" y="145" width="220" height="40" rx="6" fill="#1a3a1a" stroke="#e74c3c" stroke-width="1"/>
  <text x="40" y="160" fill="#e74c3c" font-size="13">☐</text>
  <text x="60" y="160" fill="white" font-size="11">Mise à jour Windows</text>
  <text x="60" y="175" fill="rgba(255,255,255,0.5)" font-size="10">Paramètres → Windows Update</text>
  <rect x="260" y="145" width="220" height="40" rx="6" fill="#1a3a1a" stroke="#e74c3c" stroke-width="1"/>
  <text x="280" y="160" fill="#e74c3c" font-size="13">☐</text>
  <text x="300" y="160" fill="white" font-size="11">Analyse antivirus</text>
  <text x="300" y="175" fill="rgba(255,255,255,0.5)" font-size="10">Windows Defender → Analyse complète</text>
  <!-- Commande rapide -->
  <rect x="20" y="200" width="460" height="50" rx="8" fill="#0a150a" stroke="#2ecc71" stroke-width="1.5"/>
  <text x="40" y="218" fill="#2ecc71" font-size="11" font-weight="bold">⚡ Nettoyage rapide (Win+R) :</text>
  <rect x="30" y="224" width="160" height="20" rx="4" fill="#1e3a1e"/>
  <text x="40" y="238" fill="#2ecc71" font-size="11" font-family="Courier New">cleanmgr</text>
  <text x="200" y="238" fill="rgba(255,255,255,0.6)" font-size="10">→ Nettoyage de disque</text>
  <rect x="280" y="224" width="190" height="20" rx="4" fill="#1e3a1e"/>
  <text x="290" y="238" fill="#2ecc71" font-size="11" font-family="Courier New">msconfig → Démarrage</text>
</svg>"""


def _svg_security_alert() -> str:
    return """<svg viewBox="0 0 500 280" xmlns="http://www.w3.org/2000/svg" font-family="Arial,sans-serif">
  <rect width="500" height="280" fill="#1a0a0a" rx="12"/>
  <text x="250" y="28" fill="#e74c3c" font-size="15" font-weight="bold" text-anchor="middle">🚨 Alerte Sécurité — Phishing &amp; Cybermenaces</text>
  <!-- Signaux d'alerte -->
  <rect x="20" y="45" width="145" height="100" rx="8" fill="#2d0a0a" stroke="#e74c3c" stroke-width="2"/>
  <text x="92" y="65" fill="#e74c3c" font-size="11" font-weight="bold" text-anchor="middle">❌ Signaux DANGER</text>
  <text x="35" y="82" fill="#ff6b6b" font-size="10">⚠️ Expéditeur inconnu</text>
  <text x="35" y="97" fill="#ff6b6b" font-size="10">⚠️ Fautes d'orthographe</text>
  <text x="35" y="112" fill="#ff6b6b" font-size="10">⚠️ Liens suspects</text>
  <text x="35" y="127" fill="#ff6b6b" font-size="10">⚠️ Demande identifiants</text>
  <text x="35" y="142" fill="#ff6b6b" font-size="10">⚠️ Urgence artificielle</text>
  <!-- Email phishing simulé -->
  <rect x="180" y="45" width="175" height="100" rx="8" fill="#0d0d0d" stroke="#f39c12" stroke-width="1.5"/>
  <rect x="180" y="45" width="175" height="22" rx="8" fill="#2d1f0a"/>
  <text x="267" y="61" fill="#f39c12" font-size="10" text-anchor="middle">📧 De: security@micros0ft.com</text>
  <text x="267" y="80" fill="white" font-size="10" text-anchor="middle">Votre compte va être</text>
  <text x="267" y="93" fill="white" font-size="10" text-anchor="middle">SUSPENDU dans 24h !</text>
  <rect x="200" y="102" width="135" height="22" rx="4" fill="#e74c3c"/>
  <text x="267" y="118" fill="white" font-size="11" text-anchor="middle" font-weight="bold">Cliquez ici MAINTENANT</text>
  <text x="267" y="138" fill="#e74c3c" font-size="22" text-anchor="middle">⛔</text>
  <!-- Actions à faire -->
  <rect x="370" y="45" width="110" height="100" rx="8" fill="#0a2d0a" stroke="#27ae60" stroke-width="2"/>
  <text x="425" y="65" fill="#27ae60" font-size="11" font-weight="bold" text-anchor="middle">✅ À FAIRE</text>
  <text x="385" y="82" fill="#2ecc71" font-size="10">1. Ne pas cliquer</text>
  <text x="385" y="97" fill="#2ecc71" font-size="10">2. Ne pas répondre</text>
  <text x="385" y="112" fill="#2ecc71" font-size="10">3. Signaler à IT</text>
  <text x="385" y="127" fill="#2ecc71" font-size="10">4. Supprimer</text>
  <text x="385" y="142" fill="#2ecc71" font-size="10">5. Changer MDP</text>
  <!-- Contact urgence -->
  <rect x="20" y="165" width="460" height="50" rx="8" fill="#2d0a0a" stroke="#e74c3c" stroke-width="2"/>
  <text x="250" y="183" fill="#e74c3c" font-size="12" font-weight="bold" text-anchor="middle">🚨 INCIDENT SÉCURITÉ CRITIQUE — Contacter IT immédiatement</text>
  <text x="250" y="200" fill="white" font-size="11" text-anchor="middle">support@izen.tn | Poste 101 | SLA : 15 minutes</text>
  <text x="250" y="248" fill="rgba(255,255,255,0.3)" font-size="10" text-anchor="middle">Nova — Agent IT Security IZEN</text>
</svg>"""


def _svg_email_config() -> str:
    return """<svg viewBox="0 0 500 280" xmlns="http://www.w3.org/2000/svg" font-family="Arial,sans-serif">
  <rect width="500" height="280" fill="#0a1628" rx="12"/>
  <text x="250" y="28" fill="#3498db" font-size="15" font-weight="bold" text-anchor="middle">📧 Configuration Outlook — Serveurs IZEN</text>
  <!-- IMAP/POP config -->
  <rect x="20" y="45" width="225" height="120" rx="8" fill="#0d1f35" stroke="#3498db" stroke-width="1.5"/>
  <text x="132" y="65" fill="#3498db" font-size="12" font-weight="bold" text-anchor="middle">📥 Réception (IMAP)</text>
  <text x="35" y="84" fill="rgba(255,255,255,0.7)" font-size="10">Serveur :</text>
  <text x="110" y="84" fill="white" font-size="10" font-family="Courier New">mail.izen.tn</text>
  <text x="35" y="100" fill="rgba(255,255,255,0.7)" font-size="10">Port SSL :</text>
  <text x="110" y="100" fill="#2ecc71" font-size="10" font-family="Courier New">993</text>
  <text x="35" y="116" fill="rgba(255,255,255,0.7)" font-size="10">Chiffrement :</text>
  <text x="110" y="116" fill="#2ecc71" font-size="10" font-family="Courier New">SSL/TLS</text>
  <text x="35" y="132" fill="rgba(255,255,255,0.7)" font-size="10">Login :</text>
  <text x="110" y="132" fill="white" font-size="10" font-family="Courier New">prenom.nom@izen.tn</text>
  <text x="35" y="150" fill="rgba(255,255,255,0.5)" font-size="9">Authentification : Mot de passe normal</text>
  <rect x="255" y="45" width="225" height="120" rx="8" fill="#0d1f35" stroke="#e67e22" stroke-width="1.5"/>
  <text x="367" y="65" fill="#e67e22" font-size="12" font-weight="bold" text-anchor="middle">📤 Envoi (SMTP)</text>
  <text x="270" y="84" fill="rgba(255,255,255,0.7)" font-size="10">Serveur :</text>
  <text x="345" y="84" fill="white" font-size="10" font-family="Courier New">smtp.izen.tn</text>
  <text x="270" y="100" fill="rgba(255,255,255,0.7)" font-size="10">Port TLS :</text>
  <text x="345" y="100" fill="#f39c12" font-size="10" font-family="Courier New">587</text>
  <text x="270" y="116" fill="rgba(255,255,255,0.7)" font-size="10">Chiffrement :</text>
  <text x="345" y="116" fill="#f39c12" font-size="10" font-family="Courier New">STARTTLS</text>
  <text x="270" y="132" fill="rgba(255,255,255,0.7)" font-size="10">Login :</text>
  <text x="345" y="132" fill="white" font-size="10" font-family="Courier New">prenom.nom@izen.tn</text>
  <text x="270" y="150" fill="rgba(255,255,255,0.5)" font-size="9">Auth : Identifiants IZEN standard</text>
  <!-- Chemin Outlook -->
  <rect x="20" y="180" width="460" height="60" rx="8" fill="#0a1628" stroke="#7c6ff7" stroke-width="1.5"/>
  <text x="40" y="198" fill="#7c6ff7" font-size="11" font-weight="bold">📍 Dans Outlook :</text>
  <text x="40" y="214" fill="rgba(255,255,255,0.8)" font-size="10">Fichier → Ajouter un compte → Configuration manuelle → IMAP</text>
  <text x="40" y="229" fill="rgba(255,255,255,0.5)" font-size="10">Problème persistant ? Vider le cache Outlook : fermer, supprimer dossier AppData\Local\Microsoft\Outlook</text>
</svg>"""


def _svg_it_support() -> str:
    return """<svg viewBox="0 0 500 280" xmlns="http://www.w3.org/2000/svg" font-family="Arial,sans-serif">
  <rect width="500" height="280" fill="#1a1a2e" rx="12"/>
  <text x="250" y="28" fill="#7c6ff7" font-size="15" font-weight="bold" text-anchor="middle">🤖 Nova — Agent IT Support IZEN</text>
  <!-- Centre : Nova -->
  <circle cx="250" cy="130" r="45" fill="#2d2b55" stroke="#7c6ff7" stroke-width="2"/>
  <text x="250" y="120" font-size="30" text-anchor="middle">🤖</text>
  <text x="250" y="145" fill="white" font-size="12" text-anchor="middle" font-weight="bold">Nova</text>
  <text x="250" y="160" fill="rgba(255,255,255,0.6)" font-size="10" text-anchor="middle">AI IT Agent</text>
  <!-- Services autour -->
  <rect x="20" y="80" width="100" height="40" rx="8" fill="#2d2b55" stroke="#3498db" stroke-width="1"/>
  <text x="70" y="97" fill="white" font-size="10" text-anchor="middle">📚 Base de</text>
  <text x="70" y="110" fill="white" font-size="10" text-anchor="middle">connaissances</text>
  <line x1="121" y1="100" x2="200" y2="118" stroke="#3498db" stroke-width="1" stroke-dasharray="4,3"/>
  <rect x="380" y="80" width="100" height="40" rx="8" fill="#2d2b55" stroke="#27ae60" stroke-width="1"/>
  <text x="430" y="97" fill="white" font-size="10" text-anchor="middle">🎫 Création de</text>
  <text x="430" y="110" fill="white" font-size="10" text-anchor="middle">tickets IT</text>
  <line x1="379" y1="100" x2="300" y2="118" stroke="#27ae60" stroke-width="1" stroke-dasharray="4,3"/>
  <rect x="20" y="170" width="100" height="40" rx="8" fill="#2d2b55" stroke="#e67e22" stroke-width="1"/>
  <text x="70" y="187" fill="white" font-size="10" text-anchor="middle">🖼️ Images &amp;</text>
  <text x="70" y="200" fill="white" font-size="10" text-anchor="middle">vidéos tutos</text>
  <line x1="121" y1="185" x2="200" y2="155" stroke="#e67e22" stroke-width="1" stroke-dasharray="4,3"/>
  <rect x="380" y="170" width="100" height="40" rx="8" fill="#2d2b55" stroke="#e74c3c" stroke-width="1"/>
  <text x="430" y="187" fill="white" font-size="10" text-anchor="middle">🔊 Réponses</text>
  <text x="430" y="200" fill="white" font-size="10" text-anchor="middle">vocales TTS</text>
  <line x1="379" y1="185" x2="300" y2="155" stroke="#e74c3c" stroke-width="1" stroke-dasharray="4,3"/>
  <text x="250" y="250" fill="rgba(255,255,255,0.4)" font-size="10" text-anchor="middle">IZEN IT Support — Tunis, Tunisie</text>
</svg>"""


# ============================================================
# FONCTION PRINCIPALE D'ENRICHISSEMENT
# ============================================================

def enrich_response_with_media(category: str, question: str, answer: str) -> dict:
    """
    Enrichit une réponse Nova avec :
    - Une image/schéma explicatif (SVG ou URL)
    - Une vidéo YouTube tutoriel pertinente
    
    Retourne un dict avec les clés 'image' .
    """
    media = {"image": None}
    
    # Récupérer l'image explicative
    try:
        media["image"] = get_explainer_image(category, question)
    except Exception as e:
        print(f"⚠️  Image non disponible: {e}")
    
    
    
    return media


# ============================================================
# TEST RAPIDE
# ============================================================

if __name__ == "__main__":
    test_cases = [
        ("password", "Mon mot de passe est expiré"),
        ("vpn", "Je n'arrive pas à me connecter au VPN"),
        ("security", "J'ai reçu un email de phishing"),
    ]
    
    for cat, question in test_cases:
        print(f"\n🔍 Test catégorie: {cat}")
        media = enrich_response_with_media(cat, question, "")
        
        if media["image"]:
            src = media["image"].get("source", "unknown")
            print(f"  ✅ Image ({src}): {media['image'].get('description', 'N/A')}")
        
