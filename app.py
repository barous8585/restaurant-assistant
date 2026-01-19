import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error
import warnings
import io
import re
import docx
import PyPDF2
import json
import requests
import pickle
import os
import hashlib
import time

# Import du module de gestion des sources de données
try:
    from data_sources import (
        DataSourceManager, GoogleSheetsConnector, OneDriveConnector,
        DropboxConnector, URLConnector, AutoSyncManager,
        format_last_sync, get_source_icon
    )
    DATA_SOURCES_AVAILABLE = True
except ImportError:
    DATA_SOURCES_AVAILABLE = False

warnings.filterwarnings('ignore')

st.set_page_config(page_title="Assistant Préparation Restaurant Pro", page_icon="🍽️", layout="wide")

DATA_DIR = "restaurant_data"
ADMIN_PASSWORD_HASH = "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"  # "admin"

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

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

def verify_user(username, password):
    users_file = os.path.join(DATA_DIR, "users.pkl")
    
    if not os.path.exists(users_file):
        return False
    
    with open(users_file, 'rb') as f:
        users = pickle.load(f)
    
    if username not in users:
        return False
    
    return users[username]['password_hash'] == hash_password(password)

def is_user_approved(username):
    """Vérifier si un utilisateur est approuvé par l'admin"""
    users_file = os.path.join(DATA_DIR, "users.pkl")
    
    if not os.path.exists(users_file):
        return False
    
    with open(users_file, 'rb') as f:
        users = pickle.load(f)
    
    if username not in users:
        return False
    
    # Par défaut, considérer comme approuvé si le champ n'existe pas (rétrocompatibilité)
    return users[username].get('approved', True)

def approve_user(username):
    """Approuver un utilisateur (admin seulement)"""
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

def reject_user(username):
    """Rejeter et supprimer un utilisateur (admin seulement)"""
    # Utilise la même fonction que delete_user_account
    return delete_user_account(username)

def get_user_restaurant_info(username):
    users_file = os.path.join(DATA_DIR, "users.pkl")
    
    with open(users_file, 'rb') as f:
        users = pickle.load(f)
    
    return users[username]['restaurant_info']

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

def change_admin_password(new_password):
    """Changer le mot de passe admin (nécessite modification manuelle du code)"""
    new_hash = hash_password(new_password)
    return new_hash

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

def save_restaurant_data(username, restaurants_data):
    user_data_file = os.path.join(DATA_DIR, f"{username}_data.pkl")
    
    with open(user_data_file, 'wb') as f:
        pickle.dump(restaurants_data, f)

def load_restaurant_data(username):
    user_data_file = os.path.join(DATA_DIR, f"{username}_data.pkl")
    
    if os.path.exists(user_data_file):
        try:
            with open(user_data_file, 'rb') as f:
                return pickle.load(f)
        except:
            return {}
    return {}

def get_all_users_stats():
    """Fonction admin: récupère les stats de tous les utilisateurs"""
    users_file = os.path.join(DATA_DIR, "users.pkl")
    
    if not os.path.exists(users_file):
        return []
    
    with open(users_file, 'rb') as f:
        users = pickle.load(f)
    
    stats = []
    for username, user_data in users.items():
        user_restaurants = load_restaurant_data(username)
        nb_restaurants = len(user_restaurants)
        
        stats.append({
            'Utilisateur': username,
            'Nombre de Restaurants': nb_restaurants,
            'Ville Principale': user_data['restaurant_info'].get('city', 'N/A'),
            'Date Inscription': user_data.get('created_at', 'N/A'),
            'Statut': '✅ Approuvé' if user_data.get('approved', True) else '⏳ En attente',
            'Approuvé': user_data.get('approved', True)
        })
    
    return stats

def calculate_invoice(nb_restaurants, price_per_restaurant=49.0):
    """Calcule la facture basée sur le nombre de restaurants"""
    if nb_restaurants <= 3:
        return price_per_restaurant  # Plan Standard: 49€ (1-3 restaurants)
    else:
        return 149.0  # Plan Enterprise: 149€ (4+ restaurants)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False

if 'restaurants' not in st.session_state:
    st.session_state.restaurants = {}
if 'current_restaurant' not in st.session_state:
    st.session_state.current_restaurant = None
if 'recipes' not in st.session_state:
    st.session_state.recipes = {}

WEATHER_API_KEY = "915efd1a1b7e46fb98b121706261701"

def get_weather_forecast(city="Paris", days=7):
    try:
        url = f"https://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={city}&days={days}&lang=fr"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            forecast = []
            for day in data.get('forecast', {}).get('forecastday', []):
                forecast.append({
                    'date': day['date'],
                    'condition': day['day']['condition']['text'],
                    'temp_max': day['day']['maxtemp_c'],
                    'temp_min': day['day']['mintemp_c'],
                    'rain_chance': day['day']['daily_chance_of_rain']
                })
            return forecast
        return None
    except:
        return None

def calculate_weather_impact(weather_data):
    if weather_data is None or (isinstance(weather_data, dict) and not weather_data):
        return 1.0
    
    if isinstance(weather_data, pd.Series):
        rain_chance = weather_data.get('rain_chance', 0)
        temp_max = weather_data.get('temp_max', 20)
    else:
        rain_chance = weather_data.get('rain_chance', 0)
        temp_max = weather_data.get('temp_max', 20)
    
    impact = 1.0
    
    if rain_chance > 70:
        impact *= 0.7
    elif rain_chance > 40:
        impact *= 0.85
    
    if temp_max > 30:
        impact *= 1.1
    elif temp_max < 5:
        impact *= 0.9
    
    return impact

@st.cache_data
def extract_data_from_text(text):
    lines = text.strip().split('\n')
    data = []
    
    for line in lines:
        parts = re.split(r'[,;\t|]', line)
        if len(parts) >= 3:
            try:
                date_str = parts[0].strip()
                plat = parts[1].strip()
                quantite = parts[2].strip()
                
                try:
                    quantite = int(re.sub(r'[^\d]', '', quantite))
                except:
                    continue
                
                data.append({
                    'Date': date_str,
                    'Plat': plat,
                    'Quantite': quantite
                })
            except:
                continue
    
    return pd.DataFrame(data) if data else None

def map_columns_intelligently(df):
    """Mapping intelligent de TOUTES les colonnes possibles d'un restaurant"""
    column_mapping = {}
    
    for col in df.columns:
        col_lower = col.lower().replace('_', ' ').replace('-', ' ')
        
        # Colonnes obligatoires
        if any(word in col_lower for word in ['date', 'jour', 'day']):
            column_mapping[col] = 'Date'
        elif any(word in col_lower for word in ['plat', 'produit', 'item', 'nom', 'dish', 'product']):
            column_mapping[col] = 'Plat'
        elif any(word in col_lower for word in ['quantit', 'qte', 'qty', 'quantity', 'nombre']):
            column_mapping[col] = 'Quantite'
        
        # Colonnes optionnelles - Catégorie et type
        elif any(word in col_lower for word in ['categ', 'famille', 'type plat']):
            column_mapping[col] = 'Categorie'
        elif any(word in col_lower for word in ['service', 'moment', 'shift', 'periode']):
            column_mapping[col] = 'Service'
        
        # Colonnes financières
        elif any(word in col_lower for word in ['prix unit', 'pu', 'prix vente', 'tarif']) and 'cout' not in col_lower:
            column_mapping[col] = 'Prix_unitaire'
        elif any(word in col_lower for word in ['cout unit', 'coût unit', 'cu', 'prix achat', 'cost']):
            column_mapping[col] = 'Cout_unitaire'
        elif any(word in col_lower for word in ['chiffre', 'ca', 'revenue', 'ventes']) and 'affaire' in col_lower:
            column_mapping[col] = 'Chiffre_affaires'
        elif 'marge' in col_lower and 'taux' not in col_lower:
            column_mapping[col] = 'Marge'
        elif 'tva' in col_lower and 'taux' not in col_lower:
            column_mapping[col] = 'TVA'
        
        # Colonnes contextuelles
        elif any(word in col_lower for word in ['zone', 'emplacement', 'salle', 'area']):
            column_mapping[col] = 'Zone'
        elif any(word in col_lower for word in ['table', 'numero']):
            column_mapping[col] = 'Table'
        elif any(word in col_lower for word in ['serveur', 'waiter']):
            column_mapping[col] = 'Serveur'
        elif any(word in col_lower for word in ['meteo', 'météo', 'weather', 'temps']) and 'attente' not in col_lower:
            column_mapping[col] = 'Meteo'
        elif any(word in col_lower for word in ['temperature', 'temp']) and 'ture' in col_lower:
            column_mapping[col] = 'Temperature'
        
        # Colonnes marketing
        elif any(word in col_lower for word in ['promotion', 'promo', 'offre']):
            column_mapping[col] = 'Promotion'
        elif any(word in col_lower for word in ['remise', 'discount', 'reduction']):
            column_mapping[col] = 'Remise'
        elif any(word in col_lower for word in ['canal', 'channel', 'mode vente']):
            column_mapping[col] = 'Canal'
        elif any(word in col_lower for word in ['plateforme', 'platform']):
            column_mapping[col] = 'Plateforme'
        
        # Colonnes opérationnelles
        elif any(word in col_lower for word in ['heure', 'hour', 'time']) and 'attente' not in col_lower:
            column_mapping[col] = 'Heure'
        elif any(word in col_lower for word in ['note', 'rating', 'avis', 'satisfaction']):
            column_mapping[col] = 'Note_client'
        elif any(word in col_lower for word in ['commentaire', 'comment', 'remarque']):
            column_mapping[col] = 'Commentaire'
        
        # Colonnes analytiques
        elif 'mois' in col_lower and col_lower == 'mois':
            column_mapping[col] = 'Mois'
        elif any(word in col_lower for word in ['annee', 'année', 'year']):
            column_mapping[col] = 'Annee'
        elif any(word in col_lower for word in ['trimestre', 'quarter']):
            column_mapping[col] = 'Trimestre'
        elif any(word in col_lower for word in ['semaine', 'week']) and 'jour' not in col_lower:
            column_mapping[col] = 'Semaine'
        elif any(word in col_lower for word in ['saison', 'season']):
            column_mapping[col] = 'Saison'
    
    return column_mapping

def calculate_missing_columns(df):
    """Calcule automatiquement les colonnes manquantes si possible"""
    df = df.copy()
    
    # Création d'une colonne Date si absente mais Mois/Année disponibles
    if 'Date' not in df.columns:
        if 'Mois' in df.columns and 'Annee' in df.columns:
            # Créer une date au 1er jour du mois
            df['Date'] = pd.to_datetime(df['Annee'].astype(str) + '-' + df['Mois'].astype(str) + '-01', errors='coerce')
        elif 'Mois' in df.columns:
            # Si seulement Mois disponible, utiliser l'année en cours
            current_year = datetime.now().year
            df['Date'] = pd.to_datetime(str(current_year) + '-' + df['Mois'].astype(str) + '-01', errors='coerce')
    
    # Calcul du chiffre d'affaires si manquant
    if 'Chiffre_affaires' not in df.columns and 'Prix_unitaire' in df.columns and 'Quantite' in df.columns:
        df['Chiffre_affaires'] = df['Prix_unitaire'] * df['Quantite']
    
    # Calcul du coût total si manquant
    if 'Cout_total' not in df.columns and 'Cout_unitaire' in df.columns and 'Quantite' in df.columns:
        df['Cout_total'] = df['Cout_unitaire'] * df['Quantite']
    
    # Calcul de la marge unitaire si manquant
    if 'Marge_unitaire' not in df.columns and 'Prix_unitaire' in df.columns and 'Cout_unitaire' in df.columns:
        df['Marge_unitaire'] = df['Prix_unitaire'] - df['Cout_unitaire']
    
    # Calcul de la marge totale si manquant
    if 'Marge' not in df.columns and 'Marge_unitaire' in df.columns and 'Quantite' in df.columns:
        df['Marge'] = df['Marge_unitaire'] * df['Quantite']
    elif 'Marge' not in df.columns and 'Chiffre_affaires' in df.columns and 'Cout_total' in df.columns:
        df['Marge'] = df['Chiffre_affaires'] - df['Cout_total']
    
    # Calcul du taux de marge si manquant
    if 'Taux_marge' not in df.columns and 'Marge_unitaire' in df.columns and 'Prix_unitaire' in df.columns:
        df['Taux_marge'] = (df['Marge_unitaire'] / df['Prix_unitaire'] * 100).fillna(0)
    
    return df

@st.cache_data
def load_file(uploaded_file):
    try:
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension == 'csv':
            try:
                df = pd.read_csv(uploaded_file, encoding='utf-8')
            except:
                df = pd.read_csv(uploaded_file, encoding='latin-1')
        
        elif file_extension in ['xlsx', 'xls']:
            df = pd.read_excel(uploaded_file)
        
        elif file_extension == 'json':
            df = pd.read_json(uploaded_file)
        
        elif file_extension == 'txt':
            content = uploaded_file.read().decode('utf-8', errors='ignore')
            df = extract_data_from_text(content)
        
        elif file_extension == 'docx':
            doc = docx.Document(uploaded_file)
            text = '\n'.join([para.text for para in doc.paragraphs])
            df = extract_data_from_text(text)
        
        elif file_extension == 'pdf':
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ''
            for page in pdf_reader.pages:
                text += page.extract_text() + '\n'
            df = extract_data_from_text(text)
        
        else:
            content = uploaded_file.read().decode('utf-8', errors='ignore')
            df = extract_data_from_text(content)
        
        if df is None or df.empty:
            return None
        
        df.columns = df.columns.str.strip()
        
        column_mapping = map_columns_intelligently(df)
        df = df.rename(columns=column_mapping)
        
        df = calculate_missing_columns(df)
        
        return df
    
    except Exception as e:
        st.error(f"Erreur de chargement: {str(e)}")
        return None

def safe_execute(func, *args, fallback_value=None, error_message="Une erreur est survenue", **kwargs):
    """Exécute une fonction de manière sécurisée avec gestion d'erreur"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        st.warning(f"⚠️ {error_message}: {str(e)}")
        return fallback_value

def safe_format_date(date_value):
    """Formate une date en toute sécurité"""
    try:
        if pd.isna(date_value):
            return "N/A"
        if isinstance(date_value, str):
            return date_value
        return date_value.strftime('%d/%m/%Y')
    except:
        return "N/A"

def clean_and_validate_data(df):
    """Nettoie et valide les données de manière robuste"""
    df = df.copy()
    
    # 1. Nettoyage colonnes obligatoires
    required_cols = ['Date', 'Plat', 'Quantite']
    
    # Date : Conversion ultra-robuste
    if 'Date' in df.columns:
        # Essayer plusieurs formats
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce', infer_datetime_format=True)
        
        # Supprimer lignes avec dates invalides
        invalid_dates = df['Date'].isna().sum()
        if invalid_dates > 0:
            st.warning(f"⚠️ {invalid_dates} lignes avec dates invalides supprimées")
        df = df.dropna(subset=['Date'])
    
    # Plat : Conversion en string et nettoyage
    if 'Plat' in df.columns:
        df['Plat'] = df['Plat'].astype(str).str.strip()
        # Supprimer lignes vides
        df = df[df['Plat'] != '']
        df = df[df['Plat'].str.lower() != 'nan']
    
    # Quantité : Conversion en numérique
    if 'Quantite' in df.columns:
        # Remplacer virgules par points pour les décimaux
        if df['Quantite'].dtype == 'object':
            df['Quantite'] = df['Quantite'].astype(str).str.replace(',', '.').str.replace(' ', '')
        
        df['Quantite'] = pd.to_numeric(df['Quantite'], errors='coerce')
        
        # Supprimer quantités invalides ou négatives
        invalid_qty = df['Quantite'].isna().sum()
        if invalid_qty > 0:
            st.warning(f"⚠️ {invalid_qty} lignes avec quantités invalides supprimées")
        
        df = df.dropna(subset=['Quantite'])
        df = df[df['Quantite'] > 0]
        
        # Arrondir à l'entier
        df['Quantite'] = df['Quantite'].round(0).astype(int)
    
    # 2. Nettoyage colonnes financières (si présentes)
    financial_cols = ['Prix_unitaire', 'Cout_unitaire', 'Chiffre_affaires', 'Marge', 'Cout_total', 'Marge_unitaire']
    
    for col in financial_cols:
        if col in df.columns:
            if df[col].dtype == 'object':
                # Nettoyer format monétaire (€, espaces, virgules)
                df[col] = df[col].astype(str).str.replace('€', '').str.replace(' ', '').str.replace(',', '.')
            
            df[col] = pd.to_numeric(df[col], errors='coerce')
            # Remplacer NaN par 0 pour colonnes financières
            df[col] = df[col].fillna(0)
    
    # 3. Vérification données suffisantes
    if len(df) == 0:
        return None, "Aucune donnée valide après nettoyage"
    
    if len(df) < 7:
        return None, f"Pas assez de données ({len(df)} lignes). Minimum 7 jours requis."
    
    return df, None

def create_features(df):
    df = df.copy()
    
    # Date déjà nettoyée par clean_and_validate_data
    df = df.sort_values('Date')
    
    df['Jour_Semaine'] = df['Date'].dt.dayofweek
    df['Jour_Mois'] = df['Date'].dt.day
    df['Mois'] = df['Date'].dt.month
    df['Annee'] = df['Date'].dt.year
    df['Semaine_Annee'] = df['Date'].dt.isocalendar().week
    df['Trimestre'] = df['Date'].dt.quarter
    df['Est_Weekend'] = df['Jour_Semaine'].isin([5, 6]).astype(int)
    df['Est_Debut_Mois'] = (df['Jour_Mois'] <= 5).astype(int)
    df['Est_Fin_Mois'] = (df['Jour_Mois'] >= 25).astype(int)
    
    return df

def calculate_waste_savings(df, predictions):
    if df is None or predictions is None or len(df) == 0 or len(predictions) == 0:
        return None
    
    df_temp = df.copy()
    df_temp['Date'] = pd.to_datetime(df_temp['Date'])
    daily_sales = df_temp.groupby('Date')['Quantite'].sum()
    
    # Statistiques des ventes réelles
    avg_daily_sales = daily_sales.mean()
    std_daily_sales = daily_sales.std()
    
    # Méthode traditionnelle : sur-préparer pour éviter les ruptures
    # On prépare moyenne + 20% de marge de sécurité
    traditional_prep_factor = 1.20
    
    # Méthode ML : prédictions précises + petite marge de 5%
    ml_prep_factor = 1.05
    
    # Calcul du gaspillage MOYEN PAR JOUR (pas cumulé)
    avg_pred = predictions['Quantite_Prevue'].mean()
    
    # Gaspillage traditionnel par jour
    daily_waste_traditional = max(0, (avg_daily_sales * traditional_prep_factor) - avg_daily_sales)
    
    # Gaspillage ML par jour (beaucoup plus faible)
    daily_waste_ml = max(0, (avg_pred * ml_prep_factor) - avg_pred)
    
    # Économies par jour
    daily_savings = daily_waste_traditional - daily_waste_ml
    
    # Projections mensuelles (30 jours)
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

def safe_predict_sales_ml(df, plat, jours_prevision=7):
    """Wrapper sécurisé pour predict_sales_ml"""
    try:
        return predict_sales_ml(df, plat, jours_prevision)
    except Exception as e:
        st.warning(f"⚠️ Impossible de prédire pour {plat}: {str(e)}")
        return None, None, None

def predict_sales_ml(df, plat, jours_prevision=7):
    """Prédictions ML - Note: Les erreurs doivent être gérées par l'appelant"""
    plat_data = df[df['Plat'] == plat].copy()
    
    if len(plat_data) < 14:
        return None, None, None
    
    plat_data = plat_data.sort_values('Date')
    plat_data = create_features(plat_data)

    agg_dict = {
        'Quantite': 'sum',
        'Jour_Semaine': 'first',
        'Jour_Mois': 'first',
        'Mois': 'first',
        'Annee': 'first',
        'Semaine_Annee': 'first',
        'Trimestre': 'first',
        'Est_Weekend': 'first',
        'Est_Debut_Mois': 'first',
        'Est_Fin_Mois': 'first'
    }
    
    optional_features = []
    
    if 'Prix_unitaire' in plat_data.columns:
        agg_dict['Prix_unitaire'] = 'mean'
        optional_features.append('Prix_unitaire')
    
    if 'Service' in plat_data.columns:
        plat_data['Service_encoded'] = plat_data['Service'].astype('category').cat.codes
        agg_dict['Service_encoded'] = 'first'
        optional_features.append('Service_encoded')
    
    if 'Zone' in plat_data.columns:
        plat_data['Zone_encoded'] = plat_data['Zone'].astype('category').cat.codes
        agg_dict['Zone_encoded'] = 'first'
        optional_features.append('Zone_encoded')
    
    if 'Meteo' in plat_data.columns:
        plat_data['Meteo_encoded'] = plat_data['Meteo'].astype('category').cat.codes
        agg_dict['Meteo_encoded'] = 'first'
        optional_features.append('Meteo_encoded')
    
    if 'Promotion' in plat_data.columns:
        plat_data['Promotion_encoded'] = (plat_data['Promotion'].astype(str).str.lower() == 'oui').astype(int)
        agg_dict['Promotion_encoded'] = 'max'
        optional_features.append('Promotion_encoded')
    
    if 'Canal' in plat_data.columns:
        plat_data['Canal_encoded'] = plat_data['Canal'].astype('category').cat.codes
        agg_dict['Canal_encoded'] = 'first'
        optional_features.append('Canal_encoded')
    
    plat_data_agg = plat_data.groupby('Date').agg(agg_dict).reset_index()
    
    for lag in [1, 3, 7, 14]:
        plat_data_agg[f'Lag_{lag}'] = plat_data_agg['Quantite'].shift(lag)
    
    plat_data_agg['Moyenne_Mobile_7'] = plat_data_agg['Quantite'].rolling(window=7, min_periods=1).mean()
    plat_data_agg['Moyenne_Mobile_14'] = plat_data_agg['Quantite'].rolling(window=14, min_periods=1).mean()
    plat_data_agg['Ecart_Type_7'] = plat_data_agg['Quantite'].rolling(window=7, min_periods=1).std()
    plat_data_agg['Tendance'] = range(len(plat_data_agg))
    
    plat_data_agg = plat_data_agg.dropna()
    
    if len(plat_data_agg) < 7:
        return None, None, None
    
    train_size = int(len(plat_data_agg) * 0.8)
    train_data = plat_data_agg[:train_size]
    test_data = plat_data_agg[train_size:]
    
    features = ['Jour_Semaine', 'Jour_Mois', 'Mois', 'Semaine_Annee', 'Trimestre',
                'Est_Weekend', 'Est_Debut_Mois', 'Est_Fin_Mois', 'Tendance',
                'Lag_1', 'Lag_3', 'Lag_7', 'Lag_14',
                'Moyenne_Mobile_7', 'Moyenne_Mobile_14', 'Ecart_Type_7'] + optional_features
    
    X_train = train_data[features]
    y_train = train_data['Quantite']
    
    models = {
        'RandomForest': RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42, n_jobs=-1),
        'GradientBoosting': GradientBoostingRegressor(n_estimators=150, max_depth=5, learning_rate=0.1, random_state=42)
    }
    
    best_model = None
    best_score = float('inf')
    best_name = None
    model_metrics = {}
    
    for name, model in models.items():
        model.fit(X_train, y_train)
        
        if len(test_data) > 0:
            X_test = test_data[features]
            y_test = test_data['Quantite']
            predictions = model.predict(X_test)
            
            mae = mean_absolute_error(y_test, predictions)
            rmse = np.sqrt(mean_squared_error(y_test, predictions))
            mape = mean_absolute_percentage_error(y_test, predictions) * 100
            
            model_metrics[name] = {
                'MAE': mae,
                'RMSE': rmse,
                'MAPE': mape
            }
            
            if mae < best_score:
                best_score = mae
                best_model = model
                best_name = name
        else:
            best_model = model
            best_name = name
    
    last_row = plat_data_agg.iloc[-1]
    predictions = []
    derniere_date = last_row['Date']
    
    current_data = plat_data_agg.copy()
    
    for i in range(1, jours_prevision + 1):
        future_date = derniere_date + timedelta(days=i)
        
        new_row = {
            'Date': future_date,
            'Jour_Semaine': future_date.dayofweek,
            'Jour_Mois': future_date.day,
            'Mois': future_date.month,
            'Annee': future_date.year,
            'Semaine_Annee': future_date.isocalendar()[1],
            'Trimestre': (future_date.month - 1) // 3 + 1,
            'Est_Weekend': int(future_date.dayofweek in [5, 6]),
            'Est_Debut_Mois': int(future_date.day <= 5),
            'Est_Fin_Mois': int(future_date.day >= 25),
            'Tendance': last_row['Tendance'] + i
        }
        
        for feat in optional_features:
            if feat in last_row:
                new_row[feat] = last_row[feat]
        
        if len(current_data) >= 14:
            new_row['Lag_1'] = current_data.iloc[-1]['Quantite']
            new_row['Lag_3'] = current_data.iloc[-3]['Quantite']
            new_row['Lag_7'] = current_data.iloc[-7]['Quantite']
            new_row['Lag_14'] = current_data.iloc[-14]['Quantite']
            new_row['Moyenne_Mobile_7'] = current_data.tail(7)['Quantite'].mean()
            new_row['Moyenne_Mobile_14'] = current_data.tail(14)['Quantite'].mean()
            new_row['Ecart_Type_7'] = current_data.tail(7)['Quantite'].std()
        else:
            new_row['Lag_1'] = current_data.iloc[-1]['Quantite'] if len(current_data) >= 1 else last_row['Quantite']
            new_row['Lag_3'] = current_data.iloc[-3]['Quantite'] if len(current_data) >= 3 else last_row['Quantite']
            new_row['Lag_7'] = current_data.iloc[-7]['Quantite'] if len(current_data) >= 7 else last_row['Quantite']
            new_row['Lag_14'] = current_data.iloc[-14]['Quantite'] if len(current_data) >= 14 else last_row['Quantite']
            new_row['Moyenne_Mobile_7'] = current_data.tail(7)['Quantite'].mean() if len(current_data) >= 7 else last_row['Quantite']
            new_row['Moyenne_Mobile_14'] = current_data.tail(14)['Quantite'].mean() if len(current_data) >= 14 else last_row['Quantite']
            new_row['Ecart_Type_7'] = current_data.tail(7)['Quantite'].std() if len(current_data) >= 7 else 0
        
        X_pred = pd.DataFrame([new_row])[features]
        pred_quantite = best_model.predict(X_pred)[0]
        pred_quantite = max(0, pred_quantite)
        
        predictions.append({
            'Date': future_date,
            'Jour': future_date.strftime('%A'),
            'Quantite_Prevue': int(round(pred_quantite))
        })
        
        new_row['Quantite'] = pred_quantite
        current_data = pd.concat([current_data, pd.DataFrame([new_row])], ignore_index=True)
    
    pred_df = pd.DataFrame(predictions)
    
    return pred_df, model_metrics, best_name

def extract_hour_from_data(df):
    """Extrait l'heure des données si disponible"""
    if 'Heure' not in df.columns:
        return df
    
    df = df.copy()
    
    try:
        if df['Heure'].dtype == 'object':
            df['Heure_parsed'] = pd.to_datetime(df['Heure'], format='%H:%M', errors='coerce').dt.hour
        else:
            df['Heure_parsed'] = pd.to_datetime(df['Heure'], errors='coerce').dt.hour
        
        df['Heure_parsed'] = df['Heure_parsed'].fillna(-1).astype(int)
    except:
        df['Heure_parsed'] = -1
    
    return df

def get_hourly_pattern(df, plat):
    """Analyse les patterns de vente horaires pour un plat"""
    if 'Heure' not in df.columns:
        return None
    
    df = extract_hour_from_data(df)
    plat_data = df[df['Plat'] == plat].copy()
    
    if len(plat_data) == 0 or 'Heure_parsed' not in plat_data.columns:
        return None
    
    plat_data = plat_data[plat_data['Heure_parsed'] >= 0]
    
    if len(plat_data) == 0:
        return None
    
    hourly_stats = plat_data.groupby('Heure_parsed').agg({
        'Quantite': ['mean', 'std', 'sum', 'count']
    }).reset_index()
    
    hourly_stats.columns = ['Heure', 'Moyenne', 'Ecart_type', 'Total', 'Nb_occurences']
    hourly_stats['Ecart_type'] = hourly_stats['Ecart_type'].fillna(0)
    
    return hourly_stats

def predict_intraday_sales(df, plat, current_hour=None):
    """Prédictions heure par heure pour aujourd'hui"""
    if current_hour is None:
        current_hour = datetime.now().hour
    
    hourly_pattern = get_hourly_pattern(df, plat)
    
    if hourly_pattern is None:
        plat_data = df[df['Plat'] == plat].copy()
        if len(plat_data) == 0:
            return None
        
        daily_avg = plat_data.groupby('Date')['Quantite'].sum().mean()
        
        predictions = []
        service_hours = {
            'Déjeuner': list(range(11, 15)),
            'Dîner': list(range(18, 23))
        }
        
        for service, hours in service_hours.items():
            for hour in hours:
                if hour > current_hour:
                    portion = daily_avg / len(service_hours['Déjeuner'] + service_hours['Dîner'])
                    predictions.append({
                        'Heure': f"{hour:02d}:00",
                        'Service': service,
                        'Quantite_prevue': int(portion),
                        'Confiance': 'Faible',
                        'Base': 'Moyenne journalière'
                    })
        
        return pd.DataFrame(predictions) if predictions else None
    
    plat_data = df[df['Plat'] == plat].copy()
    plat_data['Date'] = pd.to_datetime(plat_data['Date'])
    plat_data = create_features(plat_data)
    
    today = datetime.now()
    today_sales = plat_data[plat_data['Date'].dt.date == today.date()]
    
    sales_so_far = today_sales['Quantite'].sum() if len(today_sales) > 0 else 0
    
    is_weekend = today.weekday() in [5, 6]
    
    predictions = []
    for _, row in hourly_pattern.iterrows():
        hour = int(row['Heure'])
        
        if hour <= current_hour:
            continue
        
        base_qty = row['Moyenne']
        std = row['Ecart_type']
        occurrences = row['Nb_occurences']
        
        weekend_factor = 1.15 if is_weekend else 1.0
        
        adjusted_qty = base_qty * weekend_factor
        
        if 11 <= hour <= 14:
            service = 'Déjeuner'
        elif 18 <= hour <= 22:
            service = 'Dîner'
        else:
            service = 'Hors-service'
        
        if occurrences >= 5:
            confiance = 'Élevée'
        elif occurrences >= 3:
            confiance = 'Moyenne'
        else:
            confiance = 'Faible'
        
        predictions.append({
            'Heure': f"{hour:02d}:00",
            'Service': service,
            'Quantite_prevue': max(0, int(round(adjusted_qty))),
            'Ecart_type': round(std, 1),
            'Confiance': confiance,
            'Base': f"{int(occurrences)} jours"
        })
    
    pred_df = pd.DataFrame(predictions)
    
    if len(pred_df) > 0 and sales_so_far > 0:
        pred_df['Note'] = f"📊 Déjà vendu aujourd'hui: {int(sales_so_far)} portions"
    
    return pred_df

def get_realtime_adjustments(city, df, current_sales_today=0):
    """Ajustements en temps réel basés sur météo et ventes actuelles"""
    adjustments = {
        'weather_factor': 1.0,
        'sales_trend_factor': 1.0,
        'recommendations': []
    }
    
    weather_data = get_weather_forecast(city, 1)
    
    if weather_data and len(weather_data) > 0:
        today_weather = weather_data[0]
        condition = today_weather.get('condition', '').lower()
        rain_chance = today_weather.get('rain_chance', 0)
        temp = today_weather.get('temp_max', 20)
        
        if 'pluie' in condition or 'orage' in condition or rain_chance > 60:
            adjustments['weather_factor'] = 0.85
            adjustments['recommendations'].append("🌧️ Pluie prévue: -15% affluence attendue")
        elif 'ensoleillé' in condition or 'soleil' in condition:
            if temp > 25:
                adjustments['weather_factor'] = 1.20
                adjustments['recommendations'].append("☀️ Beau temps chaud: +20% affluence terrasse")
            else:
                adjustments['weather_factor'] = 1.10
                adjustments['recommendations'].append("☀️ Beau temps: +10% affluence")
        elif 'nuageux' in condition:
            adjustments['weather_factor'] = 0.95
            adjustments['recommendations'].append("☁️ Temps nuageux: -5% affluence")
        
        if temp > 28:
            adjustments['recommendations'].append("🥗 Favoriser plats froids et salades (+25%)")
        elif temp < 10:
            adjustments['recommendations'].append("🍲 Favoriser soupes et plats chauds (+20%)")
    
    if df is not None and len(df) > 0:
        df_temp = df.copy()
        df_temp['Date'] = pd.to_datetime(df_temp['Date'])
        
        same_weekday = df_temp[df_temp['Date'].dt.dayofweek == datetime.now().weekday()]
        
        if len(same_weekday) > 0:
            same_weekday_grouped = same_weekday.groupby(same_weekday['Date'].dt.date)['Quantite'].sum()
            avg_same_weekday = same_weekday_grouped.mean()
            
            current_hour = datetime.now().hour
            
            if current_hour >= 14:
                expected_by_now = avg_same_weekday * 0.6
            elif current_hour >= 12:
                expected_by_now = avg_same_weekday * 0.4
            elif current_hour >= 10:
                expected_by_now = avg_same_weekday * 0.1
            else:
                expected_by_now = 0
            
            if expected_by_now > 0 and current_sales_today > 0:
                ratio = current_sales_today / expected_by_now
                
                if ratio > 1.2:
                    adjustments['sales_trend_factor'] = 1.15
                    adjustments['recommendations'].append(f"📈 Ventes actuelles +{int((ratio-1)*100)}% vs normal: Augmenter préparations dîner")
                elif ratio < 0.8:
                    adjustments['sales_trend_factor'] = 0.90
                    adjustments['recommendations'].append(f"📉 Ventes actuelles {int((ratio-1)*100)}% vs normal: Réduire préparations dîner")
                else:
                    adjustments['recommendations'].append("✅ Ventes dans la normale")
    
    return adjustments

if not st.session_state.logged_in:
    st.title("🍽️ Assistant de Préparation Restaurant Pro")
    st.markdown("### Connexion / Inscription")
    
    tab1, tab2, tab3 = st.tabs(["Se connecter", "Créer un compte", "🔐 Admin"])
    
    with tab1:
        st.subheader("Connexion")
        login_username = st.text_input("Nom d'utilisateur", key="login_username")
        login_password = st.text_input("Mot de passe", type="password", key="login_password")
        
        if st.button("Se connecter"):
            if verify_user(login_username, login_password):
                # Vérifier si le compte est approuvé
                if not is_user_approved(login_username):
                    st.warning("⏳ **Compte en attente d'approbation**")
                    st.info("Votre compte a été créé avec succès mais est en attente de validation par l'administrateur.")
                    st.info("📧 Vous serez notifié dès que votre compte sera approuvé. Merci de votre patience !")
                else:
                    st.session_state.logged_in = True
                    st.session_state.username = login_username
                    st.session_state.restaurants = load_restaurant_data(login_username)
                    if st.session_state.restaurants:
                        st.session_state.current_restaurant = list(st.session_state.restaurants.keys())[0]
                    st.success(f"Bienvenue {login_username} !")
                    st.rerun()
            else:
                st.error("Nom d'utilisateur ou mot de passe incorrect")
    
    with tab2:
        st.subheader("Créer un compte")
        new_username = st.text_input("Nom d'utilisateur", key="new_username")
        new_password = st.text_input("Mot de passe", type="password", key="new_password")
        new_password_confirm = st.text_input("Confirmer le mot de passe", type="password", key="new_password_confirm")
        
        st.markdown("#### Informations du restaurant")
        resto_name = st.text_input("Nom du restaurant")
        resto_city = st.text_input("Ville", value="Paris")
        avg_portion_cost = st.number_input("Coût moyen par portion (€)", min_value=0.0, value=3.5, step=0.1)
        
        if st.button("Créer le compte"):
            if not new_username or not new_password:
                st.error("Veuillez remplir tous les champs")
            elif new_password != new_password_confirm:
                st.error("Les mots de passe ne correspondent pas")
            elif len(new_password) < 6:
                st.error("Le mot de passe doit contenir au moins 6 caractères")
            elif not resto_name:
                st.error("Veuillez renseigner le nom du restaurant")
            else:
                users_file = os.path.join(DATA_DIR, "users.pkl")
                if os.path.exists(users_file):
                    with open(users_file, 'rb') as f:
                        users = pickle.load(f)
                    if new_username in users:
                        st.error("Ce nom d'utilisateur existe déjà")
                    else:
                        restaurant_info = {
                            'name': resto_name,
                            'city': resto_city,
                            'cost_per_portion': avg_portion_cost
                        }
                        save_user_credentials(new_username, new_password, restaurant_info)
                        
                        initial_data = {
                            resto_name: {
                                'name': resto_name,
                                'city': resto_city,
                                'cost_per_portion': avg_portion_cost,
                                'data': None,
                                'recipes': {}
                            }
                        }
                        save_restaurant_data(new_username, initial_data)
                        
                        st.success("✅ Compte créé avec succès !")
                        st.warning("⏳ **Votre compte est en attente d'approbation par l'administrateur**")
                        st.info("📧 Vous recevrez une notification dès que votre compte sera validé. Vous pourrez alors vous connecter et utiliser l'application.")
                else:
                    restaurant_info = {
                        'name': resto_name,
                        'city': resto_city,
                        'cost_per_portion': avg_portion_cost
                    }
                    save_user_credentials(new_username, new_password, restaurant_info)
                    
                    initial_data = {
                        resto_name: {
                            'name': resto_name,
                            'city': resto_city,
                            'cost_per_portion': avg_portion_cost,
                            'data': None,
                            'recipes': {}
                        }
                    }
                    save_restaurant_data(new_username, initial_data)
                    
                    st.success("✅ Compte créé avec succès !")
                    st.warning("⏳ **Votre compte est en attente d'approbation par l'administrateur**")
                    st.info("📧 Vous recevrez une notification dès que votre compte sera validé. Vous pourrez alors vous connecter et utiliser l'application.")
    
    with tab3:
        st.subheader("🔐 Administration")
        st.info("Accès réservé au propriétaire de l'application")
        
        admin_password = st.text_input("Mot de passe administrateur", type="password", key="admin_password")
        
        if st.button("Connexion Admin"):
            if hash_password(admin_password) == ADMIN_PASSWORD_HASH:
                st.session_state.logged_in = True
                st.session_state.is_admin = True
                st.session_state.username = "ADMIN"
                st.success("🔓 Accès administrateur accordé")
                st.rerun()
            else:
                st.error("❌ Mot de passe administrateur incorrect")
    
    st.stop()

if st.session_state.is_admin:
    st.title("🔐 Tableau de Bord Administrateur")
    st.markdown("---")
    
    col_btn1, col_btn2 = st.sidebar.columns(2)
    
    with col_btn1:
        if st.button("🚪 Déconnexion", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.is_admin = False
            st.session_state.username = None
            st.rerun()
    
    st.sidebar.markdown("---")
    
    # Section Paramètres Admin
    with st.sidebar.expander("⚙️ Paramètres Admin"):
        st.markdown("### 🔐 Changer le Mot de Passe Admin")
        st.info("Le nouveau hash sera affiché. Vous devrez le copier dans le code.")
        
        admin_new_pwd = st.text_input("Nouveau mot de passe admin", type="password", key="admin_new_pwd")
        admin_new_pwd_confirm = st.text_input("Confirmer", type="password", key="admin_new_pwd_confirm")
        
        if st.button("Générer le nouveau hash"):
            if not admin_new_pwd:
                st.error("Veuillez entrer un mot de passe")
            elif admin_new_pwd != admin_new_pwd_confirm:
                st.error("Les mots de passe ne correspondent pas")
            elif len(admin_new_pwd) < 6:
                st.error("Le mot de passe doit contenir au moins 6 caractères")
            else:
                new_hash = change_admin_password(admin_new_pwd)
                st.success("✅ Hash généré avec succès !")
                st.code(f'ADMIN_PASSWORD_HASH = "{new_hash}"', language="python")
                st.warning("⚠️ Copiez cette ligne dans app.py à la ligne 26, puis redéployez l'application.")
    
    st.sidebar.markdown("---")
    
    users_stats = get_all_users_stats()
    
    if users_stats:
        df_users = pd.DataFrame(users_stats)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("👥 Total Utilisateurs", len(df_users))
        with col2:
            total_restaurants = df_users['Nombre de Restaurants'].sum()
            st.metric("🏢 Total Restaurants", total_restaurants)
        with col3:
            users_standard = len(df_users[df_users['Nombre de Restaurants'] <= 3])
            st.metric("📋 Standard (1-3)", users_standard)
        with col4:
            users_enterprise = len(df_users[df_users['Nombre de Restaurants'] > 3])
            st.metric("⭐ Enterprise (4+)", users_enterprise)
        
        st.markdown("---")
        
        # Calculer les factures et plans AVANT de filtrer
        df_users['Facture (€)'] = df_users['Nombre de Restaurants'].apply(calculate_invoice)
        df_users['Plan'] = df_users['Nombre de Restaurants'].apply(
            lambda x: "Standard (49€)" if x <= 3 else "Enterprise (149€)"
        )
        
        # Section Comptes en Attente
        pending_users = df_users[df_users['Approuvé'] == False]
        
        if len(pending_users) > 0:
            st.subheader(f"⏳ Comptes en Attente d'Approbation ({len(pending_users)})")
            st.warning(f"**{len(pending_users)} nouveau(x) compte(s)** nécessite(nt) votre validation avant d'accéder à l'application.")
            
            for idx, user in pending_users.iterrows():
                with st.expander(f"🔔 {user['Utilisateur']} - {user['Ville Principale']}", expanded=True):
                    col_info1, col_info2 = st.columns(2)
                    
                    with col_info1:
                        st.write(f"**Nom d'utilisateur** : {user['Utilisateur']}")
                        st.write(f"**Restaurant** : {user['Ville Principale']}")
                        st.write(f"**Date d'inscription** : {user['Date Inscription']}")
                    
                    with col_info2:
                        st.write(f"**Nombre de restaurants** : {user['Nombre de Restaurants']}")
                        st.write(f"**Plan prévu** : {user['Plan']}")
                        st.write(f"**Facture** : {user['Facture (€)']} €/mois")
                    
                    st.markdown("---")
                    
                    col_action1, col_action2, col_action3 = st.columns([1, 1, 2])
                    
                    with col_action1:
                        if st.button(f"✅ Approuver", key=f"approve_{user['Utilisateur']}", type="primary", use_container_width=True):
                            success, message = approve_user(user['Utilisateur'])
                            if success:
                                st.success(f"✅ {message}")
                                st.balloons()
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
                    
                    with col_action2:
                        if st.button(f"❌ Rejeter", key=f"reject_{user['Utilisateur']}", type="secondary", use_container_width=True):
                            st.session_state[f'confirm_reject_{user["Utilisateur"]}'] = True
                    
                    # Confirmation de rejet
                    if st.session_state.get(f'confirm_reject_{user["Utilisateur"]}'):
                        st.error(f"⚠️ Confirmer le rejet de **{user['Utilisateur']}** ? Cette action supprimera définitivement le compte.")
                        col_confirm1, col_confirm2 = st.columns(2)
                        with col_confirm1:
                            if st.button(f"Confirmer le rejet", key=f"confirm_reject_btn_{user['Utilisateur']}", type="primary"):
                                success, message = reject_user(user['Utilisateur'])
                                if success:
                                    st.success(f"✅ {message}")
                                    st.session_state[f'confirm_reject_{user["Utilisateur"]}'] = False
                                    st.rerun()
                                else:
                                    st.error(f"❌ {message}")
                        with col_confirm2:
                            if st.button(f"Annuler", key=f"cancel_reject_{user['Utilisateur']}"):
                                st.session_state[f'confirm_reject_{user["Utilisateur"]}'] = False
                                st.rerun()
        
        st.markdown("---")
        st.subheader("📊 Liste des Utilisateurs")
        
        st.dataframe(
            df_users[['Utilisateur', 'Statut', 'Nombre de Restaurants', 'Plan', 'Facture (€)', 'Ville Principale', 'Date Inscription']],
            use_container_width=True,
            hide_index=True
        )
        
        st.markdown("---")
        st.subheader("💰 Analyse de Facturation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            total_revenue = df_users['Facture (€)'].sum()
            st.metric("💵 Revenu Mensuel Total", f"{total_revenue:.2f} €")
            
            mrr_projection = total_revenue * 12
            st.metric("📈 Projection Annuelle (MRR x12)", f"{mrr_projection:.2f} €")
        
        with col2:
            fig_plans = px.pie(
                df_users,
                names='Plan',
                title="Répartition des Plans"
            )
            st.plotly_chart(fig_plans, use_container_width=True)
        
        st.markdown("---")
        st.subheader("📥 Export des Données")
        
        col1, col2 = st.columns(2)
        
        with col1:
            csv_export = df_users.to_csv(index=False)
            st.download_button(
                label="⬇️ Télécharger CSV",
                data=csv_export,
                file_name=f"facturation_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        with col2:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_users.to_excel(writer, index=False, sheet_name='Facturation')
            
            st.download_button(
                label="⬇️ Télécharger Excel",
                data=buffer.getvalue(),
                file_name=f"facturation_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        st.markdown("---")
        st.subheader("📈 Détails par Utilisateur")
        
        selected_user = st.selectbox("Sélectionner un utilisateur", df_users['Utilisateur'].tolist())
        
        if selected_user:
            user_restaurants = load_restaurant_data(selected_user)
            
            col_header1, col_header2 = st.columns([3, 1])
            
            with col_header1:
                st.markdown(f"#### Restaurants de **{selected_user}**")
            
            with col_header2:
                # Bouton de suppression
                if st.button(f"🗑️ Supprimer {selected_user}", type="secondary", use_container_width=True):
                    st.session_state.confirm_delete_user = selected_user
            
            # Confirmation de suppression
            if st.session_state.get('confirm_delete_user') == selected_user:
                st.warning(f"⚠️ **ATTENTION** : Vous êtes sur le point de supprimer définitivement le compte **{selected_user}**")
                st.error("Cette action est **IRRÉVERSIBLE** et supprimera :")
                st.markdown(f"""
                - ❌ Le compte utilisateur
                - ❌ Tous ses restaurants ({len(user_restaurants)} restaurant(s))
                - ❌ Toutes ses données (ventes, recettes, etc.)
                """)
                
                col_confirm1, col_confirm2, col_confirm3 = st.columns([1, 1, 1])
                
                with col_confirm1:
                    if st.button("✅ Confirmer la suppression", type="primary", use_container_width=True):
                        success, message = delete_user_account(selected_user)
                        if success:
                            st.success(f"✅ {message}")
                            st.session_state.confirm_delete_user = None
                            st.balloons()
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                
                with col_confirm2:
                    if st.button("❌ Annuler", use_container_width=True):
                        st.session_state.confirm_delete_user = None
                        st.rerun()
            
            if user_restaurants:
                resto_list = []
                for resto_name, resto_data in user_restaurants.items():
                    resto_list.append({
                        'Restaurant': resto_name,
                        'Ville': resto_data.get('city', 'N/A'),
                        'Coût/portion': f"{resto_data.get('cost_per_portion', 0)}€",
                        'Données': "✅ Oui" if resto_data.get('data') is not None else "❌ Non"
                    })
                
                df_restos = pd.DataFrame(resto_list)
                st.dataframe(df_restos, use_container_width=True, hide_index=True)
                
                nb_restos = len(user_restaurants)
                facture = calculate_invoice(nb_restos)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("🏢 Nombre de Restaurants", nb_restos)
                with col2:
                    plan = "Standard" if nb_restos <= 3 else "Enterprise"
                    st.metric("📋 Plan", plan)
                with col3:
                    st.metric("💰 Facture Mensuelle", f"{facture} €")
            else:
                st.info("Aucun restaurant pour cet utilisateur")
    
    else:
        st.info("Aucun utilisateur enregistré pour le moment")
    
    st.stop()

st.sidebar.title(f"👤 {st.session_state.username}")

if st.sidebar.button("🚪 Se déconnecter"):
    save_restaurant_data(st.session_state.username, st.session_state.restaurants)
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.restaurants = {}
    st.session_state.current_restaurant = None
    st.rerun()

st.sidebar.markdown("---")

# Section Sources de Données
if DATA_SOURCES_AVAILABLE and st.session_state.current_restaurant:
    with st.sidebar.expander("📊 Sources de Données"):
        dsm = DataSourceManager(st.session_state.username)
        
        st.markdown("### 🔗 Type de Source")
        source_options = list(DataSourceManager.SUPPORTED_SOURCES.items())
        source_labels = [f"{get_source_icon(k)} {v}" for k, v in source_options]
        source_keys = [k for k, _ in source_options]
        
        current_source = dsm.get_active_source()
        current_index = source_keys.index(current_source) if current_source in source_keys else 0
        
        selected_source = st.selectbox(
            "Sélectionnez votre source",
            options=source_keys,
            format_func=lambda x: f"{get_source_icon(x)} {DataSourceManager.SUPPORTED_SOURCES[x]}",
            index=current_index,
            key="data_source_selector"
        )
        
        st.markdown("---")
        
        # Configuration par source
        if selected_source == 'google_sheets':
            st.markdown("### 📊 Configuration Google Sheets")
            
            existing_config = dsm.get_source_config('google_sheets') or {}
            
            sheet_url = st.text_input(
                "URL de la Google Sheet",
                value=existing_config.get('sheet_url', ''),
                placeholder="https://docs.google.com/spreadsheets/d/...",
                key="gsheet_url"
            )
            
            sheet_name = st.text_input(
                "Nom de la feuille (optionnel)",
                value=existing_config.get('sheet_name', ''),
                placeholder="Feuille1",
                key="gsheet_name"
            )
            
            is_public = st.checkbox(
                "Feuille publique (accès en lecture)",
                value=existing_config.get('is_public', True),
                key="gsheet_public"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Sauvegarder", key="save_gsheet"):
                    dsm.add_source('google_sheets', {
                        'sheet_url': sheet_url,
                        'sheet_name': sheet_name,
                        'is_public': is_public
                    })
                    dsm.set_active_source('google_sheets')
                    st.success("✅ Configuration sauvegardée")
            
            with col2:
                if st.button("🧪 Tester", key="test_gsheet"):
                    connector = GoogleSheetsConnector()
                    test_df = connector.read_sheet(sheet_url, sheet_name)
                    if test_df is not None:
                        st.success(f"✅ Connexion OK - {len(test_df)} lignes")
                    else:
                        st.error("❌ Échec de connexion")
        
        elif selected_source == 'onedrive':
            st.markdown("### ☁️ Configuration OneDrive")
            
            existing_config = dsm.get_source_config('onedrive') or {}
            
            file_url = st.text_input(
                "URL du fichier Excel",
                value=existing_config.get('file_url', ''),
                placeholder="https://1drv.ms/x/...",
                key="onedrive_url"
            )
            
            use_oauth = st.checkbox(
                "Utiliser OAuth2 (avancé)",
                value=existing_config.get('use_oauth', False),
                key="onedrive_oauth"
            )
            
            if use_oauth:
                client_id = st.text_input(
                    "Client ID",
                    value=existing_config.get('client_id', ''),
                    type="password",
                    key="onedrive_client_id"
                )
                client_secret = st.text_input(
                    "Client Secret",
                    value=existing_config.get('client_secret', ''),
                    type="password",
                    key="onedrive_client_secret"
                )
            
            if st.button("💾 Sauvegarder", key="save_onedrive"):
                config = {'file_url': file_url, 'use_oauth': use_oauth}
                if use_oauth:
                    config['client_id'] = client_id
                    config['client_secret'] = client_secret
                
                dsm.add_source('onedrive', config)
                dsm.set_active_source('onedrive')
                st.success("✅ Configuration sauvegardée")
        
        elif selected_source == 'dropbox':
            st.markdown("### 📦 Configuration Dropbox")
            
            existing_config = dsm.get_source_config('dropbox') or {}
            
            st.info("💡 Créez un access token sur [Dropbox App Console](https://www.dropbox.com/developers/apps)")
            
            access_token = st.text_input(
                "Access Token",
                value=existing_config.get('access_token', ''),
                type="password",
                key="dropbox_token"
            )
            
            file_path = st.text_input(
                "Chemin du fichier",
                value=existing_config.get('file_path', ''),
                placeholder="/Restaurant/ventes.xlsx",
                key="dropbox_path"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Sauvegarder", key="save_dropbox"):
                    dsm.add_source('dropbox', {
                        'access_token': access_token,
                        'file_path': file_path
                    })
                    dsm.set_active_source('dropbox')
                    st.success("✅ Configuration sauvegardée")
            
            with col2:
                if st.button("🧪 Tester", key="test_dropbox"):
                    connector = DropboxConnector()
                    if connector.authenticate(access_token):
                        test_df = connector.read_file(file_path)
                        if test_df is not None:
                            st.success(f"✅ Connexion OK - {len(test_df)} lignes")
                        else:
                            st.error("❌ Fichier introuvable")
                    else:
                        st.error("❌ Token invalide")
        
        elif selected_source == 'url':
            st.markdown("### 🔗 Configuration URL Publique")
            
            existing_config = dsm.get_source_config('url') or {}
            
            public_url = st.text_input(
                "URL du fichier CSV/Excel",
                value=existing_config.get('url', ''),
                placeholder="https://example.com/data.csv",
                key="public_url"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Sauvegarder", key="save_url"):
                    dsm.add_source('url', {'url': public_url})
                    dsm.set_active_source('url')
                    st.success("✅ Configuration sauvegardée")
            
            with col2:
                if st.button("🧪 Tester", key="test_url"):
                    test_df = URLConnector.read_from_url(public_url)
                    if test_df is not None:
                        st.success(f"✅ Connexion OK - {len(test_df)} lignes")
                    else:
                        st.error("❌ URL invalide ou inaccessible")
        
        else:  # upload
            st.markdown("### 📁 Mode Upload Manuel")
            st.info("Mode par défaut : Importez vos fichiers manuellement dans la section principale")
        
        # Section synchronisation automatique
        if selected_source != 'upload':
            st.markdown("---")
            st.markdown("### ⚡ Synchronisation Automatique")
            
            auto_sync = st.checkbox(
                "Activer la synchronisation automatique",
                value=dsm.config.get('auto_sync', False),
                key="auto_sync_toggle"
            )
            
            if auto_sync:
                sync_interval = st.slider(
                    "Intervalle de synchronisation (minutes)",
                    min_value=1,
                    max_value=60,
                    value=dsm.config.get('sync_interval', 10),
                    key="sync_interval_slider"
                )
                
                dsm.config['auto_sync'] = True
                dsm.config['sync_interval'] = sync_interval
                dsm.save_config()
                
                # Affichage dernière sync
                source_config = dsm.get_source_config(selected_source)
                if source_config:
                    last_sync = source_config.get('last_sync')
                    st.caption(f"📅 Dernière sync: {format_last_sync(last_sync)}")
                
                # Bouton sync manuelle
                if st.button("🔄 Synchroniser Maintenant", key="sync_now"):
                    sync_manager = AutoSyncManager(dsm)
                    synced_df = sync_manager.sync_data()
                    
                    if synced_df is not None:
                        st.success(f"✅ Synchronisation réussie - {len(synced_df)} lignes")
                        # TODO: Intégrer synced_df dans le flux principal
                    else:
                        st.error("❌ Échec de la synchronisation")
            else:
                dsm.config['auto_sync'] = False
                dsm.save_config()

st.sidebar.markdown("---")

# Section Paramètres du Compte
with st.sidebar.expander("⚙️ Paramètres du Compte"):
    st.markdown("### 🔑 Changer le Mot de Passe")
    
    current_pwd = st.text_input("Mot de passe actuel", type="password", key="current_pwd")
    new_pwd = st.text_input("Nouveau mot de passe", type="password", key="new_pwd")
    new_pwd_confirm = st.text_input("Confirmer nouveau mot de passe", type="password", key="new_pwd_confirm")
    
    if st.button("Modifier le mot de passe"):
        if not current_pwd or not new_pwd:
            st.error("Veuillez remplir tous les champs")
        elif not verify_user(st.session_state.username, current_pwd):
            st.error("Mot de passe actuel incorrect")
        elif new_pwd != new_pwd_confirm:
            st.error("Les nouveaux mots de passe ne correspondent pas")
        elif len(new_pwd) < 6:
            st.error("Le nouveau mot de passe doit contenir au moins 6 caractères")
        else:
            if change_user_password(st.session_state.username, new_pwd):
                st.success("✅ Mot de passe modifié avec succès !")
            else:
                st.error("Erreur lors de la modification")
    
    st.markdown("---")
    st.markdown("### 👤 Changer le Nom d'Utilisateur")
    
    new_username = st.text_input("Nouveau nom d'utilisateur", key="new_username_input")
    confirm_pwd = st.text_input("Mot de passe pour confirmer", type="password", key="confirm_pwd_username")
    
    if st.button("Modifier le nom d'utilisateur"):
        if not new_username or not confirm_pwd:
            st.error("Veuillez remplir tous les champs")
        elif not verify_user(st.session_state.username, confirm_pwd):
            st.error("Mot de passe incorrect")
        elif new_username == st.session_state.username:
            st.error("Le nouveau nom est identique à l'ancien")
        else:
            success, message = change_username(st.session_state.username, new_username)
            if success:
                st.success(f"✅ {message}")
                st.info(f"Votre nouveau nom d'utilisateur : **{new_username}**")
                # Mettre à jour la session
                st.session_state.username = new_username
                st.rerun()
            else:
                st.error(f"❌ {message}")

st.sidebar.markdown("---")
st.sidebar.title("🏢 Gestion Multi-Restaurants")

with st.sidebar.expander("➕ Ajouter un restaurant", expanded=len(st.session_state.restaurants) == 0):
    resto_name = st.text_input("Nom du restaurant")
    resto_city = st.text_input("Ville", value="Paris")
    avg_portion_cost = st.number_input("Coût moyen par portion (€)", min_value=0.0, value=3.5, step=0.1)
    
    if st.button("Créer le restaurant"):
        if resto_name:
            st.session_state.restaurants[resto_name] = {
                'name': resto_name,
                'city': resto_city,
                'cost_per_portion': avg_portion_cost,
                'data': None,
                'recipes': {}
            }
            st.session_state.current_restaurant = resto_name
            save_restaurant_data(st.session_state.username, st.session_state.restaurants)
            st.success(f"✅ Restaurant '{resto_name}' créé !")
            st.rerun()

if st.session_state.restaurants:
    st.sidebar.markdown("### 🏪 Vos Restaurants")
    selected_resto = st.sidebar.selectbox(
        "Sélectionner un restaurant",
        list(st.session_state.restaurants.keys()),
        index=list(st.session_state.restaurants.keys()).index(st.session_state.current_restaurant) if st.session_state.current_restaurant else 0
    )
    
    if selected_resto != st.session_state.current_restaurant:
        st.session_state.current_restaurant = selected_resto
        save_restaurant_data(st.session_state.username, st.session_state.restaurants)
    
    current_resto_data = st.session_state.restaurants[selected_resto]
    
    st.sidebar.info(f"📍 {current_resto_data['city']}")
    st.sidebar.info(f"💰 {current_resto_data['cost_per_portion']}€/portion")
    
    if st.sidebar.button("🗑️ Supprimer ce restaurant"):
        del st.session_state.restaurants[selected_resto]
        if len(st.session_state.restaurants) > 0:
            st.session_state.current_restaurant = list(st.session_state.restaurants.keys())[0]
        else:
            st.session_state.current_restaurant = None
        save_restaurant_data(st.session_state.username, st.session_state.restaurants)
        st.rerun()

if not st.session_state.current_restaurant:
    st.info("👈 Créez votre premier restaurant dans la barre latérale pour commencer")
    st.stop()

st.title(f"🍽️ {st.session_state.restaurants[st.session_state.current_restaurant]['name']}")
st.markdown("**Prévisions ultra-précises basées sur Machine Learning et analyse de tendances**")

st.sidebar.markdown("---")
st.sidebar.header("📊 Données de Ventes")

uploaded_file = st.sidebar.file_uploader(
    "Importez vos données", 
    type=['csv', 'xlsx', 'xls', 'json', 'txt', 'docx', 'pdf'],
    help="Formats acceptés: CSV, Excel, JSON, TXT, Word, PDF"
)

if uploaded_file is not None:
    with st.spinner("Chargement et analyse des données..."):
        df = load_file(uploaded_file)
        if df is not None:
            # Nettoyage et validation robuste
            df_cleaned, error_msg = clean_and_validate_data(df)
            
            if df_cleaned is None:
                st.error(f"❌ {error_msg}")
                st.stop()
            else:
                # Afficher statistiques de nettoyage
                removed = len(df) - len(df_cleaned)
                if removed > 0:
                    st.info(f"ℹ️ {removed} lignes nettoyées sur {len(df)} ({(removed/len(df)*100):.1f}%)")
                
                st.session_state.restaurants[st.session_state.current_restaurant]['data'] = df_cleaned
                save_restaurant_data(st.session_state.username, st.session_state.restaurants)

current_resto_data = st.session_state.restaurants[st.session_state.current_restaurant]
df = current_resto_data.get('data')

if df is not None:
    required_columns = ['Date', 'Plat', 'Quantite']
    if not all(col in df.columns for col in required_columns):
        st.error(f"❌ Colonnes requises non trouvées. Colonnes détectées: {', '.join(df.columns)}")
        st.info(f"💡 Les colonnes nécessaires sont: {', '.join(required_columns)}")
    else:
        df = create_features(df)
        
        optional_columns = [col for col in df.columns if col not in required_columns and col not in ['Jour_Semaine', 'Jour_Mois', 'Mois', 'Annee', 'Semaine_Annee', 'Trimestre', 'Est_Weekend', 'Est_Debut_Mois', 'Est_Fin_Mois']]
        
        st.sidebar.success(f"✅ {len(df)} ventes chargées")
        
        # Affichage période sécurisé
        try:
            date_min = df['Date'].min()
            date_max = df['Date'].max()
            if pd.notna(date_min) and pd.notna(date_max):
                st.sidebar.info(f"📅 Période: {safe_format_date(date_min)} - {safe_format_date(date_max)}")
        except Exception as e:
            st.sidebar.info("📅 Période: Données disponibles")
        
        if optional_columns:
            with st.sidebar.expander(f"📊 Colonnes détectées ({len(optional_columns) + 3})"):
                st.write("**Colonnes obligatoires :**")
                st.write(", ".join(required_columns))
                st.write("**Colonnes optionnelles :**")
                st.write(", ".join(optional_columns))
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Ventes", f"{len(df)}")
        with col2:
            st.metric("Plats Différents", f"{df['Plat'].nunique()}")
        with col3:
            total_quantite = int(df['Quantite'].sum())
            st.metric("Quantité Totale", f"{total_quantite}")
        with col4:
            try:
                jours_data = (df['Date'].max() - df['Date'].min()).days
                if jours_data < 0:
                    jours_data = 0
                st.metric("Jours de Données", f"{jours_data}")
            except:
                st.metric("Jours de Données", "N/A")
        
        st.markdown("---")
        
        has_financial_data = 'Prix_unitaire' in df.columns or 'Cout_unitaire' in df.columns or 'Chiffre_affaires' in df.columns or 'Marge' in df.columns
        
        if has_financial_data:
            tab0, tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
                "⚡ Prédictions Live",
                "📈 Analyse", 
                "🔮 Prévisions ML", 
                "📋 Liste de Préparation",
                "💰 Économies & ROI",
                "💎 Rentabilité",
                "📦 Stocks & Commandes",
                "🌤️ Alertes Météo"
            ])
        else:
            tab0, tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                "⚡ Prédictions Live",
                "📈 Analyse", 
                "🔮 Prévisions ML", 
                "📋 Liste de Préparation",
                "💰 Économies & ROI",
                "📦 Stocks & Commandes",
                "🌤️ Alertes Météo"
            ])
            tab7 = None
        
        with tab0:
            st.subheader("⚡ Prédictions en Temps Réel - Aujourd'hui")
            
            # Initialisation auto_refresh (sera écrasé par le checkbox si affiché)
            auto_refresh = False
            
            current_time = datetime.now()
            st.info(f"🕐 **{current_time.strftime('%A %d %B %Y - %H:%M')}**")
            
            city = current_resto_data['city']
            
            df_temp = df.copy()
            df_temp['Date'] = pd.to_datetime(df_temp['Date'])
            today_sales = df_temp[df_temp['Date'].dt.date == current_time.date()]
            total_today = today_sales['Quantite'].sum() if len(today_sales) > 0 else 0
            
            adjustments = get_realtime_adjustments(city, df, total_today)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("📊 Ventes Aujourd'hui", f"{max(0, int(total_today))} portions")
            
            with col2:
                weather_icon = "☀️" if adjustments['weather_factor'] > 1 else ("🌧️" if adjustments['weather_factor'] < 0.95 else "☁️")
                impact_pct = int((adjustments['weather_factor'] - 1) * 100)
                st.metric(f"{weather_icon} Impact Météo", f"{impact_pct:+d}%")
            
            with col3:
                trend_icon = "📈" if adjustments['sales_trend_factor'] > 1 else ("📉" if adjustments['sales_trend_factor'] < 1 else "➡️")
                trend_pct = int((adjustments['sales_trend_factor'] - 1) * 100)
                st.metric(f"{trend_icon} Tendance Ventes", f"{trend_pct:+d}%")
            
            if adjustments['recommendations']:
                st.markdown("### 💡 Recommandations Temps Réel")
                for rec in adjustments['recommendations']:
                    st.info(rec)
            
            st.markdown("---")
            st.markdown("### 🕐 Prédictions Heure par Heure")
            
            plats_list = df['Plat'].unique().tolist()
            
            if 'Heure' in df.columns:
                st.success("✅ Colonne 'Heure' détectée - Prédictions horaires précises disponibles")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    plat_live = st.selectbox(
                        "Sélectionner un plat",
                        plats_list,
                        key="plat_live_select"
                    )
                
                with col2:
                    auto_refresh = st.checkbox("🔄 Rafraîchir auto (5min)", value=False)
                
                if plat_live:
                    intraday_pred = predict_intraday_sales(df, plat_live, current_time.hour)
                    
                    if intraday_pred is not None and len(intraday_pred) > 0:
                        intraday_pred['Quantite_ajustee'] = (
                            intraday_pred['Quantite_prevue'] * 
                            adjustments['weather_factor'] * 
                            adjustments['sales_trend_factor']
                        ).round(0).astype(int)
                        
                        st.markdown(f"#### 🍽️ {plat_live} - Prévisions Restantes Aujourd'hui")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("##### 📋 Tableau Détaillé")
                            display_df = intraday_pred[['Heure', 'Service', 'Quantite_prevue', 'Quantite_ajustee', 'Confiance']].copy()
                            display_df.columns = ['Heure', 'Service', 'Prévu Base', 'Prévu Ajusté', 'Confiance']
                            
                            st.dataframe(
                                display_df,
                                use_container_width=True,
                                hide_index=True
                            )
                            
                            total_remaining = intraday_pred['Quantite_ajustee'].sum()
                            st.metric("📦 Total à Préparer (reste du jour)", f"{int(total_remaining)} portions")
                        
                        with col2:
                            st.markdown("##### 📊 Graphique Horaire")
                            
                            fig_hourly = go.Figure()
                            
                            fig_hourly.add_trace(go.Bar(
                                x=intraday_pred['Heure'],
                                y=intraday_pred['Quantite_prevue'],
                                name='Prévu (base)',
                                marker_color='lightblue',
                                opacity=0.6
                            ))
                            
                            fig_hourly.add_trace(go.Bar(
                                x=intraday_pred['Heure'],
                                y=intraday_pred['Quantite_ajustee'],
                                name='Prévu (ajusté)',
                                marker_color='darkblue'
                            ))
                            
                            fig_hourly.update_layout(
                                title="Prévisions par Heure",
                                xaxis_title="Heure",
                                yaxis_title="Quantité",
                                barmode='group',
                                height=400
                            )
                            
                            st.plotly_chart(fig_hourly, use_container_width=True)
                        
                        if 'Note' in intraday_pred.columns and len(intraday_pred) > 0:
                            st.info(intraday_pred['Note'].iloc[0])
                        
                        st.markdown("---")
                        st.markdown("##### 🎯 Conseils de Préparation")
                        
                        dejeuner_qty = intraday_pred[intraday_pred['Service'] == 'Déjeuner']['Quantite_ajustee'].sum()
                        diner_qty = intraday_pred[intraday_pred['Service'] == 'Dîner']['Quantite_ajustee'].sum()
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if dejeuner_qty > 0:
                                st.success(f"🍽️ **Déjeuner** : Préparer {int(dejeuner_qty)} portions")
                                if current_time.hour < 11:
                                    st.caption("⏰ À préparer avant 11h00")
                                elif current_time.hour < 14:
                                    st.caption("⚠️ Service en cours")
                                else:
                                    st.caption("✅ Service terminé")
                        
                        with col2:
                            if diner_qty > 0:
                                st.success(f"🌙 **Dîner** : Préparer {int(diner_qty)} portions")
                                if current_time.hour < 18:
                                    st.caption("⏰ À préparer avant 18h00")
                                elif current_time.hour < 22:
                                    st.caption("⚠️ Service en cours")
                                else:
                                    st.caption("✅ Service terminé")
                    
                    else:
                        st.warning(f"⚠️ Pas assez de données horaires pour {plat_live}")
                        st.info("💡 Ajoutez une colonne 'Heure' dans vos données pour activer les prédictions horaires précises")
            
            else:
                st.warning("⚠️ **Prédictions horaires désactivées**")
                st.info("💡 **Pour activer** : Ajoutez une colonne **'Heure'** (format HH:MM) dans votre fichier Excel")
                st.info("📝 **Exemple** : `12:30`, `19:45`, etc.")
                
                st.markdown("### 📊 Vue d'Ensemble Journée")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    plat_overview = st.selectbox("Sélectionner un plat", plats_list, key="plat_overview")
                
                with col2:
                    auto_refresh = st.checkbox("🔄 Rafraîchir auto (5min)", value=False)
                
                if plat_overview:
                    plat_data = df[df['Plat'] == plat_overview].copy()
                    plat_data['Date'] = pd.to_datetime(plat_data['Date'])
                    
                    # Vérification données suffisantes
                    if len(plat_data) == 0:
                        st.warning(f"⚠️ Aucune donnée disponible pour {plat_overview}")
                    else:
                        daily_avg = plat_data.groupby('Date')['Quantite'].sum().mean()
                        
                        # Vérification moyenne valide
                        if pd.isna(daily_avg) or daily_avg <= 0:
                            st.warning(f"⚠️ Données insuffisantes pour calculer les prédictions de {plat_overview}")
                        else:
                            adjusted_total = daily_avg * adjustments['weather_factor'] * adjustments['sales_trend_factor']
                            
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("📊 Moyenne Journalière", f"{int(daily_avg)} portions")
                            
                            with col2:
                                st.metric("🎯 Prévu Aujourd'hui (ajusté)", f"{int(adjusted_total)} portions")
                            
                            with col3:
                                remaining = max(0, int(adjusted_total - total_today))
                                st.metric("📦 Reste à Vendre", f"{remaining} portions")
                            
                            if current_time.hour < 14:
                                dejeuner_portion = adjusted_total * 0.55
                                diner_portion = adjusted_total * 0.45
                            else:
                                dejeuner_portion = total_today
                                diner_portion = max(0, adjusted_total - total_today)
                            
                            st.markdown("#### 🍽️ Répartition Services")
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.info(f"☀️ **Déjeuner** : {int(dejeuner_portion)} portions")
                            
                            with col2:
                                st.info(f"🌙 **Dîner** : {int(diner_portion)} portions")
            
            if auto_refresh:
                st.caption("🔄 Page se rafraîchit automatiquement toutes les 5 minutes")
                time.sleep(300)
                st.rerun()
        
        with tab1:
            st.subheader("Analyse des Ventes Passées")
            
            col1, col2 = st.columns(2)
            
            with col1:
                ventes_par_plat = df.groupby('Plat')['Quantite'].sum().sort_values(ascending=False)
                fig_plats = px.bar(
                    x=ventes_par_plat.index, 
                    y=ventes_par_plat.values,
                    labels={'x': 'Plat', 'y': 'Quantité Totale'},
                    title="Plats les Plus Vendus",
                    color=ventes_par_plat.values,
                    color_continuous_scale='Blues'
                )
                st.plotly_chart(fig_plats, use_container_width=True)
            
            with col2:
                ventes_par_jour = df.groupby('Jour_Semaine')['Quantite'].sum()
                jours_noms = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
                
                fig_jours = go.Figure()
                fig_jours.add_trace(go.Bar(
                    x=[jours_noms[i] for i in ventes_par_jour.index],
                    y=ventes_par_jour.values,
                    marker_color='lightblue'
                ))
                fig_jours.update_layout(title="Ventes par Jour de la Semaine")
                st.plotly_chart(fig_jours, use_container_width=True)
            
            ventes_timeline = df.groupby('Date')['Quantite'].sum().reset_index()
            fig_timeline = px.area(
                ventes_timeline, 
                x='Date', 
                y='Quantite',
                title="Évolution des Ventes dans le Temps"
            )
            st.plotly_chart(fig_timeline, use_container_width=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                ventes_weekend = df.groupby('Est_Weekend')['Quantite'].sum()
                fig_weekend = px.pie(
                    values=ventes_weekend.values,
                    names=['Semaine', 'Weekend'],
                    title="Répartition Semaine/Weekend"
                )
                st.plotly_chart(fig_weekend, use_container_width=True)
            
            with col2:
                ventes_mois = df.groupby('Mois')['Quantite'].sum()
                fig_mois = px.line(
                    x=ventes_mois.index,
                    y=ventes_mois.values,
                    labels={'x': 'Mois', 'y': 'Quantité'},
                    title="Ventes par Mois",
                    markers=True
                )
                st.plotly_chart(fig_mois, use_container_width=True)
        
        with tab2:
            st.subheader("🤖 Prévisions Machine Learning")
            st.info("🎯 Modèles avancés: Random Forest + Gradient Boosting avec sélection automatique du meilleur")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                plats_disponibles = sorted(df['Plat'].unique())
                plat_selectionne = st.selectbox("Sélectionnez un plat", plats_disponibles)
            
            with col2:
                jours_prevision = st.slider("Jours à prévoir", 1, 30, 7)
            
            if plat_selectionne:
                with st.spinner(f"Entraînement des modèles ML pour {plat_selectionne}..."):
                    try:
                        predictions, metrics, best_model_name = predict_sales_ml(df, plat_selectionne, jours_prevision)
                    except Exception as e:
                        st.error(f"❌ Erreur lors de la prédiction : {str(e)}")
                        predictions, metrics, best_model_name = None, None, None
                
                if predictions is not None:
                    st.success(f"✅ Meilleur modèle sélectionné: **{best_model_name}**")
                    
                    if metrics:
                        col1, col2, col3 = st.columns(3)
                        best_metrics = metrics[best_model_name]
                        with col1:
                            st.metric("📉 Erreur Moyenne (MAE)", f"{best_metrics['MAE']:.2f}")
                        with col2:
                            st.metric("📊 RMSE", f"{best_metrics['RMSE']:.2f}")
                        with col3:
                            st.metric("🎯 Précision (MAPE)", f"{best_metrics['MAPE']:.2f}%")
                    
                    st.markdown(f"### Prévisions pour **{plat_selectionne}**")
                    
                    historique = df[df['Plat'] == plat_selectionne].copy()
                    historique = historique.groupby('Date')['Quantite'].sum().reset_index()
                    historique['Type'] = 'Historique'
                    
                    predictions_plot = predictions.copy()
                    predictions_plot.columns = ['Date', 'Jour', 'Quantite']
                    predictions_plot['Type'] = 'Prévision ML'
                    
                    combined = pd.concat([
                        historique[['Date', 'Quantite', 'Type']], 
                        predictions_plot[['Date', 'Quantite', 'Type']]
                    ])
                    
                    fig_pred = px.line(
                        combined, 
                        x='Date', 
                        y='Quantite', 
                        color='Type',
                        markers=True,
                        title=f"Historique et Prévisions ML - {plat_selectionne}"
                    )
                    fig_pred.update_traces(line=dict(width=3))
                    st.plotly_chart(fig_pred, use_container_width=True)
                    
                    st.markdown("#### 📊 Détails des Prévisions")
                    predictions_display = predictions.copy()
                    predictions_display['Date'] = predictions_display['Date'].dt.strftime('%d/%m/%Y')
                    
                    stats_prev = predictions['Quantite_Prevue']
                    predictions_display['Intervalle Min'] = (stats_prev * 0.9).astype(int)
                    predictions_display['Intervalle Max'] = (stats_prev * 1.1).astype(int)
                    
                    st.dataframe(predictions_display, use_container_width=True, hide_index=True)
                    
                else:
                    st.warning("⚠️ Pas assez de données pour ce plat (minimum 14 jours requis)")
        
        with tab3:
            st.subheader("📋 Liste de Préparation Recommandée")
            
            date_prep = st.date_input(
                "Date de préparation",
                datetime.now() + timedelta(days=1)
            )
            
            st.markdown(f"### 🍽️ Recommandations pour le {date_prep.strftime('%d/%m/%Y')}")
            
            city = current_resto_data['city']
            weather_forecast = get_weather_forecast(city, 7)
            
            if weather_forecast:
                for w in weather_forecast:
                    if w['date'] == date_prep.strftime('%Y-%m-%d'):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.info(f"🌡️ {w['temp_min']:.0f}°C - {w['temp_max']:.0f}°C")
                        with col2:
                            st.info(f"☁️ {w['condition']}")
                        with col3:
                            st.info(f"🌧️ Pluie: {w['rain_chance']}%")
                        break
            
            with st.spinner("Calcul des recommandations..."):
                liste_prep = []
                for plat in df['Plat'].unique():
                    pred, _, _ = safe_predict_sales_ml(df, plat, 30)
                    if pred is not None:
                        pred_date = pred[pred['Date'].dt.date == date_prep]
                        if not pred_date.empty:
                            quantite = pred_date.iloc[0]['Quantite_Prevue']
                            
                            if weather_forecast:
                                for w in weather_forecast:
                                    if w['date'] == date_prep.strftime('%Y-%m-%d'):
                                        weather_impact = calculate_weather_impact(w)
                                        quantite = int(quantite * weather_impact)
                                        break
                            
                            liste_prep.append({
                                'Plat': plat,
                                'Quantité à Préparer': quantite,
                                'Marge Sécurité (-10%)': int(quantite * 0.9),
                                'Marge Sécurité (+10%)': int(quantite * 1.1)
                            })
            
            if liste_prep:
                df_prep = pd.DataFrame(liste_prep).sort_values('Quantité à Préparer', ascending=False)
                
                st.dataframe(df_prep, use_container_width=True, hide_index=True)
                
                total_prep = df_prep['Quantité à Préparer'].sum()
                total_min = df_prep['Marge Sécurité (-10%)'].sum()
                total_max = df_prep['Marge Sécurité (+10%)'].sum()
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Recommandé", f"{total_prep} portions")
                with col2:
                    st.metric("Minimum", f"{total_min} portions")
                with col3:
                    st.metric("Maximum", f"{total_max} portions")
                
                csv = df_prep.to_csv(index=False)
                st.download_button(
                    label="⬇️ Télécharger la liste (CSV)",
                    data=csv,
                    file_name=f"preparation_{date_prep.strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("Aucune prévision disponible pour cette date")
        
        with tab4:
            st.subheader("💰 Analyse des Économies et ROI")
            
            st.markdown("### 🎯 Impact de l'IA sur vos Coûts")
            
            col1, col2 = st.columns(2)
            
            with col1:
                cost_per_portion = st.number_input(
                    "Coût moyen par portion gaspillée (€)",
                    min_value=0.0,
                    value=current_resto_data['cost_per_portion'],
                    step=0.1
                )
            
            with col2:
                analysis_days = st.slider("Période d'analyse (jours)", 7, 90, 30)
            
            all_predictions = []
            for plat in df['Plat'].unique():
                pred, _, _ = safe_predict_sales_ml(df, plat, analysis_days)
                if pred is not None:
                    pred['Plat'] = plat
                    all_predictions.append(pred)
            
            if all_predictions:
                all_pred_df = pd.concat(all_predictions, ignore_index=True)
                
                savings_data = calculate_waste_savings(df, all_pred_df)
                
                if savings_data:
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        traditional_waste_cost = savings_data['waste_traditional'] * cost_per_portion
                        st.metric(
                            "💸 Gaspillage Traditionnel",
                            f"{traditional_waste_cost:.0f}€",
                            delta=f"{savings_data['waste_traditional']:.0f} portions",
                            delta_color="inverse"
                        )
                    
                    with col2:
                        ml_waste_cost = savings_data['waste_ml'] * cost_per_portion
                        st.metric(
                            "🤖 Gaspillage avec IA",
                            f"{ml_waste_cost:.0f}€",
                            delta=f"{savings_data['waste_ml']:.0f} portions",
                            delta_color="inverse"
                        )
                    
                    with col3:
                        monthly_savings_portions = savings_data['savings_portions']
                        monthly_savings = monthly_savings_portions * cost_per_portion
                        st.metric(
                            "💚 Économies Mensuelles",
                            f"{monthly_savings:.0f}€",
                            delta=f"{savings_data['reduction_percent']:.1f}% de réduction"
                        )
                    
                    with col4:
                        annual_savings = monthly_savings * 12
                        st.metric(
                            "📅 Économies Annuelles",
                            f"{annual_savings:.0f}€",
                            delta=f"{monthly_savings_portions:.0f} portions/mois économisées"
                        )
                    
                    st.markdown("---")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### 📊 Comparaison Méthode Traditionnelle vs IA")
                        
                        comparison_data = pd.DataFrame({
                            'Méthode': ['Traditionnelle', 'Avec IA'],
                            'Gaspillage (€)': [traditional_waste_cost, ml_waste_cost],
                            'Portions Gaspillées': [savings_data['waste_traditional'], savings_data['waste_ml']]
                        })
                        
                        fig_comparison = go.Figure()
                        fig_comparison.add_trace(go.Bar(
                            name='Gaspillage',
                            x=comparison_data['Méthode'],
                            y=comparison_data['Gaspillage (€)'],
                            marker_color=['#ff6b6b', '#51cf66']
                        ))
                        fig_comparison.update_layout(title=f"Économies Mensuelles (30 jours)")
                        st.plotly_chart(fig_comparison, use_container_width=True)
                    
                    with col2:
                        st.markdown("#### 🎯 Retour sur Investissement")
                        
                        subscription_cost = st.number_input(
                            "Coût mensuel de l'abonnement (€)",
                            min_value=0.0,
                            value=49.0,
                            step=1.0
                        )
                        
                        roi = ((monthly_savings - subscription_cost) / subscription_cost * 100) if subscription_cost > 0 else 0
                        daily_savings_amount = savings_data['daily_savings'] * cost_per_portion
                        payback_days = (subscription_cost / daily_savings_amount) if daily_savings_amount > 0 else 0
                        
                        if payback_days < 1 and payback_days > 0:
                            payback_hours = payback_days * 24
                            payback_display = f"{payback_hours:.0f} heures"
                        else:
                            payback_display = f"{payback_days:.0f} jours"
                        
                        st.metric("💎 ROI Mensuel", f"{roi:.0f}%")
                        st.metric("⏱️ Retour sur Investissement", payback_display)
                        
                        net_monthly_benefit = monthly_savings - subscription_cost
                        st.metric("💰 Bénéfice Net Mensuel", f"{net_monthly_benefit:.0f}€")
                        
                        if roi > 100:
                            st.success(f"🎉 Excellent ROI ! Vous économisez {roi:.0f}% de plus que le coût de l'abonnement")
                        elif roi > 0:
                            st.info(f"✅ ROI positif ! Vous gagnez {net_monthly_benefit:.0f}€/mois")
                        else:
                            st.warning("⚠️ Augmentez vos ventes ou optimisez vos coûts")
                    
                    st.markdown("---")
                    st.markdown("#### 📈 Projection Annuelle")
                    
                    yearly_data = []
                    cumulative = 0
                    for month in range(1, 13):
                        monthly_net = monthly_savings - subscription_cost
                        cumulative += monthly_net
                        yearly_data.append({
                            'Mois': f"Mois {month}",
                            'Économies Cumulées': cumulative
                        })
                    
                    df_yearly = pd.DataFrame(yearly_data)
                    fig_yearly = px.line(
                        df_yearly,
                        x='Mois',
                        y='Économies Cumulées',
                        title="Projection des Économies sur 12 Mois",
                        markers=True
                    )
                    fig_yearly.update_traces(line_color='#51cf66', line_width=3)
                    st.plotly_chart(fig_yearly, use_container_width=True)
                    
                    st.info(f"💡 **En 1 an, vous économiserez environ {cumulative:.0f}€ en réduisant le gaspillage !**")
        
        with tab6:
            st.subheader("📦 Gestion des Stocks et Commandes Fournisseurs")
            
            st.markdown("### 🥘 Configuration des Recettes")
            
            with st.expander("➕ Ajouter/Modifier une recette"):
                plat_recipe = st.selectbox("Sélectionner un plat", sorted(df['Plat'].unique()), key='recipe_plat')
                
                st.markdown("#### Ingrédients nécessaires par portion")
                
                num_ingredients = st.number_input("Nombre d'ingrédients", min_value=1, max_value=20, value=3)
                
                ingredients = []
                for i in range(num_ingredients):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        ing_name = st.text_input(f"Ingrédient {i+1}", key=f"ing_name_{i}")
                    with col2:
                        ing_qty = st.number_input(f"Quantité", min_value=0.0, value=0.1, step=0.01, key=f"ing_qty_{i}")
                    with col3:
                        ing_unit = st.selectbox(f"Unité", ["kg", "g", "L", "ml", "pièce(s)"], key=f"ing_unit_{i}")
                    
                    if ing_name:
                        ingredients.append({
                            'ingredient': ing_name,
                            'quantite': ing_qty,
                            'unite': ing_unit
                        })
                
                if st.button("💾 Sauvegarder la recette"):
                    if plat_recipe and ingredients:
                        if 'recipes' not in st.session_state.restaurants[st.session_state.current_restaurant]:
                            st.session_state.restaurants[st.session_state.current_restaurant]['recipes'] = {}
                        
                        st.session_state.restaurants[st.session_state.current_restaurant]['recipes'][plat_recipe] = ingredients
                        save_restaurant_data(st.session_state.username, st.session_state.restaurants)
                        st.success(f"✅ Recette '{plat_recipe}' sauvegardée !")
                        st.rerun()
            
            st.markdown("---")
            st.markdown("### 🛒 Liste de Commandes Fournisseurs")
            
            date_commande = st.date_input(
                "Date de préparation prévue",
                datetime.now() + timedelta(days=1),
                key='date_commande'
            )
            
            recipes = st.session_state.restaurants[st.session_state.current_restaurant].get('recipes', {})
            
            if recipes:
                with st.spinner("Calcul des besoins en ingrédients..."):
                    ingredients_totaux = {}
                    
                    for plat in df['Plat'].unique():
                        if plat in recipes:
                            pred, _, _ = safe_predict_sales_ml(df, plat, 30)
                            if pred is not None:
                                pred_date = pred[pred['Date'].dt.date == date_commande]
                                if not pred_date.empty:
                                    quantite_prevue = pred_date.iloc[0]['Quantite_Prevue']
                                    
                                    for ingredient_data in recipes[plat]:
                                        ing_name = ingredient_data['ingredient']
                                        ing_qty = ingredient_data['quantite']
                                        ing_unit = ingredient_data['unite']
                                        
                                        key = f"{ing_name} ({ing_unit})"
                                        
                                        if key not in ingredients_totaux:
                                            ingredients_totaux[key] = 0
                                        
                                        ingredients_totaux[key] += ing_qty * quantite_prevue
                
                if ingredients_totaux:
                    st.markdown(f"#### 📋 Commande pour le {date_commande.strftime('%d/%m/%Y')}")
                    
                    commande_df = pd.DataFrame([
                        {'Ingrédient': k.split('(')[0].strip(), 'Quantité': f"{v:.2f}", 'Unité': k.split('(')[1].replace(')', '')}
                        for k, v in ingredients_totaux.items()
                    ])
                    
                    st.dataframe(commande_df, use_container_width=True, hide_index=True)
                    
                    csv_commande = commande_df.to_csv(index=False)
                    st.download_button(
                        label="⬇️ Télécharger la liste de commande",
                        data=csv_commande,
                        file_name=f"commande_fournisseurs_{date_commande.strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                    
                    st.success("✅ Liste de commande générée avec succès !")
                else:
                    st.info("💡 Aucune prévision disponible pour cette date avec les recettes configurées")
            else:
                st.info("💡 Configurez d'abord vos recettes ci-dessus pour générer automatiquement vos listes de commandes")
        
        if has_financial_data and tab7 is not None:
            with tab5:
                st.subheader("💎 Analyse de Rentabilité")
                
                if 'Chiffre_affaires' in df.columns:
                    total_ca = df['Chiffre_affaires'].sum()
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("💰 CA Total", f"{total_ca:,.0f}€")
                    
                    if 'Cout_total' in df.columns:
                        total_cout = df['Cout_total'].sum()
                        with col2:
                            st.metric("💸 Coût Total", f"{total_cout:,.0f}€")
                    
                    if 'Marge' in df.columns:
                        total_marge = df['Marge'].sum()
                        with col3:
                            st.metric("💚 Marge Totale", f"{total_marge:,.0f}€")
                        
                        if 'Cout_total' in df.columns and total_ca > 0:
                            taux_marge_global = (total_marge / total_ca) * 100
                            with col4:
                                st.metric("📊 Taux de Marge", f"{taux_marge_global:.1f}%")
                
                st.markdown("---")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 🏆 Top 10 Plats les Plus Rentables")
                    
                    if 'Marge' in df.columns:
                        top_rentables = df.groupby('Plat').agg({
                            'Marge': 'sum',
                            'Quantite': 'sum'
                        }).sort_values('Marge', ascending=False).head(10)
                        
                        fig_rentables = px.bar(
                            top_rentables,
                            x=top_rentables.index,
                            y='Marge',
                            labels={'x': 'Plat', 'Marge': 'Marge Totale (€)'},
                            title="Plats classés par marge totale",
                            color='Marge',
                            color_continuous_scale='Greens'
                        )
                        st.plotly_chart(fig_rentables, use_container_width=True)
                    else:
                        st.info("💡 Ajoutez les colonnes Prix_unitaire et Cout_unitaire pour voir cette analyse")
                
                with col2:
                    st.markdown("#### 📉 Plats à Faible Rentabilité")
                    
                    if 'Taux_marge' in df.columns:
                        faible_marge = df.groupby('Plat').agg({
                            'Taux_marge': 'mean',
                            'Quantite': 'sum',
                            'Chiffre_affaires': 'sum'
                        }).sort_values('Taux_marge').head(10)
                        
                        fig_faible = px.bar(
                            faible_marge,
                            x=faible_marge.index,
                            y='Taux_marge',
                            labels={'x': 'Plat', 'Taux_marge': 'Taux de Marge (%)'},
                            title="Plats avec le taux de marge le plus faible",
                            color='Taux_marge',
                            color_continuous_scale='Reds_r'
                        )
                        st.plotly_chart(fig_faible, use_container_width=True)
                        
                        st.warning("⚠️ Envisagez d'augmenter les prix ou de réduire les coûts pour ces plats")
                    else:
                        st.info("💡 Les colonnes Prix et Coût permettraient cette analyse")
                
                st.markdown("---")
                st.markdown("#### 📊 Analyse ABC des Plats")
                st.info("📌 **Analyse ABC** : Classement par contribution au chiffre d'affaires")
                
                if 'Chiffre_affaires' in df.columns:
                    abc_data = df.groupby('Plat').agg({
                        'Chiffre_affaires': 'sum',
                        'Quantite': 'sum'
                    }).sort_values('Chiffre_affaires', ascending=False)
                    
                    abc_data['CA_Cumul'] = abc_data['Chiffre_affaires'].cumsum()
                    abc_data['CA_Pct_Cumul'] = (abc_data['CA_Cumul'] / abc_data['Chiffre_affaires'].sum()) * 100
                    
                    abc_data['Categorie_ABC'] = 'C'
                    abc_data.loc[abc_data['CA_Pct_Cumul'] <= 80, 'Categorie_ABC'] = 'A'
                    abc_data.loc[(abc_data['CA_Pct_Cumul'] > 80) & (abc_data['CA_Pct_Cumul'] <= 95), 'Categorie_ABC'] = 'B'
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        abc_display = abc_data.reset_index()
                        abc_display['CA'] = abc_display['Chiffre_affaires'].apply(lambda x: f"{x:.0f}€")
                        abc_display['% Cumul'] = abc_display['CA_Pct_Cumul'].apply(lambda x: f"{x:.1f}%")
                        
                        st.dataframe(
                            abc_display[['Plat', 'Quantite', 'CA', '% Cumul', 'Categorie_ABC']],
                            use_container_width=True,
                            hide_index=True
                        )
                    
                    with col2:
                        abc_counts = abc_data['Categorie_ABC'].value_counts()
                        
                        st.metric("🅰️ Plats catégorie A", abc_counts.get('A', 0))
                        st.caption("80% du CA")
                        
                        st.metric("🅱️ Plats catégorie B", abc_counts.get('B', 0))
                        st.caption("15% du CA")
                        
                        st.metric("©️ Plats catégorie C", abc_counts.get('C', 0))
                        st.caption("5% du CA")
                    
                    st.success("💡 **Conseil** : Concentrez vos efforts sur les plats A, optimisez les B, envisagez de retirer les C peu rentables")
                else:
                    st.info("💡 Ajoutez une colonne Prix_unitaire pour activer l'analyse ABC")
                
                if 'Categorie' in df.columns and 'Marge' in df.columns:
                    st.markdown("---")
                    st.markdown("#### 📦 Rentabilité par Catégorie")
                    
                    cat_data = df.groupby('Categorie').agg({
                        'Chiffre_affaires': 'sum',
                        'Marge': 'sum',
                        'Quantite': 'sum'
                    }).reset_index()
                    
                    cat_data['Taux_marge'] = (cat_data['Marge'] / cat_data['Chiffre_affaires'] * 100).round(1)
                    
                    fig_cat = px.scatter(
                        cat_data,
                        x='Quantite',
                        y='Taux_marge',
                        size='Chiffre_affaires',
                        color='Categorie',
                        labels={
                            'Quantite': 'Volume vendu',
                            'Taux_marge': 'Taux de marge (%)',
                            'Chiffre_affaires': 'CA'
                        },
                        title="Matrice Volume vs Rentabilité par Catégorie",
                        hover_data=['Chiffre_affaires']
                    )
                    st.plotly_chart(fig_cat, use_container_width=True)
        
        with tab7:
            st.subheader("🌤️ Alertes Météo et Impact sur les Ventes")
            
            city = current_resto_data['city']
            st.markdown(f"### 📍 Prévisions pour {city}")
            
            weather_data = get_weather_forecast(city, 7)
            
            if weather_data:
                st.markdown("#### 📅 Prévisions 7 jours")
                
                for day_weather in weather_data:
                    with st.expander(f"📆 {day_weather['date']} - {day_weather['condition']}"):
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("🌡️ Temp. Max", f"{day_weather['temp_max']:.0f}°C")
                        with col2:
                            st.metric("🌡️ Temp. Min", f"{day_weather['temp_min']:.0f}°C")
                        with col3:
                            st.metric("🌧️ Risque de pluie", f"{day_weather['rain_chance']}%")
                        with col4:
                            impact = calculate_weather_impact(day_weather)
                            impact_percent = (impact - 1) * 100
                            st.metric("📊 Impact Ventes", f"{impact_percent:+.0f}%")
                        
                        if day_weather['rain_chance'] > 60:
                            st.warning(f"⚠️ Forte probabilité de pluie ({day_weather['rain_chance']}%). Réduisez vos préparations de ~30%")
                        elif day_weather['temp_max'] > 30:
                            st.info(f"☀️ Journée chaude prévue ({day_weather['temp_max']:.0f}°C). Augmentez les boissons fraîches et salades")
                        elif day_weather['temp_max'] < 5:
                            st.info(f"❄️ Journée froide prévue ({day_weather['temp_max']:.0f}°C). Privilégiez les plats chauds")
                
                st.markdown("---")
                st.markdown("#### 📊 Impact Météo sur la Semaine")
                
                weather_df = pd.DataFrame(weather_data)
                weather_df['impact'] = weather_df.apply(calculate_weather_impact, axis=1)
                weather_df['impact_percent'] = (weather_df['impact'] - 1) * 100
                
                fig_weather = go.Figure()
                fig_weather.add_trace(go.Bar(
                    x=weather_df['date'],
                    y=weather_df['impact_percent'],
                    marker_color=['#51cf66' if x > 0 else '#ff6b6b' for x in weather_df['impact_percent']],
                    text=[f"{x:+.0f}%" for x in weather_df['impact_percent']],
                    textposition='outside'
                ))
                fig_weather.update_layout(
                    title="Impact Météo Estimé sur les Ventes (%)",
                    yaxis_title="Variation (%)",
                    xaxis_title="Date"
                )
                st.plotly_chart(fig_weather, use_container_width=True)
                
                st.info("💡 **Astuce**: Ces prévisions météo sont automatiquement intégrées dans vos listes de préparation !")
                
            else:
                st.warning("⚠️ Impossible de récupérer les données météo. Vérifiez votre connexion internet.")

else:
    st.info("👈 Importez vos données de ventes pour commencer")
    
    st.markdown("### 📖 Formats Acceptés")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Formats de fichiers:**
        - 📊 CSV (.csv)
        - 📗 Excel (.xlsx, .xls)
        - 🔤 JSON (.json)
        - 📄 Texte (.txt)
        - 📘 Word (.docx)
        - 📕 PDF (.pdf)
        """)
    
    with col2:
        st.markdown("""
        **Colonnes requises:**
        - **Date**: Date de la vente
        - **Plat**: Nom du plat/produit
        - **Quantite**: Nombre vendu
        
        *Les colonnes sont détectées automatiquement*
        """)
    
    exemple_data = pd.DataFrame({
        'Date': pd.date_range('2026-01-01', periods=30),
        'Plat': np.random.choice(['Lasagnes', 'Salade César', 'Burger', 'Pizza'], 30),
        'Quantite': np.random.randint(20, 60, 30)
    })
    
    st.markdown("#### 📋 Exemple de fichier:")
    st.dataframe(exemple_data.head(10), use_container_width=True, hide_index=True)
    
    csv_exemple = exemple_data.to_csv(index=False)
    st.download_button(
        label="⬇️ Télécharger un fichier exemple (30 jours)",
        data=csv_exemple,
        file_name="exemple_ventes_ml.csv",
        mime="text/csv"
    )
    
    st.markdown("---")
    st.markdown("""
    ### 🤖 Technologies Utilisées
    - **Random Forest**: Ensemble de 200 arbres de décision
    - **Gradient Boosting**: Optimisation séquentielle avec 150 itérations
    - **Features Engineering**: 16+ variables (tendances, lags, moyennes mobiles, saisonnalité)
    - **Auto-sélection**: Le meilleur modèle est choisi automatiquement
    - **Météo IA**: Impact automatique des conditions météo sur les prévisions
    - **Multi-restaurants**: Gérez plusieurs établissements depuis une interface
    - **🔒 Sécurité**: Authentification et données privées par utilisateur
    """)
