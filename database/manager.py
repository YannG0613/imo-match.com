"""
Gestionnaire de base de données pour ImoMatch - Étape 1
"""
import sqlite3
import json
from datetime import datetime
import os

class DatabaseManager:
    def __init__(self, db_path="imomatch.db"):
        self.db_path = db_path
        self.create_tables()
        
    def get_connection(self):
        """Retourne une connexion à la base de données"""
        return sqlite3.connect(self.db_path)
    
    def create_tables(self):
        """Crée les tables nécessaires"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Table des utilisateurs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    first_name TEXT,
                    last_name TEXT,
                    phone TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
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
                    location TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            print("Tables créées avec succès")
            
        except Exception as e:
            print(f"Erreur création tables: {e}")
        finally:
            conn.close()
    
    def add_sample_data(self):
        """Ajoute des données d'exemple"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Vérifier si des propriétés existent déjà
            cursor.execute("SELECT COUNT(*) FROM properties")
            if cursor.fetchone()[0] > 0:
                print("Données d'exemple déjà présentes")
                return
            
            # Propriétés d'exemple
            sample_properties = [
                ("Appartement 3P - Antibes Centre", 
                 "Bel appartement rénové proche de tout", 
                 650000, "Appartement", 85, 3, "Antibes"),
                 
                ("Villa avec piscine - Cannes", 
                 "Magnifique villa avec vue mer", 
                 1200000, "Villa", 150, 4, "Cannes"),
                 
                ("Studio - Monaco", 
                 "Studio moderne vue port", 
                 450000, "Studio", 35, 1, "Monaco"),
            ]
            
            cursor.executemany('''
                INSERT INTO properties (title, description, price, property_type, surface, bedrooms, location)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', sample_properties)
            
            conn.commit()
            print("Données d'exemple ajoutées")
            
        except Exception as e:
            print(f"Erreur ajout données: {e}")
        finally:
            conn.close()
    
    def test_connection(self):
        """Test simple de connexion"""
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
    
    def get_all_properties(self):
        """Récupère toutes les propriétés"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM properties ORDER BY created_at DESC")
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            
            properties = []
            for row in rows:
                prop = dict(zip(columns, row))
                properties.append(prop)
            
            return properties
            
        except Exception as e:
            print(f"Erreur récupération propriétés: {e}")
            return []
        finally:
            conn.close()

# Pour tester ce module directement
if __name__ == "__main__":
    print("=== Test du gestionnaire de base de données ===")
    
    # Créer l'instance
    db = DatabaseManager()
    
    # Test de connexion
    if db.test_connection():
        print("✅ Connexion réussie")
    else:
        print("❌ Problème de connexion")
        exit(1)
    
    # Ajouter des données d'exemple
    db.add_sample_data()
    
    # Récupérer et afficher les propriétés
    properties = db.get_all_properties()
    print(f"\n=== Propriétés en base ({len(properties)}) ===")
    
    for prop in properties:
        print(f"- {prop['title']} | {prop['price']:,}€ | {prop['location']}")
    
    print("\n=== Test terminé ===")
