"""
Layout principal et structure de l'interface pour ImoMatch
"""
import streamlit as st
from datetime import datetime
import logging

from config.settings import COLORS, APP_CONFIG, STREAMLIT_CONFIG
from auth.authentication import auth_manager, get_current_user
from utils.helpers import get_app_statistics

logger = logging.getLogger(__name__)

def create_main_layout():
    """Crée le layout principal de l'application"""
    
    # CSS personnalisé
    _inject_custom_css()
    
    # Header de l'application
    _create_header()
    
    # Footer (sera affiché en bas)
    _create_footer()

def _inject_custom_css():
    """Injecte le CSS personnalisé dans l'application"""
    
    custom_css = f"""
    <style>
    /* Variables CSS pour les couleurs */
    :root {{
        --primary-color: {COLORS['primary']};
        --secondary-color: {COLORS['secondary']};
        --accent-color: {COLORS['accent']};
        --success-color: {COLORS['success']};
        --warning-color: {COLORS['warning']};
        --danger-color: {COLORS['danger']};
        --dark-color: {COLORS['dark']};
        --light-color: {COLORS['light']};
    }}
    
    /* Styles globaux */
    .main .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }}
    
    /* Header personnalisé */
    .custom-header {{
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        padding: 1rem 0;
        margin: -1rem -1rem 2rem -1rem;
        color: white;
        text-align: center;
        border-radius: 0 0 15px 15px;
    }}
    
    .custom-header h1 {{
        margin: 0;
        font-size: 2rem;
        font-weight: bold;
    }}
    
    .custom-header p {{
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-size: 1rem;
    }}
    
    /* Sidebar personnalisée */
    .css-1d391kg {{
        background-color: var(--light-color);
    }}
    
    /* Boutons personnalisés */
    .stButton > button {{
        border-radius: 10px;
        border: none;
        font-weight: 500;
        transition: all 0.3s ease;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }}
    
    /* Bouton primaire */
    .stButton > button[kind="primary"] {{
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: white;
    }}
    
    .stButton > button[kind="primary"]:hover {{
        background: linear-gradient(135deg, var(--secondary-color), var(--primary-color));
    }}
    
    /* Métriques personnalisées */
    .metric-card {{
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        text-align: center;
        transition: transform 0.3s ease;
    }}
    
    .metric-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 5px 20px rgba(0,0,0,0.15);
    }}
    
    .metric-value {{
        font-size: 2rem;
        font-weight: bold;
        color: var(--primary-color);
        margin: 0.5rem 0;
    }}
    
    .metric-label {{
        color: var(--dark-color);
        font-weight: 500;
        text-transform: uppercase;
        font-size: 0.9rem;
        letter-spacing: 0.5px;
    }}
    
    /* Cards de propriétés */
    .property-card {{
        background: white;
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 3px 15px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        margin-bottom: 1.5rem;
    }}
    
    .property-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }}
    
    .property-image {{
        width: 100%;
        height: 200px;
        object-fit: cover;
    }}
    
    .property-content {{
        padding: 1.5rem;
    }}
    
    .property-price {{
        font-size: 1.4rem;
        font-weight: bold;
        color: var(--primary-color);
        margin-bottom: 0.5rem;
    }}
    
    .property-title {{
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--dark-color);
        margin-bottom: 0.5rem;
    }}
    
    .property-details {{
        color: #666;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }}
    
    /* Alerts personnalisées */
    .custom-alert {{
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid;
    }}
    
    .alert-success {{
        background-color: #d4edda;
        border-color: var(--success-color);
        color: #155724;
    }}
    
    .alert-warning {{
        background-color: #fff3cd;
        border-color: var(--warning-color);
        color: #856404;
    }}
    
    .alert-danger {{
        background-color: #f8d7da;
        border-color: var(--danger-color);
        color: #721c24;
    }}
    
    .alert-info {{
        background-color: #cce7ff;
        border-color: var(--primary-color);
        color: #004085;
    }}
    
    /* Navigation tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        height: 50px;
        border-radius: 10px;
        background-color: white;
        border: 2px solid #e0e0e0;
        font-weight: 500;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: white;
        border-color: var(--primary-color);
    }}
    
    /* Formulaires */
    .stTextInput > div > div > input {{
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        padding: 0.75rem;
    }}
    
    .stTextInput > div > div > input:focus {{
        border-color: var(--primary-color);
        box-shadow: 0 0 0 0.2rem rgba(255, 107, 53, 0.25);
    }}
    
    .stSelectbox > div > div > div {{
        border-radius: 10px;
        border: 2px solid #e0e0e0;
    }}
    
    /* Progress bars */
    .stProgress > div > div > div > div {{
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        border-radius: 10px;
    }}
    
    /* Sidebar enhancements */
    .sidebar .sidebar-content {{
        background: linear-gradient(180deg, var(--light-color), white);
    }}
    
    /* Footer */
    .custom-footer {{
        background-color: var(--dark-color);
        color: white;
        padding: 2rem 1rem;
        margin-top: 3rem;
        text-align: center;
        border-radius: 15px 15px 0 0;
    }}
    
    .footer-links {{
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin-bottom: 1rem;
    }}
    
    .footer-links a {{
        color: white;
        text-decoration: none;
        font-weight: 500;
        opacity: 0.8;
    }}
    
    .footer-links a:hover {{
        opacity: 1;
        text-decoration: underline;
    }}
    
    /* Animations */
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    @keyframes slideIn {{
        from {{ transform: translateX(-100%); }}
        to {{ transform: translateX(0); }}
    }}
    
    .fade-in {{
        animation: fadeIn 0.6s ease-out;
    }}
    
    .slide-in {{
        animation: slideIn 0.5s ease-out;
    }}
    
    /* Responsive design */
    @media (max-width: 768px) {{
        .main .block-container {{
            padding-left: 1rem;
            padding-right: 1rem;
        }}
        
        .custom-header h1 {{
            font-size: 1.5rem;
        }}
        
        .footer-links {{
            flex-direction: column;
            gap: 1rem;
        }}
    }}
    
    /* Dark theme support (placeholder) */
    .dark-theme {{
        --bg-color: #1a1a1a;
        --text-color: #ffffff;
        --card-bg: #2d2d2d;
    }}
    
    /* Loading spinners */
    .loading-spinner {{
        border: 4px solid #f3f3f3;
        border-top: 4px solid var(--primary-color);
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 20px auto;
    }}
    
    @keyframes spin {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}
    
    /* Notification badges */
    .notification-badge {{
        background-color: var(--danger-color);
        color: white;
        border-radius: 50%;
        padding: 0.2rem 0.5rem;
        font-size: 0.7rem;
        font-weight: bold;
        position: absolute;
        top: -5px;
        right: -5px;
        min-width: 1.2rem;
        text-align: center;
    }}
    
    /* Tooltips */
    .tooltip {{
        position: relative;
        display: inline-block;
    }}
    
    .tooltip .tooltiptext {{
        visibility: hidden;
        width: 200px;
        background-color: var(--dark-color);
        color: white;
        text-align: center;
        border-radius: 6px;
        padding: 8px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
    }}
    
    .tooltip:hover .tooltiptext {{
        visibility: visible;
        opacity: 1;
    }}
    
    /* Scrollbar personnalisée */
    ::-webkit-scrollbar {{
        width: 8px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: var(--light-color);
        border-radius: 10px;
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: var(--primary-color);
        border-radius: 10px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: var(--secondary-color);
    }}
    </style>
    """
    
    st.markdown(custom_css, unsafe_allow_html=True)

def _create_header():
    """Crée le header de l'application"""
    
    user = get_current_user()
    current_time = datetime.now().strftime("%H:%M")
    
    # Header principal avec gradient
    st.markdown(f"""
    <div class="custom-header fade-in">
        <div style="display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto;">
            <div style="display: flex; align-items: center;">
                <div style="font-size: 2.5rem; margin-right: 1rem;">🏠</div>
                <div>
                    <h1 style="margin: 0; font-size: 1.8rem;">{APP_CONFIG['name']}</h1>
                    <p style="margin: 0; opacity: 0.9; font-size: 0.9rem;">{APP_CONFIG['description']}</p>
                </div>
            </div>
            
            <div style="text-align: right; opacity: 0.9;">
                <div style="font-size: 0.9rem;">
                    {current_time}
                </div>
                {"<div style='font-size: 0.8rem; margin-top: 0.2rem;'>👋 " + user['first_name'] + "</div>" if user else ""}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def _create_footer():
    """Crée le footer de l'application"""
    
    # Espacement avant le footer
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Footer avec informations et liens
    st.markdown(f"""
    <div class="custom-footer">
        <div class="footer-links">
            <a href="mailto:support@imomatch.fr">📧 Support</a>
            <a href="tel:+33123456789">📞 Contact</a>
            <a href="https://docs.imomatch.fr" target="_blank">📚 Documentation</a>
            <a href="#" onclick="alert('Politique de confidentialité')">🔒 Confidentialité</a>
            <a href="#" onclick="alert('Conditions d\\'utilisation')">📄 CGU</a>
        </div>
        
        <div style="border-top: 1px solid rgba(255,255,255,0.2); padding-top: 1rem; margin-top: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; max-width: 800px; margin: 0 auto;">
                <div>
                    <div style="font-weight: bold; margin-bottom: 0.5rem;">{APP_CONFIG['name']} v{APP_CONFIG['version']}</div>
                    <div style="opacity: 0.8; font-size: 0.9rem;">
                        © 2024 {APP_CONFIG['author']}. Tous droits réservés.
                    </div>
                </div>
                
                <div style="text-align: right;">
                    <div style="margin-bottom: 0.5rem;">🇫🇷 Fait en France</div>
                    <div style="opacity: 0.8; font-size: 0.8rem;">
                        Avec ❤️ pour l'immobilier
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_sidebar_info():
    """Crée la section d'informations dans la sidebar"""
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ℹ️ Informations")
    
    # Statistiques rapides
    try:
        stats = get_app_statistics()
        
        if stats:
            st.sidebar.metric(
                "Utilisateurs actifs", 
                f"{stats.get('total_users', 0):,}".replace(',', ' ')
            )
            
            st.sidebar.metric(
                "Propriétés disponibles", 
                f"{stats.get('total_properties', 0):,}".replace(',', ' ')
            )
    except:
        pass
    
    # Informations sur l'app
    st.sidebar.info(f"""
    **Version:** {APP_CONFIG['version']}
    
    **Dernière mise à jour:** Décembre 2024
    
    **Support:** {APP_CONFIG['email']}
    """)

def create_notification_area():
    """Crée une zone de notifications"""
    
    user = get_current_user()
    if not user:
        return
    
    # Vérifier s'il y a des notifications
    notifications = _get_user_notifications(user['id'])
    
    if notifications:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🔔 Notifications")
        
        for notif in notifications[:3]:  # Max 3 notifications
            notification_type = notif.get('type', 'info')
            
            if notification_type == 'new_property':
                st.sidebar.success(f"🏠 {notif['message']}")
            elif notification_type == 'price_change':
                st.sidebar.warning(f"💰 {notif['message']}")
            elif notification_type == 'search_alert':
                st.sidebar.info(f"🔍 {notif['message']}")
            else:
                st.sidebar.info(f"ℹ️ {notif['message']}")
        
        if len(notifications) > 3:
            st.sidebar.caption(f"... et {len(notifications) - 3} autres notifications")

def create_quick_stats_widget():
    """Widget de statistiques rapides pour le dashboard"""
    
    user = get_current_user()
    if not user:
        return
    
    try:
        from database.manager import get_database
        db = get_database()
        
        # Récupérer les stats utilisateur
        favorites_count = len(db.get_user_favorites(user['id']))
        searches_count = len(db.get_saved_searches(user['id']))
        
        # Afficher les stats
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 2rem;">❤️</div>
                <div class="metric-value">{favorites_count}</div>
                <div class="metric-label">Favoris</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 2rem;">💾</div>
                <div class="metric-value">{searches_count}</div>
                <div class="metric-label">Recherches</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            plan_info = user.get('plan', 'free')
            plan_emoji = "🆓" if plan_info == 'free' else "⭐" if plan_info == 'premium' else "💎"
            
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 2rem;">{plan_emoji}</div>
                <div class="metric-value">{plan_info.title()}</div>
                <div class="metric-label">Plan</div>
            </div>
            """, unsafe_allow_html=True)
    
    except Exception as e:
        logger.error(f"Erreur stats widget: {e}")

def create_search_suggestions_widget():
    """Widget de suggestions de recherche populaires"""
    
    st.markdown("### 🔥 Recherches Populaires")
    
    popular_searches = [
        {"query": "Appartement 3 pièces Antibes", "icon": "🏢"},
        {"query": "Villa piscine Cannes", "icon": "🏡"},
        {"query": "Studio Nice centre", "icon": "🏠"},
        {"query": "Maison jardin Juan-les-Pins", "icon": "🌳"},
        {"query": "Penthouse vue mer Monaco", "icon": "🏙️"}
    ]
    
    for search in popular_searches:
        if st.button(f"{search['icon']} {search['query']}", use_container_width=True, key=f"popular_{search['query']}"):
            # Lancer la recherche
            st.session_state['quick_search'] = search['query']
            st.info(f"Recherche lancée : {search['query']}")

def create_weather_widget():
    """Widget météo pour la Côte d'Azur"""
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🌤️ Météo Côte d'Azur")
    
    # Données météo simulées
    weather_data = {
        'temperature': 22,
        'condition': 'Ensoleillé',
        'humidity': 65,
        'wind': '10 km/h'
    }
    
    st.sidebar.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #87CEEB, #FFD700);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    ">
        <div style="font-size: 2rem;">☀️</div>
        <div style="font-size: 1.5rem; font-weight: bold;">{weather_data['temperature']}°C</div>
        <div>{weather_data['condition']}</div>
        <div style="font-size: 0.8rem; margin-top: 0.5rem; opacity: 0.9;">
            💧 {weather_data['humidity']}% • 💨 {weather_data['wind']}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.caption("Parfait pour visiter des biens ! 🏠")

def create_progress_indicator(current_step: int, total_steps: int, step_names: list):
    """Crée un indicateur de progression pour les processus multi-étapes"""
    
    st.markdown("### 📊 Progression")
    
    progress_html = "<div style='display: flex; align-items: center; margin: 1rem 0;'>"
    
    for i in range(total_steps):
        # Cercle d'étape
        if i < current_step:
            circle_style = f"background: {COLORS['success']}; color: white;"
            icon = "✓"
        elif i == current_step:
            circle_style = f"background: {COLORS['primary']}; color: white;"
            icon = str(i + 1)
        else:
            circle_style = "background: #e0e0e0; color: #666;"
            icon = str(i + 1)
        
        progress_html += f"""
        <div style="display: flex; flex-direction: column; align-items: center;">
            <div style="
                width: 40px;
                height: 40px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                {circle_style}
            ">{icon}</div>
            <small style="margin-top: 0.5rem; text-align: center; max-width: 80px;">
                {step_names[i] if i < len(step_names) else f"Étape {i+1}"}
            </small>
        </div>
        """
        
        # Ligne de connexion
        if i < total_steps - 1:
            line_color = COLORS['success'] if i < current_step else "#e0e0e0"
            progress_html += f"""
            <div style="
                flex: 1;
                height: 2px;
                background: {line_color};
                margin: 0 1rem;
                align-self: flex-start;
                margin-top: 20px;
            "></div>
            """
    
    progress_html += "</div>"
    st.markdown(progress_html, unsafe_allow_html=True)

def create_loading_screen(message: str = "Chargement..."):
    """Crée un écran de chargement"""
    
    st.markdown(f"""
    <div style="
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 200px;
        text-align: center;
    ">
        <div class="loading-spinner"></div>
        <p style="margin-top: 1rem; color: {COLORS['primary']}; font-weight: 500;">
            {message}
        </p>
    </div>
    """, unsafe_allow_html=True)

def create_error_page(error_type: str = "general", custom_message: str = None):
    """Crée une page d'erreur stylisée"""
    
    error_configs = {
        "404": {
            "icon": "🔍",
            "title": "Page Non Trouvée",
            "message": "La page que vous cherchez n'existe pas ou a été déplacée.",
            "color": COLORS['warning']
        },
        "403": {
            "icon": "🔒",
            "title": "Accès Refusé", 
            "message": "Vous n'avez pas l'autorisation d'accéder à cette page.",
            "color": COLORS['danger']
        },
        "500": {
            "icon": "⚠️",
            "title": "Erreur Serveur",
            "message": "Une erreur technique s'est produite. Veuillez réessayer plus tard.",
            "color": COLORS['danger']
        },
        "general": {
            "icon": "❌",
            "title": "Erreur",
            "message": custom_message or "Une erreur s'est produite.",
            "color": COLORS['danger']
        }
    }
    
    config = error_configs.get(error_type, error_configs["general"])
    
    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 3rem 1rem;
        color: {config['color']};
    ">
        <div style="font-size: 4rem; margin-bottom: 1rem;">
            {config['icon']}
        </div>
        <h2 style="color: {config['color']}; margin-bottom: 1rem;">
            {config['title']}
        </h2>
        <p style="font-size: 1.1rem; color: #666; margin-bottom: 2rem;">
            {config['message']}
        </p>
        <div>
            <button onclick="history.back()" style="
                background: {COLORS['primary']};
                color: white;
                border: none;
                padding: 0.75rem 2rem;
                border-radius: 10px;
                font-size: 1rem;
                cursor: pointer;
                margin-right: 1rem;
            ">
                ← Retour
            </button>
            <button onclick="location.href='/'" style="
                background: {COLORS['secondary']};
                color: white;
                border: none;
                padding: 0.75rem 2rem;
                border-radius: 10px;
                font-size: 1rem;
                cursor: pointer;
            ">
                🏠 Accueil
            </button>
        </div>
    </div>
    """, unsafe_allow_html=True)

def _get_user_notifications(user_id: int) -> List[Dict[str, str]]:
    """Récupère les notifications utilisateur"""
    
    # Simulation de notifications
    # Dans une vraie implémentation, récupérer depuis la base de données
    notifications = [
        {
            'type': 'new_property',
            'message': 'Nouvelle propriété correspondant à vos critères !',
            'timestamp': '2024-01-15 14:30'
        },
        {
            'type': 'price_change',
            'message': 'Baisse de prix sur une propriété en favoris',
            'timestamp': '2024-01-14 09:15'
        }
    ]
    
    return notifications

def show_debug_info():
    """Affiche des informations de debug (développement uniquement)"""
    
    if not st.secrets.get("DEBUG_MODE", False):
        return
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🐛 Debug Info")
    
    with st.sidebar.expander("Session State"):
        st.write(dict(st.session_state))
    
    with st.sidebar.expander("App Stats"):
        try:
            stats = get_app_statistics()
            st.json(stats)
        except:
            st.write("Erreur de chargement des stats")

# Fonctions utilitaires pour l'interface
def add_custom_metric(title: str, value: str, delta: str = None, color: str = COLORS['primary']):
    """Ajoute une métrique personnalisée"""
    
    delta_html = f"<div style='color: {color}; font-size: 0.8rem; margin-top: 0.2rem;'>{delta}</div>" if delta else ""
    
    st.markdown(f"""
    <div class="metric-card" style="border-left: 4px solid {color};">
        <div class="metric-value" style="color: {color};">{value}</div>
        <div class="metric-label">{title}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

def create_success_animation():
    """Crée une animation de succès"""
    
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <div style="font-size: 4rem; animation: bounce 1s ease-in-out;">
            ✅
        </div>
        <h3 style="color: var(--success-color); margin-top: 1rem;">
            Opération réussie !
        </h3>
    </div>
    
    <style>
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-20px); }
    }
    </style>
    """, unsafe_allow_html=True)