# 🔐 Guide Administrateur - Système de Facturation

## 🎯 Vue d'Ensemble

Le système d'administration vous permet de surveiller tous les utilisateurs, leurs restaurants, et calculer automatiquement les factures mensuelles.

---

## 🔑 Accès Administrateur

### Connexion

1. Allez sur l'application : https://restaurant-assistant-9ntcwrmlqglgv7an2haihy.streamlit.app
2. Cliquez sur l'onglet **"🔐 Admin"**
3. Entrez le mot de passe administrateur : **`admin`**
4. Cliquez sur **"Connexion Admin"**

> ⚠️ **Important** : Changez le mot de passe par défaut en production !

---

## 📊 Tableau de Bord

Une fois connecté, vous verrez :

### Métriques Principales (en haut)

- **👥 Total Utilisateurs** : Nombre total de comptes créés
- **🏢 Total Restaurants** : Somme de tous les restaurants de tous les utilisateurs
- **💰 Clients Payants** : Utilisateurs avec 2+ restaurants (Plan Pro ou Enterprise)
- **🆓 Gratuits** : Utilisateurs avec 1 seul restaurant

### Liste des Utilisateurs

Tableau complet affichant :
- Nom d'utilisateur
- Nombre de restaurants
- Plan actuel (Gratuit / Pro / Enterprise)
- Facture mensuelle (€)
- Ville principale
- Date d'inscription

### Analyse de Facturation

- **💵 Revenu Mensuel Total** : Somme de toutes les factures
- **📈 Projection Annuelle (MRR x12)** : Revenu annuel estimé
- **Graphique en camembert** : Répartition des plans

---

## 💰 Grille Tarifaire

Le système calcule automatiquement les factures selon cette grille :

| Nombre de Restaurants | Plan | Prix Mensuel |
|----------------------|------|--------------|
| 1 restaurant | **Gratuit** | 0 € |
| 2-3 restaurants | **Pro** | 49 € |
| 4+ restaurants | **Enterprise** | 149 € |

### Logique de Facturation

```python
if nb_restaurants <= 1:
    facture = 0€     # Gratuit
elif nb_restaurants <= 3:
    facture = 49€    # Pro
else:
    facture = 149€   # Enterprise
```

**À chaque fois qu'un utilisateur ajoute un restaurant**, sa facture est automatiquement recalculée.

---

## 📥 Export des Données

### Export CSV

1. Cliquez sur **"⬇️ Télécharger CSV"**
2. Fichier généré : `facturation_YYYYMMDD.csv`
3. Importable dans Excel, Google Sheets, etc.

### Export Excel

1. Cliquez sur **"⬇️ Télécharger Excel"**
2. Fichier généré : `facturation_YYYYMMDD.xlsx`
3. Format natif Excel avec formatage

**Contenu des exports** :
- Utilisateur
- Nombre de Restaurants
- Plan
- Facture (€)
- Ville Principale
- Date Inscription

---

## 📈 Détails par Utilisateur

### Vue Détaillée

1. Sélectionnez un utilisateur dans le menu déroulant
2. Consultez la liste complète de ses restaurants :
   - Nom du restaurant
   - Ville
   - Coût moyen par portion
   - Statut des données (Oui/Non)

### Métriques Individuelles

- 🏢 **Nombre de Restaurants**
- 📋 **Plan actuel**
- 💰 **Facture Mensuelle**

---

## 🔄 Scénarios d'Usage

### Scénario 1 : Nouveau client gratuit

1. Client crée un compte avec 1 restaurant
2. **Facture = 0€** (Plan Gratuit)
3. Utilisateur apparaît dans la liste Admin

### Scénario 2 : Upgrade vers Pro

1. Client ajoute un 2ème restaurant
2. **Facture passe automatiquement à 49€** (Plan Pro)
3. Visible immédiatement dans le tableau de bord

### Scénario 3 : Upgrade vers Enterprise

1. Client a déjà 3 restaurants (Plan Pro - 49€)
2. Il ajoute un 4ème restaurant
3. **Facture passe automatiquement à 149€** (Plan Enterprise)

### Scénario 4 : Groupe de restaurants

1. Chaîne de restaurants crée un compte
2. Ajoute 10 restaurants d'un coup
3. **Facture = 149€** (Plan Enterprise)
4. Revenue Mensuel Total augmente de 149€

---

## 🧪 Tests avec Utilisateurs Démo

Pour tester le système localement, utilisez le script fourni :

```bash
python3 create_demo_users.py
```

**Créé automatiquement** :
- `restaurant_paris` : 1 resto → 0€
- `pizza_lyon` : 2 restos → 49€
- `group_restos` : 5 restos → 149€

**Total attendu** : 198€/mois

Testez ensuite :
```bash
python3 test_admin.py
```

---

## 🔐 Sécurité

### Changement du Mot de Passe Admin

**⚠️ IMPORTANT : Changez le mot de passe par défaut AVANT déploiement !**

1. Ouvrez `app.py`
2. Ligne 26, modifiez :
```python
ADMIN_PASSWORD_HASH = "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"  # "admin"
```

3. Générez un nouveau hash SHA256 :
```python
import hashlib
nouveau_mdp = "votre_nouveau_mot_de_passe_securise"
hash_mdp = hashlib.sha256(nouveau_mdp.encode()).hexdigest()
print(hash_mdp)
```

4. Remplacez le hash dans le code
5. Commitez et pushez

### Isolation des Données

- Chaque utilisateur a son propre fichier : `restaurant_data/{username}_data.pkl`
- L'admin peut **voir** les stats mais **pas modifier** les données utilisateurs
- Les mots de passe sont hashés en SHA256 (irréversible)

---

## 📊 Rapports Mensuels

### Processus Recommandé

1. **Début du mois** :
   - Connexion Admin
   - Export Excel des facturations
   - Envoi des factures aux clients

2. **Suivi mensuel** :
   - Vérifier les nouveaux utilisateurs
   - Identifier les upgrades (Gratuit → Pro → Enterprise)
   - Calculer le MRR (Monthly Recurring Revenue)

3. **Analyses** :
   - Taux de conversion Gratuit → Payant
   - Nombre moyen de restaurants par client payant
   - Projection annuelle

---

## 💡 Fonctionnalités Futures (Optionnelles)

- [ ] Date d'inscription réelle (actuellement fixe)
- [ ] Historique des changements de plan
- [ ] Email automatique lors d'un upgrade
- [ ] Génération de factures PDF
- [ ] Intégration Stripe pour paiement automatique
- [ ] Dashboard analytics avancé (Grafana, Metabase)

---

## 🆘 Support

En cas de problème :
1. Vérifiez que le fichier `restaurant_data/users.pkl` existe
2. Testez avec les utilisateurs démo
3. Consultez les logs Streamlit
4. Contactez le développeur

---

## 📝 Notes Techniques

### Structure des Fichiers

```
restaurant_data/
├── users.pkl                    # Credentials de tous les utilisateurs
├── {username}_data.pkl          # Données restaurants par utilisateur
└── [exclu du Git via .gitignore]
```

### Fonctions Clés

- `get_all_users_stats()` : Liste tous les utilisateurs avec statistiques
- `calculate_invoice(nb_restaurants)` : Calcule facture selon grille tarifaire
- `load_restaurant_data(username)` : Charge restaurants d'un utilisateur
- `hash_password(password)` : Hachage SHA256 sécurisé

---

**Version** : 1.0  
**Dernière mise à jour** : 2026-01-17
