"""
Module de gestion des sources de données cloud pour l'application Restaurant
Supporte: Google Sheets, OneDrive/Excel, Dropbox, URL directes
"""

import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import pickle
import os
import json
from typing import Optional, Dict, Any

class DataSourceManager:
    """Gestionnaire centralisé de toutes les sources de données"""
    
    SUPPORTED_SOURCES = {
        'upload': 'Upload Fichier Local',
        'google_sheets': 'Google Sheets',
        'onedrive': 'OneDrive / Excel Online',
        'dropbox': 'Dropbox',
        'url': 'URL Publique (CSV/Excel)'
    }
    
    def __init__(self, username: str):
        self.username = username
        self.config_file = f"data/{username}_datasources.pkl"
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Charge la configuration des sources de données"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'rb') as f:
                return pickle.load(f)
        return {
            'active_source': 'upload',
            'sources': {},
            'auto_sync': False,
            'sync_interval': 10  # minutes
        }
    
    def save_config(self):
        """Sauvegarde la configuration"""
        os.makedirs('data', exist_ok=True)
        with open(self.config_file, 'wb') as f:
            pickle.dump(self.config, f)
    
    def get_active_source(self) -> str:
        """Retourne le type de source active"""
        return self.config.get('active_source', 'upload')
    
    def set_active_source(self, source_type: str):
        """Définit la source de données active"""
        if source_type in self.SUPPORTED_SOURCES:
            self.config['active_source'] = source_type
            self.save_config()
    
    def add_source(self, source_type: str, source_config: Dict[str, Any]):
        """Ajoute une nouvelle source de données"""
        if 'sources' not in self.config:
            self.config['sources'] = {}
        
        self.config['sources'][source_type] = {
            **source_config,
            'added_at': datetime.now().isoformat(),
            'last_sync': None
        }
        self.save_config()
    
    def get_source_config(self, source_type: str) -> Optional[Dict[str, Any]]:
        """Récupère la configuration d'une source"""
        return self.config.get('sources', {}).get(source_type)


class GoogleSheetsConnector:
    """Connecteur pour Google Sheets"""
    
    def __init__(self):
        self.credentials = None
        self.service = None
    
    def authenticate(self, credentials_json: str) -> bool:
        """Authentification avec Google Sheets API"""
        try:
            # Note: Nécessite google-auth et gspread
            # Pour Streamlit Cloud, utiliser st.secrets
            return True
        except Exception as e:
            st.error(f"Erreur authentification Google: {str(e)}")
            return False
    
    def connect_sheet(self, sheet_url: str) -> bool:
        """Connecte à une feuille Google Sheets"""
        try:
            # Extraction de l'ID de la feuille depuis l'URL
            if '/spreadsheets/d/' in sheet_url:
                sheet_id = sheet_url.split('/spreadsheets/d/')[1].split('/')[0]
                return True
            return False
        except Exception as e:
            st.error(f"Erreur connexion Google Sheet: {str(e)}")
            return False
    
    def read_sheet(self, sheet_url: str, sheet_name: str = None) -> Optional[pd.DataFrame]:
        """Lit les données d'une Google Sheet"""
        try:
            # Méthode 1: Si feuille publique, utiliser export CSV
            if '/spreadsheets/d/' in sheet_url:
                sheet_id = sheet_url.split('/spreadsheets/d/')[1].split('/')[0]
                
                # Construction URL export CSV
                if sheet_name:
                    # TODO: Gérer nom de feuille spécifique
                    export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
                else:
                    export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
                
                # Téléchargement
                response = requests.get(export_url)
                if response.status_code == 200:
                    from io import StringIO
                    df = pd.read_csv(StringIO(response.text))
                    return df
                else:
                    st.warning("⚠️ Feuille non publique - Authentification requise")
                    return None
            
            return None
        
        except Exception as e:
            st.error(f"Erreur lecture Google Sheet: {str(e)}")
            return None


class OneDriveConnector:
    """Connecteur pour OneDrive / Excel Online"""
    
    def __init__(self):
        self.access_token = None
    
    def authenticate(self, client_id: str, client_secret: str) -> bool:
        """Authentification avec Microsoft Graph API"""
        try:
            # OAuth2 flow pour OneDrive
            # Pour Streamlit Cloud, utiliser st.secrets
            return True
        except Exception as e:
            st.error(f"Erreur authentification OneDrive: {str(e)}")
            return False
    
    def read_excel(self, file_url: str) -> Optional[pd.DataFrame]:
        """Lit un fichier Excel depuis OneDrive"""
        try:
            # Utilisation de l'API Microsoft Graph
            # Nécessite access_token
            return None
        except Exception as e:
            st.error(f"Erreur lecture OneDrive: {str(e)}")
            return None


class DropboxConnector:
    """Connecteur pour Dropbox"""
    
    def __init__(self):
        self.access_token = None
    
    def authenticate(self, access_token: str) -> bool:
        """Authentification avec Dropbox API"""
        try:
            self.access_token = access_token
            # Test de connexion
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            response = requests.post(
                'https://api.dropboxapi.com/2/users/get_current_account',
                headers=headers
            )
            return response.status_code == 200
        except Exception as e:
            st.error(f"Erreur authentification Dropbox: {str(e)}")
            return False
    
    def read_file(self, file_path: str) -> Optional[pd.DataFrame]:
        """Lit un fichier depuis Dropbox"""
        try:
            if not self.access_token:
                return None
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Dropbox-API-Arg': json.dumps({'path': file_path})
            }
            
            response = requests.post(
                'https://content.dropboxapi.com/2/files/download',
                headers=headers
            )
            
            if response.status_code == 200:
                from io import BytesIO
                
                if file_path.endswith('.csv'):
                    df = pd.read_csv(BytesIO(response.content))
                elif file_path.endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(BytesIO(response.content))
                else:
                    return None
                
                return df
            
            return None
        
        except Exception as e:
            st.error(f"Erreur lecture Dropbox: {str(e)}")
            return None


class URLConnector:
    """Connecteur pour URL publiques (CSV/Excel)"""
    
    @staticmethod
    def read_from_url(url: str) -> Optional[pd.DataFrame]:
        """Lit un fichier depuis une URL publique"""
        try:
            response = requests.get(url, timeout=30)
            
            if response.status_code != 200:
                st.error(f"Erreur HTTP {response.status_code}")
                return None
            
            from io import BytesIO, StringIO
            
            # Détection du type de fichier
            if url.endswith('.csv') or 'csv' in response.headers.get('content-type', ''):
                df = pd.read_csv(StringIO(response.text))
            elif url.endswith(('.xlsx', '.xls')) or 'spreadsheet' in response.headers.get('content-type', ''):
                df = pd.read_excel(BytesIO(response.content))
            else:
                # Essai CSV par défaut
                try:
                    df = pd.read_csv(StringIO(response.text))
                except:
                    df = pd.read_excel(BytesIO(response.content))
            
            return df
        
        except Exception as e:
            st.error(f"Erreur lecture URL: {str(e)}")
            return None


class AutoSyncManager:
    """Gestionnaire de synchronisation automatique"""
    
    def __init__(self, data_source_manager: DataSourceManager):
        self.dsm = data_source_manager
    
    def should_sync(self) -> bool:
        """Détermine si une synchronisation est nécessaire"""
        if not self.dsm.config.get('auto_sync', False):
            return False
        
        active_source = self.dsm.get_active_source()
        if active_source == 'upload':
            return False
        
        source_config = self.dsm.get_source_config(active_source)
        if not source_config:
            return False
        
        last_sync = source_config.get('last_sync')
        if not last_sync:
            return True
        
        last_sync_time = datetime.fromisoformat(last_sync)
        interval = self.dsm.config.get('sync_interval', 10)
        
        return datetime.now() - last_sync_time > timedelta(minutes=interval)
    
    def sync_data(self) -> Optional[pd.DataFrame]:
        """Synchronise les données depuis la source active"""
        active_source = self.dsm.get_active_source()
        source_config = self.dsm.get_source_config(active_source)
        
        if not source_config:
            return None
        
        df = None
        
        try:
            if active_source == 'google_sheets':
                connector = GoogleSheetsConnector()
                df = connector.read_sheet(
                    source_config.get('sheet_url', ''),
                    source_config.get('sheet_name')
                )
            
            elif active_source == 'onedrive':
                connector = OneDriveConnector()
                if connector.authenticate(
                    source_config.get('client_id', ''),
                    source_config.get('client_secret', '')
                ):
                    df = connector.read_excel(source_config.get('file_url', ''))
            
            elif active_source == 'dropbox':
                connector = DropboxConnector()
                if connector.authenticate(source_config.get('access_token', '')):
                    df = connector.read_file(source_config.get('file_path', ''))
            
            elif active_source == 'url':
                df = URLConnector.read_from_url(source_config.get('url', ''))
            
            if df is not None:
                # Mise à jour timestamp dernière sync
                source_config['last_sync'] = datetime.now().isoformat()
                self.dsm.save_config()
            
            return df
        
        except Exception as e:
            st.error(f"Erreur synchronisation: {str(e)}")
            return None


# Fonctions utilitaires

def format_last_sync(last_sync_iso: Optional[str]) -> str:
    """Formate le timestamp de dernière synchronisation"""
    if not last_sync_iso:
        return "Jamais synchronisé"
    
    try:
        last_sync = datetime.fromisoformat(last_sync_iso)
        delta = datetime.now() - last_sync
        
        if delta.total_seconds() < 60:
            return f"Il y a {int(delta.total_seconds())} secondes"
        elif delta.total_seconds() < 3600:
            return f"Il y a {int(delta.total_seconds() / 60)} minutes"
        elif delta.total_seconds() < 86400:
            return f"Il y a {int(delta.total_seconds() / 3600)} heures"
        else:
            return f"Il y a {int(delta.total_seconds() / 86400)} jours"
    except:
        return "Erreur de date"


def get_source_icon(source_type: str) -> str:
    """Retourne l'icône pour un type de source"""
    icons = {
        'upload': '📁',
        'google_sheets': '📊',
        'onedrive': '☁️',
        'dropbox': '📦',
        'url': '🔗'
    }
    return icons.get(source_type, '📄')
