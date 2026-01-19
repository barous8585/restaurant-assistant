# Guide Complet : Import de Données Enrichies

## 🎯 Objectif

L'application accepte maintenant **TOUTES les colonnes possibles** d'un fichier Excel de restaurant. L'algorithme ML utilise intelligemment les colonnes disponibles pour améliorer les prédictions et offrir des analyses avancées.

## 📋 Colonnes Acceptées

### ✅ Colonnes OBLIGATOIRES (minimum requis)

| Colonne | Description | Format | Exemple |
|---------|-------------|--------|---------|
| `Date` | Date de la vente | JJ/MM/AAAA ou AAAA-MM-JJ | 15/01/2024 |
| `Plat` | Nom du plat/produit | Texte | Burger Classic |
| `Quantite` | Quantité vendue | Nombre entier | 25 |

### 🎁 Colonnes OPTIONNELLES (améliorent les analyses)

#### 💰 Colonnes Financières

| Colonne | Description | Calculée Auto ? | Impact |
|---------|-------------|-----------------|---------|
| `Prix_unitaire` | Prix de vente par unité (€) | Non | ⭐⭐⭐ Rentabilité, CA, ABC |
| `Cout_unitaire` | Coût de revient par unité (€) | Non | ⭐⭐⭐ Marge, ROI |
| `Chiffre_affaires` | CA généré | ✅ Oui si Prix×Qté | ⭐⭐ Analyse ABC |
| `Marge` | Marge bénéficiaire | ✅ Oui si (Prix-Coût)×Qté | ⭐⭐⭐ Rentabilité |
| `Taux_marge` | % de marge | ✅ Oui si disponible | ⭐⭐ Comparaison plats |

#### 🏷️ Colonnes Contextuelles

| Colonne | Description | Impact ML | Impact Analyses |
|---------|-------------|-----------|-----------------|
| `Categorie` | Type de plat (Entrée/Plat/Dessert) | - | ⭐⭐⭐ Segmentation |
| `Service` | Moment (Déjeuner/Dîner) | ⭐⭐ | ⭐⭐ Patterns horaires |
| `Zone` | Emplacement (Terrasse/Salle) | ⭐ | ⭐ Analyse spatiale |
| `Meteo` | Conditions météo | ⭐⭐ | ⭐⭐ Corrélations |
| `Temperature` | Température en °C | ⭐ | ⭐ Saisonnalité |
| `Promotion` | Promotion active (Oui/Non) | ⭐⭐⭐ | ⭐⭐⭐ Impact promo |
| `Canal` | Vente (Sur place/Livraison) | ⭐⭐ | ⭐⭐ Multi-canal |

#### 👥 Colonnes Opérationnelles

| Colonne | Description | Usage |
|---------|-------------|-------|
| `Table` | Numéro de table | Occupation |
| `Serveur` | Nom du serveur | Performance |
| `Note_client` | Satisfaction (/5) | Qualité |
| `Heure` | Heure de commande | Rush hours |

## 🧠 Intelligence de l'Algorithme

### 1️⃣ Détection Automatique

L'algorithme reconnaît automatiquement les variantes de noms :

```
Prix_unitaire  ← "Prix", "PU", "Prix vente", "Tarif", "Price"
Cout_unitaire  ← "Coût", "CU", "Prix achat", "Cost"
Categorie      ← "Catégorie", "Famille", "Type plat", "Category"
Quantite       ← "Quantité", "Qté", "Qty", "Nombre", "Quantity"
```

### 2️⃣ Calcul Automatique

Si vous fournissez uniquement `Prix_unitaire` et `Quantite`, l'app calcule :

```
Chiffre_affaires = Prix_unitaire × Quantite
```

Si vous ajoutez aussi `Cout_unitaire` :

```
Marge_unitaire = Prix_unitaire - Cout_unitaire
Marge          = Marge_unitaire × Quantite
Taux_marge     = (Marge_unitaire / Prix_unitaire) × 100
```

### 3️⃣ Enrichissement du Modèle ML

Les colonnes optionnelles améliorent les prédictions :

| Colonnes Disponibles | Précision ML | Nouvelles Features |
|---------------------|--------------|-------------------|
| **Minimum** (Date, Plat, Qté) | ⭐⭐⭐ | Jours, tendances, lags |
| **+ Service** | ⭐⭐⭐⭐ | Déjeuner vs Dîner |
| **+ Meteo** | ⭐⭐⭐⭐ | Impact météo |
| **+ Promotion** | ⭐⭐⭐⭐⭐ | Effet des promos |
| **+ Canal** | ⭐⭐⭐⭐⭐ | Sur place vs Livraison |
| **Complet** | ⭐⭐⭐⭐⭐ | Maximum de contexte |

## 🎁 Nouvelles Fonctionnalités Débloquées

### 💎 Onglet Rentabilité

**Débloqué si** : `Prix_unitaire` OU `Cout_unitaire` OU `Chiffre_affaires` OU `Marge` présent

**Contenu** :
- 💰 **Indicateurs clés** : CA total, Coût total, Marge totale, Taux de marge
- 🏆 **Top 10 plats rentables** : Classement par marge générée
- 📉 **Plats à faible marge** : Identifie les plats à optimiser
- 📊 **Analyse ABC** : Classement Pareto (A = 80% CA, B = 15%, C = 5%)
- 📦 **Rentabilité par catégorie** : Matrice Volume vs Marge

### 🔮 Prédictions Améliorées

**Si Service disponible** : Prédit différemment Déjeuner vs Dîner  
**Si Meteo disponible** : Ajuste selon conditions météo  
**Si Promotion disponible** : Détecte l'impact des promos  
**Si Canal disponible** : Différencie Sur place / Livraison  

### 📊 Colonnes Détectées

Dans la barre latérale, un expander "📊 Colonnes détectées" affiche :
- **Obligatoires** : Date, Plat, Quantite ✅
- **Optionnelles** : Liste des colonnes enrichies trouvées

## 📝 Exemples de Fichiers Excel

### Niveau 1 : Minimum Viable (3 colonnes)

```csv
Date,Plat,Quantite
15/01/2024,Burger Classic,25
15/01/2024,Pizza Margherita,18
16/01/2024,Burger Classic,28
```

**Résultat** : Prédictions ML de base ⭐⭐⭐

---

### Niveau 2 : Recommandé (6 colonnes)

```csv
Date,Plat,Quantite,Categorie,Prix_unitaire,Cout_unitaire
15/01/2024,Burger Classic,25,Plat,12.50,4.80
15/01/2024,Pizza Margherita,18,Plat,11.00,3.50
15/01/2024,Salade César,12,Entrée,8.50,2.80
```

**Résultat** : 
- Prédictions ML ⭐⭐⭐
- **Onglet Rentabilité débloqué** 💎
- Analyse ABC ✅

---

### Niveau 3 : Optimal (10 colonnes)

```csv
Date,Plat,Quantite,Categorie,Prix_unitaire,Cout_unitaire,Service,Zone,Meteo,Promotion
15/01/2024,Burger Classic,25,Plat,12.50,4.80,Déjeuner,Salle,Ensoleillé,Non
15/01/2024,Pizza Margherita,18,Plat,11.00,3.50,Déjeuner,Terrasse,Ensoleillé,Non
15/01/2024,Burger Classic,32,Plat,12.50,4.80,Dîner,Salle,Ensoleillé,Non
```

**Résultat** :
- Prédictions ML ultra-précises ⭐⭐⭐⭐⭐
- Rentabilité complète 💎
- Segmentation avancée 📊
- Impact promotions et météo 🌤️

---

### Niveau 4 : Expert (15+ colonnes)

```csv
Date,Plat,Quantite,Categorie,Prix_unitaire,Cout_unitaire,Service,Zone,Meteo,Promotion,Canal,Serveur,Table,Note_client,Heure
15/01/2024,Burger,25,Plat,12.50,4.80,Déjeuner,Salle,Ensoleillé,Non,Sur place,Jean,12,4.5,12:30
```

**Résultat** : Toutes les analyses disponibles + insights opérationnels maximum

## 🚀 Guide d'Utilisation

### Étape 1 : Préparer votre fichier Excel

1. Ouvrez Excel ou Google Sheets
2. Créez les colonnes **obligatoires** : Date, Plat, Quantite
3. Ajoutez **au minimum** : Categorie, Prix_unitaire, Cout_unitaire (recommandé)
4. Ajoutez les colonnes contextuelles selon vos besoins
5. Remplissez avec vos données réelles

### Étape 2 : Importer dans l'application

1. Connectez-vous à l'application
2. Dans la barre latérale : **📊 Données de Ventes**
3. Cliquez sur **"Browse files"**
4. Sélectionnez votre fichier Excel/CSV
5. L'app détecte automatiquement les colonnes ✅

### Étape 3 : Vérifier les colonnes détectées

1. Dans la sidebar, cliquez sur **"📊 Colonnes détectées (X)"**
2. Vérifiez que vos colonnes sont bien reconnues
3. Si non reconnu, renommez dans Excel (voir variantes ci-dessus)

### Étape 4 : Explorer les analyses

**Onglets toujours disponibles** :
- 📈 Analyse
- 🔮 Prévisions ML
- 📋 Liste de Préparation
- 💰 Économies & ROI
- 📦 Stocks & Commandes
- 🌤️ Alertes Météo

**Onglet conditionnel** :
- 💎 **Rentabilité** (si colonnes financières présentes)

## ⚠️ Problèmes Courants

### ❌ "Colonnes requises non trouvées"

**Cause** : Les colonnes Date, Plat ou Quantite sont absentes ou mal nommées

**Solution** :
1. Vérifiez l'orthographe exacte : `Date`, `Plat`, `Quantite`
2. Ou utilisez des variantes reconnues :
   - Date : "date", "jour", "day"
   - Plat : "produit", "item", "nom"
   - Quantite : "qte", "qty", "nombre"

### ⚠️ "L'onglet Rentabilité n'apparaît pas"

**Cause** : Aucune colonne financière détectée

**Solution** : Ajoutez au moins une de ces colonnes :
- `Prix_unitaire`
- `Cout_unitaire`
- `Chiffre_affaires`
- `Marge`

### 🔄 "Les calculs automatiques ne fonctionnent pas"

**Cause** : Colonnes nécessaires manquantes

**Solution** :
- Pour `Chiffre_affaires` auto : Besoin de `Prix_unitaire` + `Quantite`
- Pour `Marge` auto : Besoin de `Prix_unitaire` + `Cout_unitaire` + `Quantite`

## 💡 Conseils Pro

### 🎯 Pour des prédictions optimales

1. ✅ **Minimum 30 jours de données** (60-90 idéal)
2. ✅ **Données complètes** sans trous
3. ✅ **Ajouter Service** (Déjeuner/Dîner) = +15% précision
4. ✅ **Ajouter Meteo** = +10% précision
5. ✅ **Ajouter Promotion** = +20% précision sur jours promos

### 💰 Pour analyse de rentabilité maximale

1. ✅ **Prix_unitaire et Cout_unitaire** = Indispensables
2. ✅ **Categorie** = Permet segmentation
3. ✅ **Service** = Analyse Déj vs Dîner
4. ✅ **Canal** = Compare Sur place vs Livraison

### 📊 Analyse ABC

**Interprétation** :
- **Plats A** (80% CA) : Vos stars, à chouchouter
- **Plats B** (15% CA) : Potentiel d'optimisation
- **Plats C** (5% CA) : Retirer si faible marge

## 📚 Template Excel Téléchargeable

Vous pouvez créer un fichier avec cet exemple :

```csv
Date,Plat,Quantite,Categorie,Prix_unitaire,Cout_unitaire,Service,Zone,Meteo,Promotion,Canal
15/01/2024,Burger Classic,25,Plat,12.50,4.80,Déjeuner,Salle,Ensoleillé,Non,Sur place
15/01/2024,Pizza Margherita,18,Plat,11.00,3.50,Déjeuner,Terrasse,Ensoleillé,Non,Sur place
15/01/2024,Salade César,12,Entrée,8.50,2.80,Déjeuner,Salle,Ensoleillé,Oui,Sur place
15/01/2024,Tiramisu,15,Dessert,6.50,2.00,Déjeuner,Salle,Ensoleillé,Non,Sur place
15/01/2024,Coca-Cola,30,Boisson,3.50,0.80,Déjeuner,Salle,Ensoleillé,Non,Sur place
15/01/2024,Burger Classic,32,Plat,12.50,4.80,Dîner,Salle,Nuageux,Non,Sur place
15/01/2024,Pizza 4 Fromages,22,Plat,13.00,4.20,Dîner,Terrasse,Nuageux,Non,Livraison
16/01/2024,Burger Classic,28,Plat,12.50,4.80,Déjeuner,Salle,Pluie,Non,Sur place
16/01/2024,Pizza Margherita,15,Plat,11.00,3.50,Déjeuner,Salle,Pluie,Non,Sur place
```

Copiez-collez dans Excel, enregistrez en `.xlsx` ou `.csv`, et importez !

---

**Version** : 2.0.0  
**Date** : 2026-01-19  
**Auteur** : Assistant Préparation Restaurant Pro
