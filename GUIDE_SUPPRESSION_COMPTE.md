# 🗑️ Guide de Suppression de Compte Utilisateur (Admin)

## ✅ Nouvelle Fonctionnalité

Vous pouvez maintenant **supprimer complètement** les comptes d'utilisateurs qui ne sont plus clients depuis l'interface admin.

---

## 🔐 Accès (Réservé Admin)

Cette fonctionnalité est **réservée exclusivement à l'administrateur** (vous).

**Accès** :
```
Connexion Admin → Tableau de bord → Détails par Utilisateur
```

---

## 🗑️ Comment Supprimer un Compte

### Étape 1 : Accéder à l'interface admin

1. Allez sur votre application
2. Onglet **"🔐 Admin"**
3. Mot de passe : `admin` (ou votre mot de passe personnalisé)
4. Connexion Admin

### Étape 2 : Sélectionner l'utilisateur

1. Descendez jusqu'à **"📈 Détails par Utilisateur"**
2. Dans le menu déroulant, **sélectionnez l'utilisateur** à supprimer
3. Les détails de l'utilisateur s'affichent (restaurants, plan, facture)

### Étape 3 : Cliquer sur Supprimer

1. En haut à droite, cliquez sur le bouton **"🗑️ Supprimer [nom_utilisateur]"**
2. Un message d'avertissement s'affiche :

```
⚠️ ATTENTION : Vous êtes sur le point de supprimer définitivement le compte [nom_utilisateur]

Cette action est IRRÉVERSIBLE et supprimera :
- ❌ Le compte utilisateur
- ❌ Tous ses restaurants (X restaurant(s))
- ❌ Toutes ses données (ventes, recettes, etc.)
```

### Étape 4 : Confirmer la suppression

1. **Lisez attentivement l'avertissement**
2. Si vous êtes sûr :
   - Cliquez sur **"✅ Confirmer la suppression"**
   - ✅ Message : "Compte '[nom_utilisateur]' supprimé avec succès"
   - 🎈 Animation de confirmation
   - La page se rafraîchit automatiquement
3. Si vous changez d'avis :
   - Cliquez sur **"❌ Annuler"**
   - Aucune suppression n'est effectuée

---

## ⚠️ ATTENTION : Action Irréversible

### Ce qui est supprimé définitivement :

1. **Le compte utilisateur** dans `users.pkl`
   - Nom d'utilisateur
   - Mot de passe hashé
   - Informations du restaurant principal

2. **Toutes les données** dans `{username}_data.pkl`
   - Liste de tous ses restaurants
   - Données de ventes importées
   - Recettes configurées
   - Historique complet

3. **Aucune sauvegarde automatique**
   - Les données ne peuvent **PAS** être récupérées
   - Il n'y a **PAS** de corbeille
   - La suppression est **IMMÉDIATE et PERMANENTE**

---

## 💡 Quand Utiliser Cette Fonctionnalité ?

### Cas d'usage recommandés :

✅ **Client a cessé son abonnement**
```
Exemple : Le restaurant a fermé définitivement
Action : Supprimer le compte pour nettoyer la base de données
```

✅ **Compte de test ou doublon**
```
Exemple : Utilisateur a créé plusieurs comptes par erreur
Action : Supprimer les doublons
```

✅ **Impayés récurrents**
```
Exemple : Client ne paie plus depuis plusieurs mois
Action : Supprimer le compte après mise en demeure
```

✅ **Demande explicite du client (RGPD)**
```
Exemple : Client demande la suppression de ses données
Action : Supprimer pour conformité RGPD (droit à l'oubli)
```

✅ **Nettoyage de la base de données**
```
Exemple : Comptes inactifs depuis plus d'un an
Action : Archiver puis supprimer
```

---

## ❌ Quand NE PAS Utiliser

### Évitez de supprimer dans ces cas :

❌ **Client en retard de paiement temporaire**
```
Alternative : Suspendre l'accès, envoyer rappel
```

❌ **Client inactif mais compte actif**
```
Alternative : Relance commerciale, proposition d'offre
```

❌ **Dispute commerciale en cours**
```
Alternative : Attendre la résolution du litige
```

❌ **Compte avec historique de paiement important**
```
Alternative : Archiver les données avant suppression
```

---

## 🔄 Workflow Recommandé Avant Suppression

### Checklist avant de supprimer :

1. **Vérifier les paiements**
   - [ ] Le client est-il à jour de ses paiements ?
   - [ ] Y a-t-il des factures impayées ?

2. **Contacter le client**
   - [ ] Email/SMS de préavis (ex: 30 jours)
   - [ ] Proposition de réactivation si applicable
   - [ ] Confirmation écrite de la demande de suppression (si RGPD)

3. **Archiver les données (optionnel)**
   - [ ] Export CSV/Excel du compte
   - [ ] Sauvegarde manuelle si nécessaire pour comptabilité
   - [ ] Copie du fichier `{username}_data.pkl` dans un dossier d'archives

4. **Supprimer le compte**
   - [ ] Vérifier que c'est le bon utilisateur
   - [ ] Confirmer la suppression
   - [ ] Vérifier que le compte n'apparaît plus dans la liste

---

## 📊 Impact sur les Statistiques Admin

Après suppression d'un compte :

- **👥 Total Utilisateurs** : Diminue de 1
- **🏢 Total Restaurants** : Diminue du nombre de restaurants du client
- **💵 Revenu Mensuel Total** : Diminue de sa facture mensuelle
- **📈 Projection Annuelle** : Recalculée automatiquement

**Les statistiques sont mises à jour instantanément** après suppression.

---

## 🧪 Tester en Local

```bash
# Terminal
cd /Users/thiernoousmanebarry/Desktop/Restaurant

# Créer utilisateurs de démo
python3 create_demo_users.py

# Tester la fonction de suppression
python3 test_delete_account.py

# Résultat attendu :
# ✅ Utilisateur créé
# ✅ Utilisateur supprimé
# ✅ Fichier de données supprimé
# ✅ Nombre d'utilisateurs diminué de 1
```

---

## 🔧 Détails Techniques

### Fonction Backend

```python
def delete_user_account(username):
    """Supprimer complètement un compte utilisateur (admin seulement)"""
    users_file = os.path.join(DATA_DIR, "users.pkl")
    
    # Charger et supprimer de users.pkl
    with open(users_file, 'rb') as f:
        users = pickle.load(f)
    
    del users[username]
    
    with open(users_file, 'wb') as f:
        pickle.dump(users, f)
    
    # Supprimer le fichier de données
    user_data_file = os.path.join(DATA_DIR, f"{username}_data.pkl")
    if os.path.exists(user_data_file):
        os.remove(user_data_file)
    
    return True, f"Compte '{username}' supprimé avec succès"
```

### Fichiers Supprimés

1. **Entrée dans `users.pkl`** : L'utilisateur est retiré du dictionnaire
2. **Fichier `{username}_data.pkl`** : Supprimé complètement du système

---

## 📋 Exemple de Processus Complet

### Scénario : "Restaurant Le Gourmet" ferme définitivement

**Jour 1** : Restaurant annonce la fermeture
- Notification reçue par email

**Jour 7** : Vérification
- Client confirme la fermeture définitive
- Demande suppression de ses données (RGPD)

**Jour 14** : Archivage (optionnel)
- Export Excel de toutes ses données de facturation
- Copie manuelle de `le_gourmet_data.pkl` dans `/archives/2026/`

**Jour 15** : Suppression
1. Connexion Admin
2. Détails par Utilisateur → Sélectionner "le_gourmet"
3. Vérifier :
   - 3 restaurants
   - Plan Standard (49€)
   - Aucune facture impayée
4. Cliquer "🗑️ Supprimer le_gourmet"
5. Lire l'avertissement
6. Confirmer la suppression
7. ✅ Compte supprimé

**Résultat** :
- Compte "le_gourmet" n'existe plus
- Revenu mensuel : -49€
- Base de données nettoyée

---

## ❓ FAQ

### Q : Puis-je récupérer un compte supprimé ?
**R** : Non. La suppression est irréversible. Il faut créer un nouveau compte.

### Q : Les données sont-elles vraiment supprimées ?
**R** : Oui. Les fichiers sont supprimés du système. Seules les sauvegardes manuelles (si faites) subsistent.

### Q : Puis-je supprimer plusieurs comptes d'un coup ?
**R** : Non. La suppression se fait un par un pour plus de sécurité.

### Q : Un utilisateur peut-il supprimer son propre compte ?
**R** : Non. Seul l'admin peut supprimer des comptes. Les utilisateurs peuvent seulement modifier leurs informations.

### Q : Que se passe-t-il si je supprime par erreur ?
**R** : Rien n'est récupérable automatiquement. Si vous avez fait une archive manuelle, vous pouvez restaurer. Sinon, le client doit recréer un compte.

### Q : La suppression affecte-t-elle les factures déjà émises ?
**R** : Non. Les factures déjà envoyées restent valides. Seules les données dans l'application sont supprimées.

### Q : Dois-je supprimer un compte RGPD immédiatement ?
**R** : Légalement, vous avez 30 jours. Mais il est recommandé de le faire rapidement après archivage des données nécessaires à la comptabilité.

---

## 🚀 Déploiement

**Statut** : ✅ **DÉJÀ PUSHÉ SUR GITHUB**

Le code a été poussé avec le commit :
```
feat: Ajouter suppression de compte utilisateur pour l'admin
```

**Streamlit Cloud** va automatiquement redéployer l'application dans 3-5 minutes.

---

## 📱 Vérification Après Déploiement

Dans **3-5 minutes** :

1. Rafraîchir : https://restaurant-assistant-9ntcwrmlqglgv7an2haihy.streamlit.app
2. Connexion Admin
3. Créer un compte test "test_suppression"
4. Détails par Utilisateur → Sélectionner "test_suppression"
5. Bouton "🗑️ Supprimer test_suppression" doit apparaître
6. Cliquer → Message d'avertissement s'affiche
7. Confirmer → Compte supprimé
8. Vérifier que le compte n'apparaît plus dans la liste

---

**Date d'ajout** : 2026-01-17  
**Commit** : `e055b37`  
**Statut** : ✅ En cours de déploiement sur Streamlit Cloud
