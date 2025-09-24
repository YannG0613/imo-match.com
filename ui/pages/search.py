"""
Page de recherche avancée pour ImoMatch
"""
import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import logging
from typing import Dict, Any, List

from config.settings import PROPERTY_TYPES, VALIDATION_RULES, MAP_CONFIG
from database.manager import get_database
from auth.authentication import auth_manager, get_current_user
from ui.components import create_property_card, create_map_marker
from search.filters import SearchFilters
from search.engine import SearchEngine

logger = logging.getLogger(__name__)

def render():
    """Rend la page de recherche"""
    
    # Vérification des limites de recherche
    if not _check_search_limits():
        return
    
    # Interface de recherche
    st.markdown("# 🔍 Recherche Immobilière")
    
    # Layout principal
    search_col, map_col = st.columns([1, 1])
    
    with search_col:
        _render_search_filters()
    
    with map_col:
        _render_map()
    
    # Résultats de recherche
    _render_search_results()
    
    # Agent IA pour aide à la recherche
    _render_ai_assistant()

def _check_search_limits():
    """Vérifie les limites de recherche de l'utilisateur"""
    limits = auth_manager.get_search_limits()
    
    if not limits['can_search']:
        st.error("🚫 Limite de recherches atteinte pour ce mois")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"""
            **Plan actuel:** {limits['plan_name']}
            
            Vous avez atteint la limite de recherches mensuelles.
            """)
        
        with col2:
            st.markdown("### 🚀 Passez au Premium")
            from config.settings import PLANS
            
            for plan in ['premium', 'professional']:
                plan_info = PLANS[plan]
                if st.button(f"✨ {plan_info['name']} - {plan_info['price']}€/mois", key=f"upgrade_{plan}"):
                    if auth_manager.upgrade_plan(plan):
                        st.success(f"Bienvenue dans le plan {plan_info['name']} !")
                        st.rerun()
        
        return False
    
    # Afficher le nombre de recherches restantes pour les comptes gratuits
    if limits['remaining_searches'] > 0 and limits['remaining_searches'] != -1:
        st.info(f"ℹ️ {limits['remaining_searches']} recherches restantes ce mois")
    
    return True

def _render_search_filters():
    """Interface des filtres de recherche"""
    st.markdown("### 🎯 Filtres de Recherche")
    
    with st.form("search_filters"):
        # Budget
        st.markdown("#### 💰 Budget")
        col1, col2 = st.columns(2)
        
        with col1:
            budget_min = st.number_input(
                "Budget minimum (€)",
                min_value=VALIDATION_RULES['price']['min'],
                max_value=VALIDATION_RULES['price']['max'],
                value=100000,
                step=10000,
                format="%d"
            )
        
        with col2:
            budget_max = st.number_input(
                "Budget maximum (€)",
                min_value=VALIDATION_RULES['price']['min'],
                max_value=VALIDATION_RULES['price']['max'],
                value=500000,
                step=10000,
                format="%d"
            )
        
        # Type de bien
        st.markdown("#### 🏠 Type de Bien")
        property_type = st.selectbox(
            "Sélectionnez le type",
            options=["Tous"] + PROPERTY_TYPES,
            index=0
        )
        
        # Caractéristiques
        st.markdown("#### 📐 Caractéristiques")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            bedrooms = st.number_input(
                "Chambres (min)",
                min_value=0,
                max_value=10,
                value=1,
                step=1
            )
        
        with col2:
            bathrooms = st.number_input(
                "Salles de bain (min)",
                min_value=0,
                max_value=5,
                value=1,
                step=1
            )
        
        with col3:
            surface_min = st.number_input(
                "Surface min (m²)",
                min_value=10,
                max_value=1000,
                value=50,
                step=10
            )
        
        # Localisation
        st.markdown("#### 📍 Localisation")
        location = st.text_input(
            "Ville ou région",
            placeholder="Ex: Antibes, Cannes, Nice..."
        )
        
        # Critères avancés (pour utilisateurs premium)
        user = get_current_user()
        if user and auth_manager.can_access_feature('advanced_search'):
            st.markdown("#### ⚙️ Critères Avancés")
            
            with st.expander("Options avancées"):
                has_garage = st.checkbox("Garage", value=False)
                has_garden = st.checkbox("Jardin", value=False)
                has_pool = st.checkbox("Piscine", value=False)
                has_balcony = st.checkbox("Balcon/Terrasse", value=False)
                furnished = st.checkbox("Meublé", value=False)
                
                # Année de construction
                year_built_min = st.number_input(
                    "Année de construction (min)",
                    min_value=1900,
                    max_value=2024,
                    value=1980,
                    step=1
                )
                
                # Étage
                floor_min = st.number_input("Étage minimum", min_value=0, max_value=50, value=0)
                floor_max = st.number_input("Étage maximum", min_value=0, max_value=50, value=10)
        
        # Bouton de recherche
        search_button = st.form_submit_button("🔍 Rechercher", type="primary", use_container_width=True)
        
        if search_button:
            # Construire les filtres
            filters = {
                'price_min': budget_min,
                'price_max': budget_max,
                'property_type': property_type if property_type != "Tous" else None,
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'surface_min': surface_min,
                'location': location if location else None
            }
            
            # Ajouter les critères avancés si disponibles
            if user and auth_manager.can_access_feature('advanced_search'):
                advanced_criteria = {
                    'has_garage': has_garage,
                    'has_garden': has_garden,
                    'has_pool': has_pool,
                    'has_balcony': has_balcony,
                    'furnished': furnished,
                    'year_built_min': year_built_min,
                    'floor_min': floor_min,
                    'floor_max': floor_max
                }
                filters.update(advanced_criteria)
            
            # Effectuer la recherche
            _perform_search(filters)

def _perform_search(filters: Dict[str, Any]):
    """Effectue la recherche avec les filtres donnés"""
    try:
        # Utiliser une recherche (décrémenter le compteur)
        if not auth_manager.use_search():
            st.error("Impossible d'effectuer la recherche")
            return
        
        # Recherche en base de données
        db = get_database()
        properties = db.search_properties(filters)
        
        # Sauvegarder les résultats dans la session
        st.session_state['current_search_filters'] = filters
        st.session_state['current_properties'] = properties
        
        # Afficher le nombre de résultats
        st.success(f"✅ {len(properties)} propriété(s) trouvée(s)")
        
        # Option pour sauvegarder la recherche
        _render_save_search_option(filters)
        
        logger.info(f"Recherche effectuée par l'utilisateur {get_current_user()['id']}: {len(properties)} résultats")
        
    except Exception as e:
        logger.error(f"Erreur lors de la recherche: {e}")
        st.error("Erreur lors de la recherche. Veuillez réessayer.")

def _render_save_search_option(filters: Dict[str, Any]):
    """Option pour sauvegarder la recherche"""
    with st.expander("💾 Sauvegarder cette recherche"):
        search_name = st.text_input("Nom de la recherche", placeholder="Ma recherche d'appartement à Antibes")
        alert_enabled = st.checkbox("Recevoir des alertes pour de nouveaux biens")
        
        if st.button("💾 Sauvegarder", key="save_search"):
            if search_name:
                try:
                    db = get_database()
                    search_id = db.save_search(
                        user_id=get_current_user()['id'],
                        name=search_name,
                        filters=filters,
                        alert_enabled=alert_enabled
                    )
                    st.success("Recherche sauvegardée avec succès !")
                except Exception as e:
                    logger.error(f"Erreur sauvegarde recherche: {e}")
                    st.error("Erreur lors de la sauvegarde")
            else:
                st.warning("Veuillez donner un nom à votre recherche")

def _render_map():
    """Affiche la carte interactive"""
    st.markdown("### 🗺️ Carte Interactive")
    
    # Créer la carte Folium
    center = MAP_CONFIG['default_location']
    m = folium.Map(location=center, zoom_start=MAP_CONFIG['default_zoom'])
    
    # Ajouter les propriétés à la carte si des résultats existent
    if 'current_properties' in st.session_state:
        properties = st.session_state['current_properties']
        
        for prop in properties:
            if prop.get('latitude') and prop.get('longitude'):
                # Couleur du marker selon le type de bien
                color = MAP_CONFIG['marker_colors'].get(
                    prop['property_type'].lower(), 
                    'blue'
                )
                
                # Popup avec informations de la propriété
                popup_html = f"""
                <div style="width: 200px;">
                    <h4>{prop['title']}</h4>
                    <p><strong>{prop['price']:,}€</strong></p>
                    <p>{prop['property_type']} - {prop.get('surface', 'N/A')}m²</p>
                    <p>📍 {prop['location']}</p>
                </div>
                """
                
                folium.Marker(
                    location=[prop['latitude'], prop['longitude']],
                    popup=folium.Popup(popup_html, max_width=250),
                    tooltip=f"{prop['title']} - {prop['price']:,}€",
                    icon=folium.Icon(color=color, icon='home')
                ).add_to(m)
    
    # Afficher la carte
    map_data = st_folium(m, width=700, height=400)
    
    # Gérer les clics sur la carte (pour utilisateurs premium)
    user = get_current_user()
    if user and auth_manager.can_access_feature('advanced_search') and map_data['last_clicked']:
        clicked_lat = map_data['last_clicked']['lat']
        clicked_lng = map_data['last_clicked']['lng']
        st.info(f"📍 Coordonnées cliquées: {clicked_lat:.4f}, {clicked_lng:.4f}")

def _render_search_results():
    """Affiche les résultats de recherche"""
    if 'current_properties' not in st.session_state:
        st.info("👆 Utilisez les filtres ci-dessus pour commencer votre recherche")
        return
    
    properties = st.session_state['current_properties']
    
    if not properties:
        st.warning("🔍 Aucune propriété ne correspond à vos critères")
        st.markdown("**Suggestions:**")
        st.markdown("- Élargissez votre fourchette de budget")
        st.markdown("- Réduisez le nombre de chambres requises") 
        st.markdown("- Essayez une localisation différente")
        return
    
    st.markdown(f"### 🏠 Résultats ({len(properties)} propriétés)")
    
    # Options de tri
    col1, col2 = st.columns([2, 1])
    
    with col1:
        sort_option = st.selectbox(
            "Trier par:",
            options=[
                ("date", "Plus récentes"),
                ("price_asc", "Prix croissant"),
                ("price_desc", "Prix décroissant"),
                ("surface_desc", "Surface décroissante")
            ],
            format_func=lambda x: x[1]
        )
    
    with col2:
        results_per_page = st.selectbox(
            "Résultats par page:",
            options=[6, 12, 24],
            index=0
        )
    
    # Tri des propriétés
    sorted_properties = _sort_properties(properties, sort_option[0])
    
    # Pagination
    total_pages = (len(sorted_properties) + results_per_page - 1) // results_per_page
    
    if total_pages > 1:
        page = st.selectbox(
            "Page:",
            options=list(range(1, total_pages + 1)),
            index=0
        ) - 1
    else:
        page = 0
    
    start_idx = page * results_per_page
    end_idx = start_idx + results_per_page
    page_properties = sorted_properties[start_idx:end_idx]
    
    # Affichage en grille
    cols = st.columns(3)
    
    for i, prop in enumerate(page_properties):
        with cols[i % 3]:
            create_property_card(prop, show_details_button=True, show_favorite_button=True)
            
            # Bouton de contact (pour utilisateurs premium)
            user = get_current_user()
            if user and auth_manager.can_access_feature('advanced_search'):
                if st.button(f"📞 Contacter", key=f"contact_{prop['id']}"):
                    _show_contact_modal(prop)

def _sort_properties(properties: List[Dict], sort_by: str) -> List[Dict]:
    """Trie les propriétés selon le critère choisi"""
    if sort_by == "price_asc":
        return sorted(properties, key=lambda x: x.get('price', 0))
    elif sort_by == "price_desc":
        return sorted(properties, key=lambda x: x.get('price', 0), reverse=True)
    elif sort_by == "surface_desc":
        return sorted(properties, key=lambda x: x.get('surface', 0), reverse=True)
    else:  # date (par défaut)
        return sorted(properties, key=lambda x: x.get('created_at', ''), reverse=True)

def _show_contact_modal(property_data: Dict):
    """Affiche les informations de contact pour une propriété"""
    with st.expander(f"📞 Contact pour {property_data['title']}", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Informations du bien:**")
            st.write(f"Prix: {property_data['price']:,}€")
            st.write(f"Surface: {property_data.get('surface', 'N/A')}m²")
            st.write(f"Type: {property_data['property_type']}")
            st.write(f"Localisation: {property_data['location']}")
        
        with col2:
            st.markdown("**Contact:**")
            agent_info = property_data.get('agent_contact', 'Non disponible')
            st.write(f"Agent: {agent_info}")
            
            # Formulaire de contact rapide
            st.markdown("**Message rapide:**")
            message = st.text_area(
                "Votre message",
                value=f"Bonjour, je suis intéressé(e) par le bien '{property_data['title']}' au prix de {property_data['price']:,}€. Pourriez-vous me donner plus d'informations ?",
                height=100
            )
            
            if st.button("📧 Envoyer le message", key=f"send_msg_{property_data['id']}"):
                # Ici, intégrer l'envoi d'email
                st.success("Message envoyé à l'agent !")

def _render_ai_assistant():
    """Assistant IA pour aide à la recherche"""
    user = get_current_user()
    if not user or not auth_manager.can_access_feature('advanced_ai'):
        return
    
    st.markdown("---")
    st.markdown("### 🤖 Assistant IA")
    
    with st.expander("💬 Demander des conseils à l'IA", expanded=False):
        st.markdown("L'IA peut vous aider à affiner votre recherche et vous donner des conseils personnalisés.")
        
        # Historique de conversation
        if 'ai_conversation' not in st.session_state:
            st.session_state.ai_conversation = []
        
        # Afficher la conversation
        for message in st.session_state.ai_conversation:
            if message['role'] == 'user':
                st.markdown(f"**Vous:** {message['content']}")
            else:
                st.markdown(f"**🤖 Assistant:** {message['content']}")
        
        # Nouvelle question
        user_question = st.text_input(
            "Posez votre question:",
            placeholder="Ex: Quels quartiers recommandez-vous à Antibes pour une famille ?",
            key="ai_question"
        )
        
        if st.button("💬 Envoyer", key="send_ai_question"):
            if user_question:
                # Ajouter la question à l'historique
                st.session_state.ai_conversation.append({
                    'role': 'user',
                    'content': user_question
                })
                
                # Générer la réponse IA (simulée pour cet exemple)
                ai_response = _generate_ai_response(user_question, st.session_state.get('current_search_filters', {}))
                
                # Ajouter la réponse à l'historique
                st.session_state.ai_conversation.append({
                    'role': 'assistant',
                    'content': ai_response
                })
                
                st.rerun()

def _generate_ai_response(question: str, search_context: Dict) -> str:
    """Génère une réponse IA (version simulée)"""
    # Dans une vraie implémentation, utiliser l'API OpenAI
    responses = {
        'quartier': "Pour une famille à Antibes, je recommande le quartier du Vieil Antibes pour son charme historique, ou Juan-les-Pins pour sa proximité avec les plages. Le quartier de la Fontonne offre un bon rapport qualité-prix.",
        'budget': "Avec votre budget, vous pourriez considérer élargir votre recherche aux communes limitrophes comme Vallauris ou Biot, qui offrent souvent un meilleur rapport qualité-prix.",
        'surface': "Pour une famille, je recommande au minimum 80m² pour un appartement ou 100m² pour une maison. N'oubliez pas de considérer la présence d'espaces extérieurs.",
        'default': "Je peux vous aider à affiner votre recherche. Pouvez-vous me dire quels sont vos critères les plus importants : localisation, budget, surface, ou proximité des commodités ?"
    }
    
    question_lower = question.lower()
    
    if any(word in question_lower for word in ['quartier', 'zone', 'secteur']):
        return responses['quartier']
    elif any(word in question_lower for word in ['budget', 'prix', 'coût']):
        return responses['budget']
    elif any(word in question_lower for word in ['surface', 'taille', 'grand']):
        return responses['surface']
    else:
        return responses['default']

# Fonctions utilitaires
def format_price(price):
    """Formate le prix avec séparateurs de milliers"""
    return f"{price:,}€".replace(',', ' ')

def get_property_type_emoji(property_type):
    """Retourne l'emoji correspondant au type de propriété"""
    emojis = {
        'Appartement': '🏢',
        'Maison': '🏠',
        'Studio': '🏠',
        'Villa': '🏡',
        'Loft': '🏢',
        'Duplex': '🏢',
        'Penthouse': '🏢'
    }
    return emojis.get(property_type, '🏠')
