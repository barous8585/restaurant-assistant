#!/usr/bin/env python3
"""Créer des utilisateurs de démo pour tester le système admin"""

import pickle
import os
import hashlib

DATA_DIR = "restaurant_data"

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Créer fichier users.pkl
users = {
    'restaurant_paris': {
        'password_hash': hash_password('demo123'),
        'restaurant_info': {
            'name': 'Le Bistrot Parisien',
            'city': 'Paris',
            'cost_per_portion': 4.5
        }
    },
    'pizza_lyon': {
        'password_hash': hash_password('demo123'),
        'restaurant_info': {
            'name': 'Pizza Lyon',
            'city': 'Lyon',
            'cost_per_portion': 3.0
        }
    },
    'group_restos': {
        'password_hash': hash_password('demo123'),
        'restaurant_info': {
            'name': 'Groupe Resto France',
            'city': 'Marseille',
            'cost_per_portion': 5.0
        }
    }
}

users_file = os.path.join(DATA_DIR, "users.pkl")
with open(users_file, 'wb') as f:
    pickle.dump(users, f)

print("✅ Fichier users.pkl créé")

# Créer données pour restaurant_paris (1 restaurant - Gratuit)
restaurant_paris_data = {
    'Le Bistrot Parisien': {
        'name': 'Le Bistrot Parisien',
        'city': 'Paris',
        'cost_per_portion': 4.5,
        'data': None,
        'recipes': {}
    }
}

user_data_file = os.path.join(DATA_DIR, "restaurant_paris_data.pkl")
with open(user_data_file, 'wb') as f:
    pickle.dump(restaurant_paris_data, f)

print("✅ Utilisateur 'restaurant_paris' créé (1 restaurant - Plan Gratuit)")

# Créer données pour pizza_lyon (2 restaurants - Pro 49€)
pizza_lyon_data = {
    'Pizza Lyon Centre': {
        'name': 'Pizza Lyon Centre',
        'city': 'Lyon',
        'cost_per_portion': 3.0,
        'data': None,
        'recipes': {}
    },
    'Pizza Lyon Part-Dieu': {
        'name': 'Pizza Lyon Part-Dieu',
        'city': 'Lyon',
        'cost_per_portion': 3.2,
        'data': None,
        'recipes': {}
    }
}

user_data_file = os.path.join(DATA_DIR, "pizza_lyon_data.pkl")
with open(user_data_file, 'wb') as f:
    pickle.dump(pizza_lyon_data, f)

print("✅ Utilisateur 'pizza_lyon' créé (2 restaurants - Plan Pro 49€)")

# Créer données pour group_restos (5 restaurants - Enterprise 149€)
group_restos_data = {
    'Resto Marseille Vieux-Port': {
        'name': 'Resto Marseille Vieux-Port',
        'city': 'Marseille',
        'cost_per_portion': 5.0,
        'data': None,
        'recipes': {}
    },
    'Resto Nice Promenade': {
        'name': 'Resto Nice Promenade',
        'city': 'Nice',
        'cost_per_portion': 5.5,
        'data': None,
        'recipes': {}
    },
    'Resto Cannes Croisette': {
        'name': 'Resto Cannes Croisette',
        'city': 'Cannes',
        'cost_per_portion': 6.0,
        'data': None,
        'recipes': {}
    },
    'Resto Toulon Port': {
        'name': 'Resto Toulon Port',
        'city': 'Toulon',
        'cost_per_portion': 4.8,
        'data': None,
        'recipes': {}
    },
    'Resto Aix-en-Provence': {
        'name': 'Resto Aix-en-Provence',
        'city': 'Aix-en-Provence',
        'cost_per_portion': 5.2,
        'data': None,
        'recipes': {}
    }
}

user_data_file = os.path.join(DATA_DIR, "group_restos_data.pkl")
with open(user_data_file, 'wb') as f:
    pickle.dump(group_restos_data, f)

print("✅ Utilisateur 'group_restos' créé (5 restaurants - Plan Enterprise 149€)")

print("\n" + "="*60)
print("📊 RÉSUMÉ")
print("="*60)
print("👥 Total utilisateurs: 3")
print("🏢 Total restaurants: 8")
print("💰 Revenu mensuel attendu: 0€ + 49€ + 149€ = 198€")
print("\n🔑 Mot de passe pour tous les comptes démo: demo123")
print("🔐 Mot de passe admin: admin")
print("="*60)
