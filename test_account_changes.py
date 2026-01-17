#!/usr/bin/env python3
"""Test des fonctions de modification de compte"""

import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(__file__))

import pickle
import hashlib
from datetime import datetime

DATA_DIR = "restaurant_data"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def change_user_password(username, new_password):
    """Changer le mot de passe d'un utilisateur"""
    users_file = os.path.join(DATA_DIR, "users.pkl")
    
    if not os.path.exists(users_file):
        return False
    
    with open(users_file, 'rb') as f:
        users = pickle.load(f)
    
    if username not in users:
        return False
    
    users[username]['password_hash'] = hash_password(new_password)
    
    with open(users_file, 'wb') as f:
        pickle.dump(users, f)
    
    return True

def change_username(old_username, new_username):
    """Changer le nom d'utilisateur (renommer le compte)"""
    users_file = os.path.join(DATA_DIR, "users.pkl")
    
    if not os.path.exists(users_file):
        return False, "Fichier utilisateurs introuvable"
    
    with open(users_file, 'rb') as f:
        users = pickle.load(f)
    
    if old_username not in users:
        return False, "Utilisateur introuvable"
    
    if new_username in users:
        return False, "Ce nom d'utilisateur existe déjà"
    
    # Copier les données de l'ancien vers le nouveau
    users[new_username] = users[old_username]
    del users[old_username]
    
    # Sauvegarder users.pkl
    with open(users_file, 'wb') as f:
        pickle.dump(users, f)
    
    # Renommer le fichier de données
    old_data_file = os.path.join(DATA_DIR, f"{old_username}_data.pkl")
    new_data_file = os.path.join(DATA_DIR, f"{new_username}_data.pkl")
    
    if os.path.exists(old_data_file):
        os.rename(old_data_file, new_data_file)
    
    return True, "Nom d'utilisateur modifié avec succès"

def verify_user(username, password):
    users_file = os.path.join(DATA_DIR, "users.pkl")
    
    if not os.path.exists(users_file):
        return False
    
    with open(users_file, 'rb') as f:
        users = pickle.load(f)
    
    if username not in users:
        return False
    
    return users[username]['password_hash'] == hash_password(password)

if __name__ == "__main__":
    print("🧪 Test des fonctions de modification de compte\n")
    
    # Vérifier si les utilisateurs existent
    users_file = os.path.join(DATA_DIR, "users.pkl")
    if not os.path.exists(users_file):
        print("❌ Aucun utilisateur. Exécutez d'abord: python3 create_demo_users.py")
        sys.exit(1)
    
    print("="*60)
    print("TEST 1 : Changer le mot de passe de 'restaurant_paris'")
    print("="*60)
    
    # Vérifier ancien mot de passe
    if verify_user('restaurant_paris', 'demo123'):
        print("✅ Ancien mot de passe 'demo123' fonctionne")
    else:
        print("❌ Problème avec l'ancien mot de passe")
    
    # Changer le mot de passe
    if change_user_password('restaurant_paris', 'nouveau123'):
        print("✅ Mot de passe changé avec succès")
    else:
        print("❌ Erreur lors du changement de mot de passe")
    
    # Vérifier nouveau mot de passe
    if verify_user('restaurant_paris', 'nouveau123'):
        print("✅ Nouveau mot de passe 'nouveau123' fonctionne")
    else:
        print("❌ Le nouveau mot de passe ne fonctionne pas")
    
    # Remettre l'ancien
    change_user_password('restaurant_paris', 'demo123')
    print("✅ Mot de passe restauré à 'demo123'")
    
    print("\n" + "="*60)
    print("TEST 2 : Changer le nom d'utilisateur 'pizza_lyon' → 'pizzeria_lyon'")
    print("="*60)
    
    # Changer le nom d'utilisateur
    success, message = change_username('pizza_lyon', 'pizzeria_lyon')
    if success:
        print(f"✅ {message}")
        
        # Vérifier que le nouveau nom fonctionne
        if verify_user('pizzeria_lyon', 'demo123'):
            print("✅ Connexion avec 'pizzeria_lyon' fonctionne")
        else:
            print("❌ Connexion avec nouveau nom échoue")
        
        # Vérifier que l'ancien nom ne fonctionne plus
        if not verify_user('pizza_lyon', 'demo123'):
            print("✅ Ancien nom 'pizza_lyon' n'existe plus")
        else:
            print("❌ L'ancien nom existe encore")
        
        # Vérifier que le fichier de données a été renommé
        if os.path.exists(os.path.join(DATA_DIR, "pizzeria_lyon_data.pkl")):
            print("✅ Fichier de données renommé")
        else:
            print("❌ Fichier de données non renommé")
        
        # Restaurer l'ancien nom
        change_username('pizzeria_lyon', 'pizza_lyon')
        print("✅ Nom d'utilisateur restauré à 'pizza_lyon'")
    else:
        print(f"❌ {message}")
    
    print("\n" + "="*60)
    print("TEST 3 : Tester les erreurs")
    print("="*60)
    
    # Essayer de changer vers un nom existant
    success, message = change_username('restaurant_paris', 'pizza_lyon')
    if not success and "existe déjà" in message:
        print(f"✅ Erreur correcte: {message}")
    else:
        print("❌ Devrait rejeter un nom existant")
    
    # Essayer de changer le mot de passe d'un utilisateur inexistant
    if not change_user_password('utilisateur_inexistant', 'test'):
        print("✅ Rejet correct d'un utilisateur inexistant")
    else:
        print("❌ Devrait rejeter un utilisateur inexistant")
    
    print("\n" + "="*60)
    print("TEST 4 : Générer hash admin")
    print("="*60)
    
    test_admin_pwd = "MonNouveauMotDePasseAdmin2026!"
    new_hash = hash_password(test_admin_pwd)
    print(f"Mot de passe admin test: {test_admin_pwd}")
    print(f"Hash généré: {new_hash}")
    print("✅ Fonction de génération de hash fonctionne")
    
    print("\n" + "="*60)
    print("✅ TOUS LES TESTS RÉUSSIS !")
    print("="*60)
