import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
import plotly.express as px
import plotly.graph_objects as go
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import json
import hashlib
import requests
import folium
from streamlit_folium import folium_static
import time

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

# Classe pour l'authentification (version simplifiée sans DB)
class AuthManager:
    @staticmethod
    def hash_password(password):
        """Hasher un mot de passe"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verify_password(password, hashed):
        """Vérifier un mot de passe"""
        return AuthManager.hash_password(password) == hashed

# Classe pour les services géographiques
class GeoService:
    @staticmethod
    def get_coordinates(address):
        """Obtenir les coordonnées d'une adresse"""
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
        m = folium.Map(location=[48.8566, 2.3522], zoom_start=6)
        
        for prop in properties:
            coords = GeoService.get_coordinates(prop.get('ville', 'Paris'))
            
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
        if surface_souhaitee > 0:
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

# Initialisation des services
@st.cache_resource
def init_services():
    auth = AuthManager()
    geo = GeoService()
    ai = AIService()
    return auth, geo, ai

auth, geo, ai = init_services()

# Initialisation du state avec données en mémoire
if 'user' not in st.session_state:
    st.session_state.user = None
if 'users_db' not in st.session_state:
    st.session_state.users_db = {}
if 'profiles_db' not in st.session_state:
    st.session_state.profiles_db = {}
if 'properties_db' not in st.session_state:
    # Données de démonstration
    st.session_state.properties_db = {
        "prop_1": {
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
        "prop_2": {
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
        "prop_3": {
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
    }
if 'notifications' not in st.session_state:
    st.session_state.notifications = []
if 'ai_messages' not in st.session_state:
    st.session_state.ai_messages = []

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
            if st.session_state.notifications:
                for notif in st.session_state.notifications:
                    st.info(f"📧 {notif}")
            else:
                st.info("Aucune nouvelle notification")

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
                    if email in st.session_state.users_db:
                        stored_hash = st.session_state.users_db[email]['password_hash']
                        if auth.verify_password(password, stored_hash):
                            st.session_state.user = {
                                'email': email,
                                'user_type': st.session_state.users_db[email]['user_type']
                            }
                            st.success("✅ Connexion réussie !")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Mot de passe incorrect")
                    else:
                        st.error("❌ Email non trouvé")
        
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
                    elif reg_email in st.session_state.users_db:
                        st.error("❌ Cette adresse email est déjà utilisée")
                    else:
                        st.session_state.users_db[reg_email] = {
                            'password_hash': auth.hash_password(reg_password),
                            'user_type': user_type,
                            'created_at': datetime.now().isoformat()
                        }
                        st.success("✅ Compte créé avec succès !")
                        st.session_state.notifications.append("🎉 Bienvenue sur imoMatch !")
                        time.sleep(1)
                        st.rerun()
    
    else:
        # Navigation pour utilisateur connecté
        st.success(f"👤 {st.session_state.user['user_type']}")
        
        # Affichage des notifications
        if st.session_state.notifications:
            st.subheader("🔔 Notifications")
            for i, notif in enumerate(st.session_state.notifications[:3]):
                st.markdown(f"""
                <div class="notification">
                    <small>{notif}</small>
                </div>
                """, unsafe_allow_html=True)
            
            if st.button("Marquer comme lues"):
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
    st.header("🏠 Dashboard Personnel")
    
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
                    age = st.number_input("🎂 Âge", min_value=18, max_value=100, value=30)
                    profession = st.text_input("💼 Profession")
                    
                with col2:
                    situation = st.selectbox("👨‍👩‍👧‍👦 Situation familiale", 
                                           ["Célibataire", "En couple", "Marié(e)", "Divorcé(e)"])
                    revenus = st.number_input("💰 Revenus mensuels nets (€)", min_value=0, value=3000)
                    enfants = st.number_input("👶 Nombre d'enfants", min_value=0, value=0)
                    animaux = st.checkbox("🐕 Animaux de compagnie")
                
                if st.form_submit_button("💾 Sauvegarder", use_container_width=True):
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
                    
                    # Sauvegarder en mémoire
                    st.session_state.profiles_db[st.session_state.user['email']] = profile_data
                    
                    st.success("✅ Profil mis à jour avec succès !")
                    st.session_state.notifications.append("📝 Profil mis à jour - Votre score de matching va s'améliorer !")
        
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
                
                if st.form_submit_button("🎯 Sauvegarder les critères", use_container_width=True):
                    criteria = {
                        "transaction_type": transaction_type,
                        "budget_min": budget_min,
                        "budget_max": budget_max,
                        "surface_min": surface_min,
                        "pieces_min": pieces_min,
                        "pieces_max": pieces_max,
                        "type_bien": type_bien,
                        "villes": villes,
                        "balcon": balcon,
                        "parking": parking,
                        "ascenseur": ascenseur
                    }
                    
                    # Sauvegarde des critères
                    criteria_key = f"{st.session_state.user['email']}_criteria"
                    st.session_state.profiles_db[criteria_key] = criteria
                    
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
                            st.session_state.users_db[st.session_state.user['email']]['password_hash'] = auth.hash_password(new_password)
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
        # Propriétés recommandées avec IA
        fake_profile = {
            "budget_max": prix_max * 1000,
            "surface_souhaitee": 80,
            "type_bien": "appartement",
            "villes_souhaitees": ["paris", "vincennes"]
        }
        
        properties_list = list(st.session_state.properties_db.values())
        
        for prop in properties_list:
            score, factors = ai.calculate_compatibility_score(fake_profile, prop)
            
            if score >= score_min:
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
                        st.session_state.notifications.append(f"📧 Contact envoyé pour {prop['titre']}")
                    
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
            nb_results = np.random.randint(15, 45)
            st.success(f"✅ {nb_results} biens trouvés correspondant à vos critères !")
            
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
        # Filtrer les propriétés selon les critères
        filtered_props = []
        for prop in st.session_state.properties_db.values():
            if (prop['type'] in map_types and 
                prop['prix'] <= map_budget_max * 1000):
                filtered_props.append(prop)
        
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
            st.metric("Biens disponibles", len(filtered_props), "+8")

elif page == "ai_agent":
    st.header("🤖 Agent IA - Assistant Personnel Immobilier")
    
    # Interface de chat avancée
    chat_col1, chat_col2 = st.columns([3, 1])
    
    with chat_col2:
        st.subheader("🎯 Actions rapides")
        
        if st.button("🔍 Analyser le marché", use_container_width=True):
            st.session_state.ai_messages.append({
                "role": "assistant", 
                "content": "📊 D'après mon analyse, le marché est dynamique avec une hausse de 3.2% des prix. Je recommande de regarder les secteurs en développement comme Belleville ou République."
            })
            st.rerun()
        
        if st.button("💡 Conseils personnalisés", use_container_width=True):
            st.session_state.ai_messages.append({
                "role": "assistant", 
                "content": "💡 Basé sur votre profil, je suggère d'élargir votre recherche aux villes limitrophes. Vous pourriez gagner 20% sur le prix au m² !"
            })
            st.rerun()
        
        if st.button("📈 Prédictions prix", use_container_width=True):
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
        if not st.session_state.ai_messages:
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
    
    with analytics_tab1:
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
    
    with analytics_tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            # Évolution des prix par ville
            dates = pd.date_range('2024-01-01', periods=12, freq='M')
            paris_prices = 9000 + np.cumsum(np.random.normal(20, 50, 12))
            lyon_prices = 5000 + np.cumsum(np.random.normal(10, 30, 12))
            marseille_prices = 4500 + np.cumsum(np.random.normal(15, 25, 12))
            
            villes_data = pd.DataFrame({
                'Mois': dates,
                'Paris': paris_prices,
                'Lyon': lyon_prices,
                'Marseille': marseille_prices
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
        current_plan = "Gratuit"
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
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.button("📋 Plan actuel", disabled=True, use_container_width=True)
    
    with plans_col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); padding: 2rem; border-radius: 15px; border: 3px solid #f0a500; text-align: center;">
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
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Passer à Premium", use_container_width=True):
            st.balloons()
            st.success("🎉 Simulation : Bienvenue dans Premium !")
            st.session_state.notifications.append("🎉 Upgrade vers Premium réalisé !")
    
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
                <p>✅ Support dédié</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("👑 Devenir Pro", use_container_width=True):
            st.success("👔 Demande envoyée ! Un conseiller vous contactera.")

elif page == "marketplace":
    st.header("🏢 Marketplace des Services Immobiliers")
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 2rem; border-radius: 15px; color: white; margin-bottom: 2rem; text-align: center;">
        <h2 style="margin: 0; color: white;">🌟 Écosystème Complet Immobilier</h2>
        <p style="margin: 0.5rem 0 0 0; font-size: 1.1em;">Tous les professionnels dont vous avez besoin, pré-sélectionnés et notés</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Services disponibles
    service_col1, service_col2, service_col3 = st.columns(3)
    
    with service_col1:
        st.markdown("""
        <div class="metric-card">
            <h3>🏦 Financement</h3>
            <p><strong>3 banques partenaires</strong></p>
            <p>• Crédit Agricole - 3.85%</p>
            <p>• BNP Paribas - 4.10%</p>
            <p>• Courtier imoFinance - 3.75%</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🏦 Voir les offres", key="finance", use_container_width=True):
            st.success("💰 Redirection vers nos partenaires financiers...")
    
    with service_col2:
        st.markdown("""
        <div class="metric-card">
            <h3>⚖️ Juridique</h3>
            <p><strong>25 notaires référencés</strong></p>
            <p>• Me. Dubois - Paris 15e</p>
            <p>• Me. Martin - Lyon 6e</p>
            <p>• Conseil juridique inclus</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("⚖️ Consulter", key="juridique", use_container_width=True):
            st.success("📋 Mise en relation avec nos juristes...")
    
    with service_col3:
        st.markdown("""
        <div class="metric-card">
            <h3>🔧 Expertise</h3>
            <p><strong>15+ diagnostiqueurs</strong></p>
            <p>• DPE, Termites, Plomb</p>
            <p>• Expertise structure</p>
            <p>• Tarifs négociés -20%</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔧 Commander", key="expertise", use_container_width=True):
            st.success("🔍 Commande d'expertise en cours...")

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
            
            if st.button("📤 Partager la visite", use_container_width=True):
                st.success("🔗 Lien de partage généré !")
    
    with visit_tab2:
        st.subheader("🥽 Expérience de Réalité Virtuelle")
        
        vr_col1, vr_col2 = st.columns([1, 1])
        
        with vr_col1:
            st.markdown("""
            ### 🎮 Visites VR Immersives
            
            **Équipements compatibles :**
            - 🥽 Oculus Quest 2/3
            - 🎮 PlayStation VR
            - 📱 Smartphone + Casque VR
            - 💻 PC + Casque VR
            
            **Fonctionnalités VR :**
            - 👋 Interaction gestuelle
            - 🚶‍♂️ Déplacement naturel  
            - 📏 Mesures en temps réel
            - 🪑 Placement de meubles
            - 🎨 Changement déco en direct
            """)
            
            if st.button("🥽 Lancer VR", use_container_width=True):
                st.info("🚀 Simulation : Ouverture de l'application VR...")
                st.markdown("""
                <div class="ai-chat">
                    <strong>🎮 Mode VR activé !</strong><br>
                    Simulation : Mettez votre casque et utilisez les manettes pour explorer librement l'appartement.
                    <br><br>
                    💡 <em>Astuce: Pointez vers un objet et appuyez sur le trigger pour obtenir des informations.</em>
                </div>
                """, unsafe_allow_html=True)
        
        with vr_col2:
            # Simulation d'interface VR
            st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 15px; color: white; text-align: center;">
                <h3 style="color: white;">🏠 Interface VR</h3>
                
                <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; margin: 1rem 0;">
                    <h4 style="color: white;">📍 Position actuelle</h4>
                    <p style="color: #ddd;">Salon - Vue vers cuisine</p>
                </div>
                
                <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; margin: 1rem 0;">
                    <h4 style="color: white;">🎛️ Contrôles</h4>
                    <div style="display: flex; justify-content: space-around; color: #ddd;">
                        <div>🎮 Déplacer</div>
                        <div>👆 Sélectionner</div>
                        <div>📏 Mesurer</div>
                    </div>
                </div>
                
                <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px;">
                    <h4 style="color: white;">ℹ️ Objet sélectionné</h4>
                    <p style="color: #ddd;">Fenêtre principale<br>Dimensions: 1.2m x 1.8m<br>Orientation: Sud</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with visit_tab3:
        st.subheader("📱 Réalité Augmentée Mobile")
        
        ar_col1, ar_col2 = st.columns([2, 1])
        
        with ar_col1:
            st.markdown("""
            ### 📲 Application imoMatch AR
            
            Scannez le QR code ci-dessous avec votre smartphone pour lancer l'expérience AR :
            """)
            
            # QR Code simulé
            st.markdown("""
            <div style="background: white; padding: 2rem; border-radius: 15px; text-align: center; border: 2px solid #667eea;">
                <div style="font-size: 8em;">📱</div>
                <h3>QR Code AR</h3>
                <p style="color: #666;">Pointez votre caméra ici</p>
                <p style="font-size: 0.9em; color: #999;">Compatible iOS 12+ et Android 8+</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            **Fonctionnalités AR :**
            - 📐 Mesures précises avec la caméra
            - 🪑 Placement virtuel de meubles
            - 🎨 Test de couleurs murales
            - 💡 Simulation d'éclairage
            - 📷 Capture photo/vidéo annotée
            """)
        
        with ar_col2:
            st.markdown("### 🔧 Outils AR")
            
            # Outils AR
            ar_tool = st.selectbox("Outil sélectionné", [
                "📏 Mètre laser",
                "🪑 Placement mobilier", 
                "🎨 Peinture murale",
                "💡 Éclairage",
                "📷 Annotation"
            ])
            
            if ar_tool == "📏 Mètre laser":
                st.info("📏 Pointez deux endroits pour mesurer la distance")
            elif ar_tool == "🪑 Placement mobilier":
                furniture = st.selectbox("Meuble", ["Canapé", "Table", "Lit", "Armoire"])
                st.info(f"🪑 Glissez pour placer le {furniture.lower()}")
            elif ar_tool == "🎨 Peinture murale":
                color = st.color_picker("Couleur", "#FF6B6B")
                st.info("🎨 Touchez un mur pour appliquer la couleur")
    
    # Galerie de visites disponibles
    st.subheader("🎬 Galerie des Visites Virtuelles")
    
    # Liste des biens avec visites virtuelles
    visites_disponibles = [
        {
            "titre": "Appartement 3P - Bastille",
            "type": "Appartement",
            "prix": "485k€",
            "visites": ["360°", "VR", "AR"],
            "vues": 1247,
            "note": 4.8,
            "duree": "12 min"
        },
        {
            "titre": "Maison 5P - Vincennes", 
            "type": "Maison",
            "prix": "680k€",
            "visites": ["360°", "AR"],
            "vues": 892,
            "note": 4.6,
            "duree": "18 min"
        },
        {
            "titre": "Loft 2P - République",
            "type": "Loft", 
            "prix": "520k€",
            "visites": ["360°", "VR"],
            "vues": 654,
            "note": 4.7,
            "duree": "8 min"
        }
    ]
    
    gallery_col1, gallery_col2 = st.columns([3, 1])
    
    with gallery_col2:
        st.markdown("### 🔍 Filtres")
        filter_type = st.multiselect("Type de bien", ["Appartement", "Maison", "Studio", "Loft"], default=["Appartement", "Maison", "Loft"])
        filter_visit_type = st.multiselect("Type de visite", ["360°", "VR", "AR"], default=["360°", "VR", "AR"])
        sort_by = st.selectbox("Trier par", ["Plus populaires", "Plus récentes", "Mieux notées", "Prix croissant"])
    
    with gallery_col1:
        # Affichage des visites filtrées
        for visite in visites_disponibles:
            if (visite['type'] in filter_type and 
                any(v in filter_visit_type for v in visite['visites'])):
                
                st.markdown(f"""
                <div class="property-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h4 style="margin: 0; color: #667eea;">{visite['titre']}</h4>
                            <p style="margin: 0.2rem 0; color: #666;">{visite['type']} • {visite['prix']} • ⏱️ {visite['duree']}</p>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 1.2em; font-weight: bold;">⭐ {visite['note']}</div>
                            <div style="font-size: 0.9em; color: #666;">👁️ {visite['vues']} vues</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Boutons de visite
                visit_col1, visit_col2, visit_col3, visit_col4 = st.columns(4)
                
                with visit_col1:
                    if "360°" in visite['visites']:
                        if st.button(f"🎥 Visite 360°", key=f"360_{visite['titre']}"):
                            st.success("🎬 Lancement de la visite 360°...")
                    else:
                        st.button("🎥 360° (N/A)", disabled=True)
                
                with visit_col2:
                    if "VR" in visite['visites']:
                        if st.button(f"🥽 Mode VR", key=f"vr_{visite['titre']}"):
                            st.info("🚀 Préparation de l'expérience VR...")
                    else:
                        st.button("🥽 VR (N/A)", disabled=True)
                
                with visit_col3:
                    if "AR" in visite['visites']:
                        if st.button(f"📱 AR Mobile", key=f"ar_{visite['titre']}"):
                            st.info("📲 Ouverture de l'app mobile...")
                    else:
                        st.button("📱 AR (N/A)", disabled=True)
                
                with visit_col4:
                    if st.button(f"❤️ Favoris", key=f"fav_vt_{visite['titre']}"):
                        st.success("💖 Ajouté aux favoris !")
                        st.session_state.notifications.append(f"❤️ {visite['titre']} ajouté aux favoris")
                
                st.divider()

# Section footer avec statistiques et contact
st.markdown("---")

footer_col1, footer_col2, footer_col3 = st.columns(3)

with footer_col1:
    st.markdown("""
    ### 📊 Statistiques Plateforme
    
    - 👥 **15,247** utilisateurs actifs
    - 🏠 **3,891** biens référencés  
    - 🎯 **2,156** matches réalisés
    - ⭐ **4.8/5** satisfaction moyenne
    """)

with footer_col2:
    st.markdown("""
    ### 🤝 Nos Partenaires
    
    - 🏦 **25** banques partenaires
    - ⚖️ **150** notaires référencés
    - 🏢 **89** agences immobilières
    - 🔧 **200+** professionnels certifiés
    """)

with footer_col3:
    st.markdown("""
    ### 📞 Support & Contact
    
    - 💬 **Chat IA 24/7** 
    - 📧 support@imomatch.com
    - 📱 +33 6 74 55 44 32
    - 🕐 Support : Lun-Ven 9h-18h
    """)

# Footer principal avec informations sur le fondateur
st.markdown("""
<div style="text-align: center; padding: 3rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; margin-top: 3rem; color: white;">
    <h2 style="color: white; margin: 0;">🏠 imoMatch - La révolution immobilière par l'IA</h2>
    <p style="font-size: 1.2em; margin: 1rem 0; color: #ddd;">Un Demandeur, Un Logement, Une Vente</p>
    
    <div style="background: rgba(255,255,255,0.1); padding: 2rem; border-radius: 10px; margin: 2rem 0;">
        <h3 style="color: white;">👨‍💻 Yann Gouedo - Fondateur</h3>
        <p style="color: #ddd; font-style: italic; font-size: 1.1em;">
        "Ma motivation quotidienne est d'aider les citoyens et les entreprises à optimiser leur prise de décision grâce à l'intelligence artificielle, et ainsi les rendre plus efficaces."
        </p>
        <p style="color: #ddd;">
        <strong>📧 Contact :</strong> +33 6 74 55 44 32 | yann@imomatch.com<br>
        <strong>💼 Profil :</strong> Ingénieur en Mathématiques Appliquées, Expert Data Science & IA
        </p>
    </div>
    
    <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap; margin-top: 2rem;">
        <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px;">
            <strong>🎯 Mission</strong><br>
            Démocratiser l'immobilier par l'IA
        </div>
        <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px;">
            <strong>🚀 Vision</strong><br>
            L'UBER de l'immobilier
        </div>
        <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px;">
            <strong>💡 Innovation</strong><br>
            Data Science & IA appliquées
        </div>
    </div>
    
    <p style="margin-top: 2rem; font-size: 0.9em; color: #bbb;">
        © 2024 imoMatch - Tous droits réservés | Version MVP 1.0 - Compatible Streamlit Cloud
    </p>
</div>
""", unsafe_allow_html=True)

# Message de bienvenue pour les nouveaux utilisateurs
if st.session_state.user and len(st.session_state.notifications) == 0:
    st.session_state.notifications.append("🎉 Bienvenue sur imoMatch ! Complétez votre profil pour des recommandations personnalisées.")
