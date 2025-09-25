"""Module d'authentification pour ImoMatch"""
import streamlit as st
import hashlib
import sqlite3
from datetime import datetime, timedelta
import os

class AuthManager:
    def __init__(self, db_path="imomatch.db"):
        self.db_path = db_path
        self.init_auth_tables()
    
    def init_auth_tables(self):
        """Initialise les tables d'authentification"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    phone TEXT,
                    age INTEGER,
                    profession TEXT,
                    plan TEXT DEFAULT 'free',
                    trial_end_date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
        except Exception as e:
            st.error(f"Erreur initialisation tables auth : {e}")
    
    def hash_password(self, password):
        """Hash le mot de passe"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def is_authenticated(self):
        """Vérifie si l'utilisateur est authentifié"""
        return st.session_state.get('authenticated', False)
    
    def get_current_user(self):
        """Récupère les données de l'utilisateur connecté"""
        return st.session_state.get('user_data', None)
    
    def login(self, email, password):
        """Connecte un utilisateur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            
            cursor.execute('''
                SELECT id, first_name, last_name, email, phone, age, profession, plan 
                FROM users 
                WHERE email = ? AND password_hash = ?
            ''', (email, password_hash))
            
            user = cursor.fetchone()
            conn.close()
            
            if user:
                user_data = {
                    'id': user[0],
                    'first_name': user[1],
                    'last_name': user[2],
                    'email': user[3],
                    'phone': user[4],
                    'age': user[5],
                    'profession': user[6],
                    'plan': user[7]
                }
                
                st.session_state.authenticated = True
                st.session_state.user_data = user_data
                
                return True, "Connexion réussie"
            else:
                return False, "Email ou mot de passe incorrect"
                
        except Exception as e:
            return False, f"Erreur de connexion : {e}"
    
    def register(self, user_data):
        """Inscrit un nouvel utilisateur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Vérifier si l'email existe déjà
            cursor.execute('SELECT id FROM users WHERE email = ?', (user_data['email'],))
            if cursor.fetchone():
                conn.close()
                return False, "Cet email est déjà utilisé"
            
            # Hasher le mot de passe
            password_hash = self.hash_password(user_data['password'])
            
            # Insérer le nouvel utilisateur
            cursor.execute('''
                INSERT INTO users (first_name, last_name, email, password_hash, phone, age, profession)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_data['first_name'],
                user_data['last_name'],
                user_data['email'],
                password_hash,
                user_data.get('phone'),
                user_data.get('age'),
                user_data.get('profession')
            ))
            
            conn.commit()
            conn.close()
            
            return True, "Compte créé avec succès"
            
        except Exception as e:
            return False, f"Erreur lors de l'inscription : {e}"
    
    def logout(self):
        """Déconnecte l'utilisateur"""
        st.session_state.authenticated = False
        st.session_state.user_data = None

# Instance globale
auth_manager = AuthManager()

# Fonctions utilitaires pour compatibilité
def login_user(email, password):
    return auth_manager.login(email, password)

def logout_user():
    return auth_manager.logout()

def is_authenticated():
    return auth_manager.is_authenticated()

def get_current_user():
    return auth_manager.get_current_user()
