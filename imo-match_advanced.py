import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
import plotly.express as px
import plotly.graph_objects as go
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import json
import uuid
import sqlite3
import hashlib
import requests
import folium
from streamlit_folium import folium_static
import time
import base64
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import smtplib

# Configuration de la page
st.set_page_config(
    page_title="imoMatch - Un Demandeur, Un Logement, Une Vente",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé avancé
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    .main-header h1 {
        color: white;
        text-align: center;
        margin: 0;
        font-size: 2.5em;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .main-header p {
        color: white;
        text-align: center;
        margin: 0.5rem 0 0 0;
        font-size: 1.3em;
    }
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #667eea;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    .recommendation-card {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #f0a500;
        margin: 0.8rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    .property-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .property-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 35px rgba(0,0,0,0.2);
    }
    .ai-chat {
        background: linear-gradient(135deg, #e3ffe7 0%, #d9e7ff 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .notification {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #ff6b6b;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.7rem 1.5rem;
        font-weight: bold;
        transition: transform 0.2s ease;
    }
    .stButton > button:hover {
        transform: scale(1.05);
    }
    .premium-badge {
        background: linear-gradient(45deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8em;
        font-weight: bold;
    }
    .match-score {
        font-size: 2em;
        font-weight: bold;
        text-align: center;
    }
    .match-excellent { color: #28a745; }
    .match-good { color: #ffc107; }
    .match-average { color: #fd7e14; }
    .match-poor { color: #dc3545; }
</style>
""", unsafe_allow_html=True)

# Classe pour la gestion de la base de données
class DatabaseManager:
    def __init__(self, db_name="imomatch.db"):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Initialiser la base de données avec toutes les tables"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Table des utilisateurs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                user_type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_premium BOOLEAN DEFAULT FALSE,
                subscription_end DATE
            )
        ''')
        
        # Table des profils
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS profiles (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                profile_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Table des propriétés
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS properties (
                id TEXT PRIMARY KEY,
                owner_id TEXT,
                property_data TEXT,
                status TEXT DEFAULT 'active',
                views INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (owner_id) REFERENCES users (id)
            )
        ''')
        
        # Table des matches/recommandations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS matches (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                property_id TEXT,
                score REAL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (property_id) REFERENCES properties (id)
            )
        ''')
        
        # Table des notifications
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                title TEXT,
                message TEXT,
                type TEXT,
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Table des messages (chat IA)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_messages (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                message TEXT,
                role TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def execute_query(self, query, params=None):
        """Exécuter une requête SQL"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        result = cursor.fetchall()
        conn.commit()
        conn.close()
        return result
    
    def insert_user(self, user_data):
        """Insérer un nouvel utilisateur"""
        query = """
        INSERT INTO users (id, email, password_hash, user_type) 
        VALUES (?, ?, ?, ?)
        """
        self.execute_query(query, (
            user_data['id'], 
            user_data['email'], 
            user_data['password_hash'], 
            user_data['user_type']
        ))

# Classe pour l'authentification
class AuthManager:
    @staticmethod
    def hash_password(password):
        """Hasher un mot de passe"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verify_password(password, hashed):
        """Vérifier un mot de passe"""
        return AuthManager.hash_password(password) == hashed
    
    @staticmethod
    def create_user(db, email, password, user_type):
        """Créer un nouvel utilisateur"""
        user_id = str(uuid.uuid4())
        password_hash = AuthManager.hash_password(password)
        
        user_data = {
            'id': user_id,
            'email': email,
            'password_hash': password_hash,
            'user_type': user_type
        }
        
        try:
            db.insert_user(user_data)
            return user_id
        except sqlite3.IntegrityError:
            return None
    
    @staticmethod
    def authenticate_user(db, email, password):
        """Authentifier un utilisateur"""
        query = "SELECT id, password_hash, user_type FROM users WHERE email = ?"
        result = db.execute_query(query, (email,))
        
        if result and AuthManager.verify_password(password, result[0][1]):
            return {'id': result[0][0], 'user_type': result[0][2]}
        return None

# Classe pour les services géographiques
class GeoService:
    @staticmethod
    def get_coordinates(address):
        """Obtenir les coordonnées d'une adresse (simulation)"""
        # En production, utiliser une vraie API comme Google Maps ou Nominatim
        coordinates_db = {
            "paris": {"lat": 48.8566, "lon": 2.3522},
            "lyon": {"lat": 45.7640, "lon": 4.8357},
            "marseille": {"lat": 43.2965, "lon": 5.3698},
            "toulouse": {"lat": 43.6043, "lon": 1.4437},
            "nice": {"lat": 43.7102, "lon": 7.2620},
            "bordeaux": {"lat": 44.8378, "lon": -0.5792}
        }
        
        city = address.lower().split(',')[0].strip()
        return coordinates_db.get(city, {"lat": 48.8566, "lon": 2.3522})
    
    @staticmethod
    def create_map(properties):
        """Créer une carte avec les propriétés"""
        # Centre de la carte sur Paris par défaut
        m = folium.Map(location=[48.8566, 2.3522], zoom_start=6)
        
        for prop in properties:
            coords = GeoService.get_coordinates(prop.get('ville', 'Paris'))
            
            # Couleur selon le type de bien
            color_map = {
                'Appartement': 'blue',
                'Maison': 'green',
                'Studio': 'orange',
                'Loft': 'purple'
            }
            
            folium.Marker(
                [coords['lat'], coords['lon']],
                popup=f"""
                <b>{prop.get('type', 'Bien')}</b><br>
                {prop.get('ville', '')}<br>
                {prop.get('surface', 0)}m² - {prop.get('pieces', 0)} pièces<br>
                <b>{prop.get('prix', 0):,}€</b>
                """,
                icon=folium.Icon(color=color_map.get(prop.get('type'), 'blue'))
            ).add_to(m)
        
        return m

# Classe pour l'intelligence artificielle
class AIService:
    @staticmethod
    def calculate_compatibility_score(profile, property_data):
        """Calculer un score de compatibilité avancé"""
        score = 0
        factors = []
        
        # Budget compatibility (30 points)
        budget_max = profile.get('budget_max', float('inf'))
        prix = property_data.get('prix', 0)
        if prix <= budget_max:
            budget_score = 30 * (1 - (prix / budget_max) * 0.5)
            score += budget_score
            factors.append(f"Budget: {budget_score:.1f}/30")
        
        # Surface compatibility (25 points)
        surface_souhaitee = profile.get('surface_souhaitee', 70)
        surface = property_data.get('surface', 0)
        surface_diff = abs(surface - surface_souhaitee) / surface_souhaitee
        if surface_diff <= 0.3:
            surface_score = 25 * (1 - surface_diff)
            score += surface_score
            factors.append(f"Surface: {surface_score:.1f}/25")
        
        # Location preference (25 points)
        villes_souhaitees = [v.lower() for v in profile.get('villes_souhaitees', [])]
        ville = property_data.get('ville', '').lower()
        if ville in villes_souhaitees:
            score += 25
            factors.append("Localisation: 25/25")
        
        # Type preference (20 points)
        type_souhaite = profile.get('type_bien', '').lower()
        type_bien = property_data.get('type', '').lower()
        if type_souhaite == type_bien:
            score += 20
            factors.append("Type: 20/20")
        
        return min(score, 100), factors
    
    @staticmethod
    def generate_ai_response(user_message, user_profile=None):
        """Générer une réponse d'IA contextuelle"""
        responses = {
            "budget": [
                "D'après votre budget, je peux vous proposer des biens dans cette gamme. Avez-vous des préférences de quartier ?",
                "Votre budget nous ouvre plusieurs possibilités intéressantes. Souhaitez-vous des biens récents ou avec du caractère ?"
            ],
            "quartier": [
                "Excellent choix de quartier ! Je connais bien cette zone. Quels sont vos critères de transport ?",
                "Ce quartier offre de belles opportunités. Préférez-vous être proche des commerces ou dans un environnement plus calme ?"
            ],
            "famille": [
                "Avec des enfants, je recommande de regarder la proximité des écoles. Avez-vous des établissements préférés ?",
                "Pour une famille, l'espace extérieur est important. Un balcon ou une terrasse vous intéresse ?"
            ],
            "default": [
                "Interessant ! Pouvez-vous me donner plus de détails pour affiner ma recherche ?",
                "Je note cette information. Qu'est-ce qui est le plus important pour vous dans ce logement ?",
                "Parfait ! Cela m'aide à mieux comprendre vos besoins. Avez-vous d'autres critères ?"
            ]
        }
        
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ['budget', 'prix', 'coût', 'euro']):
            category = "budget"
        elif any(word in message_lower for word in ['quartier', 'zone', 'arrondissement', 'ville']):
            category = "quartier"
        elif any(word in message_lower for word in ['enfant', 'famille', 'école']):
            category = "famille"
        else:
            category = "default"
        
        return np.random.choice(responses[category])

# Classe pour les notifications
class NotificationManager:
    def __init__(self, db):
        self.db = db
    
    def create_notification(self, user_id, title, message, notification_type="info"):
        """Créer une nouvelle notification"""
        notification_id = str(uuid.uuid4())
        query = """
        INSERT INTO notifications (id, user_id, title, message, type) 
        VALUES (?, ?, ?, ?, ?)
        """
        self.db.execute_query(query, (notification_id, user_id, title, message, notification_type))
    
    def get_user_notifications(self, user_id, limit=10):
        """Récupérer les notifications d'un utilisateur"""
        query = """
        SELECT title, message, type, is_read, created_at 
        FROM notifications 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT ?
        """
        return self.db.execute_query(query, (user_id, limit))
    
    def mark_as_read(self, user_id):
        """Marquer toutes les notifications comme lues"""
        query = "UPDATE notifications SET is_read = TRUE WHERE user_id = ?"
        self.db.execute_query(query, (user_id,))

# Initialisation des services
@st.cache_resource
def init_services():
    db = DatabaseManager()
    auth = AuthManager()
    geo = GeoService()
    ai = AIService()
    return db, auth, geo, ai

db, auth, geo, ai = init_services()
notification_manager = NotificationManager(db)

# Initialisation du state
if 'user' not in st.session_state:
    st.session_state.user = None
if 'notifications' not in st.session_state:
    st.session_state.notifications = []

# Header principal avec info utilisateur
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    st.markdown("""
    <div class="main-header">
        <h1>🏠 imoMatch</h1>
        <p>Un Demandeur, Un Logement, Une Vente</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    if st.session_state.user:
        st.success(f"👤 Connecté")
        if st.button("🔔 Notifications", key="notif_btn"):
            notifications = notification_manager.get_user_notifications(st.session_state.user['id'])
            st.session_state.notifications = notifications

with col3:
    if st.session_state.user:
        if st.button("🚪 Déconnexion", key="logout"):
            st.session_state.user = None
            st.rerun()

# Sidebar pour navigation et authentification
with st.sidebar:
    st.image("https://via.placeholder.com/200x80/667eea/FFFFFF?text=imoMatch", width=200)
    
    if st.session_state.user is None:
        # Interface d'authentification
        auth_tab1, auth_tab2 = st.tabs(["🔐 Connexion", "📝 Inscription"])
        
        with auth_tab1:
            with st.form("login_form"):
                email = st.text_input("📧 Email")
                password = st.text_input("🔒 Mot de passe", type="password")
                
                if st.form_submit_button("Se connecter", use_container_width=True):
                    user = auth.authenticate_user(db, email, password)
                    if user:
                        st.session_state.user = user
                        st.success("✅ Connexion réussie !")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Email ou mot de passe incorrect")
        
        with auth_tab2:
            with st.form("register_form"):
                reg_email = st.text_input("📧 Email")
                reg_password = st.text_input("🔒 Mot de passe", type="password")
                reg_password_confirm = st.text_input("🔒 Confirmer le mot de passe", type="password")
                user_type = st.selectbox(
                    "👤 Type de compte",
                    ["Acquéreur/Locataire", "Propriétaire/Bailleur", "Professionnel Immobilier"]
                )
                
                if st.form_submit_button("Créer un compte", use_container_width=True):
                    if reg_password != reg_password_confirm:
                        st.error("❌ Les mots de passe ne correspondent pas")
                    elif len(reg_password) < 6:
                        st.error("❌ Le mot de passe doit contenir au moins 6 caractères")
                    else:
                        user_id = auth.create_user(db, reg_email, reg_password, user_type)
                        if user_id:
                            st.success("✅ Compte créé avec succès !")
                            # Notification de bienvenue
                            notification_manager.create_notification(
                                user_id,
                                "🎉 Bienvenue sur imoMatch !",
                                "Votre compte a été créé avec succès. Complétez votre profil pour recevoir des recommandations personnalisées.",
                                "success"
                            )
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Cette adresse email est déjà utilisée")
    
    else:
        # Navigation pour utilisateur connecté
        st.success(f"👤 {st.session_state.user['user_type']}")
        
        # Affichage des notifications
        if st.session_state.notifications:
            st.subheader("🔔 Notifications")
            for notif in st.session_state.notifications[:3]:
                st.markdown(f"""
                <div class="notification">
                    <strong>{notif[0]}</strong><br>
                    <small>{notif[1]}</small>
                </div>
                """, unsafe_allow_html=True)
            
            if st.button("Marquer comme lues"):
                notification_manager.mark_as_read(st.session_state.user['id'])
                st.session_state.notifications = []
                st.rerun()
        
        st.divider()
        
        # Menu de navigation
        pages = {
            "🏠 Dashboard": "dashboard",
            "👤 Mon Profil": "profile",
            "🎯 Recommandations": "recommendations", 
            "🔍 Recherche Avancée": "search",
            "🗺️ Carte Interactive": "map",
            "🤖 Agent IA": "ai_agent",
            "📊 Analytics": "analytics",
            "💰 Services Premium": "premium",
            "🏢 Marketplace": "marketplace",
            "📹 Visites Virtuelles": "virtual_tours"
        }
        
        selected_page = st.selectbox("Navigation", list(pages.keys()))
        page = pages[selected_page]

# Pages de contenu principal
if st.session_state.user is None:
    # Page d'accueil pour non-connectés
    st.markdown("""
    ## 🎯 La révolution de l'immobilier par l'Intelligence Artificielle
    
    ### ✨ Pourquoi choisir imoMatch ?
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>🔍 Matching IA</h3>
            <p>Notre algorithme analyse plus de 50 critères pour vous proposer les biens parfaits</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>⚡ Gain de temps</h3>
            <p>Réduisez votre temps de recherche de 70% grâce à nos recommandations ciblées</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>💼 Services intégrés</h3>
            <p>Notaires, banques, assurances... tout l'écosystème immobilier en un clic</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Démonstration interactive
    st.subheader("🎬 Démonstration en direct")
    
    demo_col1, demo_col2 = st.columns([1, 1])
    
    with demo_col1:
        st.markdown("### 📝 Simulez votre profil")
        
        sim_budget = st.slider("Budget maximum (k€)", 100, 1000, 400)
        sim_surface = st.slider("Surface souhaitée (m²)", 30, 200, 80)
        sim_ville = st.selectbox("Ville préférée", ["Paris", "Lyon", "Marseille", "Toulouse"])
        sim_type = st.selectbox("Type de bien", ["Appartement", "Maison", "Studio"])
        
        if st.button("🎯 Voir les matches", use_container_width=True):
            # Simulation de résultats
            st.success("✅ 12 biens trouvés avec 89% de compatibilité moyenne !")
    
    with demo_col2:
        st.markdown("### 📊 Résultats en temps réel")
        
        # Graphique de démonstration
        demo_data = pd.DataFrame({
            'Bien': ['Apt. Bastille', 'Maison Vincennes', 'Loft Marais'],
            'Score': [95, 87, 76],
            'Prix': [450, 680, 520]
        })
        
        fig = px.bar(demo_data, x='Bien', y='Score', title='Scores de compatibilité')
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

elif page == "dashboard":
    st.header("🏠 Dashboard")
    
    # Métriques personnalisées
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👁️ Profil vues", "127", "12%")
    with col2:
        st.metric("🎯 Matches reçus", "23", "5")
    with col3:
        st.metric("📧 Messages", "8", "3")
    with col4:
        st.metric("⭐ Score profil", "85%", "2%")
    
    # Activité récente
    st.subheader("📈 Activité récente")
    
    # Graphiques d'activité
    col1, col2 = st.columns(2)
    
    with col1:
        # Évolution des vues
        dates = pd.date_range('2024-09-01', periods=20, freq='D')
        views = np.random.poisson(8, 20).cumsum()
        
        fig = px.line(x=dates, y=views, title='📊 Évolution des vues de profil')
        fig.update_traces(line_color='#667eea')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Répartition des matches par score
        scores_data = pd.DataFrame({
            'Score': ['90-100%', '80-89%', '70-79%', '60-69%'],
            'Nombre': [5, 8, 7, 3]
        })
        
        fig = px.pie(scores_data, values='Nombre', names='Score', 
                    title='🎯 Répartition des scores de match')
        st.plotly_chart(fig, use_container_width=True)
    
    # Recommandations rapides
    st.subheader("⚡ Recommandations express")
    
    quick_recs = [
        {"titre": "Appartement 3P - Belleville", "prix": "425k€", "score": 92},
        {"titre": "Maison 4P - Vincennes", "prix": "680k€", "score": 88},
        {"titre": "Loft 2P - République", "prix": "520k€", "score": 85}
    ]
    
    for rec in quick_recs:
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        with col1:
            st.write(f"**{rec['titre']}**")
        with col2:
            st.write(rec['prix'])
        with col3:
            st.write(f"🎯 {rec['score']}%")
        with col4:
            if st.button("Voir", key=f"quick_{rec['score']}"):
                st.info("Détails du bien...")

elif page == "profile":
    st.header("👤 Mon Profil Complet")
    
    # Profil selon le type d'utilisateur
    if st.session_state.user['user_type'] == "Acquéreur/Locataire":
        
        profile_tab1, profile_tab2, profile_tab3 = st.tabs(["📋 Informations", "🎯 Critères", "🔒 Sécurité"])
        
        with profile_tab1:
            with st.form("profile_info"):
                st.subheader("Informations personnelles")
                
                col1, col2 = st.columns(2)
                with col1:
                    nom = st.text_input("👤 Nom complet")
                    telephone = st.text_input("📱 Téléphone")
                    age = st.number_input("🎂 Âge", min_value=18, max_value=100)
                    profession = st.text_input("💼 Profession")
                    
                with col2:
                    situation = st.selectbox("👨‍👩‍👧‍👦 Situation familiale", 
                                           ["Célibataire", "En couple", "Marié(e)", "Divorcé(e)"])
                    revenus = st.number_input("💰 Revenus mensuels nets (€)", min_value=0)
                    enfants = st.number_input("👶 Nombre d'enfants", min_value=0)
                    animaux = st.checkbox("🐕 Animaux de compagnie")
                
                if st.form_submit_button("💾 Sauvegarder", use_container_width=True):
                    # Sauvegarder le profil en base
                    profile_data = {
                        "nom": nom,
                        "telephone": telephone,
                        "age": age,
                        "profession": profession,
                        "situation": situation,
                        "revenus": revenus,
                        "enfants": enfants,
                        "animaux": animaux
                    }
                    
                    # Insertion en base de données
                    query = """
                    INSERT OR REPLACE INTO profiles (id, user_id, profile_data) 
                    VALUES (?, ?, ?)
                    """
                    profile_id = str(uuid.uuid4())
                    db.execute_query(query, (profile_id, st.session_state.user['id'], json.dumps(profile_data)))
                    
                    st.success("✅ Profil mis à jour avec succès !")
                    
                    # Notification
                    notification_manager.create_notification(
                        st.session_state.user['id'],
                        "📝 Profil mis à jour",
                        "Vos informations ont été sauvegardées. Votre score de matching va s'améliorer !",
                        "info"
                    )
        
        with profile_tab2:
            with st.form("search_criteria"):
                st.subheader("🎯 Critères de recherche avancés")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    transaction_type = st.selectbox("📋 Type de transaction", ["Achat", "Location", "Achat/Location"])
                    budget_min = st.number_input("💰 Budget minimum (€)", min_value=0, value=200000)
                    budget_max = st.number_input("💰 Budget maximum (€)", min_value=0, value=500000)
                    surface_min = st.number_input("📏 Surface minimum (m²)", min_value=10, value=60)
                    
                with col2:
                    pieces_min = st.number_input("🏠 Pièces minimum", min_value=1, value=2)
                    pieces_max = st.number_input("🏠 Pièces maximum", min_value=1, value=5)
                    type_bien = st.multiselect("🏢 Types de biens", 
                                             ["Appartement", "Maison", "Studio", "Loft", "Duplex", "Penthouse"])
                    etage_pref = st.selectbox("🏗️ Préférence d'étage", 
                                            ["Rez-de-chaussée", "Étages bas (1-3)", "Étages moyens (4-6)", "Étages hauts (7+)", "Dernier étage"])
                
                with col3:
                    villes = st.multiselect("🌆 Villes souhaitées", 
                                          ["Paris", "Lyon", "Marseille", "Toulouse", "Nice", "Bordeaux", "Strasbourg", "Montpellier"])
                    arrondissements = st.text_area("📍 Arrondissements/Quartiers préférés", 
                                                 placeholder="Ex: 15e, 16e, Belleville...")
                    transport_max = st.number_input("🚇 Distance max transport (min)", min_value=1, value=15)
                    
                st.subheader("🏠 Caractéristiques souhaitées")
                
                col4, col5 = st.columns(2)
                
                with col4:
                    balcon = st.checkbox("🌿 Balcon/Terrasse/Jardin")
                    parking = st.checkbox("🚗 Parking/Garage")
                    ascenseur = st.checkbox("🛗 Ascenseur")
                    cave = st.checkbox("🏠 Cave/Cellier")
                    
                with col5:
                    luminosite = st.selectbox("☀️ Luminosité", ["Peu importante", "Importante", "Très importante"])
                    calme = st.selectbox("🔇 Environnement calme", ["Peu important", "Important", "Très important"])
                    vue = st.selectbox("🌅 Vue", ["Peu importante", "Sur cour", "Dégagée", "Exceptionnelle"])
                    etat = st.selectbox("🔧 État du bien", ["À rénover", "Bon état", "Très bon état", "Neuf/Récent"])
                
                st.subheader("📍 Proximité souhaitée")
                
                proximites = st.multiselect("🎯 Services importants à proximité", 
                                          ["Écoles/Crèches", "Commerces", "Parcs", "Restaurants", "Salles de sport", 
                                           "Centres médicaux", "Transports", "Bureaux/Coworking"])
                
                if st.form_submit_button("🎯 Sauvegarder les critères", use_container_width=True):
                    criteria = {
                        "transaction_type": transaction_type,
                        "budget_min": budget_min,
                        "budget_max": budget_max,
                        "surface_min": surface_min,
                        "pieces_min": pieces_min,
                        "pieces_max": pieces_max,
                        "type_bien": type_bien,
                        "etage_pref": etage_pref,
                        "villes": villes,
                        "arrondissements": arrondissements,
                        "transport_max": transport_max,
                        "balcon": balcon,
                        "parking": parking,
                        "ascenseur": ascenseur,
                        "cave": cave,
                        "luminosite": luminosite,
                        "calme": calme,
                        "vue": vue,
                        "etat": etat,
                        "proximites": proximites
                    }
                    
                    # Sauvegarde des critères
                    query = """
                    INSERT OR REPLACE INTO profiles (id, user_id, profile_data) 
                    VALUES (?, ?, ?)
                    """
                    criteria_id = f"{st.session_state.user['id']}_criteria"
                    db.execute_query(query, (criteria_id, st.session_state.user['id'], json.dumps(criteria)))
                    
                    st.success("🎯 Critères de recherche sauvegardés !")
        
        with profile_tab3:
            st.subheader("🔒 Paramètres de sécurité et confidentialité")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🔐 Mot de passe")
                with st.form("change_password"):
                    current_password = st.text_input("Mot de passe actuel", type="password")
                    new_password = st.text_input("Nouveau mot de passe", type="password")
                    confirm_password = st.text_input("Confirmer le nouveau mot de passe", type="password")
                    
                    if st.form_submit_button("Changer le mot de passe"):
                        if new_password == confirm_password and len(new_password) >= 6:
                            st.success("✅ Mot de passe mis à jour !")
                        else:
                            st.error("❌ Erreur dans la modification du mot de passe")
            
            with col2:
                st.markdown("### 👁️ Confidentialité")
                
                public_profile = st.checkbox("Profil public", help="Visible par les professionnels")
                contact_direct = st.checkbox("Contact direct autorisé", help="Les propriétaires peuvent vous contacter")
                notifications_email = st.checkbox("Notifications par email", value=True)
                newsletters = st.checkbox("Newsletter et actualités")
                
                if st.button("💾 Sauvegarder les préférences"):
                    st.success("✅ Préférences de confidentialité mises à jour !")

elif page == "recommendations":
    st.header("🎯 Recommandations Personnalisées")
    
    # Système de recommandations avancé
    col1, col2 = st.columns([3, 1])
    
    with col2:
        st.subheader("🔧 Filtres")
        score_min = st.slider("Score minimum", 0, 100, 70)
        prix_max = st.number_input("Prix maximum (k€)", min_value=100, value=600)
        trier_par = st.selectbox("Trier par", ["Score de match", "Prix croissant", "Prix décroissant", "Date d'ajout"])
        
        if st.button("🔄 Actualiser"):
            st.rerun()
    
    with col1:
        # Propriétés recommandées (données simulées avec IA)
        sample_properties = [
            {
                "id": "prop_1",
                "titre": "Magnifique 3P - Bastille",
                "type": "Appartement",
                "surface": 75,
                "pieces": 3,
                "prix": 485000,
                "ville": "Paris",
                "quartier": "Bastille",
                "description": "Appartement lumineux avec parquet ancien, 2 chambres, cuisine équipée, proche métro.",
                "caracteristiques": ["Balcon", "Cave", "Interphone"],
                "photos": ["https://via.placeholder.com/300x200/4287f5/ffffff?text=Photo+1"],
                "agent": "Marie Dubois - Century 21"
            },
            {
                "id": "prop_2",
                "titre": "Maison familiale - Vincennes",
                "type": "Maison",
                "surface": 120,
                "pieces": 5,
                "prix": 680000,
                "ville": "Vincennes",
                "quartier": "Centre",
                "description": "Belle maison avec jardin, 4 chambres, garage, dans quartier calme et résidentiel.",
                "caracteristiques": ["Jardin", "Garage", "Cheminée"],
                "photos": ["https://via.placeholder.com/300x200/28a745/ffffff?text=Photo+2"],
                "agent": "Pierre Martin - Orpi"
            },
            {
                "id": "prop_3",
                "titre": "Loft d'artiste - République",
                "type": "Loft",
                "surface": 85,
                "pieces": 2,
                "prix": 520000,
                "ville": "Paris",
                "quartier": "République",
                "description": "Ancien atelier d'artiste rénové, volumes exceptionnels, très lumineux.",
                "caracteristiques": ["Hauteur 4m", "Verrière", "Terrasse"],
                "photos": ["https://via.placeholder.com/300x200/fd7e14/ffffff?text=Photo+3"],
                "agent": "Sophie Leroy - Indépendant"
            }
        ]
        
        # Calcul des scores de compatibilité
        fake_profile = {
            "budget_max": 600000,
            "surface_souhaitee": 80,
            "type_bien": "appartement",
            "villes_souhaitees": ["paris", "vincennes"]
        }
        
        for prop in sample_properties:
            score, factors = ai.calculate_compatibility_score(fake_profile, prop)
            
            # Carte de propriété avec design amélioré
            st.markdown(f"""
            <div class="property-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <h3 style="margin: 0; color: #667eea;">{prop['titre']}</h3>
                    <div class="match-score match-{'excellent' if score >= 80 else 'good' if score >= 60 else 'average'}">
                        {score:.0f}%
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col_info, col_photo, col_actions = st.columns([2, 1, 1])
            
            with col_info:
                st.write(f"**{prop['type']} • {prop['surface']}m² • {prop['pieces']} pièces**")
                st.write(f"📍 {prop['ville']} - {prop['quartier']}")
                st.write(f"💰 **{prop['prix']:,}€**")
                st.write(prop['description'])
                
                # Caractéristiques
                carac_str = " • ".join(prop['caracteristiques'])
                st.write(f"✨ {carac_str}")
                
                st.write(f"👤 **Agent:** {prop['agent']}")
            
            with col_photo:
                st.image(prop['photos'][0], use_column_width=True)
            
            with col_actions:
                st.metric("🎯 Match", f"{score:.0f}%")
                
                if st.button(f"📧 Contacter", key=f"contact_{prop['id']}"):
                    st.success("✅ Demande de contact envoyée !")
                    # Notification
                    notification_manager.create_notification(
                        st.session_state.user['id'],
                        "📧 Contact envoyé",
                        f"Votre demande pour {prop['titre']} a été transmise à l'agent.",
                        "success"
                    )
                
                if st.button(f"❤️ Favoris", key=f"fav_{prop['id']}"):
                    st.info("💖 Ajouté aux favoris !")
                
                if st.button(f"🔗 Partager", key=f"share_{prop['id']}"):
                    st.info("📤 Lien copié !")
            
            # Détails du matching
            with st.expander(f"🔍 Détails du matching pour {prop['titre']}"):
                col_factors, col_chart = st.columns([1, 1])
                
                with col_factors:
                    st.write("**Facteurs de compatibilité:**")
                    for factor in factors:
                        st.write(f"• {factor}")
                
                with col_chart:
                    # Mini graphique radar du matching
                    categories = ['Budget', 'Surface', 'Localisation', 'Type']
                    values = [85, 92, 100, 80] if score > 80 else [70, 65, 85, 75]
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatterpolar(
                        r=values,
                        theta=categories,
                        fill='toself',
                        name=f'Compatibilité'
                    ))
                    fig.update_layout(
                        polar=dict(
                            radialaxis=dict(visible=True, range=[0, 100])
                        ),
                        showlegend=False,
                        height=250
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            st.divider()

elif page == "search":
    st.header("🔍 Recherche Avancée Multi-Critères")
    
    # Interface de recherche sophistiquée
    search_col1, search_col2, search_col3 = st.columns([1, 1, 1])
    
    with search_col1:
        st.subheader("💰 Budget & Surface")
        budget_range = st.slider("Budget (k€)", 100, 1500, (300, 700))
        surface_range = st.slider("Surface (m²)", 20, 300, (60, 120))
        pieces_range = st.slider("Nombre de pièces", 1, 10, (2, 5))
    
    with search_col2:
        st.subheader("📍 Localisation")
        search_villes = st.multiselect("Villes", 
                                     ["Paris", "Lyon", "Marseille", "Toulouse", "Nice", "Bordeaux", "Strasbourg"])
        search_quartiers = st.text_input("Quartiers spécifiques")
        transport_distance = st.number_input("Distance max transport (min)", 1, 60, 15)
    
    with search_col3:
        st.subheader("🏠 Caractéristiques")
        search_types = st.multiselect("Types de biens", 
                                    ["Appartement", "Maison", "Studio", "Loft", "Duplex"])
        search_options = st.multiselect("Options", 
                                      ["Balcon/Terrasse", "Parking", "Ascenseur", "Cave", "Jardin"])
        search_etat = st.selectbox("État", ["Tous", "Neuf", "Bon état", "À rénover"])
    
    # Recherche avec IA
    if st.button("🎯 Lancer la recherche IA", use_container_width=True):
        with st.spinner("🔮 L'IA analyse le marché..."):
            time.sleep(2)
            
            # Simulation de résultats de recherche
            st.success(f"✅ {np.random.randint(15, 45)} biens trouvés correspondant à vos critères !")
            
            # Graphique de répartition des résultats
            col1, col2 = st.columns(2)
            
            with col1:
                # Répartition par prix
                prix_data = pd.DataFrame({
                    'Tranche': ['300-400k', '400-500k', '500-600k', '600-700k'],
                    'Nombre': [8, 12, 15, 9]
                })
                fig = px.bar(prix_data, x='Tranche', y='Nombre', title='Répartition par tranche de prix')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Répartition géographique
                geo_data = pd.DataFrame({
                    'Ville': ['Paris', 'Lyon', 'Marseille'],
                    'Nombre': [20, 15, 9]
                })
                fig = px.pie(geo_data, values='Nombre', names='Ville', title='Répartition géographique')
                st.plotly_chart(fig, use_container_width=True)
    
    # Recherche sauvegardée
    st.subheader("💾 Recherches sauvegardées")
    
    col1, col2, col3 = st.columns(3)
    
    saved_searches = [
        {"nom": "Appartement Paris 15e", "criteres": "3P, 400-500k€", "resultats": 12},
        {"nom": "Maison Lyon", "criteres": "4P+, jardin", "resultats": 8},
        {"nom": "Studio étudiant", "criteres": "<300k€, transport", "resultats": 25}
    ]
    
    for i, search in enumerate(saved_searches):
        with [col1, col2, col3][i]:
            st.markdown(f"""
            <div class="metric-card">
                <h4>{search['nom']}</h4>
                <p>{search['criteres']}</p>
                <p><strong>{search['resultats']} résultats</strong></p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"🔄 Relancer", key=f"rerun_{i}"):
                st.info("🔍 Recherche relancée !")

elif page == "map":
    st.header("🗺️ Carte Interactive des Biens")
    
    # Contrôles de la carte
    map_col1, map_col2 = st.columns([3, 1])
    
    with map_col2:
        st.subheader("🎛️ Contrôles")
        
        map_budget_max = st.slider("Budget max (k€)", 200, 1000, 600)
        map_types = st.multiselect("Types", ["Appartement", "Maison", "Studio", "Loft"], default=["Appartement"])
        map_ville = st.selectbox("Centrer sur", ["Paris", "Lyon", "Marseille", "Toulouse"])
        
        show_transport = st.checkbox("🚇 Stations de transport", value=True)
        show_ecoles = st.checkbox("🏫 Écoles", value=False)
        show_commerces = st.checkbox("🏪 Commerces", value=False)
    
    with map_col1:
        # Création de la carte interactive
        sample_map_properties = [
            {"ville": "Paris", "type": "Appartement", "prix": 450000, "surface": 65},
            {"ville": "Paris", "type": "Loft", "prix": 580000, "surface": 85},
            {"ville": "Lyon", "type": "Maison", "prix": 380000, "surface": 110},
        ]
        
        filtered_props = [p for p in sample_map_properties if p['type'] in map_types and p['prix'] <= map_budget_max * 1000]
        
        if filtered_props:
            interactive_map = geo.create_map(filtered_props)
            folium_static(interactive_map, width=700, height=500)
        else:
            st.warning("Aucun bien ne correspond à vos filtres.")
        
        # Statistiques de la carte
        st.subheader("📊 Statistiques de zone")
        
        stats_col1, stats_col2, stats_col3 = st.columns(3)
        
        with stats_col1:
            st.metric("Prix médian/m²", "8,450€", "2.1%")
        with stats_col2:
            st.metric("Temps de vente moyen", "45 jours", "-12%")
        with stats_col3:
            st.metric("Biens disponibles", "127", "+8")

elif page == "ai_agent":
    st.header("🤖 Agent IA - Assistant Personnel Immobilier")
    
    # Interface de chat avancée
    chat_col1, chat_col2 = st.columns([3, 1])
    
    with chat_col2:
        st.subheader("🎯 Actions rapides")
        
        if st.button("🔍 Analyser le marché", use_container_width=True):
            st.session_state.ai_messages = st.session_state.get('ai_messages', [])
            st.session_state.ai_messages.append({
                "role": "assistant", 
                "content": "📊 D'après mon analyse, le marché est dynamique avec une hausse de 3.2% des prix. Je recommande de regarder les secteurs en développement comme Belleville ou République."
            })
            st.rerun()
        
        if st.button("💡 Conseils personnalisés", use_container_width=True):
            st.session_state.ai_messages = st.session_state.get('ai_messages', [])
            st.session_state.ai_messages.append({
                "role": "assistant", 
                "content": "💡 Basé sur votre profil, je suggère d'élargir votre recherche aux villes limitrophes. Vous pourriez gagner 20% sur le prix au m² !"
            })
            st.rerun()
        
        if st.button("📈 Prédictions prix", use_container_width=True):
            st.session_state.ai_messages = st.session_state.get('ai_messages', [])
            st.session_state.ai_messages.append({
                "role": "assistant", 
                "content": "📈 Mes modèles prédisent une stabilisation des prix dans les 6 prochains mois. C'est le moment idéal pour négocier !"
            })
            st.rerun()
        
        st.divider()
        st.subheader("📊 Score IA")
        st.metric("Compatibilité profil", "87%", "2%")
        st.metric("Probabilité d'achat", "72%", "5%")
        
    with chat_col1:
        # Historique des messages
        if 'ai_messages' not in st.session_state:
            st.session_state.ai_messages = [
                {
                    "role": "assistant", 
                    "content": "🤖 Bonjour ! Je suis votre agent IA personnel imoMatch. Je connais le marché immobilier en temps réel et je peux vous aider à optimiser votre recherche. Que souhaitez-vous savoir ?"
                }
            ]
        
        # Affichage des messages avec design amélioré
        for message in st.session_state.ai_messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); padding: 1rem; border-radius: 10px; margin: 0.5rem 0; margin-left: 2rem;">
                    <strong>👤 Vous:</strong><br>{message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="ai-chat">
                    <strong>🤖 Agent IA:</strong><br>{message["content"]}
                </div>
                """, unsafe_allow_html=True)
        
        # Input utilisateur
        user_input = st.chat_input("Votre message à l'agent IA...")
        
        if user_input:
            # Ajouter le message utilisateur
            st.session_state.ai_messages.append({"role": "user", "content": user_input})
            
            # Générer une réponse IA contextuelle
            ai_response = ai.generate_ai_response(user_input)
            st.session_state.ai_messages.append({"role": "assistant", "content": ai_response})
            
            # Sauvegarder en base de données
            for msg in st.session_state.ai_messages[-2:]:
                msg_id = str(uuid.uuid4())
                query = "INSERT INTO ai_messages (id, user_id, message, role) VALUES (?, ?, ?, ?)"
                db.execute_query(query, (msg_id, st.session_state.user['id'], msg['content'], msg['role']))
            
            st.rerun()

elif page == "analytics":
    st.header("📊 Analytics et Intelligence du Marché")
    
    # Métriques avancées
    metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
    
    with metrics_col1:
        st.metric("🎯 Taux de match", "23.4%", "1.8%")
    with metrics_col2:
        st.metric("⏱️ Temps moyen recherche", "18 jours", "-27%")
    with metrics_col3:
        st.metric("💬 Messages reçus", "47", "12")
    with metrics_col4:
        st.metric("📈 Score de profil", "94/100", "3")
    
    # Graphiques analytiques avancés
    analytics_tab1, analytics_tab2, analytics_tab3 = st.tabs(["📈 Performance", "🎯 Matching", "🌍 Marché"])
    
    with analytics_tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            # Évolution des prix par ville
            villes_data = pd.DataFrame({
                'Mois': pd.date_range('2024-01-01', periods=12, freq='M'),
                'Paris': np.random.normal(9500, 200, 12).cumsum(),
                'Lyon': np.random.normal(5200, 100, 12).cumsum(),
                'Marseille': np.random.normal(4800, 80, 12).cumsum()
            })
            
            fig = px.line(villes_data, x='Mois', y=['Paris', 'Lyon', 'Marseille'], 
                         title='💰 Évolution prix/m² par ville')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Temps de vente moyen par type
            temps_vente_data = pd.DataFrame({
                'Type': ['Appartement', 'Maison', 'Studio', 'Loft'],
                'Temps (jours)': [42, 65, 28, 78]
            })
            
            fig = px.bar(temps_vente_data, x='Type', y='Temps (jours)', 
                        title='⏰ Temps de vente moyen par type')
            fig.update_traces(marker_color='#fd7e14')
            st.plotly_chart(fig, use_container_width=True)

elif page == "premium":
    st.header("💎 Services Premium - Passez au niveau supérieur")
    
    # Statut premium actuel
    premium_col1, premium_col2 = st.columns([2, 1])
    
    with premium_col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 15px; color: white; margin-bottom: 2rem;">
            <h2 style="margin: 0; color: white;">🚀 Débloquez tout le potentiel d'imoMatch</h2>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.1em;">Accédez aux fonctionnalités avancées et maximisez vos chances de trouver le bien parfait</p>
        </div>
        """, unsafe_allow_html=True)
    
    with premium_col2:
        current_plan = "Gratuit"  # Simulation
        st.markdown(f"""
        <div class="metric-card">
            <h3>📊 Votre plan actuel</h3>
            <h2 style="color: #667eea;">{current_plan}</h2>
            <p>Profil complété à 65%</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Comparaison des plans
    st.subheader("📋 Comparaison des offres")
    
    plans_col1, plans_col2, plans_col3 = st.columns(3)
    
    with plans_col1:
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 15px; border: 2px solid #e0e0e0; text-align: center;">
            <h3>🆓 GRATUIT</h3>
            <h2 style="color: #667eea;">0€</h2>
            <p style="color: #666;">par mois</p>
            
            <div style="text-align: left; margin: 1rem 0;">
                <p>✅ Profil de base</p>
                <p>✅ 5 contacts/mois</p>
                <p>✅ Recherche simple</p>
                <p>❌ Recommandations IA</p>
                <p>❌ Agent IA personnel</p>
                <p>❌ Analytics avancées</p>
                <p>❌ Support prioritaire</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.button("📋 Plan actuel", disabled=True, use_container_width=True)
    
    with plans_col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); padding: 2rem; border-radius: 15px; border: 3px solid #f0a500; text-align: center; position: relative;">
            <div class="premium-badge" style="position: absolute; top: -10px; right: 10px;">POPULAIRE</div>
            <h3>⭐ PREMIUM</h3>
            <h2 style="color: #f0a500;">9.90€</h2>
            <p style="color: #666;">par mois</p>
            
            <div style="text-align: left; margin: 1rem 0;">
                <p>✅ Tout du plan gratuit</p>
                <p>✅ Recommandations IA illimitées</p>
                <p>✅ Agent IA personnel 24/7</p>
                <p>✅ Analytics détaillées</p>
                <p>✅ Contacts illimités</p>
                <p>✅ Alertes temps réel</p>
                <p>✅ Historique complet</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Passer à Premium", use_container_width=True):
            st.balloons()
            st.success("🎉 Bienvenue dans Premium ! Redirection vers le paiement...")
    
    with plans_col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 15px; text-align: center; color: white;">
            <h3 style="color: white;">👑 PROFESSIONNEL</h3>
            <h2 style="color: white;">29.90€</h2>
            <p style="color: #ddd;">par mois</p>
            
            <div style="text-align: left; margin: 1rem 0;">
                <p>✅ Tout du plan Premium</p>
                <p>✅ Gestion par professionnel</p>
                <p>✅ Commission négociée</p>
                <p>✅ Accompagnement juridique</p>
                <p>✅ Visite organisée</p>
                <p>✅ Dossier optimisé</p>
                <p>✅ Support dédié</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("👑 Devenir Pro", use_container_width=True):
            st.success("👔 Demande envoyée ! Un conseiller vous contactera.")
    
    # Fonctionnalités premium en détail
    st.subheader("🔥 Fonctionnalités Premium en action")
    
    feature_tab1, feature_tab2, feature_tab3 = st.tabs(["🤖 IA Avancée", "📊 Analytics Pro", "🎯 Matching+"])
    
    with feature_tab1:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("""
            ### 🧠 Agent IA Personnel
            
            **Capacités exclusives Premium :**
            - 🔍 Analyse prédictive du marché
            - 📈 Recommandations personnalisées temps réel
            - 💬 Chat 24/7 avec mémoire contextuelle
            - 🎯 Optimisation automatique des critères
            - 📊 Rapports de marché hebdomadaires
            """)
            
            if st.button("🎬 Voir une démo", key="demo_ai"):
                st.info("🤖 'Basé sur l'évolution du marché, je recommande de visiter le 3P Bastille cette semaine. Le prix pourrait augmenter de 2% le mois prochain selon mes modèles prédictifs.'")
        
        with col2:
            # Simulation conversation IA avancée
            st.markdown("### 💬 Exemple de conversation Premium")
            st.markdown("""
            <div class="ai-chat">
                <strong>🤖 Agent IA Premium:</strong><br>
                📊 J'ai analysé 1,247 transactions similaires. Votre budget de 450k€ vous positionne dans le top 30% des acquéreurs pour ce secteur.
                <br><br>
                🎯 Recommandation: Négociez à 425k€ sur le bien Bastille. Probabilité d'acceptation: 73%
                <br><br>
                📈 Tendance: +2.1% d'augmentation prévue dans 3 mois dans ce quartier.
            </div>
            """, unsafe_allow_html=True)
    
    with feature_tab2:
        st.markdown("### 📊 Analytics Professionnelles")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Graphique avancé - Analyse prédictive
            dates_future = pd.date_range('2024-09-01', periods=12, freq='M')
            prix_pred = [450, 455, 462, 458, 467, 472, 478, 485, 482, 489, 495, 501]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=dates_future[:6], y=prix_pred[:6], 
                name='Historique', line=dict(color='blue')
            ))
            fig.add_trace(go.Scatter(
                x=dates_future[5:], y=prix_pred[5:], 
                name='Prédiction IA', line=dict(color='red', dash='dash')
            ))
            fig.update_layout(title='🔮 Prédiction prix/m² - Paris 15e')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Heatmap des meilleurs quartiers
            quartiers = ['Bastille', 'République', 'Marais', 'Belleville']
            criteres = ['Prix', 'Évolution', 'Liquidité', 'Potentiel']
            
            heatmap_data = np.random.rand(4, 4) * 100
            
            fig = px.imshow(heatmap_data, x=criteres, y=quartiers, 
                           title='🌡️ Analyse comparative quartiers')
            st.plotly_chart(fig, use_container_width=True)
    
    with feature_tab3:
        st.markdown("### 🎯 Matching Algorithm Pro")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("""
            **Algorithme Premium vs Standard :**
            
            📊 **Standard (Gratuit):**
            - 4 critères de base
            - Mise à jour quotidienne
            - Score simple
            
            🚀 **Premium:**
            - 50+ critères analysés
            - Mise à jour temps réel
            - IA prédictive
            - Analyse comportementale
            - Score multicritères
            """)
        
        with col2:
            # Comparaison visuelle
            comparison_data = pd.DataFrame({
                'Métrique': ['Précision', 'Rapidité', 'Personnalisation', 'Prédiction'],
                'Gratuit': [60, 70, 40, 0],
                'Premium': [95, 95, 90, 85]
            })
            
            fig = px.bar(comparison_data, x='Métrique', y=['Gratuit', 'Premium'], 
                        title='📈 Performance des algorithmes', barmode='group')
            st.plotly_chart(fig, use_container_width=True)
    
    # Témoignages clients
    st.subheader("💬 Ce que disent nos clients Premium")
    
    temoignage_col1, temoignage_col2, temoignage_col3 = st.columns(3)
    
    testimonials = [
        {
            "nom": "Marie L.", 
            "avatar": "👩‍💼",
            "text": "J'ai trouvé mon appartement parfait en 2 semaines grâce à l'IA ! Les recommandations étaient ultra-précises.",
            "note": "⭐⭐⭐⭐⭐"
        },
        {
            "nom": "Pierre M.", 
            "avatar": "👨‍💻",
            "text": "L'agent IA m'a fait économiser 15k€ en me conseillant le bon moment pour négocier. Incroyable !",
            "note": "⭐⭐⭐⭐⭐"
        },
        {
            "nom": "Sophie D.", 
            "avatar": "👩‍🎨",
            "text": "Les analytics m'ont aidée à comprendre le marché. J'ai acheté au meilleur moment !",
            "note": "⭐⭐⭐⭐⭐"
        }
    ]
    
    for i, temoignage in enumerate(testimonials):
        with [temoignage_col1, temoignage_col2, temoignage_col3][i]:
            st.markdown(f"""
            <div class="recommendation-card">
                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                    <div style="font-size: 2em; margin-right: 1rem;">{temoignage['avatar']}</div>
                    <div>
                        <h4 style="margin: 0;">{temoignage['nom']}</h4>
                        <div>{temoignage['note']}</div>
                    </div>
                </div>
                <p style="font-style: italic;">"{temoignage['text']}"</p>
            </div>
            """, unsafe_allow_html=True)

elif page == "marketplace":
    st.header("🏢 Marketplace des Services Immobiliers")
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 2rem; border-radius: 15px; color: white; margin-bottom: 2rem; text-align: center;">
        <h2 style="margin: 0; color: white;">🌟 Écosystème Complet Immobilier</h2>
        <p style="margin: 0.5rem 0 0 0; font-size: 1.1em;">Tous les professionnels dont vous avez besoin, pré-sélectionnés et notés</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Catégories de services
    service_tab1, service_tab2, service_tab3, service_tab4 = st.tabs(["🏦 Financement", "⚖️ Juridique", "🔧 Expertise", "📋 Administratif"])
    
    with service_tab1:
        st.subheader("🏦 Partenaires Financiers")
        
        banques = [
            {
                "nom": "Crédit Agricole",
                "logo": "🏦",
                "specialite": "Primo-accédants",
                "taux": "3.85%",
                "note": 4.2,
                "avantage": "Frais de dossier offerts via imoMatch"
            },
            {
                "nom": "BNP Paribas",
                "logo": "🏛️",
                "specialite": "Investissement locatif",
                "taux": "4.10%",
                "note": 4.0,
                "avantage": "Négociation privilégiée"
            },
            {
                "nom": "Courtier imoFinance",
                "logo": "💼",
                "specialite": "Meilleur taux garanti",
                "taux": "3.75%",
                "note": 4.6,
                "avantage": "Commission réduite -30%"
            }
        ]
        
        for banque in banques:
            col1, col2, col3, col4 = st.columns([1, 2, 1, 1])
            
            with col1:
                st.markdown(f"""
                <div style="text-align: center; font-size: 3em;">
                    {banque['logo']}
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                **{banque['nom']}**  
                *{banque['specialite']}*  
                🎯 {banque['avantage']}  
                ⭐ {banque['note']}/5
                """)
            
            with col3:
                st.metric("Taux indicatif", banque['taux'])
            
            with col4:
                if st.button(f"📞 Contacter", key=f"bank_{banque['nom']}"):
                    st.success("✅ Demande transmise !")
                    notification_manager.create_notification(
                        st.session_state.user['id'],
                        "🏦 Contact banque",
                        f"Votre demande a été transmise à {banque['nom']}",
                        "info"
                    )
            
            st.divider()
    
    with service_tab2:
        st.subheader("⚖️ Services Juridiques")
        
        juridique_col1, juridique_col2 = st.columns(2)
        
        with juridique_col1:
            st.markdown("### 👨‍⚖️ Notaires Partenaires")
            
            notaires = [
                {"nom": "Me. Dubois", "ville": "Paris 15e", "note": 4.8, "specialite": "Vente résidentielle"},
                {"nom": "Me. Martin", "ville": "Lyon 6e", "note": 4.6, "specialite": "Investissement"},
                {"nom": "Me. Bernard", "ville": "Marseille", "note": 4.4, "specialite": "Primo-accédant"}
            ]
            
            for notaire in notaires:
                st.markdown(f"""
                <div class="metric-card">
                    <h4>⚖️ {notaire['nom']}</h4>
                    <p>📍 {notaire['ville']}</p>
                    <p>🎯 {notaire['specialite']}</p>
                    <p>⭐ {notaire['note']}/5</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"📅 Rendez-vous", key=f"notaire_{notaire['nom']}"):
                    st.info("📞 Rendez-vous demandé !")
        
        with juridique_col2:
            st.markdown("### 🏛️ Services Juridiques")
            
            services_juridiques = [
                {"service": "Diagnostic juridique", "prix": "150€", "duree": "1h"},
                {"service": "Relecture compromis", "prix": "200€", "duree": "48h"},
                {"service": "Accompagnement signature", "prix": "300€", "duree": "½ jour"},
                {"service": "Conseil fiscal", "prix": "180€", "duree": "1h"}
            ]
            
            for service in services_juridiques:
                col_s1, col_s2, col_s3 = st.columns([2, 1, 1])
                
                with col_s1:
                    st.write(f"**{service['service']}**")
                with col_s2:
                    st.write(f"💰 {service['prix']}")
                with col_s3:
                    st.write(f"⏱️ {service['duree']}")
                
                st.divider()
    
    with service_tab3:
        st.subheader("🔧 Expertise et Diagnostics")
        
        expert_col1, expert_col2 = st.columns(2)
        
        with expert_col1:
            st.markdown("### 🏗️ Experts Bâtiment")
            
            experts = [
                {"nom": "SAS DiagPro", "note": 4.7, "prix": "450€", "delai": "48h"},
                {"nom": "Cabinet Expertise+", "note": 4.5, "prix": "380€", "delai": "72h"},
                {"nom": "Diag Immo Express", "note": 4.3, "prix": "320€", "delai": "24h"}
            ]
            
            for expert in experts:
                st.markdown(f"""
                <div class="property-card">
                    <h4>🔬 {expert['nom']}</h4>
                    <div style="display: flex; justify-content: space-between;">
                        <span>⭐ {expert['note']}/5</span>
                        <span>💰 {expert['prix']}</span>
                        <span>⏱️ {expert['delai']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"📋 Commander", key=f"expert_{expert['nom']}"):
                    st.success("✅ Expertise commandée !")
        
        with expert_col2:
            st.markdown("### 📊 Types de Diagnostics")
            
            diagnostics = [
                {"type": "DPE + Termites", "obligatoire": True, "prix": "180€"},
                {"type": "Expertise structure", "obligatoire": False, "prix": "280€"},
                {"type": "Diagnostic électricité", "obligatoire": True, "prix": "120€"},
                {"type": "Analyse humidité", "obligatoire": False, "prix": "200€"}
            ]
            
            for diag in diagnostics:
                obligation = "🔴 Obligatoire" if diag['obligatoire'] else "🟡 Conseillé"
                
                st.markdown(f"""
                <div style="background: {'#ffe6e6' if diag['obligatoire'] else '#fff7e6'}; padding: 1rem; border-radius: 8px; margin: 0.5rem 0;">
                    <strong>{diag['type']}</strong><br>
                    {obligation} - {diag['prix']}
                </div>
                """, unsafe_allow_html=True)
    
    with service_tab4:
        st.subheader("📋 Services Administratifs")
        
        admin_col1, admin_col2 = st.columns(2)
        
        with admin_col1:
            st.markdown("### 📄 Gestion Administrative")
            
            services_admin = [
                {"service": "Constitution dossier", "description": "Rassemblement de toutes les pièces", "prix": "80€"},
                {"service": "Suivi administratif", "description": "Relance et coordination", "prix": "120€/mois"},
                {"service": "Optimisation fiscale", "description": "Conseil déductibilité", "prix": "200€"},
                {"service": "Assurance emprunteur", "description": "Comparatif et négociation", "prix": "150€"}
            ]
            
            for service in services_admin:
                st.markdown(f"""
                <div class="recommendation-card">
                    <h4>📋 {service['service']}</h4>
                    <p>{service['description']}</p>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <strong>💰 {service['prix']}</strong>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"✅ Souscrire", key=f"admin_{service['service']}"):
                    st.success("📋 Service ajouté à votre dossier !")
        
        with admin_col2:
            st.markdown("### 📦 Packs Services")
            
            packs = [
                {
                    "nom": "Pack Découverte",
                    "prix": "299€",
                    "services": ["Diagnostic basic", "1h conseil juridique", "Dossier administratif"],
                    "economie": "50€"
                },
                {
                    "nom": "Pack Complet",
                    "prix": "599€", 
                    "services": ["Tous diagnostics", "Suivi complet", "Expertise", "Assurance"],
                    "economie": "120€"
                },
                {
                    "nom": "Pack Premium",
                    "prix": "899€",
                    "services": ["Pack Complet", "Conseiller dédié", "Négociation", "Garanties"],
                    "economie": "200€"
                }
            ]
            
            for pack in packs:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 12px; color: white; margin: 1rem 0;">
                    <h4 style="color: white; margin: 0;">{pack['nom']}</h4>
                    <h3 style="color: white;">{pack['prix']}</h3>
                    <p style="color: #ddd;">Économie: {pack['economie']}</p>
                    
                    <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px; margin: 1rem 0;">
                        {"<br>".join([f"✅ {s}" for s in pack['services']])}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"🛒 Choisir {pack['nom']}", key=f"pack_{pack['nom']}"):
                    st.balloons()
                    st.success(f"🎉 {pack['nom']} ajouté ! Vous économisez {pack['economie']} !")

elif page == "virtual_tours":
    st.header("📹 Visites Virtuelles & Immersives")
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%); padding: 2rem; border-radius: 15px; color: white; margin-bottom: 2rem;">
        <h2 style="margin: 0; color: white;">🎬 Visitez comme si vous y étiez</h2>
        <p style="margin: 0.5rem 0 0 0; font-size: 1.1em;">Technologie VR, visites 360°, et réalité augmentée</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Types de visites
    visit_tab1, visit_tab2, visit_tab3 = st.tabs(["🎥 Visite 360°", "🥽 Réalité Virtuelle", "📱 AR Mobile"])
    
    with visit_tab1:
        st.subheader("🎥 Visite Virtuelle 360°")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Simulation d'une visite 360°
            st.markdown("""
            <div style="background: #000; padding: 2rem; border-radius: 15px; text-align: center; color: white;">
                <h3>🏠 Appartement 3P - Bastille</h3>
                <div style="background: #333; height: 300px; border-radius: 10px; display: flex; align-items: center; justify-content: center; margin: 1rem 0;">
                    <div>
                        <div style="font-size: 4em;">📹</div>
                        <p>Visite 360° Interactive</p>
                        <p style="font-size: 0.9em; color: #ccc;">Cliquez et glissez pour explorer</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Contrôles de navigation
            nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)
            
            with nav_col1:
                if st.button("🚪 Entrée", use_container_width=True):
                    st.info("📍 Navigation vers l'entrée")
            with nav_col2:
                if st.button("🛋️ Salon", use_container_width=True):
                    st.info("📍 Navigation vers le salon")
            with nav_col3:
                if st.button("🍳 Cuisine", use_container_width=True):
                    st.info("📍 Navigation vers la cuisine")
            with nav_col4:
                if st.button("🛏️ Chambre", use_container_width=True):
                    st.info("📍 Navigation vers la chambre")
        
        with col2:
            st.markdown("### 🎛️ Outils de visite")
            
            # Outils interactifs
            show_measures = st.checkbox("📏 Afficher les mesures", value=True)
            show_furniture = st.checkbox("🪑 Meubles virtuels", value=False)
            show_lighting = st.checkbox("💡 Éclairage naturel", value=True)
            time_of_day = st.select_slider("🕐 Heure de la journée", 
                                         options=["Matin", "Midi", "Après-midi", "Soir"], 
                                         value="Après-midi")
            
            st.divider()
            
            st.markdown("### 📊 Informations")
            st.metric("Surface", "75m²")
            st.metric("Pièces", "3")
            st.metric("Étage", "4/6")
            st.metric("Orientation", "Sud-Ouest")
            
            if st.button("📤 Partager la vi1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Évolution des vues de profil
            dates = pd.date_range('2024-08-01', periods=30, freq='D')
            vues = np.random.poisson(12, 30) + np.sin(np.arange(30) * 0.2) * 3 + 12
            
            fig = px.line(x=dates, y=vues, title='📊 Évolution des vues de profil')
            fig.update_traces(line_color='#667eea', line_width=3)
            fig.add_hline(y=np.mean(vues), line_dash="dash", line_color="red", 
                         annotation_text="Moyenne")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Taux de réponse aux contacts
            response_data = pd.DataFrame({
                'Semaine': ['S-4', 'S-3', 'S-2', 'S-1'],
                'Envoyés': [12, 15, 18, 22],
                'Réponses': [8, 11, 14, 17]
            })
            
            fig = px.bar(response_data, x='Semaine', y=['Envoyés', 'Réponses'], 
                        title='📧 Messages envoyés vs réponses', barmode='group')
            st.plotly_chart(fig, use_container_width=True)
    
    with analytics_tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribution des scores de matching
            scores = np.random.normal(75, 15, 100)
            scores = np.clip(scores, 0, 100)
            
            fig = px.histogram(x=scores, nbins=20, title='📊 Distribution des scores de matching')
            fig.update_traces(marker_color='#667eea')
            fig.add_vline(x=np.mean(scores), line_dash="dash", line_color="red",
                         annotation_text=f"Moyenne: {np.mean(scores):.1f}%")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Top critères de matching
            criteres_data = pd.DataFrame({
                'Critère': ['Budget', 'Localisation', 'Surface', 'Transport', 'Type bien'],
                'Importance': [95, 88, 82, 76, 71]
            })
            
            fig = px.bar(criteres_data, x='Importance', y='Critère', 
                        title='🎯 Importance des critères', orientation='h')
            fig.update_traces(marker_color='#28a745')
            st.plotly_chart(fig, use_container_width=True)
    
    with analytics_tab
