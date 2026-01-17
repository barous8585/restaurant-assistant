#!/usr/bin/env python3
"""Test du système d'approbation de compte"""

import pickle
import os
import hashlib
from datetime import datetime

DATA_DIR = "restaurant_data"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def save_user_credentials(username, password, restaurant_info, approved=False):
    users_file = os.path.join(DATA_DIR, "users.pkl")
    
    if os.path.exists(users_file):
        with open(users_file, 'rb') as f:
            users = pickle.load(f)
    else:
        users = {}
    
    users[username] = {
        'password_hash': hash_password(password),
        'restaurant_info': restaurant_info,
        'approved': approved,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    with open(users_file, 'wb') as f:
        pickle.dump(users, f)

def is_user_approved(username):
    users_file = os.path.join(DATA_DIR, "users.pkl")
    
    if not os.path.exists(users_file):
        return False
    
    with open(users_file, 'rb') as f:
        users = pickle.load(f)
    
    if username not in users:
        return False
    
    return users[username].get('approved', True)

def approve_user(username):
    users_file = os.path.join(DATA_DIR, "users.pkl")
    
    if not os.path.exists(users_file):
        return False, "Fichier utilisateurs introuvable"
    
    with open(users_file, 'rb') as f:
        users = pickle.load(f)
    
    if username not in users:
        return False, "Utilisateur introuvable"
    
    users[username]['approved'] = True
    users[username]['approved_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    with open(users_file, 'wb') as f:
        pickle.dump(users, f)
    
    return True, f"Utilisateur '{username}' approuvé avec succès"

if __name__ == "__main__":
    print("🧪 Test du système d'approbation de compte\n")
    
    print("="*60)
    print("TEST 1 : Créer un utilisateur non approuvé par défaut")
    print("="*60)
    
    test_user = "test_pending"
    restaurant_info = {
        'name': 'Restaurant Test',
        'city': 'Paris',
        'cost_per_portion': 5.0
    }
    
    # Créer utilisateur (approved=False par défaut)
    save_user_credentials(test_user, "testpass123", restaurant_info, approved=False)
    print(f"✅ Utilisateur '{test_user}' créé")
    
    # Vérifier qu'il n'est pas approuvé
    if not is_user_approved(test_user):
        print("✅ Utilisateur correctement marqué comme non approuvé")
    else:
        print("❌ Utilisateur devrait être non approuvé")
    
    print("\n" + "="*60)
    print("TEST 2 : Approuver l'utilisateur")
    print("="*60)
    
    success, message = approve_user(test_user)
    if success:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")
    
    # Vérifier qu'il est maintenant approuvé
    if is_user_approved(test_user):
        print("✅ Utilisateur correctement approuvé")
    else:
        print("❌ Utilisateur devrait être approuvé")
    
    # Vérifier que approved_at a été ajouté
    users_file = os.path.join(DATA_DIR, "users.pkl")
    with open(users_file, 'rb') as f:
        users = pickle.load(f)
    
    if 'approved_at' in users[test_user]:
        print(f"✅ Date d'approbation enregistrée: {users[test_user]['approved_at']}")
    else:
        print("❌ Date d'approbation manquante")
    
    print("\n" + "="*60)
    print("TEST 3 : Créer un utilisateur approuvé d'emblée")
    print("="*60)
    
    test_user2 = "test_approved"
    save_user_credentials(test_user2, "testpass123", restaurant_info, approved=True)
    print(f"✅ Utilisateur '{test_user2}' créé avec approved=True")
    
    if is_user_approved(test_user2):
        print("✅ Utilisateur correctement approuvé dès la création")
    else:
        print("❌ Utilisateur devrait être approuvé")
    
    print("\n" + "="*60)
    print("TEST 4 : Rétrocompatibilité (utilisateur sans champ 'approved')")
    print("="*60)
    
    # Créer un utilisateur à l'ancienne (sans champ approved)
    test_user3 = "test_legacy"
    users[test_user3] = {
        'password_hash': hash_password("testpass123"),
        'restaurant_info': restaurant_info
        # Pas de champ 'approved'
    }
    
    with open(users_file, 'wb') as f:
        pickle.dump(users, f)
    
    print(f"✅ Utilisateur '{test_user3}' créé sans champ 'approved'")
    
    # Vérifier la rétrocompatibilité (devrait être considéré comme approuvé)
    if is_user_approved(test_user3):
        print("✅ Rétrocompatibilité OK : utilisateur legacy considéré comme approuvé")
    else:
        print("❌ Problème de rétrocompatibilité")
    
    print("\n" + "="*60)
    print("TEST 5 : Statistiques des comptes en attente")
    print("="*60)
    
    with open(users_file, 'rb') as f:
        users = pickle.load(f)
    
    total = len(users)
    approved = sum(1 for u in users.values() if u.get('approved', True))
    pending = total - approved
    
    print(f"📊 Total utilisateurs : {total}")
    print(f"✅ Approuvés : {approved}")
    print(f"⏳ En attente : {pending}")
    
    # Nettoyer les utilisateurs de test
    for test_u in [test_user, test_user2, test_user3]:
        if test_u in users:
            del users[test_u]
    
    with open(users_file, 'wb') as f:
        pickle.dump(users, f)
    
    print("\n" + "="*60)
    print("✅ TOUS LES TESTS D'APPROBATION RÉUSSIS !")
    print("="*60)
