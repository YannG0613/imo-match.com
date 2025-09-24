"""
ImoMatch - Application Principale CORRIGÉE
Point d'entrée de l'application immobilière avec IA
"""
import streamlit as st
import logging
import sys
import os
from pathlib import Path
from ui.footer import show_footer

# Ajouter le répertoire racine au PYTHONPATH
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('imomatch.log') if os.path.exists('.') else logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def check_dependencies():
    """Vérifie que toutes les dépendances sont disponibles"""
    missing_deps = []
    
    try:
        import folium
        import plotly
        import pandas
    except ImportError as e:
        missing_deps.append(str(e))
    
    if missing_deps:
        st.error("Dépendances manquantes :")
        for dep in missing_deps:
            st.write(f"- {dep}")
        st.info("Installez les dépendances avec : `pip install -r requirements.txt`")
        st.stop()

def init_streamlit_config():
    """Initialise la configuration Streamlit"""
    try:
        from config.settings import STREAMLIT_CONFIG
        st.set_page_config(**STREAMLIT_CONFIG)
    except ImportError:
        # Configuration de fallback
        st.set_page_config(
            page_title="ImoMatch - Immobilier IA",
            page_icon="🏠",
            layout="wide",
            initial_sidebar_state="expanded"
        )

def init_database():
    """Initialise la base de données si nécessaire"""
    try:
        from database.manager import get_database
        from database.migrations import get_migration_status
        
        # Vérifier l'état de la base
        status = get_migration_status()
        
        if status.get('total_properties', 0) == 0:
            st.info("🔄 Initialisation de la base de données en cours...")
            
            # Lancer les migrations si nécessaire
            from database.migrations import run_all_migrations
            if run_all_migrations():
                st.success("✅ Base de données initialisée avec succès !")
                st.rerun()
            else:
                st.error("❌ Erreur lors de l'initialisation de la base de données")
                
    except ImportError as e:
        st.error(f"Erreur d'import des modules de base de données : {e}")
        st.info("Vérifiez que tous les fichiers sont présents selon l'architecture")
    except Exception as e:
        logger.error(f"Erreur initialisation base de données : {e}")
        st.error(f"Erreur d'initialisation : {e}")

class ImoMatchApp:
    """Application principale ImoMatch"""
    
    def __init__(self):
        self.pages = {}
        self.current_page = None
        self.init_modules()
    
    def init_modules(self):
        """Initialise les modules de l'application"""
        try:
            # Import des modules essentiels
            from auth.authentication import auth_manager
            self.auth = auth_manager
            
            # Import des utilitaires
            from utils.helpers import init_session_state
            init_session_state()
            
            # Import des pages (avec gestion d'erreurs)
            self.load_pages()
            
        except ImportError as e:
            st.error(f"Erreur d'import des modules : {e}")
            st.info("Vérifiez que tous les fichiers sont présents et que la structure est correcte")
            st.stop()
    
    def load_pages(self):
        """Charge les pages disponibles avec gestion d'erreurs"""
        # Pages de base (toujours disponibles)
        self.pages = {
            "🏠 Accueil": self._home_page,
            "🔑 Authentification": self._auth_page
        }
        
        # Pages pour utilisateurs connectés
        authenticated_pages = {
            "🔍 Recherche": self._search_page,
            "👤 Profil": self._profile_page,
            "📊 Tableau de bord": self._dashboard_page
        }
        
        # Ajouter les pages authentifiées si l'utilisateur est connecté
        if self.auth.is_authenticated():
            self.pages.update(authenticated_pages)
    
    def run(self):
        """Lance l'application"""
        try:
            # Créer le layout principal
            self._create_layout()
            
            # Navigation et affichage
            self._handle_navigation()
            
            # Affiche le cartouche de bas de page
            show_footer()
        except Exception as e:
            logger.error(f"Erreur dans l'application principale: {e}")
            st.error("Une erreur s'est produite. Veuillez actualiser la page.")
            st.exception(e)
    
    def _create_layout(self):
        """Crée le layout de l'application"""
        try:
            from ui.layout import create_main_layout
            create_main_layout()
        except ImportError:
            # Layout de fallback
            st.markdown("# 🏠 ImoMatch")
            st.markdown("*Application immobilière avec Intelligence Artificielle*")
    
    def _handle_navigation(self):
        """Gère la navigation entre les pages"""
        
        # Sidebar pour la navigation
        with st.sidebar:
            st.title("🏠 ImoMatch")
            
            # Informations utilisateur
            if self.auth.is_authenticated():
                user = self.auth.get_current_user()
                st.success(f"👋 {user['first_name']}")
                
                # Bouton de déconnexion
                if st.button("🚪 Se déconnecter"):
                    self.auth.logout()
                    st.rerun()
            else:
                st.info("👤 Non connecté")
            
            # Navigation
            st.markdown("---")
            
            # Recharger les pages selon l'état de connexion
            self.load_pages()
            
            # Sélection de page
            if self.pages:
                selected_page = st.selectbox(
                    "Navigation",
                    list(self.pages.keys()),
                    key="main_navigation"
                )
                
                # Afficher la page sélectionnée
                if selected_page in self.pages:
                    self.pages[selected_page]()
                else:
                    st.error(f"Page non trouvée: {selected_page}")
            else:
                st.error("Aucune page disponible")
    
    # === PAGES DE L'APPLICATION ===
    
    def _home_page(self):
        """Page d'accueil"""
        st.markdown("## 🏠 Accueil")
        
        try:
            from ui.pages import home_page
            home_page.render()
        except ImportError:
            self._fallback_home_page()
        except Exception as e:
            logger.error(f"Erreur page d'accueil: {e}")
            st.error("Erreur lors du chargement de la page d'accueil")
    
    def _auth_page(self):
        """Pages d'authentification"""
        st.markdown("## 🔑 Authentification")
        
        try:
            from ui.pages import auth_pages
            auth_pages.render()
        except ImportError:
            self._fallback_auth_page()
        except Exception as e:
            logger.error(f"Erreur page d'authentification: {e}")
            st.error("Erreur lors du chargement de la page d'authentification")
    
    def _search_page(self):
        """Page de recherche"""
        if not self.auth.is_authenticated():
            st.warning("Veuillez vous connecter pour accéder à la recherche")
            return
        
        st.markdown("## 🔍 Recherche")
        
        try:
            from ui.pages import search_page
            search_page.render()
        except ImportError:
            self._fallback_search_page()
        except Exception as e:
            logger.error(f"Erreur page de recherche: {e}")
            st.error("Erreur lors du chargement de la page de recherche")
    
    def _profile_page(self):
        """Page de profil"""
        if not self.auth.is_authenticated():
            st.warning("Veuillez vous connecter pour accéder à votre profil")
            return
        
        st.markdown("## 👤 Profil")
        
        try:
            from ui.pages import profile_page
            profile_page.render()
        except ImportError:
            self._fallback_profile_page()
        except Exception as e:
            logger.error(f"Erreur page de profil: {e}")
            st.error("Erreur lors du chargement du profil")
    
    def _dashboard_page(self):
        """Tableau de bord"""
        if not self.auth.is_authenticated():
            st.warning("Veuillez vous connecter pour accéder au tableau de bord")
            return
        
        st.markdown("## 📊 Tableau de Bord")
        
        try:
            from ui.pages import dashboard_page
            dashboard_page.render()
        except ImportError:
            self._fallback_dashboard_page()
        except Exception as e:
            logger.error(f"Erreur tableau de bord: {e}")
            st.error("Erreur lors du chargement du tableau de bord")
    
    # === PAGES DE FALLBACK ===
    
    def _fallback_home_page(self):
        """Page d'accueil de fallback"""
        st.markdown("""
        ### 🏠 Bienvenue sur ImoMatch !
        
        ImoMatch est votre assistant IA pour la recherche immobilière sur la Côte d'Azur.
        
        **Fonctionnalités :**
        - 🔍 Recherche intelligente de propriétés
        - 🤖 Recommandations personnalisées par IA
        - 🗺️ Cartes interactives
        - ❤️ Système de favoris
        - 📊 Analyses de marché
        
        **Pour commencer :**
        1. Créez votre compte ou connectez-vous
        2. Définissez vos critères de recherche
        3. Explorez les propriétés disponibles
        4. Utilisez l'IA pour des recommandations personnalisées
        """)
        
        if not self.auth.is_authenticated():
            st.info("👆 Utilisez le menu de navigation pour vous connecter ou créer un compte")
    
    def _fallback_auth_page(self):
        """Page d'authentification de fallback"""
        tab1, tab2 = st.tabs(["🔓 Connexion", "📝 Inscription"])
        
        with tab1:
            st.markdown("### Connexion")
            
            with st.form("login_form"):
                email = st.text_input("Email")
                password = st.text_input("Mot de passe", type="password")
                
                if st.form_submit_button("Se connecter"):
                    if email and password:
                        success, message = self.auth.login(email, password)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                    else:
                        st.error("Veuillez remplir tous les champs")
        
        with tab2:
            st.markdown("### Inscription")
            
            with st.form("register_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    first_name = st.text_input("Prénom")
                    email = st.text_input("Email")
                    password = st.text_input("Mot de passe", type="password")
                
                with col2:
                    last_name = st.text_input("Nom")
                    phone = st.text_input("Téléphone (optionnel)")
                    confirm_password = st.text_input("Confirmer le mot de passe", type="password")
                
                age = st.number_input("Âge", min_value=18, max_value=99, value=30)
                profession = st.text_input("Profession (optionnel)")
                
                terms_accepted = st.checkbox("J'accepte les conditions d'utilisation")
                
                if st.form_submit_button("Créer mon compte"):
                    if not all([first_name, last_name, email, password, confirm_password]):
                        st.error("Veuillez remplir tous les champs obligatoires")
                    elif password != confirm_password:
                        st.error("Les mots de passe ne correspondent pas")
                    elif not terms_accepted:
                        st.error("Vous devez accepter les conditions d'utilisation")
                    else:
                        user_data = {
                            'first_name': first_name,
                            'last_name': last_name,
                            'email': email,
                            'password': password,
                            'confirm_password': confirm_password,
                            'phone': phone if phone else None,
                            'age': age,
                            'profession': profession if profession else None
                        }
                        
                        success, message = self.auth.register(user_data)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
    
    def _fallback_search_page(self):
        """Page de recherche de fallback"""
        st.markdown("### 🔍 Recherche de Propriétés")
        
        # Formulaire de recherche simple
        with st.form("search_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                budget_max = st.number_input("Budget maximum (€)", min_value=50000, max_value=5000000, value=500000, step=25000)
                property_type = st.selectbox("Type de bien", ["Tous", "Appartement", "Maison", "Villa", "Studio"])
            
            with col2:
                location = st.text_input("Localisation", placeholder="Ex: Antibes, Cannes...")
                bedrooms = st.number_input("Chambres minimum", min_value=0, max_value=10, value=1)
            
            if st.form_submit_button("🔍 Rechercher"):
                # Recherche basique
                try:
                    from database.manager import get_database
                    db = get_database()
                    
                    filters = {}
                    if budget_max:
                        filters['price_max'] = budget_max
                    if property_type != "Tous":
                        filters['property_type'] = property_type
                    if location:
                        filters['location'] = location
                    if bedrooms:
                        filters['bedrooms'] = bedrooms
                    
                    properties = db.search_properties(filters)
                    
                    if properties:
                        st.success(f"✅ {len(properties)} propriété(s) trouvée(s)")
                        
                        for prop in properties[:5]:  # Afficher max 5 résultats
                            with st.container():
                                st.markdown(f"**{prop['title']}**")
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    st.write(f"💰 {prop['price']:,}€")
                                with col2:
                                    st.write(f"📐 {prop.get('surface', 'N/A')}m²")
                                with col3:
                                    st.write(f"📍 {prop['location']}")
                                
                                if prop.get('description'):
                                    st.write(prop['description'][:100] + "...")
                                
                                st.markdown("---")
                    else:
                        st.info("Aucune propriété trouvée avec ces critères")
                        
                except Exception as e:
                    st.error(f"Erreur lors de la recherche : {e}")
    
    def _fallback_profile_page(self):
        """Page de profil de fallback"""
        user = self.auth.get_current_user()
        
        st.markdown(f"### 👤 Profil de {user['first_name']} {user['last_name']}")
        
        tab1, tab2 = st.tabs(["📝 Informations", "⚙️ Préférences"])
        
        with tab1:
            st.markdown("#### Informations personnelles")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Email :** {user['email']}")
                st.write(f"**Plan :** {user.get('plan', 'free').title()}")
            
            with col2:
                if user.get('phone'):
                    st.write(f"**Téléphone :** {user['phone']}")
                if user.get('profession'):
                    st.write(f"**Profession :** {user['profession']}")
        
        with tab2:
            st.markdown("#### Préférences de recherche")
            
            try:
                from database.manager import get_database
                db = get_database()
                prefs = db.get_user_preferences(user['id'])
                
                if prefs:
                    if prefs.get('budget_max'):
                        st.write(f"**Budget max :** {prefs['budget_max']:,}€")
                    if prefs.get('property_type'):
                        st.write(f"**Type préféré :** {prefs['property_type']}")
                    if prefs.get('location'):
                        st.write(f"**Localisation :** {prefs['location']}")
                else:
                    st.info("Aucune préférence définie")
                    
            except Exception as e:
                st.error(f"Erreur chargement préférences : {e}")
    
    def _fallback_dashboard_page(self):
        """Tableau de bord de fallback"""
        user = self.auth.get_current_user()
        
        st.markdown(f"### 📊 Tableau de bord de {user['first_name']}")
        
        try:
            from database.manager import get_database
            db = get_database()
            
            # Statistiques utilisateur
            favorites = db.get_user_favorites(user['id'])
            saved_searches = db.get_saved_searches(user['id'])
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Favoris", len(favorites))
            
            with col2:
                st.metric("Recherches sauvées", len(saved_searches))
            
            with col3:
                plan = user.get('plan', 'free')
                st.metric("Plan", plan.title())
            
            # Favoris récents
            if favorites:
                st.markdown("#### ❤️ Favoris récents")
                for fav in favorites[:3]:
                    st.write(f"• **{fav['title']}** - {fav['price']:,}€ à {fav['location']}")
            
        except Exception as e:
            st.error(f"Erreur chargement dashboard : {e}")


def main():
    """Fonction principale"""
    try:
        # Vérifications préliminaires
        check_dependencies()
        
        # Configuration Streamlit
        init_streamlit_config()
        
        # Initialisation de la base de données
        init_database()
        
        # Lancer l'application
        app = ImoMatchApp()
        app.run()
        
    except Exception as e:
        logger.error(f"Erreur critique dans main(): {e}")
        st.error("❌ Erreur critique de l'application")
        st.exception(e)
        
        # Instructions de dépannage
        st.markdown("""
        ### 🔧 Dépannage
        
        1. **Vérifiez que tous les fichiers sont présents** selon l'architecture
        2. **Installez les dépendances** : `pip install -r requirements.txt`
        3. **Initialisez la base de données** : `python -m database.migrations --action migrate`
        4. **Vérifiez les logs** pour plus de détails
        
        Si le problème persiste, consultez le fichier `QUICK_START.md`
        """)


if __name__ == "__main__":
    main()
