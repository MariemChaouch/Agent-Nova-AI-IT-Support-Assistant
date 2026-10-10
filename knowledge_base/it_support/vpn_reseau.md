# BASE DE CONNAISSANCES IT — VPN & Réseau
# Source : Support IT IZEN
# Version : 1.0 | Catégorie : 🌐 VPN & Réseau

---

## 1. CISCO ANYCONNECT — CONNEXION VPN

### Installation (première fois)
1. Télécharge Cisco AnyConnect depuis le portail IT interne
2. Lance l'installeur en tant qu'administrateur
3. Accepte les conditions → Terminer
4. Icône AnyConnect apparaît dans la barre des tâches

### Connexion au VPN IZEN
1. Ouvre **Cisco AnyConnect**
2. Dans le champ "VPN", saisis : `vpn.izen.tn`
3. Clique **Connecter**
4. Saisis ton login AD (prénom.nom) et mot de passe Windows
5. Valide l'authentification MFA sur ton téléphone si demandé

### Déconnexion
- Clic droit sur l'icône AnyConnect → **Déconnecter**
- Toujours déconnecter avant d'éteindre le PC

---

## 2. DÉPANNAGE VPN — PROBLÈMES COURANTS

| Problème | Solution |
|----------|----------|
| "Connexion impossible" | Vérifie ta connexion internet d'abord |
| "Identifiants incorrects" | Réinitialise ton mot de passe AD |
| VPN se déconnecte souvent | Désactive le mode veille sur WiFi |
| "Certificat non approuvé" | Réinstalle AnyConnect depuis le portail IT |
| Lenteur après connexion VPN | Passe en "Split Tunneling" (demander à IT) |

### Étapes de dépannage standard
1. **Vérifier la connexion internet** : ouvre un navigateur, va sur google.com
2. **Redémarrer AnyConnect** : fermer complètement, rouvrir
3. **Vider le cache AnyConnect** : Paramètres → Effacer les données
4. **Redémarrer le PC** : souvent suffisant pour 70% des problèmes
5. **Contacter IT** si le problème persiste : support@izen.tn | Poste 101

---

## 3. PROBLÈMES RÉSEAU — DIAGNOSTIC

### "Internet ne fonctionne pas"
```
Étape 1 : Vérifier le câble Ethernet ou la connexion WiFi
Étape 2 : ipconfig /release puis ipconfig /renew (CMD en admin)
Étape 3 : Vider le cache DNS : ipconfig /flushdns
Étape 4 : Redémarrer le routeur/switch (si accès)
Étape 5 : Contacter IT
```

### Commandes utiles (CMD)
- `ipconfig` → voir l'adresse IP actuelle
- `ping 8.8.8.8` → tester la connexion internet
- `ping serveur-izen` → tester la connexion au serveur
- `tracert vpn.izen.tn` → diagnostiquer le chemin réseau

---

## 4. TÉLÉTRAVAIL — BONNE PRATIQUES

- Toujours connecter le VPN avant d'accéder aux ressources IZEN
- Utiliser un réseau WiFi sécurisé (éviter les réseaux publics)
- Déconnecter le VPN quand non utilisé pour économiser la bande passante
- En cas de problème : appeler le **Poste 101** ou écrire à **support@izen.tn**
