import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import hashlib
import json
import time
from typing import Dict, List, Optional, Tuple
import folium
from streamlit_folium import st_folium
import numpy as np
from dataclasses import dataclass
import re

# Configuration de la page
st.set_page_config(
    page_title="ImoMatch - Trouvez votre bien immobilier idéal",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Classes et structures de données
@dataclass
class UserProfile:
    user_id: str
    email: str
    nom: str
    prenom: str
    telephone: str
    profession: str
    situation_familiale: str
    revenus: float
    apport: float
    credits_en_cours: float
    localisation_actuelle: str
    localisation_souhaitee: str
    type_bien: str
    budget_min: float
    budget_max: float
    surface_min: float
    nb_pieces_min: int
    criteres_specifiques: Dict
    date_creation: datetime
    plan: str = "Free"
    plan_expiration: Optional[datetime] = None

@dataclass
class Property:
    id: str
    titre: str
    prix: float
    surface: float
    nb_pieces: int
    localisation: str
    lat: float
    lng: float
    type_bien: str
    description: str
    caracteristiques: Dict
    photos: List[str]
    date_ajout: datetime

# Configuration des thèmes
THEMES = {
    "light": {
        "background_color": "#FFFFFF",
        "text_color": "#000000",
        "primary_color": "#FF6B35",
        "secondary_color": "#F7931E",
        "accent_color": "#2E86AB",
        "card_background": "#F8F9FA",
        "sidebar_background": "#FFFFFF"
    },
    "dark": {
        "background_color": "#0E1117",
        "text_color": "#FAFAFA",
        "primary_color": "#FF6B35",
        "secondary_color": "#F7931E",
        "accent_color": "#64B5F6",
        "card_background": "#1E1E1E",
        "sidebar_background": "#262730"
    }
}

# Configuration des langues
TRANSLATIONS = {
    "fr": {
        "app_title": "ImoMatch - Trouvez votre bien immobilier idéal",
        "welcome": "Bienvenue",
        "login": "Connexion",
        "register": "S'inscrire",
        "email": "Email",
        "password": "Mot de passe",
        "name": "Nom",
        "firstname": "Prénom",
        "phone": "Téléphone",
        "profession": "Profession",
        "family_situation": "Situation familiale",
        "income": "Revenus mensuels (€)",
        "contribution": "Apport personnel (€)",
        "current_credits": "Crédits en cours (€)",
        "current_location": "Localisation actuelle",
        "desired_location": "Localisation souhaitée",
        "property_type": "Type de bien",
        "min_budget": "Budget minimum (€)",
        "max_budget": "Budget maximum (€)",
        "min_surface": "Surface minimum (m²)",
        "min_rooms": "Nombre de pièces minimum",
        "dashboard": "Tableau de bord",
        "my_info": "Mes informations",
        "recommendations": "Recommandations",
        "advanced_search": "Recherche avancée",
        "agent_ai": "Agent AI",
        "logout": "Déconnexion",
        "free_plan": "Plan Gratuit",
        "premium_plan": "Plan Premium",
        "professional_plan": "Plan Professionnel",
        "start_trial": "Essai 14 jours gratuit",
        "value_proposition": "La solution IA qui révolutionne votre recherche immobilière",
        "contact_info": "Informations de contact"
    },
    "en": {
        "app_title": "ImoMatch - Find your ideal property",
        "welcome": "Welcome",
        "login": "Login",
        "register": "Register",
        "email": "Email",
        "password": "Password",
        "name": "Last Name",
        "firstname": "First Name",
        "phone": "Phone",
        "profession": "Profession",
        "family_situation": "Family Situation",
        "income": "Monthly Income (€)",
        "contribution": "Personal Contribution (€)",
        "current_credits": "Current Credits (€)",
        "current_location": "Current Location",
        "desired_location": "Desired Location",
        "property_type": "Property Type",
        "min_budget": "Minimum Budget (€)",
        "max_budget": "Maximum Budget (€)",
        "min_surface": "Minimum Surface (m²)",
        "min_rooms": "Minimum Number of Rooms",
        "dashboard": "Dashboard",
        "my_info": "My Information",
        "recommendations": "Recommendations",
        "advanced_search": "Advanced Search",
        "agent_ai": "AI Agent",
        "logout": "Logout",
        "free_plan": "Free Plan",
        "premium_plan": "Premium Plan",
        "professional_plan": "Professional Plan",
        "start_trial": "Start 14-day free trial",
        "value_proposition": "The AI solution that revolutionizes your real estate search",
        "contact_info": "Contact Information"
    }
}

class DatabaseManager:
    """Gestionnaire de base de données SQLite"""
    
    def __init__(self, db_path: str = "imomatch.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)
    
    def init_database(self):
        """Initialise les tables de la base de données"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Table utilisateurs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                nom TEXT,
                prenom TEXT,
                telephone TEXT,
                profession TEXT,
                situation_familiale TEXT,
                revenus REAL,
                apport REAL,
                credits_en_cours REAL,
                localisation_actuelle TEXT,
                localisation_souhaitee TEXT,
                type_bien TEXT,
                budget_min REAL,
                budget_max REAL,
                surface_min REAL,
                nb_pieces_min INTEGER,
                criteres_specifiques TEXT,
                plan TEXT DEFAULT 'Free',
                plan_expiration TEXT,
                date_creation TEXT,
                preferences TEXT
            )
        ''')
        
        # Table propriétés
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS properties (
                id TEXT PRIMARY KEY,
                titre TEXT,
                prix REAL,
                surface REAL,
                nb_pieces INTEGER,
                localisation TEXT,
                lat REAL,
                lng REAL,
                type_bien TEXT,
                description TEXT,
                caracteristiques TEXT,
                photos TEXT,
                date_ajout TEXT
            )
        ''')
        
        # Table sessions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT,
                created_at TEXT,
                expires_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Insérer des données de test si la base est vide
        self.insert_sample_data()
    
    def insert_sample_data(self):
        """Insère des données d'exemple"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Vérifier si des propriétés existent déjà
        cursor.execute("SELECT COUNT(*) FROM properties")
        if cursor.fetchone()[0] == 0:
            sample_properties = [
                ('prop_1', 'Appartement T3 Centre Ville', 250000, 65, 3, 'Paris 11ème', 48.8566, 2.3522, 'Appartement', 
                 'Bel appartement rénové en centre ville', '{"balcon": true, "parking": false, "ascenseur": true}', 
                 '[]', datetime.now().isoformat()),
                ('prop_2', 'Maison avec Jardin', 380000, 95, 4, 'Boulogne-Billancourt', 48.8414, 2.2403, 'Maison', 
                 'Maison familiale avec jardin', '{"jardin": true, "garage": true, "cave": true}', 
                 '[]', datetime.now().isoformat()),
                ('prop_3', 'Studio Moderne', 180000, 25, 1, 'Lyon 2ème', 45.7640, 4.8357, 'Studio', 
                 'Studio moderne entièrement équipé', '{"meuble": true, "cuisine_equipee": true}', 
                 '[]', datetime.now().isoformat())
            ]
            
            cursor.executemany('''
                INSERT INTO properties (id, titre, prix, surface, nb_pieces, localisation, lat, lng, 
                                      type_bien, description, caracteristiques, photos, date_ajout)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', sample_properties)
            
            conn.commit()
        
        conn.close()
    
    def create_user(self, user_data: Dict) -> bool:
        """Crée un nouvel utilisateur"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO users (user_id, email, password_hash, nom, prenom, telephone,
                                 profession, situation_familiale, revenus, apport, credits_en_cours,
                                 localisation_actuelle, localisation_souhaitee, type_bien,
                                 budget_min, budget_max, surface_min, nb_pieces_min,
                                 criteres_specifiques, plan, date_creation)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_data['user_id'], user_data['email'], user_data['password_hash'],
                user_data.get('nom', ''), user_data.get('prenom', ''), user_data.get('telephone', ''),
                user_data.get('profession', ''), user_data.get('situation_familiale', ''),
                user_data.get('revenus', 0), user_data.get('apport', 0), user_data.get('credits_en_cours', 0),
                user_data.get('localisation_actuelle', ''), user_data.get('localisation_souhaitee', ''),
                user_data.get('type_bien', ''), user_data.get('budget_min', 0), user_data.get('budget_max', 0),
                user_data.get('surface_min', 0), user_data.get('nb_pieces_min', 1),
                json.dumps(user_data.get('criteres_specifiques', {})), user_data.get('plan', 'Free'),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Erreur lors de la création de l'utilisateur: {e}")
            return False
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Récupère un utilisateur par email"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, row))
        return None
    
    def update_user(self, user_id: str, user_data: Dict) -> bool:
        """Met à jour les informations d'un utilisateur"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            set_clause = ", ".join([f"{key} = ?" for key in user_data.keys()])
            values = list(user_data.values()) + [user_id]
            
            cursor.execute(f"UPDATE users SET {set_clause} WHERE user_id = ?", values)
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Erreur lors de la mise à jour: {e}")
            return False
    
    def get_properties(self, filters: Dict = None) -> List[Dict]:
        """Récupère les propriétés avec filtres optionnels"""
        conn = self.get_connection()
        
        query = "SELECT * FROM properties"
        params = []
        
        if filters:
            conditions = []
            if 'prix_min' in filters and filters['prix_min']:
                conditions.append("prix >= ?")
                params.append(filters['prix_min'])
            if 'prix_max' in filters and filters['prix_max']:
                conditions.append("prix <= ?")
                params.append(filters['prix_max'])
            if 'surface_min' in filters and filters['surface_min']:
                conditions.append("surface >= ?")
                params.append(filters['surface_min'])
            if 'nb_pieces' in filters and filters['nb_pieces']:
                conditions.append("nb_pieces >= ?")
                params.append(filters['nb_pieces'])
            if 'type_bien' in filters and filters['type_bien']:
                conditions.append("type_bien = ?")
                params.append(filters['type_bien'])
            if 'localisation' in filters and filters['localisation']:
                conditions.append("localisation LIKE ?")
                params.append(f"%{filters['localisation']}%")
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        return df.to_dict('records')

class ThemeManager:
    """Gestionnaire des thèmes"""
    
    @staticmethod
    def apply_theme(theme_name: str):
        """Applique un thème à l'interface"""
        theme = THEMES.get(theme_name, THEMES["light"])
        
        st.markdown(f"""
        <style>
            .stApp {{
                background-color: {theme['background_color']};
                color: {theme['text_color']};
            }}
            
            .main-header {{
                background: linear-gradient(90deg, {theme['primary_color']}, {theme['secondary_color']});
                padding: 1rem;
                border-radius: 10px;
                margin-bottom: 2rem;
                text-align: center;
            }}
            
            .main-header h1 {{
                color: white !important;
                margin: 0;
                font-size: 2.5rem;
                font-weight: bold;
            }}
            
            .value-card {{
                background: {theme['card_background']};
                padding: 1.5rem;
                border-radius: 15px;
                margin: 1rem 0;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                border-left: 4px solid {theme['primary_color']};
            }}
            
            .metric-card {{
                background: {theme['card_background']};
                padding: 1rem;
                border-radius: 10px;
                text-align: center;
                border: 1px solid {theme['primary_color']};
            }}
            
            .plan-card {{
                background: {theme['card_background']};
                border: 2px solid {theme['primary_color']};
                border-radius: 15px;
                padding: 1.5rem;
                margin: 1rem;
                text-align: center;
                transition: transform 0.3s ease;
            }}
            
            .plan-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
            }}
            
            .sidebar .sidebar-content {{
                background-color: {theme['sidebar_background']};
            }}
            
            .stButton > button {{
                background: linear-gradient(90deg, {theme['primary_color']}, {theme['secondary_color']});
                color: white;
                border: none;
                border-radius: 25px;
                padding: 0.5rem 1.5rem;
                font-weight: bold;
                transition: all 0.3s ease;
            }}
            
            .stButton > button:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(255, 107, 53, 0.4);
            }}
            
            .property-card {{
                background: {theme['card_background']};
                border-radius: 15px;
                padding: 1rem;
                margin: 1rem 0;
                border-left: 4px solid {theme['primary_color']};
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            
            .agent-response {{
                background: linear-gradient(135deg, {theme['primary_color']}22, {theme['secondary_color']}22);
                border-radius: 15px;
                padding: 1rem;
                margin: 1rem 0;
                border-left: 4px solid {theme['primary_color']};
                color: {theme['text_color']} !important;
            }}
            
            .logo-container {{
                text-align: center;
                padding: 2rem 0;
            }}
            
            .logo-text {{
                font-size: 3rem;
                font-weight: bold;
                background: linear-gradient(90deg, {theme['primary_color']}, {theme['secondary_color']});
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}
        </style>
        """, unsafe_allow_html=True)

class AuthManager:
    """Gestionnaire d'authentification"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash un mot de passe"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, user_data: Dict) -> Tuple[bool, str]:
        """Enregistre un nouvel utilisateur"""
        if self.db.get_user_by_email(user_data['email']):
            return False, "Un compte avec cet email existe déjà"
        
        user_data['user_id'] = f"user_{int(time.time())}"
        user_data['password_hash'] = self.hash_password(user_data['password'])
        del user_data['password']  # Supprimer le mot de passe en clair
        
        if self.db.create_user(user_data):
            return True, "Compte créé avec succès"
        else:
            return False, "Erreur lors de la création du compte"
    
    def login_user(self, email: str, password: str) -> Tuple[bool, Optional[Dict]]:
        """Connecte un utilisateur"""
        user = self.db.get_user_by_email(email)
        if user and user['password_hash'] == self.hash_password(password):
            return True, user
        return False, None

class AIAgent:
    """Agent IA pour enrichir les informations utilisateur"""
    
    @staticmethod
    def get_completion_suggestions(user_profile: Dict, missing_fields: List[str]) -> List[str]:
        """Génère des suggestions pour compléter le profil"""
        suggestions = []
        
        if 'profession' in missing_fields:
            suggestions.append("Quelle est votre profession actuelle ? Cela nous aide à mieux évaluer votre capacité d'emprunt.")
        
        if 'revenus' in missing_fields:
            suggestions.append("Quels sont vos revenus mensuels nets ? Cette information est cruciale pour déterminer votre budget.")
        
        if 'apport' in missing_fields:
            suggestions.append("Quel apport personnel pouvez-vous mobiliser pour votre projet immobilier ?")
        
        if 'localisation_souhaitee' in missing_fields:
            suggestions.append("Dans quelle zone géographique souhaitez-vous rechercher ? Précisez la ville ou l'arrondissement.")
        
        if 'type_bien' in missing_fields:
            suggestions.append("Quel type de bien recherchez-vous ? Appartement, maison, studio... ?")
        
        return suggestions
    
    @staticmethod
    def analyze_profile_completion(user_profile: Dict) -> Dict:
        """Analyse le niveau de complétude du profil"""
        required_fields = ['profession', 'revenus', 'apport', 'localisation_souhaitee', 'type_bien', 'budget_max']
        completed_fields = [field for field in required_fields if user_profile.get(field)]
        completion_rate = len(completed_fields) / len(required_fields) * 100
        
        missing_fields = [field for field in required_fields if not user_profile.get(field)]
        
        return {
            'completion_rate': completion_rate,
            'missing_fields': missing_fields,
            'completed_fields': completed_fields
        }
    
    @staticmethod
    def generate_recommendations(user_profile: Dict, properties: List[Dict]) -> List[Dict]:
        """Génère des recommandations basées sur le profil utilisateur"""
        if not user_profile.get('budget_max') or not properties:
            return []
        
        scored_properties = []
        for prop in properties:
            score = 0
            reasons = []
            
            # Score basé sur le budget
            if prop['prix'] <= user_profile.get('budget_max', 0):
                score += 30
                reasons.append("Dans votre budget")
            elif prop['prix'] <= user_profile.get('budget_max', 0) * 1.1:
                score += 15
                reasons.append("Légèrement au-dessus du budget")
            
            # Score basé sur le type de bien
            if prop['type_bien'] == user_profile.get('type_bien'):
                score += 25
                reasons.append("Correspond à votre type de bien recherché")
            
            # Score basé sur la surface
            if prop['surface'] >= user_profile.get('surface_min', 0):
                score += 20
                reasons.append("Surface suffisante")
            
            # Score basé sur le nombre de pièces
            if prop['nb_pieces'] >= user_profile.get('nb_pieces_min', 1):
                score += 15
                reasons.append("Nombre de pièces adapté")
            
            # Score basé sur la localisation
            if user_profile.get('localisation_souhaitee') and user_profile['localisation_souhaitee'].lower() in prop['localisation'].lower():
                score += 30
                reasons.append("Localisation souhaitée")
            
            if score > 0:
                scored_properties.append({
                    **prop,
                    'match_score': score,
                    'match_reasons': reasons
                })
        
        # Trier par score décroissant
        scored_properties.sort(key=lambda x: x['match_score'], reverse=True)
        return scored_properties[:10]  # Top 10

def init_session_state():
    """Initialise les variables de session"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'
    if 'language' not in st.session_state:
        st.session_state.language = 'fr'
    if 'page' not in st.session_state:
        st.session_state.page = 'home'

def get_text(key: str) -> str:
    """Récupère le texte traduit"""
    return TRANSLATIONS[st.session_state.language].get(key, key)

def render_header():
    """Affiche l'en-tête de l'application"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("🌓", help="Changer de thème"):
            st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="logo-container">
            <div class="logo-text">🏠 ImoMatch</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        language = st.selectbox("🌐", ["fr", "en"], 
                               index=0 if st.session_state.language == 'fr' else 1,
                               key="language_selector")
        if language != st.session_state.language:
            st.session_state.language = language
            st.rerun()

def render_home_page(db_manager, auth_manager):
    """Affiche la page d'accueil"""
    render_header()
    
    # Proposition de valeur
    st.markdown(f"""
    <div class="main-header">
        <h1>{get_text('value_proposition')}</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Description des fonctionnalités
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="value-card">
            <h3>🤖 Intelligence Artificielle</h3>
            <p>Notre IA analyse vos critères et trouve les biens qui vous correspondent parfaitement.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="value-card">
            <h3>🎯 Recherche Personnalisée</h3>
            <p>Algorithmes avancés pour des recommandations sur mesure selon votre profil.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="value-card">
            <h3>📊 Analyse Complète</h3>
            <p>Évaluation détaillée de votre capacité d'emprunt et conseils personnalisés.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Statistiques
    st.subheader("📈 Nos Statistiques")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h2 style="color: #FF6B35;">10,000+</h2>
            <p>Biens référencés</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h2 style="color: #FF6B35;">5,000+</h2>
            <p>Utilisateurs satisfaits</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h2 style="color: #FF6B35;">95%</h2>
            <p>Taux de satisfaction</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h2 style="color: #FF6B35;">24h</h2>
            <p>Réponse moyenne</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Plans tarifaires
    st.subheader("💼 Choisissez votre plan")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="plan-card">
            <h3>🆓 Plan Gratuit</h3>
            <h2>0€</h2>
            <ul style="text-align: left;">
                <li>5 recherches par mois</li>
                <li>Recommandations de base</li>
                <li>Support par email</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Commencer gratuitement", key="free_plan"):
            st.session_state.page = 'register'
            st.session_state.selected_plan = 'Free'
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="plan-card">
            <h3>⭐ Plan Premium</h3>
            <h2>29€/mois</h2>
            <ul style="text-align: left;">
                <li>Recherches illimitées</li>
                <li>IA avancée</li>
                <li>Agent personnel</li>
                <li>Alertes en temps réel</li>
                <li>Support prioritaire</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button(get_text("start_trial"), key="premium_trial"):
            st.session_state.page = 'register'
            st.session_state.selected_plan = 'Premium'
            st.rerun()
    
    with col3:
        st.markdown("""
        <div class="plan-card">
            <h3>🏢 Plan Professionnel</h3>
            <h2>99€/mois</h2>
            <ul style="text-align: left;">
                <li>Tous les avantages Premium</li>
                <li>API d'intégration</li>
                <li>Dashboard avancé</li>
                <li>Support dédié 24/7</li>
                <li>Rapports personnalisés</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Contacter l'équipe", key="pro_plan"):
            st.session_state.page = 'contact'
            st.rerun()
    
    # Partenaires
    st.subheader("🤝 Nos Partenaires")
    col1, col2, col3, col4 = st.columns(4)
    
    partners = ["BNP Paribas", "Crédit Agricole", "LCL", "Société Générale"]
    for i, partner in enumerate(partners):
        with [col1, col2, col3, col4][i]:
            st.markdown(f"""
            <div class="metric-card">
                <h4>{partner}</h4>
                <p>Partenaire bancaire</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Contact
    st.subheader(f"📞 {get_text('contact_info')}")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="value-card">
            <h4>📧 Email</h4>
            <p>contact@imomatch.com</p>
            <h4>📱 Téléphone</h4>
            <p>+33 1 23 45 67 89</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="value-card">
            <h4>🏢 Adresse</h4>
            <p>123 Avenue des Champs-Élysées<br>75008 Paris, France</p>
            <h4>🕐 Horaires</h4>
            <p>Lundi - Vendredi: 9h-18h</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Boutons de connexion/inscription
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🔐 Se connecter", use_container_width=True):
            st.session_state.page = 'login'
            st.rerun()
    
    with col2:
        if st.button("📝 S'inscrire", use_container_width=True):
            st.session_state.page = 'register'
            st.rerun()
    
    with col3:
        if st.button("ℹ️ En savoir plus", use_container_width=True):
            st.session_state.page = 'about'
            st.rerun()

def render_login_page(auth_manager):
    """Affiche la page de connexion"""
    render_header()
    
    st.markdown(f"""
    <div class="main-header">
        <h1>🔐 {get_text('login')}</h1>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            email = st.text_input(get_text("email"), placeholder="votre@email.com")
            password = st.text_input(get_text("password"), type="password")
            
            submit = st.form_submit_button("Se connecter", use_container_width=True)
            
            if submit:
                if email and password:
                    success, user = auth_manager.login_user(email, password)
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.user = user
                        st.session_state.page = 'dashboard'
                        st.success("Connexion réussie !")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Email ou mot de passe incorrect")
                else:
                    st.error("Veuillez remplir tous les champs")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("← Retour à l'accueil", use_container_width=True):
            st.session_state.page = 'home'
            st.rerun()
        
        if st.button("Pas encore de compte ? S'inscrire", use_container_width=True):
            st.session_state.page = 'register'
            st.rerun()

def render_register_page(auth_manager):
    """Affiche la page d'inscription"""
    render_header()
    
    st.markdown(f"""
    <div class="main-header">
        <h1>📝 {get_text('register')}</h1>
    </div>
    """, unsafe_allow_html=True)
    
    selected_plan = getattr(st.session_state, 'selected_plan', 'Free')
    
    if selected_plan != 'Free':
        st.info(f"🎯 Vous vous inscrivez au plan {selected_plan}")
    
    with st.form("register_form"):
        # Informations personnelles
        st.subheader("👤 Informations personnelles")
        col1, col2 = st.columns(2)
        
        with col1:
            prenom = st.text_input(get_text("firstname"), placeholder="Jean")
            nom = st.text_input(get_text("name"), placeholder="Dupont")
            email = st.text_input(get_text("email"), placeholder="jean.dupont@email.com")
        
        with col2:
            telephone = st.text_input(get_text("phone"), placeholder="+33 6 12 34 56 78")
            password = st.text_input(get_text("password"), type="password")
            confirm_password = st.text_input("Confirmer le mot de passe", type="password")
        
        # Informations professionnelles
        st.subheader("💼 Informations professionnelles")
        col1, col2 = st.columns(2)
        
        with col1:
            profession = st.text_input(get_text("profession"), placeholder="Ingénieur")
            situation_familiale = st.selectbox(get_text("family_situation"), 
                                             ["Célibataire", "Marié(e)", "Pacsé(e)", "Divorcé(e)", "Veuf/Veuve"])
        
        with col2:
            revenus = st.number_input(get_text("income"), min_value=0.0, step=100.0, value=0.0)
            apport = st.number_input(get_text("contribution"), min_value=0.0, step=1000.0, value=0.0)
        
        credits_en_cours = st.number_input(get_text("current_credits"), min_value=0.0, step=100.0, value=0.0)
        
        # Critères de recherche
        st.subheader("🏠 Critères de recherche")
        col1, col2 = st.columns(2)
        
        with col1:
            localisation_actuelle = st.text_input(get_text("current_location"), placeholder="Paris")
            localisation_souhaitee = st.text_input(get_text("desired_location"), placeholder="Région parisienne")
            type_bien = st.selectbox(get_text("property_type"), 
                                   ["", "Appartement", "Maison", "Studio", "Loft", "Duplex"])
        
        with col2:
            budget_min = st.number_input(get_text("min_budget"), min_value=0.0, step=10000.0, value=0.0)
            budget_max = st.number_input(get_text("max_budget"), min_value=0.0, step=10000.0, value=0.0)
            surface_min = st.number_input(get_text("min_surface"), min_value=0.0, step=5.0, value=0.0)
        
        nb_pieces_min = st.number_input(get_text("min_rooms"), min_value=1, step=1, value=1)
        
        # Critères spécifiques
        st.subheader("🎯 Critères spécifiques (optionnel)")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            balcon = st.checkbox("Balcon/Terrasse")
            parking = st.checkbox("Parking/Garage")
        with col2:
            ascenseur = st.checkbox("Ascenseur")
            jardin = st.checkbox("Jardin")
        with col3:
            piscine = st.checkbox("Piscine")
            cave = st.checkbox("Cave/Cellier")
        
        criteres_specifiques = {
            'balcon': balcon, 'parking': parking, 'ascenseur': ascenseur,
            'jardin': jardin, 'piscine': piscine, 'cave': cave
        }
        
        # Acceptation des conditions
        st.markdown("---")
        accept_terms = st.checkbox("J'accepte les conditions générales d'utilisation")
        accept_newsletter = st.checkbox("Je souhaite recevoir la newsletter ImoMatch")
        
        submit = st.form_submit_button("Créer mon compte", use_container_width=True)
        
        if submit:
            if not all([prenom, nom, email, password, confirm_password]):
                st.error("Veuillez remplir tous les champs obligatoires")
            elif password != confirm_password:
                st.error("Les mots de passe ne correspondent pas")
            elif not accept_terms:
                st.error("Vous devez accepter les conditions générales d'utilisation")
            else:
                user_data = {
                    'email': email,
                    'password': password,
                    'nom': nom,
                    'prenom': prenom,
                    'telephone': telephone,
                    'profession': profession,
                    'situation_familiale': situation_familiale,
                    'revenus': revenus,
                    'apport': apport,
                    'credits_en_cours': credits_en_cours,
                    'localisation_actuelle': localisation_actuelle,
                    'localisation_souhaitee': localisation_souhaitee,
                    'type_bien': type_bien,
                    'budget_min': budget_min,
                    'budget_max': budget_max,
                    'surface_min': surface_min,
                    'nb_pieces_min': nb_pieces_min,
                    'criteres_specifiques': criteres_specifiques,
                    'plan': selected_plan
                }
                
                if selected_plan == 'Premium':
                    user_data['plan_expiration'] = (datetime.now() + timedelta(days=14)).isoformat()
                
                success, message = auth_manager.register_user(user_data)
                
                if success:
                    st.success("Compte créé avec succès ! Vous pouvez maintenant vous connecter.")
                    time.sleep(2)
                    st.session_state.page = 'login'
                    st.rerun()
                else:
                    st.error(message)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("← Retour à l'accueil", use_container_width=True):
            st.session_state.page = 'home'
            st.rerun()
        
        if st.button("Déjà un compte ? Se connecter", use_container_width=True):
            st.session_state.page = 'login'
            st.rerun()

def render_dashboard(user, db_manager):
    """Affiche le tableau de bord"""
    st.markdown(f"""
    <div class="main-header">
        <h1>📊 {get_text('dashboard')} - Bienvenue {user['prenom']}</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Informations du plan utilisateur
    plan_info = f"Plan {user['plan']}"
    if user.get('plan_expiration') and user['plan'] == 'Premium':
        expiration = datetime.fromisoformat(user['plan_expiration'])
        if expiration > datetime.now():
            days_left = (expiration - datetime.now()).days
            plan_info += f" (Essai - {days_left} jours restants)"
        else:
            plan_info = "Plan Premium (Expiré)"
    
    st.info(f"🎯 {plan_info}")
    
    # Statistiques personnelles
    col1, col2, col3, col4 = st.columns(4)
    
    # Récupération des propriétés correspondant aux critères de l'utilisateur
    filters = {
        'prix_min': user.get('budget_min', 0),
        'prix_max': user.get('budget_max', float('inf')),
        'surface_min': user.get('surface_min', 0),
        'nb_pieces': user.get('nb_pieces_min', 1),
        'type_bien': user.get('type_bien'),
        'localisation': user.get('localisation_souhaitee')
    }
    
    matching_properties = db_manager.get_properties(filters)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h2 style="color: #FF6B35;">{len(matching_properties)}</h2>
            <p>Biens correspondants</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        visits_count = 12  # Exemple
        st.markdown(f"""
        <div class="metric-card">
            <h2 style="color: #FF6B35;">{visits_count}</h2>
            <p>Visites planifiées</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        favorites_count = 5  # Exemple
        st.markdown(f"""
        <div class="metric-card">
            <h2 style="color: #FF6B35;">{favorites_count}</h2>
            <p>Favoris sauvegardés</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        completion_rate = AIAgent.analyze_profile_completion(user)['completion_rate']
        st.markdown(f"""
        <div class="metric-card">
            <h2 style="color: #FF6B35;">{completion_rate:.0f}%</h2>
            <p>Profil complété</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Graphiques et analyses
    st.subheader("📈 Analyse de votre recherche")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if matching_properties:
            # Graphique des prix
            prices = [prop['prix'] for prop in matching_properties]
            fig = px.histogram(x=prices, nbins=10, title="Distribution des prix des biens correspondants")
            fig.update_traces(marker_color='#FF6B35')
            fig.update_layout(
                xaxis_title="Prix (€)",
                yaxis_title="Nombre de biens",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if matching_properties:
            # Graphique des surfaces
            surfaces = [prop['surface'] for prop in matching_properties]
            fig = px.histogram(x=surfaces, nbins=10, title="Distribution des surfaces")
            fig.update_traces(marker_color='#F7931E')
            fig.update_layout(
                xaxis_title="Surface (m²)",
                yaxis_title="Nombre de biens",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Dernières recommandations
    st.subheader("🎯 Dernières recommandations")
    
    if matching_properties:
        recommendations = AIAgent.generate_recommendations(user, matching_properties)
        
        for i, prop in enumerate(recommendations[:3]):  # Top 3
            with st.expander(f"🏠 {prop['titre']} - Score: {prop['match_score']}/100"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Prix:** {prop['prix']:,} €")
                    st.write(f"**Surface:** {prop['surface']} m²")
                    st.write(f"**Pièces:** {prop['nb_pieces']}")
                    st.write(f"**Localisation:** {prop['localisation']}")
                    st.write(f"**Description:** {prop['description']}")
                    
                    # Raisons du matching
                    st.write("**Pourquoi ce bien vous correspond:**")
                    for reason in prop['match_reasons']:
                        st.write(f"✅ {reason}")
                
                with col2:
                    if st.button(f"Voir détails", key=f"detail_{i}"):
                        st.session_state.selected_property = prop['id']
                        st.session_state.page = 'property_detail'
                        st.rerun()
                    
                    if st.button(f"💝 Ajouter aux favoris", key=f"fav_{i}"):
                        st.success("Ajouté aux favoris !")
    else:
        st.info("Aucun bien ne correspond actuellement à vos critères. Modifiez vos critères dans 'Mes informations' pour voir plus de résultats.")
    
    # Suggestions d'amélioration du profil
    profile_analysis = AIAgent.analyze_profile_completion(user)
    if profile_analysis['completion_rate'] < 100:
        st.subheader("🎯 Complétez votre profil pour de meilleurs résultats")
        
        suggestions = AIAgent.get_completion_suggestions(user, profile_analysis['missing_fields'])
        for suggestion in suggestions[:3]:
            st.info(f"💡 {suggestion}")
        
        if st.button("Compléter mon profil maintenant"):
            st.session_state.page = 'my_info'
            st.rerun()

def render_my_info_page(user, db_manager):
    """Affiche la page des informations utilisateur"""
    st.markdown(f"""
    <div class="main-header">
        <h1>👤 {get_text('my_info')}</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Analyse du profil
    profile_analysis = AIAgent.analyze_profile_completion(user)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"""
        <div class="value-card">
            <h3>Complétude de votre profil: {profile_analysis['completion_rate']:.0f}%</h3>
            <div style="background-color: #ddd; border-radius: 10px; height: 20px;">
                <div style="background: linear-gradient(90deg, #FF6B35, #F7931E); 
                            width: {profile_analysis['completion_rate']}%; 
                            height: 20px; border-radius: 10px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("🤖 Agent AI", use_container_width=True):
            st.session_state.page = 'agent_ai'
            st.rerun()
    
    # Formulaire de mise à jour des informations
    with st.form("update_info_form"):
        st.subheader("👤 Informations personnelles")
        col1, col2 = st.columns(2)
        
        with col1:
            prenom = st.text_input("Prénom", value=user.get('prenom', ''))
            nom = st.text_input("Nom", value=user.get('nom', ''))
            email = st.text_input("Email", value=user.get('email', ''))
        
        with col2:
            telephone = st.text_input("Téléphone", value=user.get('telephone', ''))
            profession = st.text_input("Profession", value=user.get('profession', ''))
            situation_familiale = st.selectbox(
                "Situation familiale", 
                ["Célibataire", "Marié(e)", "Pacsé(e)", "Divorcé(e)", "Veuf/Veuve"],
                index=["Célibataire", "Marié(e)", "Pacsé(e)", "Divorcé(e)", "Veuf/Veuve"].index(user.get('situation_familiale', 'Célibataire')) if user.get('situation_familiale') in ["Célibataire", "Marié(e)", "Pacsé(e)", "Divorcé(e)", "Veuf/Veuve"] else 0
            )
        
        st.subheader("💰 Informations financières")
        col1, col2 = st.columns(2)
        
        with col1:
            revenus = st.number_input("Revenus mensuels (€)", min_value=0.0, step=100.0, value=float(user.get('revenus', 0)))
            apport = st.number_input("Apport personnel (€)", min_value=0.0, step=1000.0, value=float(user.get('apport', 0)))
        
        with col2:
            credits_en_cours = st.number_input("Crédits en cours (€)", min_value=0.0, step=100.0, value=float(user.get('credits_en_cours', 0)))
        
        st.subheader("🏠 Critères de recherche")
        col1, col2 = st.columns(2)
        
        with col1:
            localisation_actuelle = st.text_input("Localisation actuelle", value=user.get('localisation_actuelle', ''))
            localisation_souhaitee = st.text_input("Localisation souhaitée", value=user.get('localisation_souhaitee', ''))
            type_bien = st.selectbox(
                "Type de bien", 
                ["", "Appartement", "Maison", "Studio", "Loft", "Duplex"],
                index=["", "Appartement", "Maison", "Studio", "Loft", "Duplex"].index(user.get('type_bien', '')) if user.get('type_bien') in ["", "Appartement", "Maison", "Studio", "Loft", "Duplex"] else 0
            )
        
        with col2:
            budget_min = st.number_input("Budget minimum (€)", min_value=0.0, step=10000.0, value=float(user.get('budget_min', 0)))
            budget_max = st.number_input("Budget maximum (€)", min_value=0.0, step=10000.0, value=float(user.get('budget_max', 0)))
            surface_min = st.number_input("Surface minimum (m²)", min_value=0.0, step=5.0, value=float(user.get('surface_min', 0)))
        
        nb_pieces_min = st.number_input("Nombre de pièces minimum", min_value=1, step=1, value=int(user.get('nb_pieces_min', 1)))
        
        # Critères spécifiques
        st.subheader("🎯 Critères spécifiques")
        current_criteria = json.loads(user.get('criteres_specifiques', '{}')) if user.get('criteres_specifiques') else {}
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            balcon = st.checkbox("Balcon/Terrasse", value=current_criteria.get('balcon', False))
            parking = st.checkbox("Parking/Garage", value=current_criteria.get('parking', False))
        with col2:
            ascenseur = st.checkbox("Ascenseur", value=current_criteria.get('ascenseur', False))
            jardin = st.checkbox("Jardin", value=current_criteria.get('jardin', False))
        with col3:
            piscine = st.checkbox("Piscine", value=current_criteria.get('piscine', False))
            cave = st.checkbox("Cave/Cellier", value=current_criteria.get('cave', False))
        
        criteres_specifiques = {
            'balcon': balcon, 'parking': parking, 'ascenseur': ascenseur,
            'jardin': jardin, 'piscine': piscine, 'cave': cave
        }
        
        submit = st.form_submit_button("💾 Sauvegarder les modifications", use_container_width=True)
        
        if submit:
            update_data = {
                'prenom': prenom,
                'nom': nom,
                'email': email,
                'telephone': telephone,
                'profession': profession,
                'situation_familiale': situation_familiale,
                'revenus': revenus,
                'apport': apport,
                'credits_en_cours': credits_en_cours,
                'localisation_actuelle': localisation_actuelle,
                'localisation_souhaitee': localisation_souhaitee,
                'type_bien': type_bien,
                'budget_min': budget_min,
                'budget_max': budget_max,
                'surface_min': surface_min,
                'nb_pieces_min': nb_pieces_min,
                'criteres_specifiques': json.dumps(criteres_specifiques)
            }
            
            if db_manager.update_user(user['user_id'], update_data):
                st.success("✅ Informations mises à jour avec succès !")
                # Mettre à jour la session
                for key, value in update_data.items():
                    st.session_state.user[key] = value
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ Erreur lors de la mise à jour")

def render_agent_ai_page(user, db_manager):
    """Affiche la page de l'agent IA"""
    st.markdown(f"""
    <div class="main-header">
        <h1>🤖 Agent IA - Assistant Personnel</h1>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="value-card">
        <h3>🎯 Comment puis-je vous aider ?</h3>
        <p>Je suis votre assistant personnel IA. Je peux vous aider à :</p>
        <ul>
            <li>Compléter votre profil pour de meilleures recommandations</li>
            <li>Analyser vos critères de recherche</li>
            <li>Vous conseiller sur votre capacité d'emprunt</li>
            <li>Répondre à vos questions sur l'immobilier</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Analyse du profil
    profile_analysis = AIAgent.analyze_profile_completion(user)
    
    if profile_analysis['completion_rate'] < 100:
        st.subheader("🔍 Suggestions pour améliorer votre profil")
        
        suggestions = AIAgent.get_completion_suggestions(user, profile_analysis['missing_fields'])
        
        for i, suggestion in enumerate(suggestions):
            st.markdown(f"""
            <div class="agent-response">
                <strong>💡 Suggestion {i+1}:</strong><br>
                {suggestion}
            </div>
            """, unsafe_allow_html=True)
    
    # Chat avec l'agent IA
    st.subheader("💬 Conversation avec l'Agent IA")
    
    # Initialiser l'historique de conversation
    if 'ai_conversation' not in st.session_state:
        st.session_state.ai_conversation = [
            {"role": "assistant", "content": f"Bonjour {user['prenom']} ! Je suis votre assistant IA personnalisé. Comment puis-je vous aider aujourd'hui ?"}
        ]
    
    # Afficher l'historique de conversation
    for message in st.session_state.ai_conversation:
        if message["role"] == "user":
            st.markdown(f"""
            <div style="background-color: #e3f2fd; padding: 1rem; border-radius: 10px; margin: 1rem 0; margin-left: 20%;">
                <strong>Vous:</strong> {message['content']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f
