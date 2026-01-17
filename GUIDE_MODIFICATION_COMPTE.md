# 🔐 Guide de Modification de Compte

## ✅ Nouvelles Fonctionnalités Ajoutées

Vous et vos utilisateurs pouvez maintenant modifier :
- ✅ **Mot de passe**
- ✅ **Nom d'utilisateur (identifiant)**

---

## 👥 Pour les Utilisateurs (Clients)

### 📍 Où trouver les paramètres ?

1. **Connectez-vous** avec votre compte
2. Dans la **sidebar** (barre latérale gauche)
3. Cliquez sur **"⚙️ Paramètres du Compte"**

---

### 🔑 Changer le Mot de Passe

**Étapes** :

1. Ouvrir "⚙️ Paramètres du Compte"
2. Section "🔑 Changer le Mot de Passe"
3. Remplir :
   - **Mot de passe actuel** : Votre mot de passe actuel
   - **Nouveau mot de passe** : Votre nouveau mot de passe (min 6 caractères)
   - **Confirmer nouveau mot de passe** : Retaper le nouveau
4. Cliquer sur **"Modifier le mot de passe"**
5. ✅ Confirmation : "Mot de passe modifié avec succès !"

**Sécurité** :
- Le mot de passe actuel est vérifié
- Le nouveau mot de passe doit faire au moins 6 caractères
- Les deux nouveaux mots de passe doivent correspondre
- Hashage SHA256 automatique

---

### 👤 Changer le Nom d'Utilisateur

**Étapes** :

1. Ouvrir "⚙️ Paramètres du Compte"
2. Section "👤 Changer le Nom d'Utilisateur"
3. Remplir :
   - **Nouveau nom d'utilisateur** : Le nouveau nom souhaité
   - **Mot de passe pour confirmer** : Votre mot de passe actuel
4. Cliquer sur **"Modifier le nom d'utilisateur"**
5. ✅ Confirmation : "Nom d'utilisateur modifié avec succès !"
6. ✅ Message : "Votre nouveau nom d'utilisateur : **nouveau_nom**"

**Important** :
- Le nouveau nom ne doit pas déjà exister
- Toutes vos données (restaurants, recettes) sont conservées
- Vos fichiers sont automatiquement renommés
- Vous serez automatiquement reconnecté avec le nouveau nom

---

## 🔐 Pour l'Administrateur (Vous)

### 📍 Où trouver les paramètres ?

1. **Connexion Admin** : Onglet "🔐 Admin" → Mot de passe : `admin`
2. Dans la **sidebar** (barre latérale gauche)
3. Cliquez sur **"⚙️ Paramètres Admin"**

---

### 🔐 Changer le Mot de Passe Admin

**Pourquoi c'est différent ?**  
Le mot de passe admin est stocké directement dans le code (ligne 26 de `app.py`). Pour le changer, vous devez générer un nouveau hash et le copier dans le code.

**Étapes** :

1. Ouvrir "⚙️ Paramètres Admin"
2. Section "🔐 Changer le Mot de Passe Admin"
3. Remplir :
   - **Nouveau mot de passe admin** : Votre nouveau mot de passe (min 6 caractères)
   - **Confirmer** : Retaper le mot de passe
4. Cliquer sur **"Générer le nouveau hash"**
5. ✅ Un code s'affiche :
   ```python
   ADMIN_PASSWORD_HASH = "a1b2c3d4e5f6..."
   ```
6. **Copiez cette ligne**
7. **Modifiez `app.py` ligne 26** :
   - Ouvrez `app.py` dans un éditeur
   - Ligne 26, remplacez l'ancienne ligne par la nouvelle
8. **Sauvegardez et redéployez** :
   ```bash
   git add app.py
   git commit -m "security: Changer mot de passe admin"
   git push origin main
   ```
9. Attendez 3-5 min (redéploiement Streamlit Cloud)
10. ✅ Votre nouveau mot de passe admin fonctionne !

**⚠️ Important** :
- Notez votre nouveau mot de passe dans un endroit sûr
- Le hash est irréversible (si vous perdez le mot de passe, recommencez)
- Ne partagez jamais votre mot de passe admin

---

## 🧪 Tester en Local

```bash
# Terminal
cd /Users/thiernoousmanebarry/Desktop/Restaurant

# Créer utilisateurs de démo
python3 create_demo_users.py

# Tester les fonctions
python3 test_account_changes.py

# Résultat attendu :
# ✅ TOUS LES TESTS RÉUSSIS !
```

---

## 💡 Exemples d'Utilisation

### Exemple 1 : Utilisateur oublie son mot de passe

**Problème** : Le client a oublié son mot de passe.

**Solution** : 
1. Vous (admin) pouvez le réinitialiser manuellement :
   - Ouvrir `restaurant_data/users.pkl` en Python
   - Changer le hash du mot de passe
   - OU créer une fonction de réinitialisation (à implémenter)
2. Ou demandez au client de créer un nouveau compte

### Exemple 2 : Utilisateur veut renommer son compte

**Problème** : "pizza_lyon" veut devenir "pizzeria_lyon_officiel"

**Solution** :
1. Se connecter avec "pizza_lyon"
2. Paramètres du Compte → Changer le nom d'utilisateur
3. Entrer "pizzeria_lyon_officiel"
4. Confirmer avec mot de passe
5. ✅ Tous les restaurants sont conservés

### Exemple 3 : Vous voulez sécuriser l'admin

**Problème** : Le mot de passe "admin" par défaut est trop simple

**Solution** :
1. Connexion Admin
2. Paramètres Admin → Générer nouveau hash
3. Entrer un mot de passe fort : "RestaurantAdmin2026!@#"
4. Copier le hash dans `app.py` ligne 26
5. Git push
6. ✅ Admin sécurisé

---

## 🔒 Sécurité

### Mots de Passe

- **Hashage SHA256** : Tous les mots de passe sont hashés (irréversibles)
- **Minimum 6 caractères** : Imposé pour tous les comptes
- **Vérification actuelle** : L'ancien mot de passe est vérifié avant changement
- **Confirmation** : Double saisie pour éviter les erreurs

### Noms d'Utilisateur

- **Unicité** : Le système vérifie que le nouveau nom n'existe pas déjà
- **Conservation des données** : Tous les restaurants sont automatiquement transférés
- **Renommage atomique** : Les fichiers sont renommés en même temps que l'utilisateur

---

## ❓ FAQ

### Q : Puis-je changer mon mot de passe plusieurs fois ?
**R** : Oui, autant de fois que vous voulez !

### Q : Que se passe-t-il si je change mon nom d'utilisateur ?
**R** : Tous vos restaurants et données sont conservés. Seul le nom de connexion change.

### Q : Puis-je revenir à mon ancien nom d'utilisateur ?
**R** : Oui, si personne d'autre ne l'a pris entre temps.

### Q : Le mot de passe admin peut-il être changé depuis l'interface ?
**R** : Partiellement. L'interface génère le hash, mais vous devez le copier dans le code et redéployer.

### Q : Que faire si un utilisateur oublie son mot de passe ?
**R** : Actuellement, il doit créer un nouveau compte. Vous pouvez aussi implémenter une fonction de réinitialisation par email (à développer).

### Q : Les mots de passe sont-ils stockés en clair ?
**R** : Non ! Tous les mots de passe sont hashés en SHA256 (irréversible).

---

## 🚀 Déploiement

**Statut** : ✅ **DÉJÀ PUSHÉ SUR GITHUB**

Le code a été poussé avec le commit :
```
feat: Ajouter modification mot de passe et identifiant pour utilisateurs et admin
```

**Streamlit Cloud** va automatiquement redéployer l'application dans 3-5 minutes.

---

## 📱 Vérification sur l'Application Déployée

Dans **3-5 minutes** :

1. Rafraîchir : https://restaurant-assistant-9ntcwrmlqglgv7an2haihy.streamlit.app
2. Créer un compte test
3. Vérifier la sidebar → "⚙️ Paramètres du Compte" existe
4. Tester changement de mot de passe
5. Tester changement de nom d'utilisateur
6. Connexion Admin → "⚙️ Paramètres Admin" existe
7. Tester génération hash admin

---

## 📝 Fichiers Modifiés

1. **app.py** :
   - Fonctions : `change_user_password()`, `change_username()`, `change_admin_password()`
   - Interface utilisateur : lignes 772-817
   - Interface admin : lignes 644-663

2. **test_account_changes.py** :
   - Tests automatisés de toutes les fonctions

---

**Date d'ajout** : 2026-01-17  
**Commit** : `f16f93b`  
**Statut** : ✅ En cours de déploiement sur Streamlit Cloud
