#!/usr/bin/env python3
"""Test du système d'administration"""

import pickle
import os
from datetime import datetime

DATA_DIR = "restaurant_data"

def get_all_users_stats():
    """Fonction admin: récupère les stats de tous les utilisateurs"""
    users_file = os.path.join(DATA_DIR, "users.pkl")
    
    if not os.path.exists(users_file):
        return []
    
    with open(users_file, 'rb') as f:
        users = pickle.load(f)
    
    stats = []
    for username, user_data in users.items():
        # Charger les données de l'utilisateur
        user_data_file = os.path.join(DATA_DIR, f"{username}_data.pkl")
        
        if os.path.exists(user_data_file):
            with open(user_data_file, 'rb') as f:
                user_restaurants = pickle.load(f)
        else:
            user_restaurants = {}
        
        nb_restaurants = len(user_restaurants)
        
        stats.append({
            'Utilisateur': username,
            'Nombre de Restaurants': nb_restaurants,
            'Ville Principale': user_data['restaurant_info'].get('city', 'N/A'),
            'Date Inscription': datetime.now().strftime('%Y-%m-%d')
        })
    
    return stats

def calculate_invoice(nb_restaurants, price_per_restaurant=49.0):
    """Calcule la facture basée sur le nombre de restaurants"""
    if nb_restaurants <= 3:
        return price_per_restaurant  # Plan Standard: 49€ (1-3 restaurants)
    else:
        return 149.0  # Plan Enterprise: 149€ (4+ restaurants)

if __name__ == "__main__":
    print("🔐 Test du système d'administration\n")
    
    stats = get_all_users_stats()
    
    if stats:
        print(f"👥 Nombre d'utilisateurs: {len(stats)}\n")
        
        total_revenue = 0
        
        for user in stats:
            facture = calculate_invoice(user['Nombre de Restaurants'])
            total_revenue += facture
            
            plan = "Standard (49€)" if user['Nombre de Restaurants'] <= 3 else "Enterprise (149€)"
            
            print(f"Utilisateur: {user['Utilisateur']}")
            print(f"  🏢 Restaurants: {user['Nombre de Restaurants']}")
            print(f"  📍 Ville: {user['Ville Principale']}")
            print(f"  📋 Plan: {plan}")
            print(f"  💰 Facture: {facture} €")
            print()
        
        print("="*50)
        print(f"💵 REVENU MENSUEL TOTAL: {total_revenue} €")
        print(f"📈 PROJECTION ANNUELLE: {total_revenue * 12} €")
        print("="*50)
    else:
        print("❌ Aucun utilisateur enregistré")
