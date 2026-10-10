# BASE DE CONNAISSANCES IT — Logiciels
# Source : Support IT IZEN
# Version : 1.0 | Catégorie : 💻 Logiciels

---

## 1. MICROSOFT OFFICE — CRASH / BLOCAGE

### Office ne s'ouvre pas / plante au démarrage
1. Ferme tous les processus Office : **Gestionnaire des tâches** → chercher WINWORD, EXCEL, OUTLOOK → Fin de tâche
2. Lance Office en **mode sans échec** : Win+R → `winword /safe`
3. Si ça fonctionne en mode sans échec → un complément pose problème
4. Désactiver les compléments : Fichier → Options → Compléments → Gérer les compléments COM → Décocher tout
5. Relancer normalement

### Réparation Office
- Panneau de configuration → Programmes → Microsoft Office → **Modifier → Réparation rapide**
- Si ça ne suffit pas : **Réparation en ligne** (nécessite internet, ~30 min)

### Fichier Office corrompu
- Ouvre Word/Excel → Fichier → Ouvrir → Browse
- Au lieu de cliquer "Ouvrir", clique sur la **flèche** à côté → **"Ouvrir et réparer"**

---

## 2. MICROSOFT OUTLOOK — PROBLÈMES

### Outlook ne reçoit/n'envoie plus d'emails
1. Vérifie la connexion internet et VPN
2. Clique sur **Envoyer/Recevoir** (F9)
3. Vérifie le mode hors connexion : onglet Envoyer/Recevoir → **Travailler hors connexion** (doit être décoché)
4. Vider le cache Outlook : fermer Outlook → supprimer les fichiers `.ost` dans `%localappdata%\Microsoft\Outlook`

### Problème de profil Outlook
- Panneau de configuration → Mail → Afficher les profils → Ajouter un nouveau profil
- Ou contacter IT pour reconfiguration

---

## 3. MICROSOFT TEAMS — AUDIO / VIDÉO

### Micro ne fonctionne pas dans Teams
1. Teams → Paramètres (icône engrenage) → Périphériques
2. Sélectionne le bon micro dans la liste déroulante
3. Clique "Effectuer un appel test"
4. Vérifie que Windows autorise Teams à accéder au micro : Paramètres Windows → Confidentialité → Microphone → Teams = Activé

### Caméra ne fonctionne pas dans Teams
1. Paramètres Teams → Périphériques → sélectionner la caméra
2. Vérifier les autorisations Windows : Paramètres → Confidentialité → Caméra → Teams = Activé
3. Fermer les autres apps qui utilisent la caméra (Zoom, etc.)

### Teams lent / qui plante
- Vider le cache : fermer Teams → `%appdata%\Microsoft\Teams` → supprimer tous les fichiers sauf `storage.json`
- Réinstaller Teams si le problème persiste

---

## 4. INSTALLATION DE LOGICIELS

- Les employés ne peuvent pas installer de logiciels sans autorisation IT
- Faire une demande à **support@izen.tn** avec :
  - Nom du logiciel
  - Justification métier
  - Validation du manager
- Délai de traitement : 48h
