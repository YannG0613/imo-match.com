"""
Gestionnaire de base de données enrichi pour ImoMatch - Étape 1
Intègre les structures de données complètes
"""
import sqlite3
import json
from datetime import datetime
import random

class DatabaseManager:
    def __init__(self, db_path="imomatch.db"):
        self.db_path = db_path
        self.create_tables()
        
    def get_connection(self):
        """Retourne une connexion à la base de données"""
        return sqlite3.connect(self.db_path)
    
    def create_tables(self):
        """Crée les tables principales"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Table utilisateurs enrichie
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    first_name TEXT,
                    last_name TEXT,
                    phone TEXT,
                    age INTEGER,
                    user_type TEXT DEFAULT 'acquéreur',
                    
                    -- Budget et critères
                    budget_min INTEGER,
                    budget_max INTEGER,
                    property_types TEXT, -- JSON array
                    surface_min INTEGER,
                    bedrooms_min INTEGER,
                    preferred_locations TEXT, -- JSON array
                    
                    -- Profil démographique
                    marital_status TEXT,
                    children_count INTEGER DEFAULT 0,
                    lifestyle TEXT,
                    work_arrangement TEXT,
                    
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table propriétés enrichie
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS properties (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    property_type TEXT NOT NULL,
                    property_subtype TEXT,
                    
                    -- Caractéristiques physiques
                    surface_total INTEGER,
                    surface_habitable INTEGER,
                    surface_terrain INTEGER,
                    bedrooms INTEGER,
                    bathrooms INTEGER,
                    floor_number INTEGER,
                    
                    -- Informations techniques
                    construction_year INTEGER,
                    energy_class TEXT,
                    heating_type TEXT,
                    
                    -- Équipements
                    elevator BOOLEAN DEFAULT 0,
                    balcony BOOLEAN DEFAULT 0,
                    terrace BOOLEAN DEFAULT 0,
                    garden BOOLEAN DEFAULT 0,
                    swimming_pool BOOLEAN DEFAULT 0,
                    garage_count INTEGER DEFAULT 0,
                    parking_spaces INTEGER DEFAULT 0,
                    
                    -- Finances
                    price INTEGER NOT NULL,
                    price_per_sqm INTEGER,
                    monthly_charges INTEGER,
                    
                    -- Localisation
                    address TEXT,
                    city TEXT NOT NULL,
                    postal_code TEXT,
                    
                    -- Qualité et standing
                    luxury_level INTEGER DEFAULT 3,
                    view_quality TEXT,
                    quietness_level INTEGER DEFAULT 3,
                    brightness_level INTEGER DEFAULT 3,
                    
                    -- Disponibilité
                    availability_date DATE,
                    listing_status TEXT DEFAULT 'active',
                    
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table agents
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS real_estate_agents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    agency_name TEXT,
                    email TEXT,
                    phone TEXT,
                    specialization TEXT,
                    experience_years INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table favoris
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS favorites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    property_id INTEGER,
                    interest_level INTEGER DEFAULT 3,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (property_id) REFERENCES properties (id),
                    UNIQUE(user_id, property_id)
                )
            ''')
            
            conn.commit()
            print("Tables enrichies créées avec succès")
            
        except Exception as e:
            print(f"Erreur création tables: {e}")
        finally:
            conn.close()
    
    def add_comprehensive_sample_data(self):
        """Ajoute des données d'exemple enrichies"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Vérifier si des données existent déjà
            cursor.execute("SELECT COUNT(*) FROM properties")
            if cursor.fetchone()[0] > 0:
                print("Données d'exemple déjà présentes")
                return
            
            # Agents d'exemple
            agents = [
                ("Marie", "Dubois", "Century 21 Nice", "marie.dubois@c21.fr", "0493123456", "luxe", 8),
                ("Pierre", "Martin", "Orpi Antibes", "pierre.martin@orpi.fr", "0493789123", "vente", 12),
                ("Sophie", "Leroy", "Laforêt Cannes", "sophie.leroy@laforet.fr", "0493456789", "location", 6),
                ("Jean", "Moreau", "Indépendant Nice", "jean.moreau@immobilier.fr", "0493987654", "investissement", 15),
                ("Isabelle", "Garcia", "Prestige Monaco", "isabelle.garcia@prestige.mc", "0493654321", "luxe", 10)
            ]
            
            for agent in agents:
                cursor.execute('''
                    INSERT INTO real_estate_agents 
                    (first_name, last_name, agency_name, email, phone, specialization, experience_years)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', agent)
            
            # Propriétés d'exemple variées
            properties = [
                {
                    'title': 'Penthouse Exceptionnel - Croisette Cannes',
                    'description': 'Magnifique penthouse 200m² avec terrasse 150m², vue mer panoramique, prestations luxe',
                    'property_type': 'Penthouse', 'property_subtype': 'T5',
                    'surface_total': 200, 'surface_habitable': 180, 'bedrooms': 4, 'bathrooms': 3,
                    'construction_year': 2019, 'energy_class': 'A', 'heating_type': 'pompe_à_chaleur',
                    'elevator': 1, 'terrace': 1, 'swimming_pool': 1, 'garage_count': 2,
                    'price': 4500000, 'price_per_sqm': 22500,
                    'city': 'Cannes', 'postal_code': '06400',
                    'luxury_level': 5, 'view_quality': 'mer', 'quietness_level': 4, 'brightness_level': 5
                },
                {
                    'title': 'Villa Contemporaine - Hauteurs de Nice',
                    'description': 'Superbe villa 250m² avec piscine, jardin 1500m², vue panoramique, prestations haut de gamme',
                    'property_type': 'Villa', 'property_subtype': 'T6',
                    'surface_total': 250, 'surface_habitable': 220, 'surface_terrain': 1500,
                    'bedrooms': 5, 'bathrooms': 4, 'construction_year': 2010,
                    'energy_class': 'B', 'heating_type': 'gaz',
                    'garden': 1, 'swimming_pool': 1, 'garage_count': 2,
                    'price': 1800000, 'price_per_sqm': 7200,
                    'city': 'Nice', 'postal_code': '06000',
                    'luxury_level': 4, 'view_quality': 'montagne', 'quietness_level': 5, 'brightness_level': 4
                },
                {
                    'title': 'Appartement Familial - Centre Antibes',
                    'description': 'Bel appartement T4 rénové, proche plages et commerces, copropriété sécurisée',
                    'property_type': 'Appartement', 'property_subtype': 'T4',
                    'surface_total': 95, 'surface_habitable': 90, 'bedrooms': 3, 'bathrooms': 2,
                    'construction_year': 1980, 'energy_class': 'D', 'heating_type': 'électrique',
                    'elevator': 1, 'balcony': 1, 'parking_spaces': 1,
                    'price': 650000, 'price_per_sqm': 6842, 'monthly_charges': 180,
                    'city': 'Antibes', 'postal_code': '06600',
                    'luxury_level': 3, 'view_quality': 'ville', 'quietness_level': 3, 'brightness_level': 4
                },
                {
                    'title': 'Studio Investissement - Gare de Monaco',
                    'description': 'Studio 28m² rénové, idéal investissement locatif, proche transports',
                    'property_type': 'Studio', 'property_subtype': 'T1',
                    'surface_total': 28, 'surface_habitable': 26, 'bedrooms': 1, 'bathrooms': 1,
                    'construction_year': 2000, 'energy_class': 'C', 'heating_type': 'électrique',
                    'elevator': 1, 'price': 420000, 'price_per_sqm': 15000,
                    'city': 'Monaco', 'postal_code': '98000',
                    'luxury_level': 2, 'view_quality': 'cour', 'quietness_level': 2, 'brightness_level': 3
                },
                {
                    'title': 'Maison de Charme - Vieux Grasse',
                    'description': 'Authentique maison provençale, terrasses, vue panoramique, cachet exceptionnel',
                    'property_type': 'Maison', 'property_subtype': 'T5',
                    'surface_total': 140, 'surface_habitable': 130, 'surface_terrain': 400,
                    'bedrooms': 4, 'bathrooms': 2, 'construction_year': 1920,
                    'energy_class': 'E', 'heating_type': 'bois',
                    'garden': 1, 'terrace': 1, 'fireplace': 1,
                    'price': 580000, 'price_per_sqm': 4143,
                    'city': 'Grasse', 'postal_code': '06130',
                    'luxury_level': 3, 'view_quality': 'montagne', 'quietness_level': 5, 'brightness_level': 4
                },
                {
                    'title': 'Loft Atypique - Port de Saint-Laurent',
                    'description': 'Magnifique loft 120m², volumes exceptionnels, proche marina, moderne',
                    'property_type': 'Loft', 'property_subtype': 'T3',
                    'surface_total': 120, 'surface_habitable': 115, 'bedrooms': 2, 'bathrooms': 2,
                    'construction_year': 2005, 'energy_class': 'C', 'heating_type': 'pompe_à_chaleur',
                    'elevator': 1, 'terrace': 1, 'parking_spaces': 1,
                    'price': 750000, 'price_per_sqm': 6250,
                    'city': 'Saint-Laurent-du-Var', 'postal_code': '06700',
                    'luxury_level': 4, 'view_quality': 'mer', 'quietness_level': 3, 'brightness_level': 5
                }
            ]
            
            for prop in properties:
                columns = ', '.join(prop.keys())
                placeholders = ', '.join(['?' for _ in prop])
                cursor.execute(f'INSERT INTO properties ({columns}) VALUES ({placeholders})', 
                             list(prop.values()))
            
            # Utilisateurs d'exemple avec profils variés
            users = [
                {
                    'email': 'jean.famille@email.fr', 'password_hash': 'hash123',
                    'first_name': 'Jean', 'last_name': 'Dupont', 'phone': '0612345678',
                    'age': 38, 'user_type': 'acquéreur',
                    'budget_min': 800000, 'budget_max': 1200000,
                    'property_types': json.dumps(['Villa', 'Maison']),
                    'surface_min': 150, 'bedrooms_min': 4,
                    'preferred_locations': json.dumps(['Nice', 'Antibes']),
                    'marital_status': 'marié', 'children_count': 2,
                    'lifestyle': 'périurbain', 'work_arrangement': 'mixte'
                },
                {
                    'email': 'sophie.jeune@email.fr', 'password_hash': 'hash456',
                    'first_name': 'Sophie', 'last_name': 'Martin', 'phone': '0623456789',
                    'age': 26, 'user_type': 'locataire',
                    'budget_min': 800, 'budget_max': 1500,
                    'property_types': json.dumps(['Appartement', 'Studio']),
                    'surface_min': 35, 'bedrooms_min': 1,
                    'preferred_locations': json.dumps(['Cannes', 'Antibes']),
                    'marital_status': 'célibataire', 'children_count': 0,
                    'lifestyle': 'urbain', 'work_arrangement': 'bureau'
                },
                {
                    'email': 'pierre.investisseur@email.fr', 'password_hash': 'hash789',
                    'first_name': 'Pierre', 'last_name': 'Investisseur', 'phone': '0634567890',
                    'age': 52, 'user_type': 'investisseur',
                    'budget_min': 300000, 'budget_max': 800000,
                    'property_types': json.dumps(['Appartement', 'Studio']),
                    'surface_min': 25, 'bedrooms_min': 1,
                    'preferred_locations': json.dumps(['Monaco', 'Nice', 'Cannes']),
                    'marital_status': 'marié', 'children_count': 3,
                    'lifestyle': 'urbain', 'work_arrangement': 'mixte'
                }
            ]
            
            for user in users:
                columns = ', '.join(user.keys())
                placeholders = ', '.join(['?' for _ in user])
                cursor.execute(f'INSERT INTO users ({columns}) VALUES ({placeholders})', 
                             list(user.values()))
            
            conn.commit()
            print("Données d'exemple enrichies ajoutées avec succès")
            
        except Exception as e:
            print(f"Erreur ajout données: {e}")
        finally:
            conn.close()
    
    def search_properties_advanced(self, filters=None):
        """Recherche avancée avec tous les critères"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            query = "SELECT * FROM properties WHERE listing_status = 'active'"
            params = []
            
            if filters:
                if filters.get('price_max'):
                    query += " AND price <= ?"
                    params.append(filters['price_max'])
                
                if filters.get('price_min'):
                    query += " AND price >= ?"
                    params.append(filters['price_min'])
                
                if filters.get('property_type'):
                    query += " AND property_type = ?"
                    params.append(filters['property_type'])
                
                if filters.get('city'):
                    query += " AND city LIKE ?"
                    params.append(f"%{filters['city']}%")
                
                if filters.get('bedrooms_min'):
                    query += " AND bedrooms >= ?"
                    params.append(filters['bedrooms_min'])
                
                if filters.get('surface_min'):
                    query += " AND surface_total >= ?"
                    params.append(filters['surface_min'])
                
                if filters.get('luxury_level'):
                    query += " AND luxury_level >= ?"
                    params.append(filters['luxury_level'])
                
                if filters.get('has_garden'):
                    query += " AND garden = 1"
                
                if filters.get('has_pool'):
                    query += " AND swimming_pool = 1"
                
                if filters.get('has_garage'):
                    query += " AND garage_count > 0"
            
            query += " ORDER BY created_at DESC LIMIT 50"
            
            cursor.execute(query, params)
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            
            properties = []
            for row in rows:
                prop = dict(zip(columns, row))
                properties.append(prop)
            
            return properties
            
        except Exception as e:
            print(f"Erreur recherche: {e}")
            return []
        finally:
            conn.close()
    
    def get_property_by_id(self, property_id):
        """Récupère une propriété par son ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM properties WHERE id = ?", (property_id,))
            row = cursor.fetchone()
            
            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            return None
            
        except Exception as e:
            print(f"Erreur récupération propriété: {e}")
            return None
        finally:
            conn.close()
    
    def get_user_profile(self, user_id):
        """Récupère le profil complet d'un utilisateur"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            
            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            return None
            
        except Exception as e:
            print(f"Erreur récupération utilisateur: {e}")
            return None
        finally:
            conn.close()
    
    def get_statistics(self):
        """Retourne des statistiques de la base"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            stats = {}
            
            # Comptages généraux
            cursor.execute("SELECT COUNT(*) FROM properties WHERE listing_status = 'active'")
            stats['total_properties'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM users")
            stats['total_users'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM real_estate_agents")
            stats['total_agents'] = cursor.fetchone()[0]
            
            # Prix moyens par ville
            cursor.execute('''
                SELECT city, AVG(price), COUNT(*) 
                FROM properties 
                WHERE listing_status = 'active' 
                GROUP BY city 
                ORDER BY AVG(price) DESC
            ''')
            stats['price_by_city'] = [
                {'city': row[0], 'avg_price': int(row[1]), 'count': row[2]}
                for row in cursor.fetchall()
            ]
            
            # Répartition par type
            cursor.execute('''
                SELECT property_type, COUNT(*) 
                FROM properties 
                WHERE listing_status = 'active' 
                GROUP BY property_type
            ''')
            stats['properties_by_type'] = dict(cursor.fetchall())
            
            return stats
            
        except Exception as e:
            print(f"Erreur statistiques: {e}")
            return {}
        finally:
            conn.close()
    
    def test_connection(self):
        """Test de connexion à la base"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM properties")
            count = cursor.fetchone()[0]
            conn.close()
            print(f"Test réussi: {count} propriétés en base")
            return True
        except Exception as e:
            print(f"Test échoué: {e}")
            return False

# Instance globale
db_manager = DatabaseManager()

# Fonctions utilitaires
def get_database():
    return db_manager

def search_properties(filters=None):
    return db_manager.search_properties_advanced(filters)

def get_stats():
    return db_manager.get_statistics()

# Test du module
if __name__ == "__main__":
    print("=== Test Base de Données Enrichie ===")
    
    # Test de connexion
    if db_manager.test_connection():
        print("✅ Connexion réussie")
    else:
        print("❌ Problème de connexion")
        exit(1)
    
    # Ajouter des données d'exemple
    print("\n=== Ajout des données d'exemple ===")
    db_manager.add_comprehensive_sample_data()
    
    # Statistiques
    print("\n=== Statistiques ===")
    stats = db_manager.get_statistics()
    print(f"Propriétés actives: {stats.get('total_properties', 0)}")
    print(f"Utilisateurs: {stats.get('total_users', 0)}")
    print(f"Agents: {stats.get('total_agents', 0)}")
    
    # Test de recherche
    print("\n=== Test de recherche ===")
    results = db_manager.search_properties_advanced({
        'price_max': 1000000,
        'bedrooms_min': 2,
        'city': 'Nice'
    })
    
    print(f"Résultats de recherche: {len(results)} propriétés trouvées")
    for prop in results[:3]:  # Afficher les 3 premiers
        print(f"- {prop['title']} | {prop['price']:,}€ | {prop['city']}")
    
    print("\n=== Test terminé ===")
