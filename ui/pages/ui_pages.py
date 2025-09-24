"""
Page d'accueil de l'application ImoMatch
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import logging

from config.settings import APP_CONFIG, COLORS, PLANS
from database.manager import get_database
from auth.authentication import is_authenticated, get_current_user
from ui.components import create_property_card, create_metric_card

logger = logging.getLogger(__name__)

def render():
    """Rend la page d'accueil"""
    
    # En-tête de bienvenue
    _render_hero_section()
    
    # Statistiques générales
    _render_statistics()
    
    # Section pour les utilisateurs connectés
    if is_authenticated():
        _render_user_dashboard()
    else:
        _render_visitor_content()
    
    # Propriétés récentes/populaires
    _render_featured_properties()
    
    # Call-to-action
    _render_cta_section()

def _render_hero_section():
    """Section hero de la page d'accueil"""
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem 0; background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['secondary']}); border-radius: 15px; margin-bottom: 2rem; color: white;">
        <h1 style="font-size: 3rem; margin-bottom: 1rem;">🏠 {APP_CONFIG['name']}</h1>
        <h3 style="font-weight: 300; margin-bottom: 2rem;">{APP_CONFIG['description']}</h3>
        <p style="font-size: 1.2rem; opacity: 0.9;">Trouvez votre bien immobilier idéal grâce à l'Intelligence Artificielle</p>
    </div>
    """, unsafe_allow_html=True)

def _render_statistics():
    """Affiche les statistiques générales de la plateforme"""
    try:
        db = get_database()
        stats = db.get_statistics()
        
        st.markdown("### 📊 Notre Plateforme en Chiffres")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            create_metric_card(
                title="Utilisateurs",
                value=f"{stats['total_users']:,}",
                icon="👥",
                color=COLORS['primary']
            )
        
        with col2:
            create_metric_card(
                title="Propriétés",
                value=f"{stats['total_properties']:,}",
                icon="🏠",
                color=COLORS['secondary']
            )
        
        with col3:
            create_metric_card(
                title="Prix Moyen",
                value=f"{stats['average_price']:,.0f}€",
                icon="💰",
                color=COLORS['accent']
            )
        
        with col4:
            # Type de propriété le plus populaire
            if stats['popular_property_types']:
                popular_type = stats['popular_property_types'][0]
                create_metric_card(
                    title="Plus Populaire",
                    value=popular_type['type'],
                    delta=f"{popular_type['count']} biens",
                    icon="⭐",
                    color=COLORS['success']
                )
        
        # Graphique des types de propriétés
        if stats['popular_property_types']:
            _render_property_types_chart(stats['popular_property_types'])
            
    except Exception as e:
        logger.error(f"Erreur lors du chargement des statistiques: {e}")
        st.warning("Impossible de charger les statistiques")

def _render_property_types_chart(property_types):
    """Affiche un graphique des types de propriétés"""
    st.markdown("### 🏘️ Répartition des Types de Biens")
    
    # Préparer les données
    types = [item['type'] for item in property_types]
    counts = [item['count'] for item in property_types]
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Graphique en barres
        fig_bar = px.bar(
            x=types,
            y=counts,
            title="Nombre de biens par type",
            color=counts,
            color_continuous_scale="Viridis"
        )
        fig_bar.update_layout(
            showlegend=False,
            xaxis_title="Type de bien",
            yaxis_title="Nombre",
            height=400
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        # Graphique en secteurs
        fig_pie = px.pie(
            values=counts,
            names=types,
            title="Répartition des types"
        )
        fig_pie.update_layout(height=400)
        st.plotly_chart(fig_pie, use_container_width=True)

def _render_user_dashboard():
    """Section spéciale pour les utilisateurs connectés"""
    user = get_current_user()
    st.markdown(f"### 👋 Bonjour {user['first_name']} !")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎯 Vos Actions Rapides")
        
        if st.button("🔍 Nouvelle Recherche", use_container_width=True):
            st.switch_page("search_page")
        
        if st.button("❤️ Mes Favoris", use_container_width=True):
            st.session_state['show_favorites'] = True
            st.rerun()
        
        if st.button("⚙️ Modifier mon Profil", use_container_width=True):
            st.switch_page("profile_page")
    
    with col2:
        st.markdown("#### 📈 Votre Activité")
        
        # Informations sur le plan
        plan_name = PLANS[user.get('plan', 'free')]['name']
        st.info(f"**Plan actuel:** {plan_name}")
        
        # Limites de recherche
        try:
            from auth.authentication import auth_manager
            limits = auth_manager.get_search_limits()
            
            if limits['remaining_searches'] == -1:
                st.success("🚀 Recherches illimitées")
            else:
                st.warning(f"📊 {limits['remaining_searches']} recherches restantes ce mois")
        except:
            pass

def _render_visitor_content():
    """Contenu pour les visiteurs non connectés"""
    st.markdown("### 🚀 Commencez Votre Recherche")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### ✨ Pourquoi Choisir ImoMatch ?
        
        - 🤖 **IA Avancée** : Recommandations personnalisées
        - 🗺️ **Cartes Interactives** : Visualisation géographique
        - 🔍 **Recherche Intelligente** : Filtres avancés
        - 💬 **Assistant IA** : Aide personnalisée
        - 📱 **Interface Moderne** : Design responsive
        """)
    
    with col2:
        st.markdown("#### 🎯 Nos Plans")
        
        for plan_key, plan_info in PLANS.items():
            with st.container():
                if plan_key == 'free':
                    color = COLORS['success']
                elif plan_key == 'premium':
                    color = COLORS['primary']
                else:
                    color = COLORS['secondary']
                
                st.markdown(f"""
                <div style="border: 2px solid {color}; border-radius: 10px; padding: 1rem; margin-bottom: 1rem;">
                    <h4 style="color: {color}; margin-top: 0;">{plan_info['name']}</h4>
                    <p><strong>{plan_info['price']}€/mois</strong></p>
                    <ul style="margin-bottom: 0;">
                        {''.join([f'<li>{feature}</li>' for feature in plan_info['features']])}
                    </ul>
                </div>
                """, unsafe_allow_html=True)
        
        if st.button("🔑 S'inscrire Maintenant", use_container_width=True, type="primary"):
            st.session_state['auth_tab'] = 'register'
            st.switch_page("auth_page")

def _render_featured_properties():
    """Affiche les propriétés mises en avant"""
    st.markdown("### 🌟 Propriétés à la Une")
    
    try:
        db = get_database()
        
        # Récupérer quelques propriétés récentes
        properties = db.search_properties({'limit': 6})
        
        if properties:
            # Afficher en grille 3x2
            cols = st.columns(3)
            
            for i, property_data in enumerate(properties):
                with cols[i % 3]:
                    create_property_card(property_data, show_details_button=True)
        else:
            st.info("Aucune propriété disponible pour le moment")
            
    except Exception as e:
        logger.error(f"Erreur lors du chargement des propriétés: {e}")
        st.warning("Impossible de charger les propriétés")

def _render_cta_section():
    """Section call-to-action finale"""
    if not is_authenticated():
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; padding: 3rem 1rem; background-color: #f8f9fa; border-radius: 15px; margin-top: 2rem;">
            <h2>🚀 Prêt à Trouver Votre Bien Idéal ?</h2>
            <p style="font-size: 1.2rem; margin-bottom: 2rem; color: #666;">
                Rejoignez des milliers d'utilisateurs qui font confiance à ImoMatch
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🎯 Créer Mon Compte Gratuit", use_container_width=True, type="primary"):
                st.session_state['auth_tab'] = 'register'
                st.switch_page("auth_page")
    
    else:
        # Pour les utilisateurs connectés
        user = get_current_user()
        if user.get('plan') == 'free':
            st.markdown("---")
            st.markdown("""
            <div style="text-align: center; padding: 2rem 1rem; background: linear-gradient(135deg, #FF6B35, #F7931E); border-radius: 15px; margin-top: 2rem; color: white;">
                <h2>⬆️ Passez au Premium !</h2>
                <p style="font-size: 1.1rem; margin-bottom: 1.5rem;">
                    Recherches illimitées • IA avancée • Support prioritaire
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("✨ Découvrir Premium", use_container_width=True, type="primary"):
                    st.switch_page("profile_page")

# Fonction utilitaire pour formater les nombres
def format_number(number):
    """Formate un nombre avec des séparateurs de milliers"""
    return f"{number:,}".replace(",", " ")

# Fonction pour créer des métriques colorées
def create_colored_metric(title, value, delta=None, color=COLORS['primary']):
    """Crée une métrique avec couleur personnalisée"""
    delta_html = f"<p style='color: {color}; font-size: 0.8rem; margin: 0;'>{delta}</p>" if delta else ""
    
    st.markdown(f"""
    <div style="background-color: white; padding: 1rem; border-radius: 10px; border-left: 4px solid {color}; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <p style="color: #666; font-size: 0.9rem; margin: 0;">{title}</p>
        <h3 style="color: {color}; margin: 0.5rem 0 0 0;">{value}</h3>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)