import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Configuration de la page
st.set_page_config(layout="wide")

# --- Configuration du style et des couleurs ---
def set_style():
    st.markdown(
        """
        <style>
        .css-1d391kg {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
        .css-1v3h82o {
            color: #FF6700;
        }
        .st-emotion-cache-1f19p1e{
            background-color: #f0f2f6;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
# Appel de la fonction de style
set_style()

# --- Fonctions utilitaires ---
def display_logo():
    # Remplacez l'URL ou le chemin par votre logo ImoMatch
    logo_url = "https://imo-match.streamlit.app/app/static/imomatch_logo.png"
    st.image(logo_url, width=150)

# --- Pages de l'application ---

def display_home_page():
    st.header("Découvrez votre match immobilier parfait 🏡")
    st.write("ImoMatch vous connecte avec les biens immobiliers qui correspondent VRAIMENT à vos critères, en utilisant une technologie de matching innovante.")
    
    st.subheader("Nos statistiques clés")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Propriétés matchées", value="1500+")
    with col2:
        st.metric(label="Transactions facilitées", value="200+")
    with col3:
        st.metric(label="Utilisateurs satisfaits", value="98%")
    
    st.subheader("Nos partenaires")
    st.write("Nous travaillons avec les plus grandes agences pour vous offrir le meilleur choix.")
    # Ajoutez des logos ou des noms de partenaires ici
    
    st.subheader("Connexion")
    st.info("Pour une expérience complète, connectez-vous ou inscrivez-vous.")
    login_type = st.radio("Choisissez votre type de compte", ["Gratuit", "Premium (14 jours d'essai)", "Professionnel"])
    
    st.text_input("Adresse e-mail")
    st.text_input("Mot de passe", type="password")
    st.button("Se connecter")
    
    if login_type == "Professionnel":
        st.warning("Contactez-nous pour les comptes professionnels.")

def display_my_info_page():
    st.title("Mes informations")
    st.info("Complétez ou mettez à jour vos informations pour affiner vos recommandations.")

    with st.expander("Informations de base"):
        st.text_input("Nom", value="Yann Gouedo")
        st.text_input("Adresse e-mail", value="yann.gouedo@imomatch.com")
        
    with st.expander("Critères de recherche"):
        st.slider("Prix maximum", 50000, 1000000, 350000)
        st.slider("Surface minimum (m²)", 20, 300, 85)
        st.selectbox("Type de bien", ["Appartement", "Maison", "Villa"])
        st.text_input("Ville de recherche", value="Paris")
    
    # Intégration simulée de l'Agent AI
    st.subheader("Agent AI")
    st.write("L'Agent AI est là pour vous aider à enrichir vos informations et à trouver des biens uniques.")
    st.text_area("Posez votre question à l'Agent AI...", height=100)
    st.button("Envoyer")
    
    st.success("Toutes vos modifications ont été sauvegardées.")

def display_search_page():
    st.title("Recherches avancées")
    st.text_input("Mots-clés de recherche")
    st.button("Rechercher")

    st.subheader("Résultats de recherche")
    # Simulation des données de recherche
    search_data = pd.DataFrame({
        'Bien': ['Appartement 3 pièces', 'Maison de ville', 'Studio', 'Duplex'],
        'Ville': ['Paris', 'Lyon', 'Marseille', 'Paris'],
        'Prix': [450000, 620000, 250000, 580000],
        'Surface (m²)': [75, 120, 30, 95]
    })
    
    st.dataframe(search_data, use_container_width=True)
    
    st.subheader("Carte interactive")
    # Simulation d'une carte avec des points d'intérêt
    map_data = pd.DataFrame(
        np.random.randn(10, 2) / [50, 50] + [48.85, 2.35],
        columns=['lat', 'lon']
    )
    st.map(map_data)

def display_recommendations_page():
    st.title("Mes Recommandations")
    st.write("Découvrez les biens qui correspondent le mieux à vos critères.")
    
    # Simulation des données du radar
    criteria_data = pd.DataFrame({
        'Critère': ['Prix', 'Surface', 'Localisation', 'État', 'Proximité'],
        'Score': [85, 92, 78, 65, 88] 
    })
    
    fig = px.line_polar(criteria_data, r='Score', theta='Critère', line_close=True)
    fig.update_traces(fill='toself', marker_color='orange')
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Biens recommandés")
    # Simuler une liste de biens
    st.markdown("---")
    st.write("**Appartement 3 pièces**")
    st.write("📍 Paris | 💰 450 000€ | 📐 75 m²")
    st.button("Voir les détails", key="details_1")
    
    st.markdown("---")
    st.write("**Maison avec jardin**")
    st.write("📍 Lyon | 💰 620 000€ | 📐 120 m²")
    st.button("Voir les détails", key="details_2")
    
    st.markdown("---")
    
# --- Structure principale de l'application ---
def main():
    display_logo()
    
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        
    if not st.session_state['logged_in']:
        # Page d'accueil pour les utilisateurs non connectés
        display_home_page()
        # Simulation d'un login pour la démo
        if st.button("Simuler la connexion"):
            st.session_state['logged_in'] = True
            st.rerun()
    else:
        # Menus pour les utilisateurs connectés
        st.sidebar.title("Menu")
        selection = st.sidebar.radio("Navigation", ["Tableau de bord", "Mes informations", "Recherches avancées", "Recommandations"])
        
        if selection == "Tableau de bord":
            # Le dashboard est désormais la page d'accueil après connexion
            display_recommendations_page()
        elif selection == "Mes informations":
            display_my_info_page()
        elif selection == "Recherches avancées":
            display_search_page()
        elif selection == "Recommandations":
            display_recommendations_page()

if __name__ == "__main__":
    main()
