# Prédictions en Temps Réel (Intra-Journée)

## 🎯 Vue d'Ensemble

La fonctionnalité **Prédictions Live** offre des prévisions **heure par heure** pour la journée en cours, avec ajustements dynamiques basés sur :
- 📊 Ventes actuelles de la journée
- 🌤️ Météo en temps réel
- 📈 Tendances par rapport aux journées similaires
- 🕐 Heure actuelle et services restants

---

## ⚡ Fonctionnalités Principales

### 1️⃣ **Dashboard Temps Réel**

Affichage instantané de :
- **Ventes Aujourd'hui** : Total des portions vendues jusqu'à maintenant
- **Impact Météo** : Ajustement basé sur conditions météo (+/- X%)
- **Tendance Ventes** : Comparaison avec moyennes historiques

### 2️⃣ **Recommandations Intelligentes**

Conseils automatiques comme :
- ☀️ "Beau temps chaud : +20% affluence terrasse"
- 🌧️ "Pluie prévue : -15% affluence attendue"
- 🥗 "Température >28°C : Favoriser plats froids et salades (+25%)"
- 📈 "Ventes actuelles +25% vs normal : Augmenter préparations dîner"

### 3️⃣ **Prédictions Horaires (Mode Précis)**

**Activé si** : Colonne 'Heure' présente dans vos données

**Affiche** :
- 📋 Tableau détaillé heure par heure
- 📊 Graphique visuel des prévisions
- 🎯 Conseils de préparation par service (Déjeuner/Dîner)
- ✅ Statut des services (À préparer / En cours / Terminé)

**Exemple de tableau** :
```
Heure  | Service   | Prévu Base | Prévu Ajusté | Confiance
-------|-----------|------------|--------------|----------
12:00  | Déjeuner  | 45         | 52           | Élevée
13:00  | Déjeuner  | 38         | 44           | Élevée
19:00  | Dîner     | 60         | 69           | Élevée
20:00  | Dîner     | 55         | 63           | Moyenne
```

### 4️⃣ **Prédictions Simplifiées (Mode Fallback)**

**Activé si** : Pas de colonne 'Heure' dans les données

**Affiche** :
- 📊 Moyenne journalière du plat
- 🎯 Total prévu aujourd'hui (ajusté météo/tendances)
- 📦 Quantité restante à vendre
- 🍽️ Répartition Déjeuner (55%) / Dîner (45%)

---

## 🧠 Intelligence des Ajustements

### Facteur Météo (weather_factor)

| Conditions | Facteur | Impact |
|-----------|---------|--------|
| ☀️ Ensoleillé chaud (>25°C) | 1.20 | +20% |
| ☀️ Ensoleillé | 1.10 | +10% |
| ☁️ Nuageux | 0.95 | -5% |
| 🌧️ Pluie / Orage | 0.85 | -15% |

**Conseils supplémentaires** :
- 🥗 Si température >28°C → Plats froids +25%
- 🍲 Si température <10°C → Soupes et plats chauds +20%

### Facteur Tendance Ventes (sales_trend_factor)

Comparaison en temps réel vs moyenne historique même jour de semaine :

| Ratio Actuel/Normal | Facteur | Action |
|---------------------|---------|--------|
| >120% | 1.15 | 📈 Augmenter préparations dîner |
| 80-120% | 1.00 | ✅ Ventes dans la normale |
| <80% | 0.90 | 📉 Réduire préparations dîner |

**Calcul intelligent** basé sur heure actuelle :
- Avant 10h : 10% du total journalier attendu
- 12h-14h : 40% du total attendu
- Après 14h : 60% du total attendu

### Facteur Weekend

- 🎉 Weekend (samedi/dimanche) : +15% sur toutes les prédictions horaires
- 📅 Semaine : Pas d'ajustement

---

## 📋 Comment Activer le Mode Précis ?

### Étape 1 : Ajouter Colonne 'Heure'

Dans votre fichier Excel, ajoutez une colonne **'Heure'** :

```csv
Date,Plat,Quantite,Heure
15/01/2024,Burger Classic,5,12:30
15/01/2024,Pizza Margherita,3,12:45
15/01/2024,Burger Classic,8,13:15
15/01/2024,Pizza Margherita,6,19:30
```

**Formats acceptés** :
- ✅ `HH:MM` (12:30, 19:45)
- ✅ `HH:MM:SS` (12:30:00)
- ✅ Timestamp complet

### Étape 2 : Importer les Données

1. Sauvegardez votre fichier Excel
2. Dans l'app : **📊 Données de Ventes** → **Browse files**
3. Sélectionnez votre fichier
4. L'app détecte automatiquement la colonne 'Heure' ✅

### Étape 3 : Accéder à Prédictions Live

1. Ouvrez l'onglet **⚡ Prédictions Live**
2. Vous verrez "✅ Colonne 'Heure' détectée"
3. Sélectionnez un plat
4. Les prédictions horaires s'affichent !

---

## 🎨 Interface Utilisateur

### Section 1 : Indicateurs Temps Réel

```
┌─────────────────────────────────────────────────────┐
│ 🕐 Dimanche 19 Janvier 2026 - 18:30                │
├─────────────────────────────────────────────────────┤
│  📊 Ventes Aujourd'hui    ☀️ Impact Météo   📈 Tendance │
│       125 portions             +10%            +5%    │
└─────────────────────────────────────────────────────┘
```

### Section 2 : Recommandations

```
💡 Recommandations Temps Réel
ℹ️ ☀️ Beau temps : +10% affluence
ℹ️ 📈 Ventes actuelles +5% vs normal: Ventes dans la normale
```

### Section 3 : Prédictions Horaires

**Tableau interactif** avec :
- Heure (19:00, 20:00, 21:00...)
- Service (Déjeuner / Dîner)
- Quantité prévue (base historique)
- Quantité ajustée (avec météo + tendances)
- Niveau de confiance (Élevée / Moyenne / Faible)

**Graphique visuel** :
- Barres bleues claires = Prévu base
- Barres bleues foncées = Prévu ajusté

### Section 4 : Conseils de Préparation

```
🎯 Conseils de Préparation

┌─────────────────────┬─────────────────────┐
│ 🍽️ Déjeuner         │ 🌙 Dîner            │
│ Préparer 52 portions│ Préparer 68 portions│
│ ✅ Service terminé  │ ⚠️ Service en cours  │
└─────────────────────┴─────────────────────┘
```

---

## 🔄 Rafraîchissement Automatique

Option **"🔄 Rafraîchir auto (5min)"** :
- ✅ Activé : Page se recharge toutes les 5 minutes
- 📊 Idéal pour affichage permanent en cuisine
- ⚡ Met à jour ventes actuelles et recommandations

**Usage recommandé** :
- Tablette en cuisine
- Écran d'affichage permanent
- Monitoring en temps réel

---

## 📊 Cas d'Usage Réels

### Scénario 1 : Matin (10h)

**Situation** :
- Heure actuelle : 10:00
- Ventes du matin : 15 portions
- Météo : Ensoleillé, 22°C

**Prédictions Live** :
```
11:00 Déjeuner : 25 portions (Confiance Élevée)
12:00 Déjeuner : 45 portions (Confiance Élevée)
13:00 Déjeuner : 38 portions (Confiance Élevée)
19:00 Dîner    : 60 portions (Confiance Moyenne)
20:00 Dîner    : 55 portions (Confiance Moyenne)
```

**Conseil** : ⏰ À préparer avant 11h00 : 108 portions déjeuner

---

### Scénario 2 : Après-midi (15h)

**Situation** :
- Heure actuelle : 15:00
- Ventes déjeuner : 120 portions (+15% vs normal)
- Météo : Nuageux, pluie prévue ce soir

**Recommandations** :
- 📈 Ventes actuelles +15% vs normal : Augmenter préparations dîner
- 🌧️ Pluie prévue : -15% affluence attendue

**Prédictions ajustées** :
```
Original dîner : 150 portions
Ajusté tendance (+15%) : 172 portions
Ajusté météo pluie (-15%) : 146 portions
→ PRÉPARATION FINALE : 146 portions
```

---

### Scénario 3 : Sans Données Horaires

**Si pas de colonne 'Heure'**, le système utilise :
- 📊 Moyenne journalière : 180 portions
- ☀️ Météo ensoleillée : +10% = 198 portions
- ✅ Ventes normales : +0% = 198 portions

**Répartition** :
- 🍽️ Déjeuner (55%) : 109 portions
- 🌙 Dîner (45%) : 89 portions

---

## 💡 Conseils Pro

### 1. **Qualité des Données Horaires**

Pour prédictions précises :
- ✅ **Minimum 14 jours** de données avec heures
- ✅ **Couvrir tous les services** (déjeuner + dîner)
- ✅ **Plusieurs semaines** pour capturer variations
- ✅ **Inclure weekends** pour facteur weekend

### 2. **Fiabilité des Prédictions**

**Confiance Élevée** = ≥5 jours historiques pour cette heure
**Confiance Moyenne** = 3-4 jours historiques
**Confiance Faible** = <3 jours historiques

→ **Conseil** : Fiez-vous aux heures avec Confiance Élevée

### 3. **Utilisation en Cuisine**

**Workflow recommandé** :
1. **10h** : Consulter prédictions déjeuner → Préparer
2. **14h** : Vérifier ventes déjeuner → Ajuster dîner si tendance forte
3. **17h** : Consulter prédictions dîner finales → Préparer
4. **21h** : Bilans et insights pour lendemain

### 4. **Cas Spéciaux**

**Événements exceptionnels non détectés** (concert, match) :
- Utilisez la prédiction de base
- Ajoutez manuellement +20-30% si événement majeur
- Consultez réservations si disponibles

**Jours fériés** :
- Le système détecte automatiquement patterns jours fériés passés
- Si premier jour férié = Utilisez prédiction dimanche +15%

### 5. **Optimisation Continue**

Plus vous utilisez, plus c'est précis :
- 📈 Chaque jour ajoute des données
- 🧠 Patterns saisonniers capturés sur 6-12 mois
- ⚡ Ajustements météo affinés avec historique

---

## 🔧 Configuration Technique

### Variables Configurables

```python
# Heures de service (modifiables dans le code)
SERVICE_HOURS = {
    'Déjeuner': [11, 12, 13, 14],
    'Dîner': [18, 19, 20, 21, 22]
}

# Répartition par défaut sans données horaires
DEJEUNER_RATIO = 0.55  # 55% du total journalier
DINER_RATIO = 0.45     # 45% du total journalier

# Facteurs d'ajustement
WEEKEND_FACTOR = 1.15  # +15% le weekend
```

### Météo API

Utilise la même API que l'onglet "Alertes Météo" :
- Prévisions jour actuel
- Conditions, température, risque pluie
- Mise à jour temps réel

---

## 📝 FAQ

**Q : Dois-je avoir la colonne 'Heure' obligatoirement ?**  
R : Non ! Sans 'Heure', vous avez quand même les prédictions simplifiées avec ajustements météo et tendances.

**Q : Comment le système calcule les ajustements ?**  
R : Il combine 3 facteurs : (1) Pattern horaire historique, (2) Météo du jour, (3) Ventes actuelles vs moyenne.

**Q : Les prédictions changent pendant la journée ?**  
R : Oui ! Plus la journée avance, plus les ajustements de tendance sont précis (basés sur ventes réelles).

**Q : Puis-je ajouter des réservations ?**  
R : Actuellement non, mais c'est dans le backlog ! En attendant, ajoutez mentalement +X couverts si grosses réservations.

**Q : Quelle précision attendre ?**  
R : Avec bonnes données horaires (30+ jours), attendez ±15-20% de précision. Ajustements météo/tendances améliorent à ±10-15%.

---

**Version** : 2.1.0  
**Date** : 2026-01-19  
**Feature** : Prédictions Temps Réel Intra-Journée
