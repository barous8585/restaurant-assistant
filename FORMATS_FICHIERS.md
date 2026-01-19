# 📋 Formats de Fichiers Supportés

## Vue d'ensemble

L'application accepte plusieurs formats de données pour une flexibilité maximale. Cette page détaille tous les formats supportés.

---

## 🎯 Formats de Date Supportés

### Format 1 : Date Complète (Recommandé)

**Colonne** : `Date`  
**Format** : `YYYY-MM-DD`, `DD/MM/YYYY`, etc.  
**Exemple** :

```csv
Date,Plat,Quantite
2024-01-15,Burger Classic,25
2024-01-16,Pizza Margherita,18
2024-01-17,Salade César,12
```

**Avantages** :
- ✅ Précision maximale
- ✅ Prédictions jour par jour
- ✅ Analyse tendances fine

---

### Format 2 : Mois + Année (Nouveau !)

**Colonnes** : `Mois` + `Annee`  
**Format** : Mois = 1-12, Année = YYYY  
**Exemple** :

```csv
Mois,Annee,Plat,Quantite,Prix_unitaire,Cout_unitaire
1,2024,Burger Classic,750,12.50,4.80
2,2024,Burger Classic,820,12.50,4.80
3,2024,Burger Classic,880,12.50,4.80
```

**Avantages** :
- ✅ Données agrégées mensuelles
- ✅ Simplifie la saisie
- ✅ Compatible avec rapports comptables

**Conversion automatique** :
- L'application crée automatiquement `Date = 1er jour du mois`
- Exemple : Mois=1, Année=2024 → Date=2024-01-01

**⚠️ Limitation** :
- Prédictions au niveau mensuel uniquement
- Pas de détection patterns quotidiens/hebdomadaires

**📄 Fichier d'exemple** : `exemple_mois_annee.csv`

---

### Format 3 : Mois Uniquement (Année Courante)

**Colonne** : `Mois` (sans Année)  
**Format** : 1-12  
**Exemple** :

```csv
Mois,Plat,Quantite
1,Burger Classic,750
2,Burger Classic,820
3,Burger Classic,880
```

**Conversion automatique** :
- L'application utilise l'année en cours
- Exemple : Mois=1 → Date=2026-01-01 (si on est en 2026)

**⚠️ Attention** :
- Fonctionne seulement pour données de l'année en cours
- Peut causer erreurs si données historiques

---

## 📊 Colonnes Obligatoires

Quel que soit le format choisi, votre fichier DOIT contenir :

| Colonne | Format | Exemple |
|---------|--------|---------|
| **Date** OU **Mois** | Voir ci-dessus | 2024-01-15 OU Mois=1 |
| **Plat** | Texte | "Burger Classic" |
| **Quantite** | Nombre entier | 25 |

---

## 💎 Colonnes Optionnelles (Recommandées)

Pour des prédictions plus précises et analyses financières :

### Colonnes Financières

```csv
Date,Plat,Quantite,Prix_unitaire,Cout_unitaire,Chiffre_affaires,Marge
2024-01-15,Burger,25,12.50,4.80,312.50,192.50
```

| Colonne | Description | Calcul Auto |
|---------|-------------|-------------|
| `Prix_unitaire` | Prix de vente HT | ❌ Non |
| `Cout_unitaire` | Coût de revient | ❌ Non |
| `Chiffre_affaires` | CA total | ✅ Oui (Prix × Quantité) |
| `Marge` | Bénéfice | ✅ Oui (CA - Coût) |
| `Taux_marge` | Marge en % | ✅ Oui ((Marge/CA)×100) |

### Colonnes Contextuelles

```csv
Date,Plat,Quantite,Categorie,Service,Zone,Meteo,Promotion
2024-01-15,Burger,25,Plat,Déjeuner,Salle,Ensoleillé,Non
```

| Colonne | Valeurs Possibles | Impact Prédictions |
|---------|-------------------|-------------------|
| `Categorie` | Entrée, Plat, Dessert, Boisson | +10% précision |
| `Service` | Déjeuner, Dîner, Brunch | +15% précision |
| `Zone` | Salle, Terrasse, Bar | +5% précision |
| `Meteo` | Ensoleillé, Pluie, Nuageux | +20% précision |
| `Promotion` | Oui, Non | +10% précision |
| `Canal` | Sur place, Livraison, Emporter | +8% précision |

### Colonnes Horaires (Prédictions Intra-Journée)

```csv
Date,Heure,Plat,Quantite
2024-01-15,12:30,Burger,15
2024-01-15,13:00,Burger,20
2024-01-15,19:30,Burger,18
```

| Colonne | Format | Impact |
|---------|--------|--------|
| `Heure` | HH:MM (ex: 12:30) | ⚡ Active prédictions temps réel |

**Active** :
- Prédictions heure par heure
- Conseils préparation par service
- Ajustements dynamiques

---

## 🔧 Calculs Automatiques

L'application calcule automatiquement ces colonnes si les données sources sont disponibles :

### 1. Chiffre d'Affaires
```
Chiffre_affaires = Prix_unitaire × Quantite
```
**Requis** : `Prix_unitaire`, `Quantite`

### 2. Coût Total
```
Cout_total = Cout_unitaire × Quantite
```
**Requis** : `Cout_unitaire`, `Quantite`

### 3. Marge Unitaire
```
Marge_unitaire = Prix_unitaire - Cout_unitaire
```
**Requis** : `Prix_unitaire`, `Cout_unitaire`

### 4. Marge Totale
```
Marge = Marge_unitaire × Quantite
OU
Marge = Chiffre_affaires - Cout_total
```
**Requis** : Voir formules ci-dessus

### 5. Taux de Marge
```
Taux_marge = (Marge_unitaire / Prix_unitaire) × 100
```
**Requis** : `Marge_unitaire`, `Prix_unitaire`

### 6. Date (depuis Mois/Année) ⭐ NOUVEAU
```
Date = YYYY-MM-01
```
**Requis** : `Mois` + `Annee` (ou seulement `Mois`)

---

## 📁 Formats de Fichiers Acceptés

| Extension | Description | Support |
|-----------|-------------|---------|
| `.csv` | Valeurs séparées virgules | ✅ Complet |
| `.xlsx` | Excel moderne | ✅ Complet |
| `.xls` | Excel ancien | ✅ Complet |
| `.json` | JSON structuré | ✅ Partiel |
| `.txt` | Texte délimité | ✅ Auto-détection |
| `.pdf` | PDF avec tableaux | ⚠️ Extraction basique |
| `.docx` | Word avec tableaux | ⚠️ Extraction basique |

---

## 🎯 Exemples Complets

### Exemple 1 : Minimum Viable

**Fichier** : `ventes_simple.csv`

```csv
Date,Plat,Quantite
2024-01-15,Burger Classic,25
2024-01-16,Burger Classic,28
2024-01-17,Burger Classic,22
```

**Résultat** :
- ✅ Fonctionne
- ⚠️ Prédictions basiques uniquement

---

### Exemple 2 : Recommandé

**Fichier** : `ventes_complet.csv`

```csv
Date,Plat,Categorie,Quantite,Prix_unitaire,Cout_unitaire,Service
2024-01-15,Burger Classic,Plat,25,12.50,4.80,Déjeuner
2024-01-15,Pizza Margherita,Plat,18,11.00,3.50,Déjeuner
2024-01-15,Salade César,Entrée,12,8.50,2.80,Déjeuner
```

**Résultat** :
- ✅ Prédictions précises
- ✅ Analyses financières
- ✅ Onglet Rentabilité actif

---

### Exemple 3 : Expert (avec Heure)

**Fichier** : `ventes_horaires.csv`

```csv
Date,Heure,Plat,Quantite,Prix_unitaire,Cout_unitaire,Service,Zone,Meteo
2024-01-15,12:00,Burger,10,12.50,4.80,Déjeuner,Salle,Ensoleillé
2024-01-15,12:30,Burger,15,12.50,4.80,Déjeuner,Terrasse,Ensoleillé
2024-01-15,13:00,Burger,8,12.50,4.80,Déjeuner,Salle,Ensoleillé
2024-01-15,19:00,Burger,12,12.50,4.80,Dîner,Salle,Nuageux
```

**Résultat** :
- ✅ Prédictions temps réel
- ✅ Conseils heure par heure
- ✅ Ajustements météo dynamiques

---

### Exemple 4 : Format Mensuel (Nouveau)

**Fichier** : `ventes_mensuelles.csv`

```csv
Mois,Annee,Plat,Quantite,Prix_unitaire,Cout_unitaire
1,2024,Burger Classic,750,12.50,4.80
2,2024,Burger Classic,820,12.50,4.80
3,2024,Burger Classic,880,12.50,4.80
1,2024,Pizza Margherita,580,11.00,3.50
2,2024,Pizza Margherita,620,11.00,3.50
3,2024,Pizza Margherita,690,11.00,3.50
```

**Résultat** :
- ✅ Prédictions mensuelles
- ✅ Analyses financières
- ⚠️ Pas de patterns quotidiens

**➡️ Fichier d'exemple fourni** : `exemple_mois_annee.csv`

---

## 🚨 Erreurs Courantes

### Erreur 1 : "Colonnes requises non trouvées"

**Cause** : Fichier sans `Date` ni `Mois`, ou sans `Plat`/`Quantite`

**Solution** :
1. Vérifiez noms de colonnes (respectez majuscules)
2. Variantes acceptées :
   - Date : `date`, `jour`, `day`
   - Plat : `plat`, `produit`, `item`, `nom`
   - Quantité : `quantite`, `qte`, `qty`, `quantity`

### Erreur 2 : Données mal formatées

**Cause** : Dates invalides, quantités texte, etc.

**Solution** :
- Dates : Format YYYY-MM-DD ou DD/MM/YYYY
- Quantités : Nombres entiers uniquement
- Prix : Nombres décimaux avec `.` (pas `,`)

### Erreur 3 : Fichier trop gros

**Limite** : 200 MB par fichier

**Solution** :
- Filtrez données (derniers 12 mois suffisent)
- Agrégez par jour/semaine
- Utilisez format CSV (plus léger que Excel)

---

## 📞 Besoin d'Aide ?

**Templates disponibles** :
- `exemple_ventes_ml.csv` - Format quotidien complet
- `exemple_mois_annee.csv` - Format mensuel ⭐ NOUVEAU

**Documentation** :
- [Guide Sources de Données](./GUIDE_SOURCES_DONNEES.md)
- [Comprendre Prédictions ML](./COMPRENDRE_PREDICTIONS_ML.md)
- [Template Colonnes](./colonnes_restaurant_template.py)

**Support** : Consultez les exemples ci-dessus ou contactez l'administrateur.

---

**Dernière mise à jour** : 19 janvier 2026  
**Version** : 2.1.0 - Support format mensuel Mois/Année
