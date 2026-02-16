"""
ImoMatch - Application Immobilière Complète avec IA
Business Case Implementation
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import hashlib
import sqlite3

# Configuration de la page
st.set_page_config(
    page_title="ImoMatch - Trouvez votre bien idéal",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        color: #FF6B35;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .property-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 5px solid #FF6B35;
    }
    .match-score {
        background: linear-gradient(135deg, #FF6B35, #F7931E);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
    }
    .price-tag {
        font-size: 1.8rem;
        color: #FF6B35;
        font-weight: bold;
    }
    .feature-badge {
        background: #f0f2f6;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        margin: 0.2rem;
        display: inline-block;
        font-size: 0.9rem;
    }
    .agent-card {
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .stat-box {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ==================== BASE DE DONNÉES ====================

class ImoMatchDatabase:
    def __init__(self, db_path="imomatch.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialise toutes les tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Table utilisateurs
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
                budget_min INTEGER,
                budget_max INTEGER,
                property_types TEXT,
                surface_min INTEGER,
                bedrooms_min INTEGER,
                preferred_locations TEXT,
                marital_status TEXT,
                children_count INTEGER DEFAULT 0,
                lifestyle TEXT,
                work_arrangement TEXT,
                pets TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table propriétés
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS properties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                property_type TEXT NOT NULL,
                surface_total INTEGER,
                bedrooms INTEGER,
                bathrooms INTEGER,
                construction_year INTEGER,
                energy_class TEXT,
                heating_type TEXT,
                elevator BOOLEAN DEFAULT 0,
                balcony BOOLEAN DEFAULT 0,
                terrace BOOLEAN DEFAULT 0,
                garden BOOLEAN DEFAULT 0,
                swimming_pool BOOLEAN DEFAULT 0,
                garage_count INTEGER DEFAULT 0,
                price INTEGER NOT NULL,
                price_per_sqm INTEGER,
                city TEXT NOT NULL,
                postal_code TEXT,
                luxury_level INTEGER DEFAULT 3,
                view_quality TEXT,
                quietness_level INTEGER DEFAULT 3,
                brightness_level INTEGER DEFAULT 3,
                latitude REAL,
                longitude REAL,
                listing_status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table agents
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT,
                last_name TEXT,
                agency_name TEXT,
                email TEXT,
                phone TEXT,
                specialization TEXT,
                experience_years INTEGER,
                photo_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table favoris
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                property_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (property_id) REFERENCES properties (id),
                UNIQUE(user_id, property_id)
            )
        ''')
        
        # Table visites
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS visits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                property_id INTEGER,
                agent_id INTEGER,
                visit_date DATETIME,
                status TEXT DEFAULT 'scheduled',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (property_id) REFERENCES properties (id),
                FOREIGN KEY (agent_id) REFERENCES agents (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        self.add_sample_data()
    
    def add_sample_data(self):
        """Ajoute des données d'exemple si la base est vide"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM properties")
        if cursor.fetchone()[0] > 0:
            conn.close()
            return
        
        # Agents d'exemple
        agents = [
            ("Marie", "Dubois", "Century 21 Côte d'Azur", "marie.dubois@c21.fr", "0493123456", "luxe", 10, None),
            ("Pierre", "Martin", "Orpi Antibes", "pierre.martin@orpi.fr", "0493789123", "familial", 15, None),
            ("Sophie", "Leroy", "Laforêt Monaco", "sophie.leroy@laforet.fr", "0493456789", "prestige", 8, None),
        ]
        
        for agent in agents:
            cursor.execute('''
                INSERT INTO agents (first_name, last_name, agency_name, email, phone, specialization, experience_years, photo_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', agent)
        
        # Propriétés d'exemple
        properties = [
            ("Penthouse Exceptionnel - Croisette Cannes", "Magnifique penthouse avec vue mer panoramique, terrasse 100m², piscine sur le toit", 
             "Penthouse", 180, 4, 3, 2019, "A", "pompe_à_chaleur", 1, 0, 1, 0, 1, 2, 3800000, 21111, "Cannes", "06400", 5, "mer", 5, 5, 43.5511, 7.0128),
            
            ("Villa Contemporaine - Nice", "Superbe villa moderne avec piscine, jardin paysager, vue panoramique sur la Baie des Anges",
             "Villa", 250, 5, 4, 2015, "B", "pompe_à_chaleur", 0, 0, 1, 1, 1, 2, 1850000, 7400, "Nice", "06000", 4, "mer", 5, 5, 43.7102, 7.2620),
            
            ("Appartement Familial - Antibes", "Bel appartement T4, proche plages, commerces et écoles, résidence sécurisée",
             "Appartement", 95, 3, 2, 2005, "C", "gaz", 1, 1, 0, 0, 0, 1, 680000, 7158, "Antibes", "06600", 3, "ville", 4, 4, 43.5808, 7.1251),
            
            ("Studio Investissement - Monaco", "Studio moderne, idéal investissement locatif, proche gare et commerces",
             "Studio", 28, 1, 1, 2018, "B", "électrique", 1, 1, 0, 0, 0, 0, 520000, 18571, "Monaco", "98000", 3, "ville", 3, 4, 43.7384, 7.4246),
            
            ("Maison de Village - Grasse", "Charmante maison provençale, terrasses, vue panoramique, calme absolu",
             "Maison", 140, 4, 2, 1950, "D", "bois", 0, 0, 1, 1, 0, 1, 520000, 3714, "Grasse", "06130", 3, "montagne", 5, 4, 43.6584, 6.9222),
            
            ("Loft Atypique - Nice Port", "Magnifique loft industriel rénové, volumes exceptionnels, proche port",
             "Loft", 110, 2, 2, 2010, "C", "pompe_à_chaleur", 1, 0, 1, 0, 0, 1, 780000, 7091, "Nice", "06000", 4, "mer", 3, 5, 43.6950, 7.2760),
        ]
        
        for prop in properties:
            cursor.execute('''
                INSERT INTO properties (title, description, property_type, surface_total, bedrooms, bathrooms,
                                      construction_year, energy_class, heating_type, elevator, balcony, terrace,
                                      garden, swimming_pool, garage_count, price, price_per_sqm, city, postal_code,
                                      luxury_level, view_quality, quietness_level, brightness_level, latitude, longitude)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', prop)
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, user_data):
        """Enregistre un nouvel utilisateur"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (email, password_hash, first_name, last_name, phone, age, user_type,
                                 budget_min, budget_max, property_types, surface_min, bedrooms_min,
                                 preferred_locations, marital_status, children_count, lifestyle, work_arrangement, pets)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_data['email'],
                self.hash_password(user_data['password']),
                user_data.get('first_name'),
                user_data.get('last_name'),
                user_data.get('phone'),
                user_data.get('age'),
                user_data.get('user_type', 'acquéreur'),
                user_data.get('budget_min'),
                user_data.get('budget_max'),
                json.dumps(user_data.get('property_types', [])),
                user_data.get('surface_min'),
                user_data.get('bedrooms_min'),
                json.dumps(user_data.get('preferred_locations', [])),
                user_data.get('marital_status'),
                user_data.get('children_count', 0),
                user_data.get('lifestyle'),
                user_data.get('work_arrangement'),
                user_data.get('pets')
            ))
            conn.commit()
            return True, "Compte créé avec succès"
        except sqlite3.IntegrityError:
            return False, "Cet email est déjà utilisé"
        except Exception as e:
            return False, f"Erreur: {str(e)}"
        finally:
            conn.close()
    
    def login_user(self, email, password):
        """Connecte un utilisateur"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, email, first_name, last_name, user_type, budget_min, budget_max,
                   property_types, preferred_locations, bedrooms_min
            FROM users WHERE email = ? AND password_hash = ?
        ''', (email, self.hash_password(password)))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return True, {
                'id': user[0],
                'email': user[1],
                'first_name': user[2],
                'last_name': user[3],
                'user_type': user[4],
                'budget_min': user[5],
                'budget_max': user[6],
                'property_types': json.loads(user[7]) if user[7] else [],
                'preferred_locations': json.loads(user[8]) if user[8] else [],
                'bedrooms_min': user[9]
            }
        return False, None
    
    def search_properties(self, filters=None):
        """Recherche de propriétés avec filtres"""
        conn = self.get_connection()
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
        
        query += " ORDER BY created_at DESC LIMIT 50"
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df.to_dict('records') if not df.empty else []
    
    def calculate_match_score(self, user_prefs, property_data):
        """Calcule un score de compatibilité IA"""
        score = 0
        factors = 0
        
        # Budget
        if user_prefs.get('budget_max') and property_data.get('price'):
            if property_data['price'] <= user_prefs['budget_max']:
                score += 30
            elif property_data['price'] <= user_prefs['budget_max'] * 1.1:
                score += 15
            factors += 1
        
        # Type de propriété
        if user_prefs.get('property_types') and property_data.get('property_type'):
            if property_data['property_type'] in user_prefs['property_types']:
                score += 25
            factors += 1
        
        # Nombre de chambres
        if user_prefs.get('bedrooms_min') and property_data.get('bedrooms'):
            if property_data['bedrooms'] >= user_prefs['bedrooms_min']:
                score += 20
            factors += 1
        
        # Localisation
        if user_prefs.get('preferred_locations') and property_data.get('city'):
            if property_data['city'] in user_prefs['preferred_locations']:
                score += 25
            factors += 1
        
        return min(100, int(score * (4 / max(factors, 1))))

# Instance globale
db = ImoMatchDatabase()

# ==================== GESTION SESSION ====================

def init_session():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'

# ==================== PAGES ====================

def page_home():
    """Page d'accueil"""
    st.markdown('<h1 class="main-header">🏠 ImoMatch</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Trouvez votre bien immobilier idéal grâce à l\'Intelligence Artificielle</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        st.metric("Propriétés disponibles", "1,247")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        st.metric("Utilisateurs satisfaits", "856")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        st.metric("Correspondances réussies", "432")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    col_a, col_b = st.columns([2, 1])
    
    with col_a:
        st.subheader("Comment ça marche ?")
        st.markdown("""
        ### 1. Créez votre profil 👤
        Définissez vos critères : budget, type de bien, localisation, équipements souhaités
        
        ### 2. L'IA analyse vos besoins 🤖
        Notre algorithme intelligent comprend vos préférences et mode de vie
        
        ### 3. Recevez des recommandations personnalisées 🎯
        Découvrez les biens qui correspondent parfaitement à votre profil
        
        ### 4. Visitez et trouvez votre bonheur 🏡
        Prenez rendez-vous avec nos agents partenaires
        """)
    
    with col_b:
        st.subheader("Nos atouts")
        st.success("✅ Matching IA intelligent")
        st.success("✅ Base de données exhaustive")
        st.success("✅ Alertes en temps réel")
        st.success("✅ Agents certifiés")
        st.success("✅ Visite virtuelle 360°")
        st.success("✅ Accompagnement personnalisé")

def page_auth():
    """Page d'authentification"""
    tab1, tab2 = st.tabs(["🔓 Connexion", "📝 Inscription"])
    
    with tab1:
        st.subheader("Connexion à votre compte")
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Mot de passe", type="password")
            
            if st.form_submit_button("Se connecter", type="primary"):
                if email and password:
                    success, user_data = db.login_user(email, password)
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.user = user_data
                        st.success("Connexion réussie !")
                        st.rerun()
                    else:
                        st.error("Email ou mot de passe incorrect")
                else:
                    st.error("Veuillez remplir tous les champs")
    
    with tab2:
        st.subheader("Créer un compte")
        with st.form("register_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                first_name = st.text_input("Prénom *")
                email = st.text_input("Email *")
                password = st.text_input("Mot de passe *", type="password")
                age = st.number_input("Âge", min_value=18, max_value=99, value=30)
                
            with col2:
                last_name = st.text_input("Nom *")
                phone = st.text_input("Téléphone")
                confirm_password = st.text_input("Confirmer mot de passe *", type="password")
                user_type = st.selectbox("Type de recherche", ["Acquéreur", "Locataire", "Investisseur"])
            
            st.markdown("### Vos critères de recherche")
            
            col3, col4 = st.columns(2)
            with col3:
                budget_min = st.number_input("Budget minimum (€)", min_value=0, value=300000, step=50000)
                property_types = st.multiselect("Types de biens", ["Appartement", "Maison", "Villa", "Studio", "Loft"])
                bedrooms_min = st.number_input("Chambres minimum", min_value=1, max_value=10, value=2)
                
            with col4:
                budget_max = st.number_input("Budget maximum (€)", min_value=0, value=800000, step=50000)
                preferred_locations = st.multiselect("Villes préférées", ["Nice", "Cannes", "Antibes", "Monaco", "Grasse"])
                surface_min = st.number_input("Surface minimum (m²)", min_value=20, max_value=500, value=60)
            
            if st.form_submit_button("Créer mon compte", type="primary"):
                if not all([first_name, last_name, email, password, confirm_password]):
                    st.error("Veuillez remplir tous les champs obligatoires (*)")
                elif password != confirm_password:
                    st.error("Les mots de passe ne correspondent pas")
                elif not property_types:
                    st.error("Veuillez sélectionner au moins un type de bien")
                else:
                    user_data = {
                        'first_name': first_name,
                        'last_name': last_name,
                        'email': email,
                        'password': password,
                        'phone': phone,
                        'age': age,
                        'user_type': user_type.lower(),
                        'budget_min': budget_min,
                        'budget_max': budget_max,
                        'property_types': property_types,
                        'surface_min': surface_min,
                        'bedrooms_min': bedrooms_min,
                        'preferred_locations': preferred_locations
                    }
                    
                    success, message = db.register_user(user_data)
                    if success:
                        st.success(message + " Vous pouvez maintenant vous connecter !")
                    else:
                        st.error(message)

def page_search():
    """Page de recherche"""
    if not st.session_state.authenticated:
        st.warning("Veuillez vous connecter pour accéder à la recherche")
        return
    
    st.header("🔍 Recherche de Propriétés")
    
    with st.form("search_form"):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            price_max = st.number_input("Budget max (€)", min_value=100000, value=1000000, step=50000)
        with col2:
            property_type = st.selectbox("Type", ["Tous", "Appartement", "Maison", "Villa", "Studio", "Loft", "Penthouse"])
        with col3:
            city = st.selectbox("Ville", ["Toutes", "Nice", "Cannes", "Antibes", "Monaco", "Grasse"])
        with col4:
            bedrooms_min = st.number_input("Chambres min", min_value=1, max_value=10, value=2)
        
        search_clicked = st.form_submit_button("🔍 Rechercher", type="primary")
    
    if search_clicked:
        filters = {
            'price_max': price_max,
            'property_type': property_type if property_type != "Tous" else None,
            'city': city if city != "Toutes" else None,
            'bedrooms_min': bedrooms_min
        }
        
        properties = db.search_properties(filters)
        
        if properties:
            st.success(f"✅ {len(properties)} propriété(s) trouvée(s)")
            
            for prop in properties:
                # Calculer le score de compatibilité
                match_score = db.calculate_match_score(st.session_state.user, prop)
                
                st.markdown('<div class="property-card">', unsafe_allow_html=True)
                
                col_info, col_details, col_action = st.columns([3, 2, 1])
                
                with col_info:
                    st.markdown(f"### {prop['title']}")
                    st.write(prop['description'])
                    
                    # Badges des équipements
                    features = []
                    if prop.get('elevator'): features.append("🛗 Ascenseur")
                    if prop.get('balcony'): features.append("🏝️ Balcon")
                    if prop.get('terrace'): features.append("☀️ Terrasse")
                    if prop.get('garden'): features.append("🌳 Jardin")
                    if prop.get('swimming_pool'): features.append("🏊 Piscine")
                    if prop.get('garage_count', 0) > 0: features.append(f"🚗 Garage ({prop['garage_count']})")
                    
                    for feature in features:
                        st.markdown(f'<span class="feature-badge">{feature}</span>', unsafe_allow_html=True)
                
                with col_details:
                    st.markdown(f'<p class="price-tag">{prop["price"]:,}€</p>', unsafe_allow_html=True)
                    st.write(f"📐 Surface: {prop['surface_total']}m²")
                    st.write(f"🛏️ Chambres: {prop['bedrooms']}")
                    st.write(f"🚿 Salles de bain: {prop['bathrooms']}")
                    st.write(f"📍 {prop['city']}")
                    st.write(f"⚡ DPE: {prop.get('energy_class', 'N/A')}")
                
                with col_action:
                    st.markdown(f'<div class="match-score">Match {match_score}%</div>', unsafe_allow_html=True)
                    st.write("")
                    if st.button("❤️ Favoris", key=f"fav_{prop['id']}"):
                        st.success("Ajouté aux favoris!")
                    if st.button("👁️ Détails", key=f"view_{prop['id']}"):
                        st.info("Fonctionnalité bientôt disponible")
                    if st.button("📅 Visite", key=f"visit_{prop['id']}"):
                        st.success("Demande envoyée!")
                
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Aucune propriété trouvée avec ces critères")

def page_recommendations():
    """Page des recommandations IA"""
    if not st.session_state.authenticated:
        st.warning("Veuillez vous connecter pour voir vos recommandations")
        return
    
    st.header("🎯 Vos Recommandations Personnalisées")
    
    user = st.session_state.user
    
    # Afficher le profil utilisateur
    with st.expander("📊 Votre profil de recherche"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**Budget:** {user.get('budget_min', 0):,}€ - {user.get('budget_max', 0):,}€")
        with col2:
            st.write(f"**Types recherchés:** {', '.join(user.get('property_types', []))}")
        with col3:
            st.write(f"**Chambres min:** {user.get('bedrooms_min', 1)}")
    
    # Recherche basée sur le profil
    filters = {
        'price_max': user.get('budget_max'),
        'bedrooms_min': user.get('bedrooms_min')
    }
    
    all_properties = db.search_properties(filters)
    
    # Calculer les scores et trier
    recommendations = []
    for prop in all_properties:
        score = db.calculate_match_score(user, prop)
        if score >= 60:  # Seuil minimum
            recommendations.append({**prop, 'match_score': score})
    
    recommendations.sort(key=lambda x: x['match_score'], reverse=True)
    
    if recommendations:
        st.success(f"✨ {len(recommendations)} recommandations IA pour vous")
        
        # Top 3 en mise en avant
        if len(recommendations) >= 3:
            st.subheader("🏆 Top 3 Correspondances")
            
            cols = st.columns(3)
            for idx, prop in enumerate(recommendations[:3]):
                with cols[idx]:
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #FF6B35, #F7931E); 
                                padding: 1.5rem; border-radius: 10px; color: white; text-align: center;'>
                        <h3 style='color: white; margin: 0;'>#{idx+1}</h3>
                        <h4 style='color: white;'>{prop['title'][:30]}...</h4>
                        <h2 style='color: white;'>{prop['match_score']}% Match</h2>
                        <p style='color: white; font-size: 1.2rem;'>{prop['price']:,}€</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("Voir détails", key=f"top_{prop['id']}"):
                        st.info("Fonctionnalité en développement")
            
            st.markdown("---")
        
        # Toutes les recommandations
        st.subheader("Toutes vos recommandations")
        
        for prop in recommendations:
            st.markdown('<div class="property-card">', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.markdown(f"### {prop['title']}")
                st.write(f"📍 {prop['city']} | {prop['surface_total']}m² | {prop['bedrooms']} chambres")
                
            with col2:
                st.markdown(f'<p class="price-tag">{prop["price"]:,}€</p>', unsafe_allow_html=True)
                st.write(f"💰 {prop['price_per_sqm']:,}€/m²")
                
            with col3:
                st.markdown(f'<div class="match-score">{prop["match_score"]}% Match</div>', unsafe_allow_html=True)
                if st.button("Détails", key=f"rec_{prop['id']}"):
                    st.info("Bientôt disponible")
            
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Aucune recommandation disponible pour le moment. Essayez d'élargir vos critères.")

def page_dashboard():
    """Tableau de bord utilisateur"""
    if not st.session_state.authenticated:
        st.warning("Veuillez vous connecter")
        return
    
    user = st.session_state.user
    st.header(f"📊 Tableau de bord - {user['first_name']} {user['last_name']}")
    
    # Métriques
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Recherches sauvegardées", "8", "+2")
    with col2:
        st.metric("Favoris", "15", "+5")
    with col3:
        st.metric("Visites programmées", "3", "+1")
    with col4:
        st.metric("Alertes actives", "12", "0")
    
    st.markdown("---")
    
    # Graphiques
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("📈 Évolution des prix - Zone recherchée")
        
        # Données simulées
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='M')
        prices_data = pd.DataFrame({
            'Date': dates,
            'Nice': [4800, 4850, 4900, 4950, 5000, 5050, 5100, 5150, 5200, 5250, 5300, 5350],
            'Cannes': [6500, 6550, 6600, 6700, 6800, 6900, 7000, 7100, 7200, 7300, 7400, 7500],
            'Antibes': [5200, 5250, 5300, 5350, 5400, 5450, 5500, 5550, 5600, 5650, 5700, 5750]
        })
        
        fig = px.line(prices_data, x='Date', y=['Nice', 'Cannes', 'Antibes'],
                      title="Prix moyen au m² (€)",
                      labels={'value': 'Prix (€/m²)', 'variable': 'Ville'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col_b:
        st.subheader("🎯 Répartition de vos recherches")
        
        search_data = pd.DataFrame({
            'Type': ['Appartement', 'Maison', 'Villa', 'Studio'],
            'Nombre': [35, 25, 20, 20]
        })
        
        fig2 = px.pie(search_data, values='Nombre', names='Type',
                      title="Types de biens recherchés")
        st.plotly_chart(fig2, use_container_width=True)
    
    # Activité récente
    st.subheader("📅 Activité récente")
    
    activities = [
        {"date": "Aujourd'hui", "action": "Nouvelle alerte activée", "details": "Appartement T3 à Nice"},
        {"date": "Hier", "action": "Visite programmée", "details": "Villa 200m² à Antibes - 15 Jan 14h00"},
        {"date": "Il y a 2 jours", "action": "Ajout aux favoris", "details": "Penthouse Cannes Croisette"},
        {"date": "Il y a 3 jours", "action": "Recherche sauvegardée", "details": "Maison 150m² budget 800k€"}
    ]
    
    for activity in activities:
        col_date, col_action, col_details = st.columns([1, 2, 3])
        with col_date:
            st.write(activity['date'])
        with col_action:
            st.write(f"**{activity['action']}**")
        with col_details:
            st.write(activity['details'])

# ==================== NAVIGATION ====================

def main():
    init_session()
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🏠 ImoMatch")
        
        if st.session_state.authenticated:
            user = st.session_state.user
            st.success(f"👋 {user['first_name']} {user['last_name']}")
            st.write(f"*{user['user_type'].title()}*")
            
            if st.button("🚪 Déconnexion"):
                st.session_state.authenticated = False
                st.session_state.user = None
                st.rerun()
        else:
            st.info("👤 Non connecté")
        
        st.markdown("---")
        
        # Navigation
        pages = {
            "🏠 Accueil": "home",
            "🔑 Connexion": "auth"
        }
        
        if st.session_state.authenticated:
            pages.update({
                "🔍 Recherche": "search",
                "🎯 Recommandations IA": "recommendations",
                "📊 Tableau de bord": "dashboard"
            })
        
        selected = st.selectbox("Navigation", list(pages.keys()))
        st.session_state.current_page = pages[selected]
    
    # Affichage de la page
    if st.session_state.current_page == "home":
        page_home()
    elif st.session_state.current_page == "auth":
        page_auth()
    elif st.session_state.current_page == "search":
        page_search()
    elif st.session_state.current_page == "recommendations":
        page_recommendations()
    elif st.session_state.current_page == "dashboard":
        page_dashboard()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <p>© 2024 ImoMatch - Plateforme immobilière intelligente | 
        <a href='#'>Mentions légales</a> | <a href='#'>CGU</a> | <a href='#'>Contact</a></p>
        <p style='font-size: 0.8rem;'>Fait avec ❤️ pour révolutionner l'immobilier sur la Côte d'Azur</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
