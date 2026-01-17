#!/usr/bin/env python3
"""Test de la fonction de suppression de compte"""

import pickle
import os
import hashlib

DATA_DIR = "restaurant_data"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def delete_user_account(username):
    """Supprimer complètement un compte utilisateur (admin seulement)"""
    users_file = os.path.join(DATA_DIR, "users.pkl")
    
    if not os.path.exists(users_file):
        return False, "Fichier utilisateurs introuvable"
    
    # Charger les utilisateurs
    with open(users_file, 'rb') as f:
        users = pickle.load(f)
    
    if username not in users:
        return False, "Utilisateur introuvable"
    
    # Supprimer de users.pkl
    del users[username]
    
    with open(users_file, 'wb') as f:
        pickle.dump(users, f)
    
    # Supprimer le fichier de données
    user_data_file = os.path.join(DATA_DIR, f"{username}_data.pkl")
    if os.path.exists(user_data_file):
        os.remove(user_data_file)
    
    return True, f"Compte '{username}' supprimé avec succès"

def create_test_user(username, password):
    """Créer un utilisateur de test"""
    users_file = os.path.join(DATA_DIR, "users.pkl")
    
    if os.path.exists(users_file):
        with open(users_file, 'rb') as f:
            users = pickle.load(f)
    else:
        users = {}
    
    users[username] = {
        'password_hash': hash_password(password),
        'restaurant_info': {
            'name': f'Restaurant {username}',
            'city': 'Test City',
            'cost_per_portion': 5.0
        }
    }
    
    with open(users_file, 'wb') as f:
        pickle.dump(users, f)
    
    # Créer fichier de données
    user_data = {
        f'Restaurant {username}': {
            'name': f'Restaurant {username}',
            'city': 'Test City',
            'cost_per_portion': 5.0,
            'data': None,
            'recipes': {}
        }
    }
    
    user_data_file = os.path.join(DATA_DIR, f"{username}_data.pkl")
    with open(user_data_file, 'wb') as f:
        pickle.dump(user_data, f)

def count_users():
    """Compter le nombre d'utilisateurs"""
    users_file = os.path.join(DATA_DIR, "users.pkl")
    
    if not os.path.exists(users_file):
        return 0
    
    with open(users_file, 'rb') as f:
        users = pickle.load(f)
    
    return len(users)

if __name__ == "__main__":
    print("🧪 Test de suppression de compte utilisateur\n")
    
    print("="*60)
    print("PRÉPARATION : Créer un utilisateur de test")
    print("="*60)
    
    test_username = "test_to_delete"
    
    # Créer l'utilisateur de test
    create_test_user(test_username, "testpass123")
    print(f"✅ Utilisateur '{test_username}' créé")
    
    # Vérifier que le fichier de données existe
    data_file = os.path.join(DATA_DIR, f"{test_username}_data.pkl")
    if os.path.exists(data_file):
        print(f"✅ Fichier de données créé : {test_username}_data.pkl")
    else:
        print(f"❌ Fichier de données non créé")
    
    nb_users_before = count_users()
    print(f"📊 Nombre d'utilisateurs avant suppression : {nb_users_before}")
    
    print("\n" + "="*60)
    print("TEST : Supprimer l'utilisateur")
    print("="*60)
    
    success, message = delete_user_account(test_username)
    
    if success:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")
    
    # Vérifier que l'utilisateur n'existe plus
    users_file = os.path.join(DATA_DIR, "users.pkl")
    with open(users_file, 'rb') as f:
        users = pickle.load(f)
    
    if test_username not in users:
        print(f"✅ Utilisateur '{test_username}' supprimé de users.pkl")
    else:
        print(f"❌ Utilisateur '{test_username}' existe encore dans users.pkl")
    
    # Vérifier que le fichier de données n'existe plus
    if not os.path.exists(data_file):
        print(f"✅ Fichier de données supprimé : {test_username}_data.pkl")
    else:
        print(f"❌ Fichier de données existe encore")
    
    nb_users_after = count_users()
    print(f"📊 Nombre d'utilisateurs après suppression : {nb_users_after}")
    
    if nb_users_after == nb_users_before - 1:
        print("✅ Nombre d'utilisateurs correct (diminué de 1)")
    else:
        print(f"❌ Nombre d'utilisateurs incorrect (attendu: {nb_users_before - 1}, obtenu: {nb_users_after})")
    
    print("\n" + "="*60)
    print("TEST : Essayer de supprimer un utilisateur inexistant")
    print("="*60)
    
    success, message = delete_user_account("utilisateur_inexistant")
    
    if not success and "introuvable" in message:
        print(f"✅ Erreur correcte : {message}")
    else:
        print("❌ Devrait retourner une erreur")
    
    print("\n" + "="*60)
    print("✅ TOUS LES TESTS DE SUPPRESSION RÉUSSIS !")
    print("="*60)
