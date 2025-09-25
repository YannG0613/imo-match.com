"""Module de gestion de base de données pour ImoMatch"""
import sqlite3
import pandas as pd
from datetime import datetime
import json
import os

class DatabaseManager:
    def __init__(self, db_path="imomatch.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialise toutes les tables nécessaires"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Table des propriétés
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS properties (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    price INTEGER NOT NULL,
                    property_type TEXT NOT NULL,
                    surface INTEGER,
                    bedrooms INTEGER,
                    bathrooms INTEGER,
                    location TEXT NOT NULL,
                    latitude REAL,
                    longitude REAL,
                    features TEXT, -- JSON
                    images TEXT, -- JSON
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table des préférences utilisateur
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    budget_min INTEGER,
                    budget_max INTEGER,
                    property_type TEXT,
                    bedrooms INTEGER,
                    bathrooms INTEGER,
                    surface_min INTEGER,
                    location TEXT,
                    criteria TEXT, -- JSON
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Table des favoris
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_favorites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    property_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (property_id) REFERENCES properties (id),
                    UNIQUE(user_id, property_id)
                )
            ''')
            
            # Table des recherches sauvegardées
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS saved_searches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    search_name TEXT NOT NULL,
                    search_criteria TEXT NOT NULL, -- JSON
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            conn.commit()
            self.populate_sample_data(conn)
            conn.close()
            
        except Exception as e:
            print(f"Erreur initialisation database : {e}")
    
    def populate_sample_data(self, conn=None):
        """Ajoute des données d'exemple si la base est vide"""
        try:
            if conn is None:
                conn = sqlite3.connect(self.db_path)
                should_close = True
            else:
                should_close = False
            
            cursor = conn.cursor()
            
            # Vérifier s'il y a déjà des propriétés
            cursor.execute('SELECT COUNT(*) FROM properties')
            count = cursor.fetchone()[0]
            
            if count == 0:
                # Ajouter des propriétés d'exemple
                sample_properties = [
                    {
                        'title': 'Appartement lumineux - Centre Antibes',
                        'description': 'Magnifique appartement de 3 pièces entièrement rénové avec vue sur mer partielle. Proche de toutes commodités.',
                        'price': 650000,
                        'property_type': 'Appartement',
                        'surface': 85,
                        'bedrooms': 2,
                        'bathrooms': 1,
                        'location': 'Antibes',
                        'features': json.dumps(['Balcon', 'Parking', 'Cave'])
                    },
                    {
                        'title': 'Villa avec piscine - Collines de Cannes',
                        'description': 'Superbe villa contemporaine avec piscine et jardin paysager. Vue panoramique sur la baie de Cannes.',
                        'price': 1200000,
                        'property_type': 'Villa',
                        'surface': 150,
                        'bedrooms': 4,
                        'bathrooms': 3,
                        'location': 'Cannes',
                        'features': json.dumps(['Piscine', 'Jardin', 'Garage', 'Vue mer'])
                    },
                    {
                        'title': 'Penthouse vue mer - Nice',
                        'description': 'Exceptionnel penthouse avec terrasse de 50m² et vue mer à 180°. Standing haut de gamme.',
                        'price': 890000,
                        'property_type': 'Appartement',
                        'surface': 95,
                        'bedrooms': 3,
                        'bathrooms': 2,
                        'location': 'Nice',
                        'features': json.dumps(['Terrasse', 'Vue mer', 'Parking', 'Climatisation'])
                    },
                    {
                        'title': 'Maison de ville - Vieux Antibes',
                        'description': 'Charmante maison de ville dans le cœur historique d\'Antibes. Entièrement restaurée avec goût.',
                        'price': 750000,
                        'property_type': 'Maison',
                        'surface': 110,
                        'bedrooms': 4,
                        'bathrooms': 2,
                        'location': 'Antibes',
                        'features': json.dumps(['Terrasse', 'Cave', 'Proximité plage'])
                    },
                    {
                        'title': 'Studio moderne - Port de Monaco',
                        'description': 'Studio moderne et fonctionnel avec vue sur le port. Idéal investissement locatif.',
                        'price': 450000,
                        'property_type': 'Studio',
                        'surface': 35,
                        'bedrooms': 1,
                        'bathrooms': 1,
                        'location': 'Monaco',
                        'features': json.dumps(['Vue port', 'Climatisation', 'Meublé'])
                    }
                ]
                
                for prop in sample_properties:
                    cursor.execute('''
                        INSERT INTO properties (title, description, price, property_type, surface, bedrooms, bathrooms, location, features)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        prop['title'], prop['description'], prop['price'], prop['property_type'],
                        prop['surface'], prop['bedrooms'], prop['bathrooms'], prop['location'], prop['features']
                    ))
                
                conn.commit()
            
            if should_close:
                conn.close()
                
        except Exception as e:
            print(f"Erreur ajout données d'exemple : {e}")
    
    def get_connection(self):
        """Retourne une connexion à la base de données"""
        return sqlite3.connect(self.db_path)
    
    def search_properties(self, filters=None):
        """Recherche des propriétés selon les filtres"""
        try:
            conn = self.get_connection()
            
            query = "SELECT * FROM properties WHERE 1=1"
            params = []
            
            if filters:
                if filters.get('price_max'):
                    query += " AND price <= ?"
                    params.append(filters['price_max'])
                
                if filters.get('property_type') and filters['property_type'] != 'Tous':
                    query += " AND property_type = ?"
                    params.append(filters['property_type'])
                
                if filters.get('location'):
                    query += " AND location LIKE ?"
                    params.append(f"%{filters['location']}%")
                
                if filters.get('bedrooms'):
                    query += " AND bedrooms >= ?"
                    params.append(filters['bedrooms'])
                
                if filters.get('surface_min'):
                    query += " AND surface >= ?"
                    params.append(filters['surface_min'])
            
            query += " ORDER BY created_at DESC"
            
            df = pd.read_sql_query(query, conn, params=params)
            conn.close()
            
            return df.to_dict('records')
            
        except Exception as e:
            print(f"Erreur recherche propriétés : {e}")
            return []
    
    def get_user_favorites(self, user_id):
        """Récupère les favoris d'un utilisateur"""
        try:
            conn = self.get_connection()
            
            query = '''
                SELECT p.* FROM properties p
                JOIN user_favorites uf ON p.id = uf.property_id
                WHERE uf.user_id = ?
                ORDER BY uf.created_at DESC
            '''
            
            df = pd.read_sql_query(query, conn, params=(user_id,))
            conn.close()
            
            return df.to_dict('records')
            
        except Exception as e:
            print(f"Erreur récupération favoris : {e}")
            return []
    
    def get_saved_searches(self, user_id):
        """Récupère les recherches sauvegardées d'un utilisateur"""
        try:
            conn = self.get_connection()
            
            query = '''
                SELECT * FROM saved_searches
                WHERE user_id = ?
                ORDER BY created_at DESC
            '''
            
            df = pd.read_sql_query(query, conn, params=(user_id,))
            conn.close()
            
            return df.to_dict('records')
            
        except Exception as e:
            print(f"Erreur récupération recherches : {e}")
            return []
    
    def get_user_preferences(self, user_id):
        """Récupère les préférences d'un utilisateur"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM user_preferences WHERE user_id = ?
            ''', (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, result))
            
            return None
            
        except Exception as e:
            print(f"Erreur récupération préférences : {e}")
            return None
    
    def add_to_favorites(self, user_id, property_id):
        """Ajoute une propriété aux favoris"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR IGNORE INTO user_favorites (user_id, property_id)
                VALUES (?, ?)
            ''', (user_id, property_id))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Erreur ajout favoris : {e}")
            return False

# Instance globale
database_manager = DatabaseManager()

# Fonctions utilitaires pour compatibilité
def get_database():
    return database_manager

def get_connection():
    return database_manager.get_connection()
