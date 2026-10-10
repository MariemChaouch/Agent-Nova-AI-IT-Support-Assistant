# BASE DE CONNAISSANCES IT — Matériel
# Source : Support IT IZEN
# Version : 1.0 | Catégorie : 🖥️ Matériel

---

## 1. PC LENT — DIAGNOSTIC ET OPTIMISATION

### Causes fréquentes
- Trop de programmes au démarrage
- Disque dur presque plein (< 10% d'espace libre)
- Mémoire RAM insuffisante
- Malware ou virus

### Optimisation rapide
1. **Gestionnaire des tâches** (Ctrl+Shift+Échap) → onglet Performances → identifier la ressource saturée
2. **Libérer de l'espace disque** : Nettoyage de disque (cleanmgr) → cocher tout → OK
3. **Désactiver les démarrages automatiques** : Gestionnaire des tâches → Démarrage → désactiver les non essentiels
4. **Redémarrer** le PC (pas juste "mettre en veille")
5. **Défragmenter le disque** (HDD uniquement, pas SSD) : chercher "Défragmenter" dans Windows

### Si le PC reste lent
- Signaler à IT via **support@izen.tn** ou Poste 101
- IT peut diagnostiquer, ajouter de la RAM, ou remplacer le matériel

---

## 2. IMPRIMANTE HP — PROBLÈMES

### L'imprimante n'imprime pas
1. Vérifie que l'imprimante est **allumée** et **connectée** (câble ou WiFi)
2. Vérifie le niveau d'encre/toner : bouton état sur l'imprimante
3. Vide la file d'impression : Panneau de configuration → Périphériques → clic droit sur l'imprimante → **Afficher les impressions en cours** → Annuler tout
4. Redémarre l'imprimante (éteindre/allumer)
5. Réinstalle le pilote HP depuis hp.com si nécessaire

### Imprimante hors ligne
- Clic droit sur l'imprimante → **Définir comme imprimante par défaut**
- Décocher **"Utiliser l'imprimante hors connexion"** si coché
- Redémarre le service Spouleur : CMD admin → `net stop spooler && net start spooler`

---

## 3. ÉCRAN NOIR / PROBLÈMES D'AFFICHAGE

### Écran noir au démarrage
1. Vérifie les câbles (HDMI, DisplayPort, VGA) — les débrancher et rebrancher
2. Teste avec un autre câble ou un autre port
3. Appuie sur **Win+P** pour basculer le mode affichage (si le PC tourne mais écran noir)
4. Redémarre en mode sans échec : Shift + Redémarrer → Dépannage → Options avancées → Mode sans échec

### Double écran qui ne fonctionne pas
- **Win+P** → choisir "Étendre" pour activer le double écran
- Clic droit bureau → Paramètres d'affichage → Détecter
- Vérifier les connexions des câbles

---

## 4. DEMANDE DE MATÉRIEL / REMPLACEMENT

- PC défectueux, matériel endommagé → contacter **support@izen.tn**
- Inclure : description du problème, numéro de série du matériel, urgence
- SLA matériel : remplacement sous 24-48h en cas de panne critique
