# BASE DE CONNAISSANCES IT — Accès & Mots de Passe
# Source : Support IT IZEN
# Version : 1.0 | Catégorie : 🔑 Accès & Mots de passe

---

## 1. RÉINITIALISATION DE MOT DE PASSE WINDOWS / ACTIVE DIRECTORY

### Procédure pour l'employé
1. Appuie sur **Ctrl+Alt+Suppr** sur ton poste
2. Clique sur **"Modifier un mot de passe"**
3. Saisis l'ancien mot de passe, puis le nouveau (2 fois)
4. Le mot de passe doit contenir : 8 caractères min, 1 majuscule, 1 chiffre, 1 caractère spécial

### Si le compte est bloqué (trop de tentatives)
- Contacte le support IT : **support@izen.tn** ou **Poste 101**
- L'IT peut débloquer le compte via Active Directory Console
- Délai de déverrouillage automatique : 30 minutes

### Réinitialisation par IT (côté admin)
```
Active Directory → Utilisateurs → Clic droit → Réinitialiser le mot de passe
Cocher "L'utilisateur doit changer le mot de passe à la prochaine ouverture de session"
```

---

## 2. COMPTE BLOQUÉ — DIAGNOSTIC

| Symptôme | Cause probable | Solution |
|----------|---------------|----------|
| "Compte bloqué" au login | 5 tentatives échouées | Attendre 30 min ou appeler IT |
| "Mot de passe expiré" | Politique 90 jours | Changer via Ctrl+Alt+Suppr |
| "Accès refusé" sur un dossier | Droits insuffisants | Demander accès à son manager |
| Impossible de se connecter au VPN | Compte AD désactivé | Contacter support@izen.tn |

---

## 3. ACCÈS REFUSÉ À UN DOSSIER RÉSEAU

### Diagnostic rapide
1. Vérifie si le dossier est bien sur le réseau : `\\serveur\partage`
2. Assure-toi d'être connecté au VPN si en télétravail
3. Clique droit sur le dossier → Propriétés → Sécurité → vérifier tes droits

### Demande d'accès
- Envoie un mail à **support@izen.tn** avec :
  - Chemin complet du dossier
  - Type d'accès demandé (lecture / écriture)
  - Validation de ton manager en copie

---

## 4. GESTION DES COMPTES — ONBOARDING / OFFBOARDING

### Création de compte (nouvel employé)
- Délai : 24h avant la date d'arrivée
- Formulaire à remplir par RH → transmis à IT
- Comptes créés : Windows AD, Email, VPN, applications métier

### Désactivation de compte (départ)
- Désactivation immédiate le jour du départ
- Archivage des données : 30 jours
- Contact : support@izen.tn | Poste 101
