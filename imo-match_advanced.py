import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sqlite3
import hashlib
import json
from typing import Dict, List, Optional, Tuple
import openai
import folium
from streamlit_folium import st_folium

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
            ai_response = "Analysons vos critères actuels. Je vois que vous cherchez un bien entre " + str(st.session_state.db.get_user_preferences(st.session_state.user['id']) or {}).get('budget_min', 'N/A') + "€ et " + str(st.session_
