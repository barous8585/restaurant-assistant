#!/usr/bin/env python3
"""
Script de test pour vérifier les calculs ROI
"""
import pandas as pd

def calculate_waste_savings_test(avg_daily_sales, avg_predictions):
    """Simule la fonction calculate_waste_savings()"""
    
    traditional_prep_factor = 1.20
    ml_prep_factor = 1.05
    
    # Gaspillage par jour
    daily_waste_traditional = max(0, (avg_daily_sales * traditional_prep_factor) - avg_daily_sales)
    daily_waste_ml = max(0, (avg_predictions * ml_prep_factor) - avg_predictions)
    daily_savings = daily_waste_traditional - daily_waste_ml
    
    # Projections mensuelles
    monthly_waste_traditional = daily_waste_traditional * 30
    monthly_waste_ml = daily_waste_ml * 30
    monthly_savings = daily_savings * 30
    
    return {
        'daily_waste_traditional': daily_waste_traditional,
        'daily_waste_ml': daily_waste_ml,
        'daily_savings': daily_savings,
        'waste_traditional': monthly_waste_traditional,
        'waste_ml': monthly_waste_ml,
        'savings_portions': monthly_savings,
        'reduction_percent': (monthly_savings / monthly_waste_traditional * 100) if monthly_waste_traditional > 0 else 0
    }

# Simulation avec données réalistes
print("=" * 60)
print("TEST DES CALCULS ROI - Restaurant moyen")
print("=" * 60)

# Scénario: restaurant avec ventes moyennes de 200 portions/jour
avg_daily_sales = 200  # portions/jour
avg_predictions = 200   # prédictions ML (similaire car c'est la moyenne)
cost_per_portion = 5.0  # 5€ par portion

savings = calculate_waste_savings_test(avg_daily_sales, avg_predictions)

print(f"\n📊 DONNÉES D'ENTRÉE:")
print(f"  • Ventes moyennes quotidiennes: {avg_daily_sales} portions")
print(f"  • Prédictions ML moyennes: {avg_predictions} portions")
print(f"  • Coût par portion: {cost_per_portion}€")

print(f"\n💸 GASPILLAGE QUOTIDIEN:")
print(f"  • Méthode traditionnelle (20% marge): {savings['daily_waste_traditional']:.1f} portions = {savings['daily_waste_traditional'] * cost_per_portion:.2f}€")
print(f"  • Méthode ML (5% marge): {savings['daily_waste_ml']:.1f} portions = {savings['daily_waste_ml'] * cost_per_portion:.2f}€")
print(f"  • Économies quotidiennes: {savings['daily_savings']:.1f} portions = {savings['daily_savings'] * cost_per_portion:.2f}€")

print(f"\n📅 PROJECTIONS MENSUELLES (30 jours):")
print(f"  • Gaspillage traditionnel: {savings['waste_traditional']:.0f} portions = {savings['waste_traditional'] * cost_per_portion:.0f}€")
print(f"  • Gaspillage avec ML: {savings['waste_ml']:.0f} portions = {savings['waste_ml'] * cost_per_portion:.0f}€")
print(f"  • Économies mensuelles: {savings['savings_portions']:.0f} portions = {savings['savings_portions'] * cost_per_portion:.0f}€")
print(f"  • Réduction: {savings['reduction_percent']:.1f}%")

print(f"\n🎯 RETOUR SUR INVESTISSEMENT:")
subscription_cost = 49.0
monthly_savings_euro = savings['savings_portions'] * cost_per_portion
daily_savings_euro = savings['daily_savings'] * cost_per_portion

roi = ((monthly_savings_euro - subscription_cost) / subscription_cost * 100) if subscription_cost > 0 else 0
payback_days = (subscription_cost / daily_savings_euro) if daily_savings_euro > 0 else 0
net_monthly_benefit = monthly_savings_euro - subscription_cost

print(f"  • Abonnement mensuel: {subscription_cost}€")
print(f"  • ROI mensuel: {roi:.0f}%")
print(f"  • Retour sur investissement: {payback_days:.0f} jours")
print(f"  • Bénéfice net mensuel: {net_monthly_benefit:.0f}€")
print(f"  • Bénéfice net annuel: {net_monthly_benefit * 12:.0f}€")

print("\n" + "=" * 60)
print("✅ TEST TERMINÉ - Vérifiez que les valeurs sont réalistes")
print("=" * 60)

# Test avec des données de burger (d'après screenshot)
print("\n" + "=" * 60)
print("TEST AVEC DONNÉES BURGER (d'après screenshot)")
print("=" * 60)

avg_daily_sales_burger = 35  # estimation basée sur screenshot
avg_predictions_burger = 25  # d'après le screenshot (22-27)
cost_per_portion_burger = 8.0  # coût burger

savings_burger = calculate_waste_savings_test(avg_daily_sales_burger, avg_predictions_burger)

print(f"\n📊 DONNÉES D'ENTRÉE:")
print(f"  • Ventes moyennes quotidiennes (historique): {avg_daily_sales_burger} burgers")
print(f"  • Prédictions ML moyennes: {avg_predictions_burger} burgers")
print(f"  • Coût par burger: {cost_per_portion_burger}€")

print(f"\n💸 GASPILLAGE QUOTIDIEN:")
print(f"  • Méthode traditionnelle: {savings_burger['daily_waste_traditional']:.1f} burgers = {savings_burger['daily_waste_traditional'] * cost_per_portion_burger:.2f}€")
print(f"  • Méthode ML: {savings_burger['daily_waste_ml']:.1f} burgers = {savings_burger['daily_waste_ml'] * cost_per_portion_burger:.2f}€")
print(f"  • Économies quotidiennes: {savings_burger['daily_savings']:.1f} burgers = {savings_burger['daily_savings'] * cost_per_portion_burger:.2f}€")

monthly_savings_burger = savings_burger['savings_portions'] * cost_per_portion_burger
daily_savings_burger = savings_burger['daily_savings'] * cost_per_portion_burger

roi_burger = ((monthly_savings_burger - subscription_cost) / subscription_cost * 100)
payback_days_burger = (subscription_cost / daily_savings_burger) if daily_savings_burger > 0 else 0

print(f"\n🎯 ROI BURGER:")
print(f"  • Économies mensuelles: {monthly_savings_burger:.0f}€")
print(f"  • ROI mensuel: {roi_burger:.0f}%")
print(f"  • Retour sur investissement: {payback_days_burger:.0f} jours")
print(f"  • Bénéfice net mensuel: {monthly_savings_burger - subscription_cost:.0f}€")

print("\n✅ Si les valeurs sont cohérentes, les corrections sont bonnes !")
