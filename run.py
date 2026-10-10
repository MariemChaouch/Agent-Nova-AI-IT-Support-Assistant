"""
run.py — Point d'entrée principal du Projet KM Avatar AI
Lance l'interface Streamlit
"""

import subprocess
import sys
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent


def create_default_avatar():
    """Crée l'avatar par défaut si nécessaire."""
    avatar_path = BASE_DIR / "data" / "avatar_photo.jpg"
    if not avatar_path.exists():
        try:
            sys.path.insert(0, str(BASE_DIR / "src"))
            from avatar import create_default_avatar as _create
            _create()
        except Exception as e:
            print(f"⚠️  Avatar par défaut non créé: {e}")


def main():
    print("")
    print("╔═══════════════════════════════════════════╗")
    print("║    PROJET KM — AVATAR AI ASSISTANT       ║")
    print("╚═══════════════════════════════════════════╝")
    print("")
    

    
    
    
    
    
    # 3. Créer avatar par défaut
    print("▶ Vérification de l'avatar...")
    create_default_avatar()
    print("  ✅ Avatar configuré")
    
    # 4. Lancer Streamlit
    print("")
    print("🌐 Lancement de l'interface web...")
    print("   → Ouvre ton navigateur sur : http://localhost:8501")
    print("")
    print("   (Ctrl+C pour arrêter)")
    print("")
    
    interface_path = BASE_DIR / "src" / "interface.py"
    
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        str(interface_path),
        "--server.port=8501",
        "--server.address=localhost",
        "--server.headless=true",
        "--browser.gatherUsageStats=false",
        "--theme.primaryColor=#764ba2",
        "--theme.backgroundColor=#ffffff",
    ]
    
    try:
        subprocess.run(cmd, cwd=str(BASE_DIR))
    except KeyboardInterrupt:
        print("\n\n👋 Au revoir !")


if __name__ == "__main__":
    main()
