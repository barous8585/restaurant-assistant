"""
Template Excel Complet pour Restaurant - Assistant Prédiction ML

Ce fichier définit TOUTES les colonnes possibles qu'un restaurant peut avoir.
L'algorithme prendra automatiquement ce dont il a besoin.
"""

# COLONNES OBLIGATOIRES (minimum requis)
REQUIRED_COLUMNS = ['Date', 'Plat', 'Quantite']

# COLONNES OPTIONNELLES (améliore les prédictions et analyses)
OPTIONAL_COLUMNS = {
    # Informations basiques
    'Categorie': 'Catégorie du plat (Entrée, Plat, Dessert, Boisson, etc.)',
    'Type': 'Type de service (Déjeuner, Dîner, Brunch, etc.)',
    'Service': 'Moment de service (Midi, Soir, etc.)',
    
    # Informations financières
    'Prix_unitaire': 'Prix de vente unitaire du plat (€)',
    'Cout_unitaire': 'Coût de revient unitaire du plat (€)',
    'Prix_total': 'Prix total de la vente (€)',
    'Cout_total': 'Coût total de la vente (€)',
    'Marge_unitaire': 'Marge bénéficiaire unitaire (€)',
    'Marge_totale': 'Marge bénéficiaire totale (€)',
    'Chiffre_affaires': 'Chiffre d\'affaires généré (€)',
    'TVA': 'Montant de TVA (€)',
    'Taux_TVA': 'Taux de TVA appliqué (%)',
    
    # Informations géographiques et contexte
    'Table': 'Numéro de table',
    'Zone': 'Zone du restaurant (Terrasse, Salle, Bar, etc.)',
    'Serveur': 'Nom du serveur',
    'Client': 'Nom/ID du client',
    'Ville': 'Ville du restaurant',
    'Region': 'Région',
    
    # Informations météo et contexte externe
    'Meteo': 'Conditions météo (Ensoleillé, Pluie, etc.)',
    'Temperature': 'Température en °C',
    'Evenement': 'Événement spécial (Fête, Match, Concert, etc.)',
    'Vacances': 'Période de vacances (Oui/Non)',
    'Jour_ferie': 'Jour férié (Oui/Non)',
    
    # Informations promotion et marketing
    'Promotion': 'Promotion active (Oui/Non)',
    'Remise': 'Montant de remise (€)',
    'Code_promo': 'Code promo utilisé',
    'Canal': 'Canal de vente (Sur place, Livraison, Emporter)',
    'Plateforme': 'Plateforme de commande (Direct, Uber, Deliveroo, etc.)',
    
    # Informations opérationnelles
    'Heure': 'Heure de commande',
    'Temps_preparation': 'Temps de préparation (minutes)',
    'Temps_attente': 'Temps d\'attente client (minutes)',
    'Note_client': 'Note donnée par le client (/5)',
    'Commentaire': 'Commentaire client',
    
    # Informations stock et approvisionnement
    'Stock_initial': 'Stock initial du jour',
    'Stock_final': 'Stock final du jour',
    'Rupture': 'Rupture de stock (Oui/Non)',
    'Fournisseur': 'Nom du fournisseur',
    'Lot': 'Numéro de lot',
    'Date_peremption': 'Date de péremption',
    
    # Informations nutritionnelles (optionnel)
    'Calories': 'Nombre de calories',
    'Allergenes': 'Allergènes présents',
    'Vegetarien': 'Plat végétarien (Oui/Non)',
    'Vegan': 'Plat vegan (Oui/Non)',
    'Sans_gluten': 'Sans gluten (Oui/Non)',
    
    # Informations analytiques
    'Saison': 'Saison (Printemps, Été, Automne, Hiver)',
    'Periode': 'Période spéciale (Noël, Été, Rentrée, etc.)',
    'Semaine': 'Numéro de semaine dans l\'année',
    'Mois': 'Mois (1-12 ou nom)',
    'Annee': 'Année',
    'Trimestre': 'Trimestre (T1, T2, T3, T4)',
}

# MAPPING AUTOMATIQUE (variantes de noms de colonnes)
COLUMN_ALIASES = {
    'Date': ['date', 'jour', 'day', 'fecha', 'data'],
    'Plat': ['plat', 'produit', 'item', 'nom', 'dish', 'product', 'name', 'article'],
    'Quantite': ['quantite', 'quantité', 'qte', 'qty', 'quantity', 'nombre', 'number', 'count'],
    'Categorie': ['categorie', 'catégorie', 'category', 'type_plat', 'famille'],
    'Prix_unitaire': ['prix_unitaire', 'prix', 'price', 'prix_vente', 'pu', 'tarif'],
    'Cout_unitaire': ['cout_unitaire', 'coût_unitaire', 'cout', 'coût', 'cost', 'prix_achat', 'cu'],
    'Chiffre_affaires': ['chiffre_affaires', 'ca', 'revenue', 'ventes', 'sales'],
    'Marge': ['marge', 'margin', 'benefice', 'bénéfice', 'profit', 'marge_totale'],
    'Service': ['service', 'moment', 'shift', 'periode_service'],
    'Zone': ['zone', 'emplacement', 'area', 'location', 'salle'],
    'Meteo': ['meteo', 'météo', 'weather', 'temps'],
    'Temperature': ['temperature', 'température', 'temp'],
    'Promotion': ['promotion', 'promo', 'offre', 'deal'],
    'Canal': ['canal', 'channel', 'mode', 'type_vente'],
    'Note_client': ['note_client', 'note', 'rating', 'avis', 'satisfaction'],
}

# COLONNES CALCULÉES AUTOMATIQUEMENT (si données disponibles)
CALCULATED_COLUMNS = {
    'Chiffre_affaires': 'Prix_unitaire * Quantite',
    'Cout_total': 'Cout_unitaire * Quantite',
    'Marge_unitaire': 'Prix_unitaire - Cout_unitaire',
    'Marge_totale': '(Prix_unitaire - Cout_unitaire) * Quantite',
    'Taux_marge': '(Marge_unitaire / Prix_unitaire) * 100',
    'Coefficient_multiplicateur': 'Prix_unitaire / Cout_unitaire',
}

# EXEMPLE DE FICHIER EXCEL COMPLET
EXAMPLE_DATA = """
Date,Plat,Quantite,Categorie,Prix_unitaire,Cout_unitaire,Service,Zone,Meteo,Promotion,Canal
2024-01-15,Burger Classic,25,Plat,12.50,4.80,Déjeuner,Salle,Ensoleillé,Non,Sur place
2024-01-15,Pizza Margherita,18,Plat,11.00,3.50,Déjeuner,Terrasse,Ensoleillé,Non,Sur place
2024-01-15,Salade César,12,Entrée,8.50,2.80,Déjeuner,Salle,Ensoleillé,Oui,Sur place
2024-01-15,Tiramisu,15,Dessert,6.50,2.00,Déjeuner,Salle,Ensoleillé,Non,Sur place
2024-01-15,Coca-Cola,30,Boisson,3.50,0.80,Déjeuner,Salle,Ensoleillé,Non,Sur place
2024-01-15,Burger Classic,32,Plat,12.50,4.80,Dîner,Salle,Nuageux,Non,Sur place
2024-01-15,Pizza 4 Fromages,22,Plat,13.00,4.20,Dîner,Terrasse,Nuageux,Non,Livraison
2024-01-16,Burger Classic,28,Plat,12.50,4.80,Déjeuner,Salle,Pluie,Non,Sur place
"""

if __name__ == "__main__":
    print("=" * 80)
    print("TEMPLATE EXCEL RESTAURANT - GUIDE DES COLONNES")
    print("=" * 80)
    
    print("\n📋 COLONNES OBLIGATOIRES (minimum requis):")
    print("-" * 80)
    for col in REQUIRED_COLUMNS:
        print(f"  • {col}")
    
    print("\n📊 COLONNES OPTIONNELLES (améliore les analyses):")
    print("-" * 80)
    
    categories = {
        'Financières': ['Prix_unitaire', 'Cout_unitaire', 'Prix_total', 'Cout_total', 
                        'Marge_unitaire', 'Marge_totale', 'Chiffre_affaires', 'TVA', 'Taux_TVA'],
        'Contextuelles': ['Categorie', 'Type', 'Service', 'Meteo', 'Temperature', 
                         'Evenement', 'Vacances', 'Jour_ferie'],
        'Géographiques': ['Table', 'Zone', 'Serveur', 'Client', 'Ville', 'Region'],
        'Marketing': ['Promotion', 'Remise', 'Code_promo', 'Canal', 'Plateforme'],
        'Opérationnelles': ['Heure', 'Temps_preparation', 'Temps_attente', 
                           'Note_client', 'Commentaire'],
        'Stock': ['Stock_initial', 'Stock_final', 'Rupture', 'Fournisseur', 
                 'Lot', 'Date_peremption'],
    }
    
    for category, columns in categories.items():
        print(f"\n  📁 {category}:")
        for col in columns:
            if col in OPTIONAL_COLUMNS:
                print(f"    • {col}: {OPTIONAL_COLUMNS[col]}")
    
    print("\n💡 COLONNES CALCULÉES AUTOMATIQUEMENT:")
    print("-" * 80)
    for col, formula in CALCULATED_COLUMNS.items():
        print(f"  • {col} = {formula}")
    
    print("\n✅ L'ALGORITHME EST INTELLIGENT:")
    print("-" * 80)
    print("  • Détecte automatiquement les colonnes disponibles")
    print("  • Utilise uniquement ce dont il a besoin")
    print("  • Calcule les colonnes manquantes si possible")
    print("  • Améliore les prédictions avec les données optionnelles")
    
    print("\n📝 EXEMPLE DE FICHIER EXCEL:")
    print("-" * 80)
    print(EXAMPLE_DATA)
    
    print("\n🎯 RECOMMANDATIONS:")
    print("-" * 80)
    print("  Minimum viable : Date, Plat, Quantite")
    print("  Recommandé     : + Categorie, Prix_unitaire, Cout_unitaire")
    print("  Optimal        : + Service, Zone, Meteo, Promotion, Canal")
    print("  Expert         : Toutes les colonnes ci-dessus")
