import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import time
import sqlite3
from datetime import datetime, timedelta
import requests
from PIL import Image
import io
import base64
import os

# Configuration de la page
st.set_page_config(
    page_title="imoMatch - Votre assistant immobilier intelligent",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Gestion des langues
def load_translations(lang):
    translations = {
        "fr": {
            "title": "imoMatch - Votre assistant immobilier intelligent",
            "welcome": "Bienvenue sur imoMatch",
            "tagline": "La plateforme qui révolutionne votre recherche immobilière grâce à l'IA",
            "login": "Connexion",
            "signup": "Inscription",
            "logout": "Déconnexion",
            "dashboard": "Tableau de bord",
            "profile": "Mes informations",
            "search": "Recherche",
            "ai_agent": "Agent IA",
            "settings": "Paramètres",
            "theme": "Thème",
            "light": "Clair",
            "dark": "Sombre",
            "language": "Langue",
            "french": "Français",
            "english": "Anglais",
            "stats": "Statistiques",
            "partners": "Partenaires",
            "contact": "Contact",
            "free_tier": "Gratuit",
            "premium_tier": "Premium (14 jours d'essai)",
            "pro_tier": "Professionnel",
            "name": "Nom complet",
            "email": "Email",
            "phone": "Téléphone",
            "budget": "Budget",
            "location": "Localisation recherchée",
            "property_type": "Type de bien",
            "size": "Surface souhaitée (m²)",
            "rooms": "Nombre de pièces",
            "features": "Équipements souhaités",
            "save": "Enregistrer",
            "update": "Mettre à jour",
            "edit": "Modifier",
            "preferences": "Préférences",
            "recommendations": "Recommandations",
            "advanced_search": "Recherche avancée",
            "search_results": "Résultats de recherche",
            "map_view": "Vue carte",
            "list_view": "Vue liste",
            "property_details": "Détails du bien",
            "contact_agent": "Contacter un agent",
            "ai_assistant": "Assistant IA imoMatch",
            "ai_help": "Comment puis-je vous aider à affiner votre recherche aujourd'hui?",
            "ask_question": "Posez votre question...",
            "send": "Envoyer",
            "clear": "Effacer"
        },
        "en": {
            "title": "imoMatch - Your Intelligent Real Estate Assistant",
            "welcome": "Welcome to imoMatch",
            "tagline": "The platform that revolutionizes your property search with AI",
            "login": "Login",
            "signup": "Sign up",
            "logout": "Logout",
            "dashboard": "Dashboard",
            "profile": "My Information",
            "search": "Search",
            "ai_agent": "AI Agent",
            "settings": "Settings",
            "theme": "Theme",
            "light": "Light",
            "dark": "Dark",
            "language": "Language",
            "french": "French",
            "english": "English",
            "stats": "Statistics",
            "partners": "Partners",
            "contact": "Contact",
            "free_tier": "Free",
            "premium_tier": "Premium (14-day trial)",
            "pro_tier": "Professional",
            "name": "Full name",
            "email": "Email",
            "phone": "Phone",
            "budget": "Budget",
            "location": "Desired location",
            "property_type": "Property type",
            "size": "Desired surface (m²)",
            "rooms": "Number of rooms",
            "features": "Desired amenities",
            "save": "Save",
            "update": "Update",
            "edit": "Edit",
            "preferences": "Preferences",
            "recommendations": "Recommendations",
            "advanced_search": "Advanced search",
            "search_results": "Search results",
            "map_view": "Map view",
            "list_view": "List view",
            "property_details": "Property details",
            "contact_agent": "Contact agent",
            "ai_assistant": "imoMatch AI Assistant",
            "ai_help": "How can I help you refine your search today?",
            "ask_question": "Ask your question...",
            "send": "Send",
            "clear": "Clear"
        }
    }
    return translations.get(lang, translations["fr"])

# Initialisation de la session state
def init_session_state():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user" not in st.session_state:
        st.session_state.user = None
    if "user_tier" not in st.session_state:
        st.session_state.user_tier = "free"
    if "theme" not in st.session_state:
        st.session_state.theme = "light"
    if "language" not in st.session_state:
        st.session_state.language = "fr"
    if "db_initialized" not in st.session_state:
        st.session_state.db_initialized = False
    if "ai_conversation" not in st.session_state:
        st.session_state.ai_conversation = []

# Initialisation de la base de données
def init_database():
    if not st.session_state.db_initialized:
        conn = sqlite3.connect('imomatch.db')
        c = conn.cursor()
        
        # Table des utilisateurs
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     name TEXT NOT NULL,
                     email TEXT UNIQUE NOT NULL,
                     phone TEXT,
                     password TEXT NOT NULL,
                     tier TEXT NOT NULL DEFAULT 'free',
                     subscription_date DATE,
                     trial_end_date DATE,
                     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        # Table des profils utilisateurs
        c.execute('''CREATE TABLE IF NOT EXISTS user_profiles
                     (user_id INTEGER PRIMARY KEY,
                     budget REAL,
                     location TEXT,
                     property_type TEXT,
                     size INTEGER,
                     rooms INTEGER,
                     features TEXT,
                     preferences TEXT,
                     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                     FOREIGN KEY (user_id) REFERENCES users (id))''')
        
        # Table des propriétés
        c.execute('''CREATE TABLE IF NOT EXISTS properties
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     title TEXT NOT NULL,
                     description TEXT,
                     price REAL NOT NULL,
                     location TEXT NOT NULL,
                     property_type TEXT NOT NULL,
                     size REAL NOT NULL,
                     rooms INTEGER NOT NULL,
                     features TEXT,
                     latitude REAL,
                     longitude REAL,
                     agent_id INTEGER,
                     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        # Insertion de données exemple si nécessaire
        c.execute("SELECT COUNT(*) FROM properties")
        if c.fetchone()[0] == 0:
            sample_properties = [
                ("Appartement lumineux", "Bel appartement de 75m² avec terrasse", 350000, "Paris 15ème", "apartment", 75, 3, "terrasse, ascenseur, cave", 48.841, 2.287, 1),
                ("Maison de caractère", "Maison avec jardin proche centre ville", 495000, "Bordeaux", "house", 110, 4, "jardin, garage, cheminée", 44.837, -0.579, 2),
                ("Studio étudiant", "Studio meublé proche université", 185000, "Lyon", "apartment", 25, 1, "meublé, digicode", 45.748, 4.847, 3)
            ]
            c.executemany('''INSERT INTO properties 
                          (title, description, price, location, property_type, size, rooms, features, latitude, longitude, agent_id)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', sample_properties)
        
        conn.commit()
        conn.close()
        st.session_state.db_initialized = True

# Fonctions de base de données
def get_db_connection():
    return sqlite3.connect('imomatch.db')

def get_user_by_email(email):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    conn.close()
    return user

def create_user(name, email, phone, password, tier='free'):
    conn = get_db_connection()
    c = conn.cursor()
    trial_end = datetime.now() + timedelta(days=14) if tier == 'premium' else None
    c.execute('''INSERT INTO users (name, email, phone, password, tier, subscription_date, trial_end_date)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
                 (name, email, phone, password, tier, datetime.now(), trial_end))
    user_id = c.lastrowid
    conn.commit()
    conn.close()
    return user_id

def get_user_profile(user_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,))
    profile = c.fetchone()
    conn.close()
    return profile

def update_user_profile(user_id, data):
    conn = get_db_connection()
    c = conn.cursor()
    
    # Vérifier si le profil existe déjà
    c.execute("SELECT COUNT(*) FROM user_profiles WHERE user_id = ?", (user_id,))
    if c.fetchone()[0] > 0:
        # Mise à jour
        c.execute('''UPDATE user_profiles 
                     SET budget=?, location=?, property_type=?, size=?, rooms=?, features=?, preferences=?, updated_at=?
                     WHERE user_id=?''',
                     (data['budget'], data['location'], data['property_type'], data['size'], 
                      data['rooms'], data['features'], data.get('preferences', ''), datetime.now(), user_id))
    else:
        # Insertion
        c.execute('''INSERT INTO user_profiles 
                     (user_id, budget, location, property_type, size, rooms, features, preferences)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                     (user_id, data['budget'], data['location'], data['property_type'], data['size'], 
                      data['rooms'], data['features'], data.get('preferences', '')))
    
    conn.commit()
    conn.close()

def get_properties(filters=None):
    conn = get_db_connection()
    
    query = "SELECT * FROM properties"
    params = []
    
    if filters:
        conditions = []
        if 'property_type' in filters and filters['property_type']:
            conditions.append("property_type = ?")
            params.append(filters['property_type'])
        if 'location' in filters and filters['location']:
            conditions.append("location LIKE ?")
            params.append(f'%{filters["location"]}%')
        if 'min_price' in filters and filters['min_price']:
            conditions.append("price >= ?")
            params.append(filters['min_price'])
        if 'max_price' in filters and filters['max_price']:
            conditions.append("price <= ?")
            params.append(filters['max_price'])
        if 'min_size' in filters and filters['min_size']:
            conditions.append("size >= ?")
            params.append(filters['min_size'])
        if 'min_rooms' in filters and filters['min_rooms']:
            conditions.append("rooms >= ?")
            params.append(filters['min_rooms'])
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

# Gestion de l'authentification
def login_user(email, password):
    user = get_user_by_email(email)
    if user and user[4] == password:  # Index 4 correspond au mot de passe
        st.session_state.authenticated = True
        st.session_state.user = user
        st.session_state.user_tier = user[5]  # Index 5 correspond au tier
        return True
    return False

def logout_user():
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.user_tier = "free"

# Composants d'interface
def display_header():
    t = load_translations(st.session_state.language)
    
    # Charger le logo (à remplacer par votre logo réel)
    try:
        logo = Image.open("logo_imomatch.png")
    except:
        # Créer un logo temporaire si le fichier n'existe pas
        logo = Image.new('RGB', (200, 60), color=(255, 102, 0))
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.image(logo, width=200)
    with col2:
        st.title(t['title'])
    with col3:
        if st.session_state.authenticated:
            if st.button(t['logout']):
                logout_user()
                st.rerun()
        else:
            if st.button(t['login']):
                st.session_state.show_login = True
                st.rerun()

def display_sidebar():
    t = load_translations(st.session_state.language)
    
    with st.sidebar:
        st.header("Navigation")
        
        if st.session_state.authenticated:
            menu_options = [t['dashboard'], t['profile'], t['search'], t['ai_agent']]
            choice = st.radio("", menu_options)
            
            st.divider()
            st.header(t['settings'])
            
            # Sélecteur de thème
            theme = st.selectbox(t['theme'], [t['light'], t['dark']], 
                                index=0 if st.session_state.theme == "light" else 1)
            if theme != st.session_state.theme:
                st.session_state.theme = "light" if theme == t['light'] else "dark"
                st.rerun()
            
            # Sélecteur de langue
            lang = st.selectbox(t['language'], [t['french'], t['english']], 
                               index=0 if st.session_state.language == "fr" else 1)
            if lang != st.session_state.language:
                st.session_state.language = "fr" if lang == t['french'] else "en"
                st.rerun()
                
            return choice
        else:
            return None

def apply_theme():
    if st.session_state.theme == "dark":
        st.markdown("""
        <style>
        .stApp {
            background-color: #1E1E1E;
            color: #FFFFFF;
        }
        .css-18e3th9 {
            background-color: #1E1E1E;
        }
        .css-1d391kg {
            background-color: #1E1E1E;
        }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        .stApp {
            background-color: #FFFFFF;
            color: #000000;
        }
        </style>
        """, unsafe_allow_html=True)

# Pages de l'application
def login_signup_page():
    t = load_translations(st.session_state.language)
    
    st.title(t['welcome'])
    st.subheader(t['tagline'])
    
    tab1, tab2, tab3 = st.tabs([t['free_tier'], t['premium_tier'], t['pro_tier']])
    
    with tab1:
        st.header(t['free_tier'])
        st.write("Accès aux fonctionnalités de base")
        st.write("✅ Recherche limitée")
        st.write("✅ 5 contacts/mois")
        st.write("❌ Pas d'assistance prioritaire")
        
        if st.button(f"Choisir {t['free_tier']}", key="free_btn"):
            st.session_state.show_signup = True
            st.session_state.selected_tier = "free"
    
    with tab2:
        st.header(t['premium_tier'])
        st.write("Accès complet avec essai gratuit")
        st.write("✅ Recherche illimitée")
        st.write("✅ Contacts illimités")
        st.write("✅ Assistance prioritaire")
        st.write("🎯 14 jours d'essai gratuit")
        
        if st.button(f"Choisir {t['premium_tier']}", key="premium_btn"):
            st.session_state.show_signup = True
            st.session_state.selected_tier = "premium"
    
    with tab3:
        st.header(t['pro_tier'])
        st.write("Pour les professionnels de l'immobilier")
        st.write("✅ Tous les avantages Premium")
        st.write("✅ Outils de gestion avancés")
        st.write("✅ Support dédié 24/7")
        st.write("✅ Statistiques détaillées")
        
        if st.button(f"Choisir {t['pro_tier']}", key="pro_btn"):
            st.session_state.show_signup = True
            st.session_state.selected_tier = "pro"
    
    # Afficher les statistiques, partenaires et contacts
    st.divider()
    display_stats()
    display_partners()
    display_contact()
    
    # Formulaire de connexion/inscription
    if st.session_state.get('show_login') or st.session_state.get('show_signup'):
        if st.session_state.get('show_login'):
            with st.form("login_form"):
                st.header(t['login'])
                email = st.text_input("Email")
                password = st.text_input("Mot de passe", type="password")
                submit = st.form_submit_button(t['login'])
                
                if submit:
                    if login_user(email, password):
                        st.success("Connexion réussie!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Email ou mot de passe incorrect")
        
        if st.session_state.get('show_signup'):
            with st.form("signup_form"):
                st.header(t['signup'])
                name = st.text_input(t['name'])
                email = st.text_input("Email")
                phone = st.text_input(t['phone'])
                password = st.text_input("Mot de passe", type="password")
                confirm_password = st.text_input("Confirmer le mot de passe", type="password")
                submit = st.form_submit_button(t['signup'])
                
                if submit:
                    if password != confirm_password:
                        st.error("Les mots de passe ne correspondent pas")
                    else:
                        user_id = create_user(name, email, phone, password, st.session_state.selected_tier)
                        st.success("Inscription réussie! Vous pouvez maintenant vous connecter.")
                        st.session_state.show_signup = False
                        st.session_state.show_login = True

def display_stats():
    t = load_translations(st.session_state.language)
    
    st.header(t['stats'])
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Utilisateurs actifs", "12,458", "+15%")
    with col2:
        st.metric("Biens disponibles", "34,721", "+8%")
    with col3:
        st.metric("Transactions/mois", "1,243", "+22%")
    
    # Graphique des prix moyens par région
    data = {
        'Région': ['Île-de-France', 'Auvergne-Rhône-Alpes', 'Nouvelle-Aquitaine', 'Occitanie', 'Provence-Alpes-Côte d\'Azur'],
        'Prix_m²': [6500, 3800, 2500, 2700, 4200]
    }
    df = pd.DataFrame(data)
    
    fig = px.bar(df, x='Région', y='Prix_m²', title="Prix moyen au m² par région")
    st.plotly_chart(fig)

def display_partners():
    t = load_translations(st.session_state.language)
    
    st.header(t['partners'])
    partners = [
        {"name": "Notaire de France", "logo": "🏛️", "description": "Réseau national de notaires"},
        {"name": "Crédit Immobilier", "logo": "💰", "description": "Solutions de financement adaptées"},
        {"name": "Home Inspection", "logo": "🔍", "description": "Experts en diagnostic immobilier"}
    ]
    
    for partner in partners:
        with st.expander(partner["name"]):
            st.write(partner["logo"] + " " + partner["description"])

def display_contact():
    t = load_translations(st.session_state.language)
    
    st.header(t['contact'])
    st.write("📞 01 23 45 67 89")
    st.write("✉️ contact@imomatch.fr")
    st.write("🏢 123 Avenue de l'Immobilier, 75000 Paris")
    
    with st.form("contact_form"):
        name = st.text_input("Votre nom")
        email = st.text_input("Votre email")
        message = st.text_area("Votre message")
        submit = st.form_submit_button("Envoyer")
        
        if submit:
            st.success("Message envoyé! Nous vous répondrons dans les 24h.")

def dashboard_page():
    t = load_translations(st.session_state.language)
    
    st.header(t['dashboard'])
    
    if st.session_state.user_tier == "free":
        st.warning("Vous utilisez la version gratuite. Passez à Premium pour débloquer toutes les fonctionnalités!")
    
    # Statistiques personnalisées
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Biens correspondants", "24", "+5")
    with col2:
        st.metric("Recherches sauvegardées", "3", "0")
    with col3:
        st.metric("Agents contactés", "2", "+1")
    
    # Recommandations personnalisées
    st.subheader(t['recommendations'])
    properties = get_properties()
    
    if not properties.empty:
        for _, prop in properties.head(3).iterrows():
            with st.container():
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image("https://via.placeholder.com/200x150?text=Property+Image", width=200)
                with col2:
                    st.subheader(prop['title'])
                    st.write(f"**{prop['price']:,.0f} €** - {prop['location']}")
                    st.write(f"{prop['size']} m² - {prop['rooms']} pièces")
                    st.write(prop['description'])
                    if st.button("Voir les détails", key=f"prop_{prop['id']}"):
                        st.session_state.selected_property = prop
                        st.rerun()
                st.divider()
    else:
        st.info("Aucune propriété ne correspond à vos critères. Essayez d'ajuster vos préférences.")

def profile_page():
    t = load_translations(st.session_state.language)
    
    st.header(t['profile'])
    
    # Récupérer les informations du profil
    profile = get_user_profile(st.session_state.user[0]) if st.session_state.user else None
    
    with st.form("profile_form"):
        name = st.text_input(t['name'], value=st.session_state.user[1] if st.session_state.user else "")
        email = st.text_input("Email", value=st.session_state.user[2] if st.session_state.user else "", disabled=True)
        phone = st.text_input(t['phone'], value=st.session_state.user[3] if st.session_state.user else "")
        
        st.subheader("Préférences de recherche")
        budget = st.slider(t['budget'], 50000, 1000000, 
                          value=int(profile[1]) if profile and profile[1] else 200000, 
                          step=10000) if profile else st.slider(t['budget'], 50000, 1000000, 200000, step=10000)
        
        location = st.text_input(t['location'], 
                                value=profile[2] if profile and profile[2] else "") if profile else st.text_input(t['location'])
        
        property_type = st.selectbox(t['property_type'], ["Appartement", "Maison", "Terrain", "Commercial"],
                                    index=0 if profile and profile[3] == "Appartement" else 
                                          1 if profile and profile[3] == "Maison" else
                                          2 if profile and profile[3] == "Terrain" else 3) if profile else st.selectbox(t['property_type'], ["Appartement", "Maison", "Terrain", "Commercial"])
        
        size = st.slider(t['size'], 20, 500, 
                        value=int(profile[4]) if profile and profile[4] else 80, 
                        step=5) if profile else st.slider(t['size'], 20, 500, 80, step=5)
        
        rooms = st.slider(t['rooms'], 1, 10, 
                         value=int(profile[5]) if profile and profile[5] else 3, 
                         step=1) if profile else st.slider(t['rooms'], 1, 10, 3, step=1)
        
        features = st.multiselect(t['features'], ["Balcon", "Terrasse", "Jardin", "Parking", "Cave", "Ascenseur", "Piscine"],
                                 default=profile[6].split(", ") if profile and profile[6] else []) if profile else st.multiselect(t['features'], ["Balcon", "Terrasse", "Jardin", "Parking", "Cave", "Ascenseur", "Piscine"])
        
        if st.form_submit_button(t['save']):
            profile_data = {
                'budget': budget,
                'location': location,
                'property_type': property_type,
                'size': size,
                'rooms': rooms,
                'features': ", ".join(features)
            }
            update_user_profile(st.session_state.user[0], profile_data)
            st.success("Profil mis à jour avec succès!")

def search_page():
    t = load_translations(st.session_state.language)
    
    st.header(t['search'])
    
    # Formulaire de recherche avancée
    with st.expander(t['advanced_search']):
        col1, col2 = st.columns(2)
        
        with col1:
            location = st.text_input(t['location'])
            min_price = st.number_input("Prix minimum", 0, 2000000, 0, 10000)
            max_price = st.number_input("Prix maximum", 0, 2000000, 1000000, 10000)
            property_type = st.selectbox(t['property_type'], ["Tous", "Appartement", "Maison", "Terrain", "Commercial"])
        
        with col2:
            min_size = st.number_input("Surface minimum (m²)", 0, 500, 0, 5)
            min_rooms = st.number_input("Pièces minimum", 0, 10, 0, 1)
            features = st.multiselect(t['features'], ["Balcon", "Terrasse", "Jardin", "Parking", "Cave", "Ascenseur", "Piscine"])
        
        search_clicked = st.button("Rechercher")
    
    # Affichage des résultats
    if search_clicked:
        filters = {
            'location': location if location != "" else None,
            'min_price': min_price if min_price > 0 else None,
            'max_price': max_price if max_price < 2000000 else None,
            'property_type': property_type if property_type != "Tous" else None,
            'min_size': min_size if min_size > 0 else None,
            'min_rooms': min_rooms if min_rooms > 0 else None
        }
        
        properties = get_properties(filters)
        
        if not properties.empty:
            st.subheader(f"{len(properties)} {t['search_results']}")
            
            # Options d'affichage
            view_option = st.radio("Mode d'affichage", [t['map_view'], t['list_view']])
            
            if view_option == t['map_view']:
                # Carte interactive
                if 'latitude' in properties.columns and 'longitude' in properties.columns:
                    properties = properties.dropna(subset=['latitude', 'longitude'])
                    if not properties.empty:
                        properties['size_str'] = properties['size'].astype(str) + ' m²'
                        properties['price_str'] = properties['price'].astype(str) + ' €'
                        
                        fig = px.scatter_mapbox(
                            properties, 
                            lat="latitude", 
                            lon="longitude", 
                            hover_name="title",
                            hover_data={"price_str": True, "size_str": True, "rooms": True, "location": True},
                            zoom=10,
                            height=600,
                            color="price",
                            color_continuous_scale=px.colors.sequential.Viridis
                        )
                        fig.update_layout(mapbox_style="open-street-map")
                        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Les données de localisation ne sont pas disponibles pour ces propriétés.")
            
            else:
                # Vue liste
                for _, prop in properties.iterrows():
                    with st.container():
                        col1, col2 = st.columns([1, 2])
                        with col1:
                            st.image("https://via.placeholder.com/200x150?text=Property+Image", width=200)
                        with col2:
                            st.subheader(prop['title'])
                            st.write(f"**{prop['price']:,.0f} €** - {prop['location']}")
                            st.write(f"{prop['size']} m² - {prop['rooms']} pièces")
                            st.write(prop['description'])
                            
                            col21, col22 = st.columns(2)
                            with col21:
                                if st.button("Voir les détails", key=f"detail_{prop['id']}"):
                                    st.session_state.selected_property = prop
                                    st.rerun()
                            with col22:
                                if st.button("Contacter", key=f"contact_{prop['id']}"):
                                    st.session_state.contact_property = prop
                                    st.rerun()
                        st.divider()
        else:
            st.info("Aucun résultat ne correspond à vos critères de recherche.")

def ai_agent_page():
    t = load_translations(st.session_state.language)
    
    st.header(t['ai_agent'])
    
    # Interface de chat
    st.subheader(t['ai_assistant'])
    st.write(t['ai_help'])
    
    # Affichage de la conversation
    for message in st.session_state.ai_conversation:
        if message['role'] == 'user':
            st.chat_message("user").write(message['content'])
        else:
            st.chat_message("assistant").write(message['content'])
    
    # Input utilisateur
    if prompt := st.chat_input(t['ask_question']):
        # Ajouter le message de l'utilisateur
        st.session_state.ai_conversation.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        
        # Simuler une réponse de l'IA
        response = simulate_ai_response(prompt)
        
        # Ajouter la réponse de l'IA
        st.session_state.ai_conversation.append({"role": "assistant", "content": response})
        st.chat_message("assistant").write(response)
    
    # Bouton pour effacer la conversation
    if st.button(t['clear']):
        st.session_state.ai_conversation = []
        st.rerun()

def simulate_ai_response(prompt):
    # Cette fonction simule une réponse de l'IA - à remplacer par une vraie intégration IA
    prompt_lower = prompt.lower()
    
    if "budget" in prompt_lower:
        return "Votre budget actuel est de 200 000 €. Souhaitez-vous que je vous aide à trouver des biens dans cette fourchette de prix ou voulez-vous le modifier?"
    elif "localisation" in prompt_lower or "ville" in prompt_lower or "endroit" in prompt_lower:
        return "Actuellement, vous recherchez dans la région Parisienne. Je peux vous suggérer des quartiers en fonction de vos préférences."
    elif "appartement" in prompt_lower or "maison" in prompt_lower:
        return "Vos préférences indiquent que vous cherchez un appartement. Souhaitez-vous explorer aussi des maisons ou rester sur ce type de bien?"
    elif "recommandation" in prompt_lower or "suggestion" in prompt_lower:
        return "En fonction de votre profil, je vous recommande de regarder les biens dans le 15ème arrondissement qui correspondent à vos critères de budget et surface."
    elif "merci" in prompt_lower:
        return "Je vous en prie! N'hésitez pas si vous avez d'autres questions."
    else:
        return "Je comprends que vous souhaitez des informations sur: " + prompt + ". Pouvez-vous préciser votre demande pour que je puisse vous aider au mieux?"

# Page de détail d'une propriété
def property_detail_page():
    if 'selected_property' in st.session_state:
        prop = st.session_state.selected_property
        t = load_translations(st.session_state.language)
        
        st.header(prop['title'])
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.image("https://via.placeholder.com/600x400?text=Property+Image", use_column_width=True)
            
            # Galerie d'images (simulée)
            st.subheader("Galerie photos")
            cols = st.columns(4)
            for i, col in enumerate(cols):
                col.image(f"https://via.placeholder.com/150x100?text=Photo+{i+1}", use_column_width=True)
        
        with col2:
            st.subheader(f"{prop['price']:,.0f} €")
            st.metric("Surface", f"{prop['size']} m²")
            st.metric("Pièces", prop['rooms'])
            st.metric("Localisation", prop['location'])
            st.metric("Type", prop['property_type'])
            
            if st.button(t['contact_agent']):
                st.session_state.contact_property = prop
                st.rerun()
        
        st.subheader("Description")
        st.write(prop['description'])
        
        # Caractéristiques
        st.subheader("Caractéristiques")
        if prop['features']:
            features = prop['features'].split(", ")
            for feature in features:
                st.write(f"✅ {feature}")
        
        # Carte de localisation
        st.subheader("Localisation")
        if 'latitude' in prop and 'longitude' in prop and prop['latitude'] and prop['longitude']:
            map_data = pd.DataFrame({
                'lat': [prop['latitude']],
                'lon': [prop['longitude']]
            })
            st.map(map_data, zoom=12)
        else:
            st.info("Localisation non disponible")
        
        if st.button("Retour aux résultats"):
            del st.session_state.selected_property
            st.rerun()

# Page de contact pour une propriété
def contact_agent_page():
    if 'contact_property' in st.session_state:
        prop = st.session_state.contact_property
        t = load_translations(st.session_state.language)
        
        st.header(f"Contacter l'agent - {prop['title']}")
        
        with st.form("contact
