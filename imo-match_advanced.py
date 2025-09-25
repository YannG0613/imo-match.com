import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Configuration de la page
st.set_page_config(
    page_title="ImoMatch - Immobilier IA",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS pour améliorer l'apparence
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #FF6B35;
    text-align: center;
    margin-bottom: 2rem;
}
.metric-card {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 10px;
    border-left: 5px solid #FF6B35;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_data' not in st.session_state:
        st.session_state.user_data = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Accueil"

def show_login_form():
    """Affiche le formulaire de connexion"""
    with st.form("login_form"):
        st.subheader("Connexion")
        email = st.text_input("Email")
        password = st.text_input("Mot de passe", type="password")
        
        if st.form_submit_button("Se connecter"):
            if email and password:
                # Simulation de connexion
                st.session_state.authenticated = True
                st.session_state.user_data = {
                    'email': email,
                    'first_name': 'Utilisateur',
                    'last_name': 'Test'
                }
                st.success("Connexion réussie!")
                st.rerun()
            else:
                st.error("Veuillez remplir tous les champs")

def show_register_form():
    """Affiche le formulaire d'inscription"""
    with st.form("register_form"):
        st.subheader("Inscription")
        
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("Prénom")
            email = st.text_input("Email")
            password = st.text_input("Mot de passe", type="password")
        
        with col2:
            last_name = st.text_input("Nom")
            phone = st.text_input("Téléphone (optionnel)")
            confirm_password = st.text_input("Confirmer le mot de passe", type="password")
        
        if st.form_submit_button("Créer mon compte"):
            if first_name and last_name and email and password and confirm_password:
                if password == confirm_password:
                    st.success("Compte créé avec succès! Vous pouvez maintenant vous connecter.")
                else:
                    st.error("Les mots de passe ne correspondent pas")
            else:
                st.error("Veuillez remplir tous les champs obligatoires")

def show_home_page():
    """Page d'accueil"""
    st.markdown('<h1 class="main-header">🏠 ImoMatch</h1>', unsafe_allow_html=True)
    st.markdown("### Application immobilière avec Intelligence Artificielle")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        **ImoMatch** est votre assistant IA pour la recherche immobilière sur la Côte d'Azur.
        
        #### Fonctionnalités principales :
        - 🔍 **Recherche intelligente** de propriétés
        - 🤖 **Recommandations personnalisées** par IA
        - 🗺️ **Cartes interactives** avec géolocalisation
        - ❤️ **Système de favoris** pour sauvegarder vos biens préférés
        - 📊 **Analyses de marché** en temps réel
        - 💬 **Agent IA conversationnel** pour vous guider
        """)
        
        # Métriques de démonstration
        st.subheader("Statistiques de la plateforme")
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            st.metric("Propriétés disponibles", "1,247", "↗️ +23")
        with col_b:
            st.metric("Utilisateurs actifs", "856", "↗️ +12")
        with col_c:
            st.metric("Recherches quotidiennes", "2,341", "↗️ +156")
    
    with col2:
        st.subheader("Commencer")
        st.info("💡 Créez un compte pour accéder à toutes les fonctionnalités!")
        
        if st.button("🚀 Découvrir les propriétés", type="primary"):
            st.session_state.current_page = "Recherche"
            st.rerun()

def show_search_page():
    """Page de recherche"""
    if not st.session_state.authenticated:
        st.warning("Veuillez vous connecter pour accéder à la recherche")
        return
    
    st.header("🔍 Recherche de Propriétés")
    
    # Filtres de recherche
    with st.form("search_filters"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            budget_max = st.number_input("Budget maximum (€)", 
                                        min_value=100000, 
                                        max_value=5000000, 
                                        value=800000, 
                                        step=50000)
            property_type = st.selectbox("Type de bien", 
                                       ["Tous", "Appartement", "Maison", "Villa", "Studio"])
        
        with col2:
            location = st.selectbox("Ville", 
                                  ["Antibes", "Cannes", "Nice", "Monaco", "Saint-Tropez", "Autre"])
            bedrooms = st.number_input("Chambres minimum", min_value=1, max_value=10, value=2)
        
        with col3:
            surface_min = st.number_input("Surface minimale (m²)", min_value=20, max_value=500, value=60)
            with_terrace = st.checkbox("Avec terrasse/balcon")
        
        search_clicked = st.form_submit_button("🔍 Rechercher", type="primary")
    
    if search_clicked:
        # Simulation de résultats de recherche
        with st.spinner("Recherche en cours..."):
            import time
            time.sleep(1)  # Simulation du temps de recherche
        
        st.success(f"✅ 12 propriétés trouvées")
        
        # Affichage des résultats simulés
        properties = [
            {"title": "Appartement lumineux - Centre Antibes", "price": 650000, "surface": 85, "rooms": 3, "location": "Antibes"},
            {"title": "Villa avec piscine - Collines de Cannes", "price": 1200000, "surface": 120, "rooms": 4, "location": "Cannes"},
            {"title": "Penthouse vue mer - Nice", "price": 890000, "surface": 95, "rooms": 3, "location": "Nice"},
            {"title": "Maison de ville - Vieux Antibes", "price": 750000, "surface": 110, "rooms": 4, "location": "Antibes"}
        ]
        
        for i, prop in enumerate(properties):
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    st.subheader(prop["title"])
                    st.write(f"📍 {prop['location']}")
                
                with col2:
                    st.metric("Prix", f"{prop['price']:,}€")
                
                with col3:
                    st.metric("Surface", f"{prop['surface']}m²")
                
                with col4:
                    st.metric("Pièces", prop['rooms'])
                
                col_a, col_b, col_c = st.columns([1, 1, 2])
                with col_a:
                    st.button("❤️ Favoris", key=f"fav_{i}")
                with col_b:
                    st.button("👁️ Voir", key=f"view_{i}")
                with col_c:
                    st.button("📞 Contacter l'agent", key=f"contact_{i}")
                
                st.markdown("---")

def show_profile_page():
    """Page de profil"""
    if not st.session_state.authenticated:
        st.warning("Veuillez vous connecter pour accéder à votre profil")
        return
    
    user = st.session_state.user_data
    st.header(f"👤 Profil de {user['first_name']} {user['last_name']}")
    
    tab1, tab2, tab3 = st.tabs(["📝 Informations", "⚙️ Préférences", "❤️ Favoris"])
    
    with tab1:
        st.subheader("Informations personnelles")
        with st.form("profile_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                first_name = st.text_input("Prénom", value=user.get('first_name', ''))
                email = st.text_input("Email", value=user.get('email', ''))
                phone = st.text_input("Téléphone", value=user.get('phone', ''))
            
            with col2:
                last_name = st.text_input("Nom", value=user.get('last_name', ''))
                profession = st.text_input("Profession", value=user.get('profession', ''))
                age = st.number_input("Âge", min_value=18, max_value=99, value=user.get('age', 30))
            
            if st.form_submit_button("💾 Sauvegarder"):
                st.success("Profil mis à jour avec succès!")
    
    with tab2:
        st.subheader("Préférences de recherche")
        
        with st.form("preferences_form"):
            budget_range = st.slider("Fourchette de budget (€)", 
                                   min_value=100000, 
                                   max_value=3000000, 
                                   value=(300000, 800000),
                                   step=50000)
            
            preferred_locations = st.multiselect("Villes préférées", 
                                               ["Antibes", "Cannes", "Nice", "Monaco", "Saint-Tropez"])
            
            property_types = st.multiselect("Types de biens recherchés", 
                                          ["Appartement", "Maison", "Villa", "Studio"])
            
            min_rooms = st.number_input("Nombre de pièces minimum", min_value=1, max_value=10, value=2)
            
            must_have = st.multiselect("Équipements indispensables", 
                                     ["Terrasse/Balcon", "Parking", "Piscine", "Vue mer", "Jardin"])
            
            if st.form_submit_button("💾 Sauvegarder les préférences"):
                st.success("Préférences sauvegardées!")
    
    with tab3:
        st.subheader("Vos biens favoris")
        st.info("Vos propriétés favorites apparaîtront ici")

def show_auth_page():
    """Page d'authentification"""
    if st.session_state.authenticated:
        user = st.session_state.user_data
        st.success(f"Connecté en tant que {user['first_name']} {user['last_name']}")
        
        if st.button("🚪 Se déconnecter"):
            st.session_state.authenticated = False
            st.session_state.user_data = None
            st.success("Déconnexion réussie!")
            st.rerun()
    else:
        tab1, tab2 = st.tabs(["🔓 Connexion", "📝 Inscription"])
        
        with tab1:
            show_login_form()
        
        with tab2:
            show_register_form()

def show_dashboard():
    """Tableau de bord"""
    if not st.session_state.authenticated:
        st.warning("Veuillez vous connecter pour accéder au tableau de bord")
        return
    
    user = st.session_state.user_data
    st.header(f"📊 Tableau de bord de {user['first_name']}")
    
    # Métriques utilisateur
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Recherches sauvées", "5", "↗️ +2")
    with col2:
        st.metric("Favoris", "12", "↗️ +3")
    with col3:
        st.metric("Visites programmées", "3", "→ 0")
    with col4:
        st.metric("Alertes actives", "8", "↗️ +1")
    
    # Graphique des prix par ville
    st.subheader("📈 Évolution des prix par ville")
    
    # Données simulées
    chart_data = pd.DataFrame({
        'Ville': ['Antibes', 'Cannes', 'Nice', 'Monaco', 'Saint-Tropez'] * 3,
        'Prix moyen (€/m²)': [5200, 7800, 4900, 15000, 9500, 5400, 8100, 5100, 15500, 9800, 5600, 8400, 5300, 16000, 10100],
        'Mois': ['Jan'] * 5 + ['Fév'] * 5 + ['Mar'] * 5
    })
    
    fig = px.line(chart_data, x='Mois', y='Prix moyen (€/m²)', color='Ville', 
                  title="Évolution des prix moyens au m²")
    st.plotly_chart(fig, use_container_width=True)

def main():
    """Fonction principale"""
    # Initialiser les variables de session
    init_session_state()
    
    # Navigation dans la sidebar
    with st.sidebar:
        st.title("🏠 ImoMatch")
        
        # Statut de connexion
        if st.session_state.authenticated:
            user = st.session_state.user_data
            st.success(f"👋 {user['first_name']}")
        else:
            st.info("👤 Non connecté")
        
        st.markdown("---")
        
        # Navigation
        pages = {
            "🏠 Accueil": "Accueil",
            "🔑 Authentification": "Authentification"
        }
        
        # Ajouter les pages pour utilisateurs connectés
        if st.session_state.authenticated:
            pages.update({
                "🔍 Recherche": "Recherche",
                "👤 Profil": "Profil", 
                "📊 Tableau de bord": "Dashboard"
            })
        
        selected_page = st.selectbox("Navigation", list(pages.keys()))
        st.session_state.current_page = pages[selected_page]
    
    # Affichage de la page sélectionnée
    if st.session_state.current_page == "Accueil":
        show_home_page()
    elif st.session_state.current_page == "Authentification":
        show_auth_page()
    elif st.session_state.current_page == "Recherche":
        show_search_page()
    elif st.session_state.current_page == "Profil":
        show_profile_page()
    elif st.session_state.current_page == "Dashboard":
        show_dashboard()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; opacity: 0.8; font-size: 0.9rem;'>
        © 2024 ImoMatch - Application immobilière avec IA | 
        <a href='#'>Support</a> | <a href='#'>Documentation</a> | <a href='#'>CGU</a>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
