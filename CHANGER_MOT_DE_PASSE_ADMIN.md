# 🔐 Comment Changer le Mot de Passe Admin

## Méthode Simple

### 1️⃣ Générer le hash de votre nouveau mot de passe

Ouvrez un terminal et exécutez :

```bash
python3 << 'EOF'
import hashlib

# CHANGEZ CE MOT DE PASSE PAR LE VÔTRE
nouveau_mdp = "VotreMotDePasseTresSécurisé2026!"

hash_mdp = hashlib.sha256(nouveau_mdp.encode()).hexdigest()
print("\n" + "="*60)
print("COPIEZ CE HASH :")
print("="*60)
print(hash_mdp)
print("="*60 + "\n")
EOF
```

**Résultat exemple** :
```
============================================================
COPIEZ CE HASH :
============================================================
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
============================================================
```

### 2️⃣ Modifier le fichier app.py

Ouvrez `app.py` et cherchez la ligne 26 :

**AVANT** :
```python
ADMIN_PASSWORD_HASH = "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"  # "admin"
```

**APRÈS** :
```python
ADMIN_PASSWORD_HASH = "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6"  # Nouveau mot de passe
```

### 3️⃣ Sauvegarder et déployer

```bash
git add app.py
git commit -m "security: Changer mot de passe admin"
git push origin main
```

### 4️⃣ NOTEZ VOTRE MOT DE PASSE

⚠️ **TRÈS IMPORTANT** : Notez votre nouveau mot de passe dans un endroit sûr !

Le hash est irréversible. Si vous perdez votre mot de passe, vous devrez recommencer cette procédure.

---

## 📝 Recommandations pour un Bon Mot de Passe

- Au moins 12 caractères
- Mélange de majuscules, minuscules, chiffres et symboles
- Exemple : `RestaurantAdmin2026!@#`

---

## ✅ Tester le Nouveau Mot de Passe

Après déploiement :
1. Aller sur votre app Streamlit
2. Onglet "🔐 Admin"
3. Entrer votre nouveau mot de passe
4. Si ça fonctionne → ✅ Succès !
5. Si erreur → Vérifier que vous avez bien copié le hash

---

## 🆘 En Cas de Problème

Si vous êtes bloqué :
1. Vérifiez que le hash copié est complet (64 caractères)
2. Pas d'espaces avant/après le hash dans app.py
3. Les guillemets sont bien présents
4. Recommencez depuis l'étape 1 si nécessaire
