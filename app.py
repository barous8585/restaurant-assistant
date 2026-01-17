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

warnings.filterwarnings('ignore')

st.set_page_config(page_title="Assistant Préparation Restaurant Pro", page_icon="🍽️", layout="wide")

DATA_FILE = "restaurants_data.pkl"

def save_restaurants_data():
    with open(DATA_FILE, 'wb') as f:
        data_to_save = {
            'restaurants': st.session_state.restaurants,
            'current_restaurant': st.session_state.current_restaurant
        }
        pickle.dump(data_to_save, f)

def load_restaurants_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'rb') as f:
                data = pickle.load(f)
                return data.get('restaurants', {}), data.get('current_restaurant', None)
        except:
            return {}, None
    return {}, None

if 'restaurants' not in st.session_state:
    loaded_restaurants, loaded_current = load_restaurants_data()
    st.session_state.restaurants = loaded_restaurants
    st.session_state.current_restaurant = loaded_current
    
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
        
        column_mapping = {}
        for col in df.columns:
            col_lower = col.lower()
            if 'date' in col_lower or 'jour' in col_lower:
                column_mapping[col] = 'Date'
            elif 'plat' in col_lower or 'produit' in col_lower or 'item' in col_lower or 'nom' in col_lower:
                column_mapping[col] = 'Plat'
            elif 'quantit' in col_lower or 'nombre' in col_lower or 'qte' in col_lower or 'qty' in col_lower:
                column_mapping[col] = 'Quantite'
        
        df = df.rename(columns=column_mapping)
        
        return df
    
    except Exception as e:
        st.error(f"Erreur de chargement: {str(e)}")
        return None

def create_features(df):
    df = df.copy()
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])
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
    if df is None or predictions is None or len(df) == 0:
        return None
    
    df_temp = df.copy()
    df_temp['Date'] = pd.to_datetime(df_temp['Date'])
    daily_sales = df_temp.groupby('Date')['Quantite'].sum()
    
    avg_daily_sales = daily_sales.mean()
    std_daily_sales = daily_sales.std()
    
    traditional_prep = avg_daily_sales + (std_daily_sales * 1.5)
    
    total_waste_traditional = 0
    total_waste_ml = 0
    
    for _, pred_row in predictions.iterrows():
        pred_qty = pred_row['Quantite_Prevue']
        actual_avg = avg_daily_sales
        
        waste_traditional = max(0, traditional_prep - actual_avg)
        waste_ml = max(0, pred_qty - actual_avg) * 0.3
        
        total_waste_traditional += waste_traditional
        total_waste_ml += waste_ml
    
    savings = total_waste_traditional - total_waste_ml
    
    return {
        'waste_traditional': total_waste_traditional,
        'waste_ml': total_waste_ml,
        'savings_portions': savings,
        'reduction_percent': (savings / total_waste_traditional * 100) if total_waste_traditional > 0 else 0
    }

def predict_sales_ml(df, plat, jours_prevision=7):
    plat_data = df[df['Plat'] == plat].copy()
    
    if len(plat_data) < 14:
        return None, None, None
    
    plat_data = plat_data.sort_values('Date')
    plat_data = create_features(plat_data)
    
    plat_data_agg = plat_data.groupby('Date').agg({
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
    }).reset_index()
    
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
                'Moyenne_Mobile_7', 'Moyenne_Mobile_14', 'Ecart_Type_7']
    
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
            save_restaurants_data()
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
        save_restaurants_data()
    
    current_resto_data = st.session_state.restaurants[selected_resto]
    
    st.sidebar.info(f"📍 {current_resto_data['city']}")
    st.sidebar.info(f"💰 {current_resto_data['cost_per_portion']}€/portion")
    
    if st.sidebar.button("🗑️ Supprimer ce restaurant"):
        del st.session_state.restaurants[selected_resto]
        if len(st.session_state.restaurants) > 0:
            st.session_state.current_restaurant = list(st.session_state.restaurants.keys())[0]
        else:
            st.session_state.current_restaurant = None
        save_restaurants_data()
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
            st.session_state.restaurants[st.session_state.current_restaurant]['data'] = df
            save_restaurants_data()

current_resto_data = st.session_state.restaurants[st.session_state.current_restaurant]
df = current_resto_data.get('data')

if df is not None:
    required_columns = ['Date', 'Plat', 'Quantite']
    if not all(col in df.columns for col in required_columns):
        st.error(f"❌ Colonnes requises non trouvées. Colonnes détectées: {', '.join(df.columns)}")
        st.info(f"💡 Les colonnes nécessaires sont: {', '.join(required_columns)}")
    else:
        df = create_features(df)
        
        st.sidebar.success(f"✅ {len(df)} ventes chargées")
        st.sidebar.info(f"📅 Période: {df['Date'].min().strftime('%d/%m/%Y')} - {df['Date'].max().strftime('%d/%m/%Y')}")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Ventes", f"{len(df)}")
        with col2:
            st.metric("Plats Différents", f"{df['Plat'].nunique()}")
        with col3:
            total_quantite = df['Quantite'].sum()
            st.metric("Quantité Totale", f"{total_quantite}")
        with col4:
            jours_data = (df['Date'].max() - df['Date'].min()).days
            st.metric("Jours de Données", f"{jours_data}")
        
        st.markdown("---")
        
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📈 Analyse", 
            "🔮 Prévisions ML", 
            "📋 Liste de Préparation",
            "💰 Économies & ROI",
            "📦 Stocks & Commandes",
            "🌤️ Alertes Météo"
        ])
        
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
                    predictions, metrics, best_model_name = predict_sales_ml(df, plat_selectionne, jours_prevision)
                
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
                    pred, _, _ = predict_sales_ml(df, plat, 30)
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
                pred, _, _ = predict_sales_ml(df, plat, analysis_days)
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
                        savings_amount = savings_data['savings_portions'] * cost_per_portion
                        st.metric(
                            "💚 Économies Réalisées",
                            f"{savings_amount:.0f}€",
                            delta=f"{savings_data['reduction_percent']:.1f}% de réduction"
                        )
                    
                    with col4:
                        monthly_savings = (savings_amount / analysis_days) * 30
                        st.metric(
                            "📅 Économies Mensuelles",
                            f"{monthly_savings:.0f}€",
                            delta=f"{monthly_savings * 12:.0f}€/an"
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
                        fig_comparison.update_layout(title=f"Économies sur {analysis_days} jours")
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
                        payback_days = (subscription_cost / (savings_amount / analysis_days)) if savings_amount > 0 else 0
                        
                        st.metric("💎 ROI Mensuel", f"{roi:.0f}%")
                        st.metric("⏱️ Retour sur Investissement", f"{payback_days:.0f} jours")
                        
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
        
        with tab5:
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
                        save_restaurants_data()
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
                            pred, _, _ = predict_sales_ml(df, plat, 30)
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
        
        with tab6:
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
                st.info("💡 Pour activer les prévisions météo réelles, configurez une clé API WeatherAPI dans le code (gratuit sur weatherapi.com)")

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
    - **💾 Sauvegarde Automatique**: Toutes vos données sont préservées entre les sessions
    """)
