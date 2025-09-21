import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sqlite3
import hashlib
import json
from typing import Dict, List, Optional, Tuple
import folium
from streamlit_folium import st_folium
import random

# Gestion optionnelle d'OpenAI
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# ================================
# CONFIGURATION ET CONSTANTES
# ================================

COLORS = {
    'primary': '#FF6B35',      # Orange principal
    'secondary': '#F7931E',    # Orange secondaire
    'accent': '#FFB84D',       # Orange clair
    'dark': '#2C3E50',         # Bleu foncé
    'light': '#ECF0F1',        # Gris clair
    'success': '#27AE60',      # Vert
    'danger': '#E74C3C',       # Rouge
    'warning': '#F39C12',      # Orange foncé
    'info': '#3498DB'          # Bleu
}

TRANSLATIONS = {
    'fr': {
        'title': 'ImoMatch - Trouvez votre bien immobilier idéal',
        'subtitle': 'Intelligence artificielle au service de votre recherche immobilière',
        'login': 'Connexion',
        'register': 'S\'inscrire',
        'dashboard': 'Tableau de bord',
        'my_info': 'Mes informations',
        'search': 'Recherche',
        'recommendations': 'Recommandations',
        'agent_ai': 'Agent IA',
        'logout': 'Déconnexion',
        'welcome': 'Bienvenue sur ImoMatch',
        'value_prop': 'Notre plateforme utilise l\'intelligence artificielle pour vous aider à trouver le bien immobilier parfait selon vos critères personnalisés.',
        'free_plan': 'Gratuit',
        'premium_plan': 'Premium',
        'pro_plan': 'Professionnel',
        'statistics': 'Statistiques',
        'partners': 'Partenaires',
        'contact': 'Contact'
    },
    'en': {
        'title': 'ImoMatch - Find your ideal property',
        'subtitle': 'Artificial intelligence for your real estate search',
        'login': 'Login',
        'register': 'Sign Up',
        'dashboard': 'Dashboard',
        'my_info': 'My Information',
        'search': 'Search',
        'recommendations': 'Recommendations',
        'agent_ai': 'AI Agent',
        'logout': 'Logout',
        'welcome': 'Welcome to ImoMatch',
        'value_prop': 'Our platform uses artificial intelligence to help you find the perfect property according to your personalized criteria.',
        'free_plan': 'Free',
        'premium_plan': 'Premium',
        'pro_plan': 'Professional',
        'statistics': 'Statistics',
        'partners': 'Partners',
        'contact': 'Contact'
    }
}

# ================================
# CLASSE DE GESTION DE BASE DE DONNÉES
# ================================

class DatabaseManager:
    def __init__(self, db_path: str = "imomatch.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialise la base de données avec les tables nécessaires"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table des utilisateurs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                first_name TEXT,
                last_name TEXT,
                phone TEXT,
                age INTEGER,
                profession TEXT,
                plan TEXT DEFAULT 'free',
                trial_end_date TEXT,
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
                criteria JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Table des biens immobiliers
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS properties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                price INTEGER NOT NULL,
                property_type TEXT,
                bedrooms INTEGER,
                bathrooms INTEGER,
                surface INTEGER,
                location TEXT,
                latitude REAL,
                longitude REAL,
                description TEXT,
                features JSON,
                images JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_user(self, email: str, password: str, **kwargs) -> Optional[int]:
        """Crée un nouvel utilisateur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        try:
            cursor.execute('''
                INSERT INTO users (email, password_hash, first_name, last_name, phone, age, profession, plan)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                email, password_hash, 
                kwargs.get('first_name', ''),
                kwargs.get('last_name', ''),
                kwargs.get('phone', ''),
                kwargs.get('age'),
                kwargs.get('profession', ''),
                kwargs.get('plan', 'free')
            ))
            user_id = cursor.lastrowid
            conn.commit()
            return user_id
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """Authentifie un utilisateur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        cursor.execute('''
            SELECT * FROM users WHERE email = ? AND password_hash = ?
        ''', (email, password_hash))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            columns = ['id', 'email', 'password_hash', 'first_name', 'last_name', 
                      'phone', 'age', 'profession', 'plan', 'trial_end_date', 
                      'created_at', 'updated_at']
            return dict(zip(columns, user))
        return None
    
    def get_user_preferences(self, user_id: int) -> Optional[Dict]:
        """Récupère les préférences d'un utilisateur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM user_preferences WHERE user_id = ? ORDER BY updated_at DESC LIMIT 1
        ''', (user_id,))
        
        prefs = cursor.fetchone()
        conn.close()
        
        if prefs:
            columns = ['id', 'user_id', 'budget_min', 'budget_max', 'property_type',
                      'bedrooms', 'bathrooms', 'surface_min', 'location', 'criteria',
                      'created_at', 'updated_at']
            result = dict(zip(columns, prefs))
            if result['criteria']:
                result['criteria'] = json.loads(result['criteria'])
            return result
        return None
    
    def save_user_preferences(self, user_id: int, preferences: Dict):
        """Sauvegarde les préférences utilisateur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_preferences 
            (user_id, budget_min, budget_max, property_type, bedrooms, bathrooms, 
             surface_min, location, criteria, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (
            user_id,
            preferences.get('budget_min'),
            preferences.get('budget_max'),
            preferences.get('property_type'),
            preferences.get('bedrooms'),
            preferences.get('bathrooms'),
            preferences.get('surface_min'),
            preferences.get('location'),
            json.dumps(preferences.get('criteria', {}))
        ))
        
        conn.commit()
        conn.close()
    
    def search_properties(self, filters: Dict) -> List[Dict]:
        """Recherche des biens selon des filtres"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM properties WHERE 1=1"
        params = []
        
        if filters.get('budget_min'):
            query += " AND price >= ?"
            params.append(filters['budget_min'])
        
        if filters.get('budget_max'):
            query += " AND price <= ?"
            params.append(filters['budget_max'])
        
        if filters.get('property_type'):
            query += " AND property_type = ?"
            params.append(filters['property_type'])
        
        if filters.get('location'):
            query += " AND location LIKE ?"
            params.append(f"%{filters['location']}%")
        
        cursor.execute(query, params)
        properties = cursor.fetchall()
        conn.close()
        
        columns = ['id', 'title', 'price', 'property_type', 'bedrooms', 'bathrooms',
                  'surface', 'location', 'latitude', 'longitude', 'description',
                  'features', 'images', 'created_at']
        
        result = []
        for prop in properties:
            prop_dict = dict(zip(columns, prop))
            if prop_dict['features']:
                prop_dict['features'] = json.loads(prop_dict['features'])
            if prop_dict['images']:
                prop_dict['images'] = json.loads(prop_dict['images'])
            result.append(prop_dict)
        
        return result

# ================================
# FONCTIONS UTILITAIRES
# ================================

def init_session_state():
    """Initialise les variables de session"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'language' not in st.session_state:
        st.session_state.language = 'fr'
    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'
    if 'db' not in st.session_state:
        st.session_state.db = DatabaseManager()

def get_text(key: str) -> str:
    """Récupère le texte traduit"""
    return TRANSLATIONS[st.session_state.language].get(key, key)

def apply_theme():
    """Applique le thème choisi"""
    if st.session_state.theme == 'dark':
        st.markdown("""
        <style>
        .stApp {
            background-color: #1E1E1E;
            color: #FFFFFF;
        }
        .stSidebar {
            background-color: #2D2D2D;
        }
        .stSelectbox, .stTextInput, .stTextArea, .stNumberInput {
            background-color: #3D3D3D;
            color: #FFFFFF;
        }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <style>
        .stApp {{
            background-color: #FFFFFF;
            color: #333333;
        }}
        .main-header {{
            background: linear-gradient(90deg, {COLORS['primary']}, {COLORS['secondary']});
            color: white;
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 2rem;
        }}
        .metric-card {{
            background: white;
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid {COLORS['primary']};
        }}
        .plan-card {{
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
            margin: 1rem 0;
        }}
        .plan-card.premium {{
            border: 2px solid {COLORS['primary']};
            transform: scale(1.05);
        }}
        .ai-chat {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 1rem;
            margin: 0.5rem 0;
        }}
        .user-message {{
            background: {COLORS['primary']};
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 15px;
            margin: 0.5rem 0;
            margin-left: 20%;
        }}
        .ai-message {{
            background: white;
            color: #333;
            padding: 0.5rem 1rem;
            border-radius: 15px;
            margin: 0.5rem 0;
            margin-right: 20%;
            border: 1px solid #ddd;
        }}
        </style>
        """, unsafe_allow_html=True)

def create_logo():
    """Crée le logo ImoMatch"""
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem 0;">
        <div style="background: linear-gradient(45deg, {COLORS['primary']}, {COLORS['secondary']}); 
                    width: 80px; height: 80px; border-radius: 50%; 
                    display: inline-flex; align-items: center; justify-content: center;
                    margin-bottom: 1rem;">
            <span style="color: white; font-size: 2rem; font-weight: bold;">IM</span>
        </div>
        <h1 style="color: {COLORS['primary']}; margin: 0;">ImoMatch</h1>
        <p style="color: #666; margin: 0;">{get_text('subtitle')}</p>
    </div>
    """, unsafe_allow_html=True)

# ================================
# PAGES DE L'APPLICATION
# ================================

def show_landing_page():
    """Page d'accueil pour les utilisateurs non connectés"""
    create_logo()
    
    st.markdown(f"""
    <div class="main-header">
        <h2>{get_text('welcome')}</h2>
        <p>{get_text('value_prop')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Statistiques
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>10,000+</h3>
            <p>Biens analysés</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>95%</h3>
            <p>Satisfaction client</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>5,000+</h3>
            <p>Utilisateurs actifs</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>24/7</h3>
            <p>Support IA</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Plans tarifaires
    st.markdown("## Nos offres")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="plan-card">
            <h3>{get_text('free_plan')}</h3>
            <h2>0€</h2>
            <ul style="text-align: left;">
                <li>5 recherches/mois</li>
                <li>Support de base</li>
                <li>Accès limité à l'IA</li>
            </ul>
            <button style="background: {COLORS['primary']}; color: white; border: none; padding: 10px 20px; border-radius: 5px;">
                Gratuit
            </button>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="plan-card premium">
            <h3>{get_text('premium_plan')}</h3>
            <h2>29€/mois</h2>
            <p><small>Essai gratuit 14 jours</small></p>
            <ul style="text-align: left;">
                <li>Recherches illimitées</li>
                <li>IA avancée</li>
                <li>Support prioritaire</li>
                <li>Notifications en temps réel</li>
            </ul>
            <button style="background: {COLORS['primary']}; color: white; border: none; padding: 10px 20px; border-radius: 5px;">
                Essayer gratuitement
            </button>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="plan-card">
            <h3>{get_text('pro_plan')}</h3>
            <h2>99€/mois</h2>
            <ul style="text-align: left;">
                <li>Tout Premium +</li>
                <li>API access</li>
                <li>Rapports personnalisés</li>
                <li>Support dédié</li>
            </ul>
            <button style="background: {COLORS['primary']}; color: white; border: none; padding: 10px 20px; border-radius: 5px;">
                Contacter
            </button>
        </div>
        """, unsafe_allow_html=True)
    
    # Partenaires
    st.markdown("## Nos partenaires")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("🏠 **Century 21**")
    with col2:
        st.markdown("🏢 **Orpi**")
    with col3:
        st.markdown("🏗️ **Nexity**")
    with col4:
        st.markdown("🔑 **Foncia**")
    
    # Contact
    st.markdown("## Contact")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("📧 **contact@imomatch.fr**")
        st.markdown("📞 **+33 1 23 45 67 89**")
    with col2:
        st.markdown("📍 **Paris, France**")
        st.markdown("🌐 **www.imomatch.fr**")

def show_login_page():
    """Page de connexion"""
    create_logo()
    
    tab1, tab2 = st.tabs([get_text('login'), get_text('register')])
    
    with tab1:
        st.markdown("### Connexion")
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Mot de passe", type="password")
            submitted = st.form_submit_button("Se connecter")
            
            if submitted and email and password:
                user = st.session_state.db.authenticate_user(email, password)
                if user:
                    st.session_state.authenticated = True
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("Email ou mot de passe incorrect")
    
    with tab2:
        st.markdown("### Inscription")
        with st.form("register_form"):
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("Prénom")
                last_name = st.text_input("Nom")
                email = st.text_input("Email", key="reg_email")
            with col2:
                phone = st.text_input("Téléphone")
                age = st.number_input("Âge", min_value=18, max_value=100)
                profession = st.text_input("Profession")
            
            password = st.text_input("Mot de passe", type="password", key="reg_password")
            password_confirm = st.text_input("Confirmer le mot de passe", type="password")
            plan = st.selectbox("Plan", ["free", "premium", "professional"])
            
            submitted = st.form_submit_button("S'inscrire")
            
            if submitted:
                if password != password_confirm:
                    st.error("Les mots de passe ne correspondent pas")
                elif len(password) < 6:
                    st.error("Le mot de passe doit contenir au moins 6 caractères")
                else:
                    user_id = st.session_state.db.create_user(
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name,
                        phone=phone,
                        age=age,
                        profession=profession,
                        plan=plan
                    )
                    
                    if user_id:
                        st.success("Inscription réussie ! Vous pouvez maintenant vous connecter.")
                    else:
                        st.error("Cet email est déjà utilisé")

def show_my_info_page():
    """Page des informations utilisateur avec Agent IA"""
    st.markdown("# Mes informations")
    
    user = st.session_state.user
    
    # Onglets pour organiser les informations
    tab1, tab2, tab3 = st.tabs(["Profil", "Préférences", "Agent IA"])
    
    with tab1:
        st.markdown("## Informations personnelles")
        
        with st.form("user_info_form"):
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("Prénom", value=user.get('first_name', ''))
                last_name = st.text_input("Nom", value=user.get('last_name', ''))
                email = st.text_input("Email", value=user.get('email', ''), disabled=True)
            with col2:
                phone = st.text_input("Téléphone", value=user.get('phone', ''))
                age = st.number_input("Âge", value=user.get('age', 25), min_value=18, max_value=100)
                profession = st.text_input("Profession", value=user.get('profession', ''))
            
            submitted = st.form_submit_button("Mettre à jour")
            if submitted:
                st.success("Informations mises à jour avec succès !")
    
    with tab2:
        st.markdown("## Préférences de recherche")
        
        prefs = st.session_state.db.get_user_preferences(user['id']) or {}
        
        with st.form("preferences_form"):
            col1, col2 = st.columns(2)
            with col1:
                budget_min = st.number_input("Budget minimum (€)", 
                                           value=prefs.get('budget_min', 100000), 
                                           min_value=0, step=10000)
                budget_max = st.number_input("Budget maximum (€)", 
                                           value=prefs.get('budget_max', 500000), 
                                           min_value=0, step=10000)
                property_type = st.selectbox("Type de bien", 
                                           ["Appartement", "Maison", "Studio", "Loft"],
                                           index=0 if not prefs.get('property_type') else 
                                           ["Appartement", "Maison", "Studio", "Loft"].index(prefs.get('property_type', 'Appartement')))
            
            with col2:
                bedrooms = st.number_input("Nombre de chambres", 
                                         value=prefs.get('bedrooms', 2), 
                                         min_value=1, max_value=10)
                bathrooms = st.number_input("Nombre de salles de bain", 
                                          value=prefs.get('bathrooms', 1), 
                                          min_value=1, max_value=5)
                surface_min = st.number_input("Surface minimale (m²)", 
                                            value=prefs.get('surface_min', 50), 
                                            min_value=10, step=10)
            
            location = st.text_input("Localisation préférée", 
                                   value=prefs.get('location', ''))
            
            submitted = st.form_submit_button("Sauvegarder les préférences")
            if submitted:
                preferences = {
                    'budget_min': budget_min,
                    'budget_max': budget_max,
                    'property_type': property_type,
                    'bedrooms': bedrooms,
                    'bathrooms': bathrooms,
                    'surface_min': surface_min,
                    'location': location
                }
                st.session_state.db.save_user_preferences(user['id'], preferences)
                st.success("Préférences sauvegardées avec succès !")
    
    with tab3:
        show_ai_agent()

def show_ai_agent():
    """Agent IA pour enrichir les informations utilisateur"""
    st.markdown("## 🤖 Agent IA - Assistant personnel")
    
    # Initialiser l'historique de chat s'il n'existe pas
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", "content": "Bonjour ! Je suis votre assistant IA personnel. Je peux vous aider à affiner vos critères de recherche immobilière. Que souhaitez-vous savoir ou améliorer dans votre profil ?"}
        ]
    
    # Affichage de l'historique de chat
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="user-message">
                    {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="ai-message">
                    {message["content"]}
                </div>
                """, unsafe_allow_html=True)
    
    # Zone de saisie pour nouveau message
    user_input = st.text_input("Posez votre question...", key="ai_input")
    
    if st.button("Envoyer") and user_input:
        # Ajouter le message utilisateur
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Simuler une réponse de l'IA (en production, vous utiliseriez une vraie API IA)
        ai_response = generate_ai_response(user_input, st.session_state.user)
        st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
        
        st.rerun()
    
    # Questions suggérées
    st.markdown("### Questions suggérées :")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Aidez-moi à définir mon budget"):
            st.session_state.chat_history.append({"role": "user", "content": "Aidez-moi à définir mon budget"})
            ai_response = "Pour vous aider à définir votre budget, j'ai besoin de quelques informations : Quel est votre revenu mensuel net ? Avez-vous des économies pour l'apport ? Quel est votre situation familiale ?"
            st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
            st.rerun()
        
        if st.button("Quels quartiers me recommandez-vous ?"):
            st.session_state.chat_history.append({"role": "user", "content": "Quels quartiers me recommandez-vous ?"})
            ai_response = "Basé sur votre profil, je peux vous recommander des quartiers. Pouvez-vous me dire : Travaillez-vous dans un lieu spécifique ? Préférez-vous le calme ou l'animation ? Avez-vous des enfants scolarisés ?"
            st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
            st.rerun()
    
    with col2:
        if st.button("Optimiser mes critères de recherche"):
            st.session_state.chat_history.append({"role": "user", "content": "Optimiser mes critères de recherche"})
            prefs = st.session_state.db.get_user_preferences(st.session_state.user['id']) or {}
            budget_info = f"{prefs.get('budget_min', 'N/A')}€ et {prefs.get('budget_max', 'N/A')}€" if prefs.get('budget_min') else "non défini"
            ai_response = f"Analysons vos critères actuels. Votre budget est {budget_info}. Voulez-vous que j'analyse le marché pour optimiser vos chances de trouver le bien idéal ?"
            st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
            st.rerun()
        
        if st.button("Analyser le marché immobilier"):
            st.session_state.chat_history.append({"role": "user", "content": "Analyser le marché immobilier"})
            ai_response = "D'après les données récentes, le marché immobilier dans votre zone de recherche présente les tendances suivantes : prix en hausse de 3% sur l'année, délai moyen de vente de 45 jours. Souhaitez-vous des conseils personnalisés ?"
            st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
            st.rerun()

def generate_ai_response(user_input: str, user: Dict) -> str:
    """Génère une réponse de l'IA basée sur l'input utilisateur"""
    # Simulation d'une réponse IA (en production, utilisez OpenAI, Claude, etc.)
    user_input_lower = user_input.lower()
    
    if "budget" in user_input_lower:
        return f"Bonjour {user.get('first_name', '')} ! Pour définir votre budget optimal, je recommande de ne pas dépasser 30% de vos revenus mensuels en remboursement. Avec votre profil ({user.get('profession', 'professionnel')}), voulez-vous que nous calculions ensemble votre capacité d'emprunt ?"
    
    elif "quartier" in user_input_lower or "zone" in user_input_lower:
        return "Basé sur vos préférences, je peux analyser les quartiers qui correspondent à vos critères. Privilégiez-vous la proximité des transports, des écoles, ou des commerces ? Votre lieu de travail influence-t-il votre choix ?"
    
    elif "marché" in user_input_lower or "prix" in user_input_lower:
        return "Le marché immobilier évolue constamment. Dans votre zone de recherche, les prix ont évolué de +2.5% ces 6 derniers mois. Je peux vous alerter sur les bonnes opportunités si vous le souhaitez."
    
    else:
        return "Je comprends votre question. Basé sur votre profil, je peux vous donner des conseils personnalisés pour votre recherche immobilière. Pouvez-vous être plus spécifique sur ce que vous souhaitez améliorer ?"

def show_search_page():
    """Page de recherche avancée avec carte interactive"""
    st.markdown("# 🔍 Recherche avancée")
    
    # Formulaire de recherche
    with st.form("advanced_search"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            location = st.text_input("Localisation", placeholder="Paris, Lyon, Marseille...")
            property_type = st.selectbox("Type de bien", ["Tous", "Appartement", "Maison", "Studio", "Loft"])
            bedrooms = st.selectbox("Chambres", ["Indifférent", "1", "2", "3", "4", "5+"])
        
        with col2:
            budget_min = st.number_input("Budget min (€)", min_value=0, step=10000, value=100000)
            budget_max = st.number_input("Budget max (€)", min_value=0, step=10000, value=500000)
            surface_min = st.number_input("Surface min (m²)", min_value=0, step=10, value=50)
        
        with col3:
            amenities = st.multiselect("Équipements souhaités", 
                                     ["Parking", "Balcon", "Terrasse", "Ascenseur", "Cave", "Jardin"])
            transport = st.selectbox("Proximité transports", ["Indifférent", "Métro", "RER", "Bus", "Tramway"])
            
        submitted = st.form_submit_button("🔍 Lancer la recherche", use_container_width=True)
    
    if submitted:
        # Simulation de données de recherche
        results = generate_mock_properties(location, property_type, budget_min, budget_max)
        
        if results:
            st.success(f"✅ {len(results)} biens trouvés correspondant à vos critères")
            
            # Onglets pour afficher les résultats
            tab1, tab2 = st.tabs(["📋 Liste des biens", "🗺️ Carte interactive"])
            
            with tab1:
                show_property_list(results)
            
            with tab2:
                show_interactive_map(results)
        else:
            st.warning("Aucun bien ne correspond à vos critères. Essayez d'élargir votre recherche.")

def generate_mock_properties(location, property_type, budget_min, budget_max):
    """Génère des données fictives de propriétés"""
    import random
    
    properties = []
    locations_coords = {
        "paris": [(48.8566, 2.3522), (48.8584, 2.2945), (48.8738, 2.2950)],
        "lyon": [(45.7640, 4.8357), (45.7489, 4.8467), (45.7797, 4.8278)],
        "marseille": [(43.2965, 5.3698), (43.3102, 5.3781), (43.2841, 5.3656)]
    }
    
    base_coords = locations_coords.get(location.lower(), [(48.8566, 2.3522)])
    
    for i in range(random.randint(5, 15)):
        coord = random.choice(base_coords)
        price = random.randint(budget_min, min(budget_max, budget_min + 200000))
        
        property_data = {
            'id': i + 1,
            'title': f"Bel appartement {random.randint(2,4)} pièces - {location}",
            'price': price,
            'property_type': random.choice(["Appartement", "Maison", "Studio"]),
            'bedrooms': random.randint(1, 4),
            'bathrooms': random.randint(1, 2),
            'surface': random.randint(40, 120),
            'location': f"{location} - {random.choice(['Centre', 'Nord', 'Sud', 'Est', 'Ouest'])}",
            'latitude': coord[0] + random.uniform(-0.05, 0.05),
            'longitude': coord[1] + random.uniform(-0.05, 0.05),
            'description': f"Magnifique {property_data.get('property_type', 'bien')} de {random.randint(40,120)}m² dans un quartier recherché.",
            'features': random.sample(["Parking", "Balcon", "Terrasse", "Ascenseur", "Cave"], random.randint(1,3))
        }
        properties.append(property_data)
    
    return properties

def show_property_list(properties):
    """Affiche la liste des propriétés"""
    for prop in properties:
        with st.container():
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.markdown(f"### {prop['title']}")
                st.markdown(f"📍 {prop['location']}")
                st.markdown(f"📐 {prop['surface']}m² • 🛏️ {prop['bedrooms']} ch. • 🚿 {prop['bathrooms']} sdb")
            
            with col2:
                st.markdown(f"### 💰 {prop['price']:,}€")
                if prop.get('features'):
                    st.markdown("🏷️ " + " • ".join(prop['features']))
                st.markdown(prop['description'])
            
            with col3:
                if st.button(f"Voir détails", key=f"detail_{prop['id']}"):
                    show_property_details(prop)
                
                if st.button(f"❤️ Favoris", key=f"fav_{prop['id']}"):
                    st.success("Ajouté aux favoris !")
            
            st.divider()

def show_property_details(property_data):
    """Affiche les détails d'une propriété dans un modal"""
    with st.expander(f"Détails - {property_data['title']}", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Informations générales")
            st.markdown(f"**Prix :** {property_data['price']:,}€")
            st.markdown(f"**Type :** {property_data['property_type']}")
            st.markdown(f"**Surface :** {property_data['surface']}m²")
            st.markdown(f"**Chambres :** {property_data['bedrooms']}")
            st.markdown(f"**Salles de bain :** {property_data['bathrooms']}")
        
        with col2:
            st.markdown("### Localisation")
            st.markdown(f"**Adresse :** {property_data['location']}")
            st.markdown(f"**Coordonnées :** {property_data['latitude']:.4f}, {property_data['longitude']:.4f}")
            
            if property_data.get('features'):
                st.markdown("### Équipements")
                for feature in property_data['features']:
                    st.markdown(f"✅ {feature}")

def show_interactive_map(properties):
    """Affiche une carte interactive avec les propriétés"""
    if not properties:
        st.warning("Aucune propriété à afficher sur la carte")
        return
    
    # Centre de la carte basé sur la première propriété
    center_lat = properties[0]['latitude']
    center_lon = properties[0]['longitude']
    
    # Création de la carte avec Folium
    m = folium.Map(location=[center_lat, center_lon], zoom_start=12)
    
    # Ajout des marqueurs pour chaque propriété
    for prop in properties:
        popup_text = f"""
        <b>{prop['title']}</b><br>
        💰 {prop['price']:,}€<br>
        📐 {prop['surface']}m²<br>
        🛏️ {prop['bedrooms']} chambres<br>
        📍 {prop['location']}
        """
        
        folium.Marker(
            location=[prop['latitude'], prop['longitude']],
            popup=folium.Popup(popup_text, max_width=300),
            tooltip=f"{prop['price']:,}€",
            icon=folium.Icon(color='orange', icon='home')
        ).add_to(m)
    
    # Affichage de la carte
    map_data = st_folium(m, width=700, height=500, returned_objects=["last_object_clicked_popup"])
    
    # Affichage des détails si un marqueur est cliqué
    if map_data['last_object_clicked_popup']:
        clicked_property = None
        # Ici, vous pourriez identifier la propriété cliquée et afficher ses détails
        st.info("Propriété sélectionnée sur la carte")

def show_recommendations_page():
    """Page des recommandations avec radar des critères"""
    st.markdown("# 🎯 Recommandations personnalisées")
    
    user_prefs = st.session_state.db.get_user_preferences(st.session_state.user['id'])
    
    if not user_prefs:
        st.warning("⚠️ Veuillez d'abord renseigner vos préférences dans la section 'Mes informations'")
        return
    
    # Radar des critères
    st.markdown("## 📊 Analyse de vos critères")
    
    # Données pour le radar chart
    criteria = ['Budget', 'Localisation', 'Surface', 'Transport', 'Commodités', 'Environnement']
    values = [85, 75, 90, 60, 70, 80]  # Scores basés sur les préférences utilisateur
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=criteria,
        fill='toself',
        name='Vos critères',
        line_color=COLORS['primary']
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=True,
        title="Radar de vos critères de recherche"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Recommandations basées sur le profil
    st.markdown("## 🏠 Biens recommandés pour vous")
    
    recommended_properties = generate_recommendations(user_prefs)
    
    for i, prop in enumerate(recommended_properties[:5]):  # Top 5 recommandations
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                st.markdown(f"### {prop['title']}")
                st.markdown(f"📍 {prop['location']}")
                
                # Score de compatibilité
                compatibility_score = prop.get('compatibility_score', 85)
                st.progress(compatibility_score / 100, f"Compatibilité: {compatibility_score}%")
                
                # Raisons de la recommandation
                reasons = prop.get('reasons', ['Prix dans votre budget', 'Localisation préférée'])
                st.markdown("**Pourquoi ce bien :**")
                for reason in reasons:
                    st.markdown(f"✅ {reason}")
            
            with col2:
                st.markdown(f"### 💰 {prop['price']:,}€")
                st.markdown(f"📐 {prop['surface']}m² • 🛏️ {prop['bedrooms']} ch.")
                
                # Graphique de comparaison prix/m²
                price_per_sqm = prop['price'] / prop['surface']
                market_avg = 5500  # Prix moyen du marché au m²
                
                fig_bar = go.Figure()
                fig_bar.add_trace(go.Bar(
                    x=['Ce bien', 'Marché'],
                    y=[price_per_sqm, market_avg],
                    marker_color=[COLORS['primary'], COLORS['light']]
                ))
                fig_bar.update_layout(
                    title="Prix au m²",
                    yaxis_title="€/m²",
                    height=200,
                    showlegend=False
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            
            with col3:
                if st.button(f"Voir détails", key=f"rec_detail_{i}"):
                    show_property_details(prop)
                
                if st.button(f"❤️ Favoris", key=f"rec_fav_{i}"):
                    st.success("Ajouté aux favoris !")
                
                if st.button(f"📞 Contacter", key=f"rec_contact_{i}"):
                    st.info("Agent contacté !")
            
            st.divider()

def generate_recommendations(user_prefs):
    """Génère des recommandations basées sur les préférences utilisateur"""
    import random
    
    recommendations = []
    
    for i in range(10):
        # Génère des biens qui correspondent mieux aux préférences
        price = random.randint(
            max(user_prefs.get('budget_min', 100000) - 50000, 50000),
            user_prefs.get('budget_max', 500000)
        )
        
        prop = {
            'id': i + 100,
            'title': f"Recommandation {i+1} - {user_prefs.get('property_type', 'Appartement')}",
            'price': price,
            'property_type': user_prefs.get('property_type', 'Appartement'),
            'bedrooms': user_prefs.get('bedrooms', 2),
            'bathrooms': user_prefs.get('bathrooms', 1),
            'surface': random.randint(user_prefs.get('surface_min', 50), user_prefs.get('surface_min', 50) + 50),
            'location': user_prefs.get('location', 'Paris'),
            'latitude': 48.8566 + random.uniform(-0.1, 0.1),
            'longitude': 2.3522 + random.uniform(-0.1, 0.1),
            'compatibility_score': random.randint(75, 95),
            'reasons': random.sample([
                'Prix dans votre budget',
                'Correspond à vos critères de surface',
                'Localisation préférée',
                'Nombre de chambres idéal',
                'Proche des transports',
                'Quartier recherché',
                'Bon rapport qualité-prix'
            ], random.randint(2, 4))
        }
        recommendations.append(prop)
    
    # Trier par score de compatibilité
    return sorted(recommendations, key=lambda x: x['compatibility_score'], reverse=True)

def show_dashboard():
    """Tableau de bord principal"""
    st.markdown(f"# 👋 Bienvenue, {st.session_state.user.get('first_name', 'Utilisateur')} !")
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Recherches sauvegardées", "12", "2")
    
    with col2:
        st.metric("Biens en favoris", "8", "3")
    
    with col3:
        st.metric("Alertes actives", "5", "1")
    
    with col4:
        st.metric("Visites planifiées", "3", "1")
    
    # Graphique d'évolution des prix
    st.markdown("## 📈 Évolution des prix dans vos zones de recherche")
    
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='M')
    prices = [4500 + i*50 + random.randint(-100, 100) for i in range(len(dates))]
    
    fig = px.line(
        x=dates, 
        y=prices,
        title="Prix moyen au m² dans vos zones de recherche",
        labels={'x': 'Mois', 'y': 'Prix au m² (€)'}
    )
    fig.update_traces(line_color=COLORS['primary'])
    st.plotly_chart(fig, use_container_width=True)
    
    # Alertes et notifications
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("## 🔔 Alertes récentes")
        
        alerts = [
            {"type": "success", "message": "Nouveau bien correspondant à vos critères!", "time": "Il y a 2h"},
            {"type": "info", "message": "Baisse de prix sur un bien en favori", "time": "Il y a 1 jour"},
            {"type": "warning", "message": "Visite programmée demain à 14h", "time": "Il y a 2 jours"}
        ]
        
        for alert in alerts:
            icon = "🟢" if alert["type"] == "success" else "🔵" if alert["type"] == "info" else "🟡"
            st.markdown(f"{icon} **{alert['message']}** - *{alert['time']}*")
    
    with col2:
        st.markdown("## 📊 Vos statistiques")
        
        # Graphique en camembert des types de biens recherchés
        labels = ['Appartements', 'Maisons', 'Studios']
        values = [60, 30, 10]
        
        fig_pie = px.pie(
            values=values, 
            names=labels,
            title="Répartition de vos recherches",
            color_discrete_sequence=[COLORS['primary'], COLORS['secondary'], COLORS['accent']]
        )
        st.plotly_chart(fig_pie, use_container_width=True)

# ================================
# INTERFACE PRINCIPALE
# ================================

def main():
    """Fonction principale de l'application"""
    # Configuration de la page
    st.set_page_config(
        page_title="ImoMatch - Votre assistant immobilier IA",
        page_icon="🏠",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialisation des variables de session
    init_session_state()
    
    # Application du thème
    apply_theme()
    
    # Interface de contrôle en haut
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col2:
        # Sélecteur de langue
        languages = {'fr': '🇫🇷 Français', 'en': '🇬🇧 English'}
        selected_lang = st.selectbox(
            "",
            options=list(languages.keys()),
            format_func=lambda x: languages[x],
            index=0 if st.session_state.language == 'fr' else 1,
            key="lang_selector"
        )
        
        if selected_lang != st.session_state.language:
            st.session_state.language = selected_lang
            st.rerun()
    
    with col3:
        # Sélecteur de thème
        theme_options = {'light': '☀️ Clair', 'dark': '🌙 Sombre'}
        selected_theme = st.selectbox(
            "",
            options=list(theme_options.keys()),
            format_func=lambda x: theme_options[x],
            index=0 if st.session_state.theme == 'light' else 1,
            key="theme_selector"
        )
        
        if selected_theme != st.session_state.theme:
            st.session_state.theme = selected_theme
            st.rerun()
    
    # Navigation principale
    if not st.session_state.authenticated:
        # Pages pour utilisateurs non connectés
        tab1, tab2 = st.tabs([get_text('welcome'), get_text('login')])
        
        with tab1:
            show_landing_page()
        
        with tab2:
            show_login_page()
    
    else:
        # Interface pour utilisateurs connectés
        with st.sidebar:
            create_logo()
            
            # Menu de navigation
            menu_options = [
                get_text('dashboard'),
                get_text('my_info'),
                get_text('search'),
                get_text('recommendations')
            ]
            
            selected_page = st.selectbox("Navigation", menu_options)
            
            # Informations utilisateur
            st.markdown("---")
            st.markdown(f"**{st.session_state.user.get('first_name', '')} {st.session_state.user.get('last_name', '')}**")
            st.markdown(f"Plan: **{st.session_state.user.get('plan', 'free').title()}**")
            
            if st.button(get_text('logout')):
                st.session_state.authenticated = False
                st.session_state.user = None
                st.rerun()
        
        # Affichage de la page sélectionnée
        if selected_page == get_text('dashboard'):
            show_dashboard()
        elif selected_page == get_text('my_info'):
            show_my_info_page()
        elif selected_page == get_text('search'):
            show_search_page()
        elif selected_page == get_text('recommendations'):
            show_recommendations_page()

if __name__ == "__main__":
    main()
