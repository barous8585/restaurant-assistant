# 📊 Guide d'Utilisation des Sources de Données Cloud

## Vue d'ensemble

L'application supporte désormais **5 modes de synchronisation** pour vos données de ventes :

| Source | Icône | Synchronisation Auto | Difficulté |
|--------|-------|---------------------|------------|
| **Upload Manuel** | 📁 | ❌ Non | ⭐ Facile |
| **Google Sheets** | 📊 | ✅ Oui | ⭐⭐ Moyen |
| **OneDrive / Excel Online** | ☁️ | ✅ Oui | ⭐⭐⭐ Avancé |
| **Dropbox** | 📦 | ✅ Oui | ⭐⭐ Moyen |
| **URL Publique** | 🔗 | ✅ Oui | ⭐ Facile |

---

## 📁 Mode 1 : Upload Manuel (Par Défaut)

**Quand l'utiliser** : Mise à jour ponctuelle, fichiers locaux

**Avantages** :
- ✅ Simple et rapide
- ✅ Aucune configuration nécessaire
- ✅ Fonctionne hors ligne

**Limitations** :
- ❌ Synchronisation manuelle uniquement
- ❌ Nécessite re-upload à chaque mise à jour

**Utilisation** :
1. Gardez "📁 Upload Fichier Local" sélectionné dans la sidebar
2. Importez votre fichier depuis la section principale

---

## 📊 Mode 2 : Google Sheets

**Quand l'utiliser** : Saisie collaborative, mise à jour en temps réel

**Avantages** :
- ✅ Synchronisation automatique
- ✅ Modification en ligne depuis n'importe où
- ✅ Collaboration avec votre équipe

**Limitations** :
- ⚠️ Nécessite feuille publique (lecture seule) OU OAuth2

### Configuration (Méthode Simple - Feuille Publique)

**Étape 1 : Préparer votre Google Sheet**

1. Ouvrez votre feuille Google Sheets
2. Cliquez sur **"Partager"** (coin supérieur droit)
3. Changez en **"Tous les utilisateurs disposant du lien"**
4. Assurez-vous que l'accès est **"Lecteur"** (lecture seule)
5. Copiez le lien de partage

**Étape 2 : Configurer dans l'application**

1. Dans la sidebar, section **"📊 Sources de Données"**
2. Sélectionnez **"📊 Google Sheets"**
3. Collez l'URL dans **"URL de la Google Sheet"**
   ```
   https://docs.google.com/spreadsheets/d/1ABC...XYZ/edit
   ```
4. (Optionnel) Spécifiez le nom de la feuille (ex: "Feuille1")
5. Cochez **"Feuille publique (accès en lecture)"**
6. Cliquez **"💾 Sauvegarder"** puis **"🧪 Tester"**

**Étape 3 : Activer la synchronisation automatique**

1. Cochez **"Activer la synchronisation automatique"**
2. Réglez l'intervalle (recommandé : **10 minutes**)
3. Cliquez **"🔄 Synchroniser Maintenant"** pour la première sync

### Configuration Avancée (OAuth2)

> 🚧 **Nécessite configuration Streamlit Cloud Secrets**

Pour utiliser OAuth2 avec des feuilles privées :

1. Créez un projet Google Cloud Platform
2. Activez l'API Google Sheets
3. Créez des identifiants OAuth 2.0
4. Ajoutez les credentials dans `st.secrets` (Streamlit Cloud)

**Format secrets.toml** :
```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "..."
private_key = "..."
client_email = "..."
```

---

## ☁️ Mode 3 : OneDrive / Excel Online

**Quand l'utiliser** : Environnement Microsoft 365, fichiers Excel partagés

**Avantages** :
- ✅ Intégration Microsoft 365
- ✅ Édition Excel en ligne
- ✅ Synchronisation automatique

**Limitations** :
- ⚠️ Configuration OAuth2 complexe pour fichiers privés
- ⚠️ Lien public plus simple mais moins sécurisé

### Configuration (Méthode Simple - Lien Public)

**Étape 1 : Créer un lien partagé OneDrive**

1. Ouvrez votre fichier Excel sur OneDrive
2. Cliquez **"Partager"**
3. Choisissez **"Tous les utilisateurs disposant du lien peuvent afficher"**
4. Copiez le lien de partage

**Étape 2 : Configurer dans l'application**

1. Sélectionnez **"☁️ OneDrive / Excel Online"**
2. Collez l'URL dans **"URL du fichier Excel"**
   ```
   https://1drv.ms/x/s!ABC...XYZ
   ```
3. Laissez **"Utiliser OAuth2"** décoché
4. Cliquez **"💾 Sauvegarder"**

### Configuration Avancée (OAuth2 Microsoft Graph)

> 🚧 **Pour développeurs avancés uniquement**

1. Créez une application Azure AD
2. Ajoutez permissions Microsoft Graph : `Files.Read`
3. Générez Client ID et Client Secret
4. Configurez dans l'application avec **"Utiliser OAuth2"** coché

---

## 📦 Mode 4 : Dropbox

**Quand l'utiliser** : Synchronisation multi-appareils, backup automatique

**Avantages** :
- ✅ Configuration simple (access token)
- ✅ Synchronisation fiable
- ✅ Support CSV et Excel

**Limitations** :
- ⚠️ Nécessite création d'une app Dropbox (gratuit)

### Configuration Complète

**Étape 1 : Créer un Access Token Dropbox**

1. Allez sur **[Dropbox App Console](https://www.dropbox.com/developers/apps)**
2. Cliquez **"Create app"**
3. Choisissez :
   - **API** : Scoped access
   - **Type d'accès** : Full Dropbox (ou App folder)
   - **Nom** : "Restaurant Predictions" (ou autre)
4. Cliquez **"Create app"**

**Étape 2 : Générer le token**

1. Dans l'onglet **"Settings"** de votre app
2. Scrollez jusqu'à **"OAuth 2"** → **"Generated access token"**
3. Cliquez **"Generate"**
4. Copiez le token (commence par `sl.`)

**Étape 3 : Uploader votre fichier sur Dropbox**

1. Uploadez votre fichier CSV/Excel dans Dropbox
2. Notez le chemin complet, ex : `/Restaurant/ventes.xlsx`
   - ⚠️ Le chemin doit commencer par `/`

**Étape 4 : Configurer dans l'application**

1. Sélectionnez **"📦 Dropbox"**
2. Collez le token dans **"Access Token"**
3. Entrez le chemin : `/Restaurant/ventes.xlsx`
4. Cliquez **"💾 Sauvegarder"** puis **"🧪 Tester"**

**Étape 5 : Activer la synchronisation**

1. Cochez **"Activer la synchronisation automatique"**
2. Réglez l'intervalle (recommandé : **5-10 minutes**)
3. À chaque modification du fichier sur Dropbox, l'app se mettra à jour automatiquement

---

## 🔗 Mode 5 : URL Publique

**Quand l'utiliser** : API externe, fichier hébergé en ligne

**Avantages** :
- ✅ Extrêmement simple
- ✅ Fonctionne avec n'importe quelle URL publique
- ✅ Idéal pour intégrations API

**Limitations** :
- ⚠️ URL doit être publique (pas d'authentification)
- ⚠️ Format CSV ou Excel uniquement

### Configuration

**Étape 1 : Héberger votre fichier**

Options possibles :
- GitHub Raw : `https://raw.githubusercontent.com/user/repo/main/data.csv`
- Serveur web : `https://monsite.com/data/ventes.csv`
- Cloud storage public : `https://storage.cloud.com/bucket/file.csv`

**Étape 2 : Configurer dans l'application**

1. Sélectionnez **"🔗 URL Publique (CSV/Excel)"**
2. Collez l'URL dans **"URL du fichier CSV/Excel"**
3. Cliquez **"🧪 Tester"** pour vérifier l'accès
4. Si OK, cliquez **"💾 Sauvegarder"**

**Étape 3 : Synchronisation automatique**

- Activez la sync auto avec intervalle court (1-5 min) si vos données changent souvent
- L'app téléchargera le fichier à chaque intervalle

---

## ⚡ Synchronisation Automatique

### Comment ça marche ?

1. **Activation** : Cochez "Activer la synchronisation automatique"
2. **Intervalle** : Réglez la fréquence (1-60 minutes)
3. **Automatique** : L'app vérifie et télécharge les nouvelles données à intervalle régulier
4. **Manuel** : Vous pouvez aussi cliquer **"🔄 Synchroniser Maintenant"**

### Recommandations par cas d'usage

| Cas d'usage | Intervalle recommandé |
|-------------|----------------------|
| Saisie en temps réel (Google Sheets) | **5-10 minutes** |
| Mise à jour quotidienne | **30-60 minutes** |
| Mise à jour hebdomadaire | **Sync manuelle** (désactivée) |
| Tests / développement | **1-2 minutes** |

### Affichage de la dernière synchronisation

L'interface affiche :
```
📅 Dernière sync: Il y a 5 minutes
```

Formats :
- **< 1 min** : "Il y a X secondes"
- **< 1h** : "Il y a X minutes"
- **< 24h** : "Il y a X heures"
- **> 24h** : "Il y a X jours"

---

## 🔧 Dépannage

### Google Sheets : "Feuille non publique"

**Problème** : Message "⚠️ Feuille non publique - Authentification requise"

**Solutions** :
1. Vérifiez que le lien est bien public (Partager → Tous les utilisateurs)
2. Testez le lien dans un navigateur en navigation privée
3. Assurez-vous que l'accès est "Lecteur" (pas "Aucun accès")

### Dropbox : "Token invalide"

**Problème** : Message "❌ Token invalide"

**Solutions** :
1. Re-générez le token sur Dropbox App Console
2. Vérifiez que vous avez bien copié le token complet (commence par `sl.`)
3. Assurez-vous que l'app Dropbox n'est pas supprimée

### URL Publique : "URL invalide ou inaccessible"

**Problème** : Impossible de télécharger le fichier

**Solutions** :
1. Testez l'URL dans votre navigateur (doit télécharger directement)
2. Vérifiez qu'il n'y a pas d'authentification requise
3. Assurez-vous que le format est CSV ou Excel (`.csv`, `.xlsx`, `.xls`)
4. Vérifiez que l'URL commence par `https://`

### Synchronisation bloquée

**Problème** : La sync auto ne fonctionne plus

**Solutions** :
1. Cliquez **"🔄 Synchroniser Maintenant"** pour forcer la sync
2. Désactivez puis réactivez la sync automatique
3. Testez la connexion avec **"🧪 Tester"**
4. Vérifiez que la source est toujours accessible

---

## 📋 Format des Données

### Colonnes Obligatoires

Quel que soit la source, votre fichier doit contenir au minimum :

```
Date,Plat,Quantite
2024-01-15,Burger Classic,25
2024-01-15,Pizza Margherita,18
```

### Colonnes Optionnelles (Recommandées)

Pour des prédictions plus précises, ajoutez :

```csv
Date,Plat,Quantite,Categorie,Prix_unitaire,Cout_unitaire,Service,Zone,Meteo,Promotion,Canal
2024-01-15,Burger Classic,25,Plat,12.50,4.80,Déjeuner,Salle,Ensoleillé,Non,Sur place
```

**➡️ Voir `colonnes_restaurant_template.py` pour la liste complète**

---

## 🎯 Cas d'Usage Recommandés

### Scenario 1 : Restaurant avec équipe

**Besoin** : L'équipe saisit les ventes en temps réel depuis différents appareils

**Solution** : **Google Sheets**
- Créez une feuille partagée avec votre équipe
- Chaque serveur/manager peut mettre à jour depuis son téléphone
- Sync auto toutes les 10 minutes
- Prédictions mises à jour en continu

### Scenario 2 : Restaurateur solo avec Excel

**Besoin** : Vous travaillez déjà sur Excel, vous voulez juste synchroniser

**Solution** : **OneDrive** ou **Dropbox**
- Sauvegardez votre fichier Excel sur OneDrive/Dropbox
- Sync auto toutes les 30 minutes
- Continuez à travailler normalement sur Excel
- Les prédictions se mettent à jour automatiquement

### Scenario 3 : Intégration avec caisse enregistreuse

**Besoin** : Votre caisse exporte automatiquement les ventes vers une URL

**Solution** : **URL Publique**
- Configurez l'export de votre caisse vers un serveur web
- Utilisez l'URL du fichier export
- Sync auto toutes les 5 minutes
- Prédictions en temps réel basées sur les ventes actuelles

### Scenario 4 : Mise à jour manuelle hebdomadaire

**Besoin** : Vous mettez à jour vos données une fois par semaine

**Solution** : **Upload Manuel**
- Gardez le mode par défaut
- Upload manuel chaque lundi matin
- Simple et efficace

---

## 🔒 Sécurité et Confidentialité

### Stockage des Credentials

- ✅ **Access tokens** : Chiffrés et stockés localement par utilisateur
- ✅ **Mots de passe** : Hachés SHA256, jamais en clair
- ✅ **Données** : Isolées par compte utilisateur

### Bonnes Pratiques

1. **Google Sheets** : Utilisez un lien en lecture seule uniquement
2. **Dropbox** : Créez un access token spécifique (révocable)
3. **OneDrive** : Privilégiez OAuth2 pour fichiers sensibles
4. **URL Publique** : Ne publiez jamais de données sensibles/personnelles

### Révocation d'Accès

Pour révoquer l'accès :
- **Dropbox** : App Console → Supprimez l'app ou régénérez le token
- **Google** : Paramètres Google → Sécurité → Accès tiers → Révocez
- **OneDrive** : Azure AD → Supprimez l'app

---

## 📞 Support

### Questions Fréquentes

**Q : Puis-je utiliser plusieurs sources en même temps ?**  
R : Non, une seule source active à la fois. Mais vous pouvez basculer facilement.

**Q : Que se passe-t-il si la connexion échoue ?**  
R : L'app utilise les dernières données synchronisées et affiche un avertissement.

**Q : Les données sont-elles sauvegardées localement ?**  
R : Oui, à chaque synchronisation réussie, les données sont aussi stockées en local.

**Q : Combien de temps prend la synchronisation ?**  
R : Généralement < 5 secondes pour des fichiers de taille normale (<10 000 lignes).

**Q : Puis-je changer de source sans perdre mes données ?**  
R : Oui, les données de chaque restaurant sont conservées indépendamment.

### Besoin d'Aide ?

- 📧 Contact : support@restaurant-predictions.app (fictif)
- 📖 Documentation : [COMPRENDRE_PREDICTIONS_ML.md](./COMPRENDRE_PREDICTIONS_ML.md)
- 🐛 Signaler un bug : GitHub Issues

---

**Dernière mise à jour** : 19 janvier 2025  
**Version** : 2.0.0 - Cloud Data Sources
