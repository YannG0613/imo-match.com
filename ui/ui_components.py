"""
Composants UI réutilisables pour ImoMatch
"""
import streamlit as st
import folium
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

from config.settings import COLORS
from database.manager import get_database
from auth.authentication import get_current_user

logger = logging.getLogger(__name__)

def create_property_card(property_data: Dict[str, Any], 
                        show_details_button: bool = True,
                        show_favorite_button: bool = False,
                        compact: bool = False) -> None:
    """
    Crée une carte de propriété réutilisable
    
    Args:
        property_data: Données de la propriété
        show_details_button: Afficher le bouton de détails
        show_favorite_button: Afficher le bouton favoris
        compact: Version compacte de la carte
    """
    # Images de la propriété (utiliser une image par défaut si aucune)
    images = property_data.get('images', [])
    if images and isinstance(images, list) and len(images) > 0:
        image_url = images[0]
    else:
        image_url = "https://via.placeholder.com/300x200/FF6B35/FFFFFF?text=Propriété"
    
    # Style de la carte
    card_style = """
    <div style="
        border: 1px solid #e0e0e0;
        border-radius: 15px;
        padding: 1rem;
        margin-bottom: 1rem;
        background: white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: box-shadow 0.3s ease;
    ">
    """
    
    # Version compacte ou complète
    if compact:
        _render_compact_property_card(property_data, image_url, card_style, 
                                    show_details_button, show_favorite_button)
    else:
        _render_full_property_card(property_data, image_url, card_style,
                                 show_details_button, show_favorite_button)

def _render_compact_property_card(property_data: Dict, image_url: str, 
                                card_style: str, show_details: bool, 
                                show_favorite: bool) -> None:
    """Rend une carte de propriété compacte"""
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image(image_url, width=150)
    
    with col2:
        st.markdown(f"**{property_data['title']}**")
        st.markdown(f"💰 **{property_data['price']:,}€**")
        st.markdown(f"📍 {property_data['location']}")
        
        if property_data.get('surface'):
            st.markdown(f"📐 {property_data['surface']}m²")
        
        _render_property_buttons(property_data, show_details, show_favorite, compact=True)

def _render_full_property_card(property_data: Dict, image_url: str,
                             card_style: str, show_details: bool,
                             show_favorite: bool) -> None:
    """Rend une carte de propriété complète"""
    
    # Image principale
    st.image(image_url, use_column_width=True)
    
    # Titre et prix
    st.markdown(f"### {property_data['title']}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"💰 **{property_data['price']:,}€**")
    with col2:
        price_per_m2 = property_data['price'] / property_data.get('surface', 1) if property_data.get('surface') else 0
        if price_per_m2 > 0:
            st.markdown(f"📊 **{price_per_m2:,.0f}€/m²**")
    
    # Caractéristiques
    characteristics = []
    if property_data.get('bedrooms'):
        characteristics.append(f"🛏️ {property_data['bedrooms']} ch.")
    if property_data.get('bathrooms'):
        characteristics.append(f"🚿 {property_data['bathrooms']} sdb")
    if property_data.get('surface'):
        characteristics.append(f"📐 {property_data['surface']}m²")
    
    if characteristics:
        st.markdown(" • ".join(characteristics))
    
    # Type et localisation
    st.markdown(f"🏠 {property_data['property_type']} • 📍 {property_data['location']}")
    
    # Description (tronquée)
    if property_data.get('description'):
        description = property_data['description']
        if len(description) > 100:
            description = description[:100] + "..."
        st.markdown(f"*{description}*")
    
    # Équipements (si disponibles)
    if property_data.get('features'):
        features = property_data['features'][:3]  # Afficher max 3 équipements
        if features:
            feature_text = " • ".join(features)
            st.markdown(f"✨ {feature_text}")
    
    # Boutons d'action
    _render_property_buttons(property_data, show_details, show_favorite)

def _render_property_buttons(property_data: Dict, show_details: bool, 
                           show_favorite: bool, compact: bool = False) -> None:
    """Rend les boutons d'action pour une propriété"""
    
    if compact:
        cols = st.columns(2)
    else:
        cols = st.columns(3)
    
    # Bouton de détails
    if show_details:
        with cols[0]:
            if st.button("👁️ Voir", key=f"details_{property_data['id']}", use_container_width=True):
                _show_property_details(property_data)
    
    # Bouton favoris
    if show_favorite and get_current_user():
        with cols[1]:
            db = get_database()
            user_id = get_current_user()['id']
            is_favorite = db.is_favorite(user_id, property_data['id'])
            
            if is_favorite:
                if st.button("❤️ Retiré", key=f"unfav_{property_data['id']}", use_container_width=True):
                    if db.remove_from_favorites(user_id, property_data['id']):
                        st.success("Retiré des favoris")
                        st.rerun()
            else:
                if st.button("🤍 Ajouter", key=f"fav_{property_data['id']}", use_container_width=True):
                    if db.add_to_favorites(user_id, property_data['id']):
                        st.success("Ajouté aux favoris !")
                        st.rerun()
    
    # Bouton de contact (si pas en mode compact)
    if not compact and len(cols) > 2:
        with cols[2]:
            if st.button("📞 Contact", key=f"contact_{property_data['id']}", use_container_width=True):
                _show_contact_info(property_data)

def _show_property_details(property_data: Dict) -> None:
    """Affiche les détails complets d'une propriété dans une modale"""
    with st.expander(f"🏠 {property_data['title']}", expanded=True):
        
        # Images (carousel simulé)
        images = property_data.get('images', [])
        if images:
            selected_image = st.selectbox(
                "Images",
                options=list(range(len(images))),
                format_func=lambda x: f"Image {x+1}",
                key=f"img_select_{property_data['id']}"
            )
            st.image(images[selected_image], use_column_width=True)
        
        # Informations principales
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 💰 Prix et Surface")
            st.write(f"**Prix:** {property_data['price']:,}€")
            if property_data.get('surface'):
                st.write(f"**Surface:** {property_data['surface']}m²")
                price_per_m2 = property_data['price'] / property_data['surface']
                st.write(f"**Prix/m²:** {price_per_m2:,.0f}€")
            
            st.markdown("#### 🏠 Caractéristiques")
            st.write(f"**Type:** {property_data['property_type']}")
            if property_data.get('bedrooms'):
                st.write(f"**Chambres:** {property_data['bedrooms']}")
            if property_data.get('bathrooms'):
                st.write(f"**Salles de bain:** {property_data['bathrooms']}")
        
        with col2:
            st.markdown("#### 📍 Localisation")
            st.write(f"**Adresse:** {property_data['location']}")
            
            # Carte si coordonnées disponibles
            if property_data.get('latitude') and property_data.get('longitude'):
                create_single_property_map(property_data)
            
            st.markdown("#### 📞 Contact")
            agent_contact = property_data.get('agent_contact', 'Non disponible')
            st.write(f"**Agent:** {agent_contact}")
        
        # Description complète
        if property_data.get('description'):
            st.markdown("#### 📝 Description")
            st.write(property_data['description'])
        
        # Équipements complets
        if property_data.get('features'):
            st.markdown("#### ✨ Équipements")
            features = property_data['features']
            cols = st.columns(3)
            for i, feature in enumerate(features):
                with cols[i % 3]:
                    st.write(f"• {feature}")

def _show_contact_info(property_data: Dict) -> None:
    """Affiche les informations de contact"""
    st.info(f"Contact pour {property_data['title']}: {property_data.get('agent_contact', 'Non disponible')}")

def create_metric_card(title: str, value: str, icon: str = "📊",
                      color: str = COLORS['primary'], delta: str = None) -> None:
    """
    Crée une carte de métrique
    
    Args:
        title: Titre de la métrique
        value: Valeur à afficher
        icon: Icône à afficher
        color: Couleur de la carte
        delta: Variation (optionnel)
    """
    
    delta_html = f"<p style='color: #666; font-size: 0.8rem; margin: 0.2rem 0 0 0;'>{delta}</p>" if delta else ""
    
    st.markdown(f"""
    <div style="
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid {color};
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        text-align: center;
    ">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
        <h3 style="color: {color}; margin: 0.5rem 0; font-size: 1.8rem;">{value}</h3>
        <p style="color: #666; font-size: 0.9rem; margin: 0; text-transform: uppercase; font-weight: 500;">{title}</p>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

def create_single_property_map(property_data: Dict) -> None:
    """Crée une carte pour une seule propriété"""
    if not (property_data.get('latitude') and property_data.get('longitude')):
        st.warning("Coordonnées non disponibles")
        return
    
    # Carte centrée sur la propriété
    m = folium.Map(
        location=[property_data['latitude'], property_data['longitude']],
        zoom_start=15
    )
    
    # Marker de la propriété
    folium.Marker(
        location=[property_data['latitude'], property_data['longitude']],
        popup=f"{property_data['title']}<br>{property_data['price']:,}€",
        tooltip=property_data['title'],
        icon=folium.Icon(color='red', icon='home')
    ).add_to(m)
    
    # Afficher la carte
    from streamlit_folium import st_folium
    st_folium(m, width=400, height=300)

def create_radar_chart(criteria: Dict[str, float], title: str = "Score de Compatibilité") -> None:
    """
    Crée un graphique radar pour les critères utilisateur
    
    Args:
        criteria: Dictionnaire des critères avec leurs scores (0-1)
        title: Titre du graphique
    """
    
    # Préparer les données
    categories = list(criteria.keys())
    values = list(criteria.values())
    
    # Créer le graphique radar
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Score',
        fillcolor=f"rgba({COLORS['primary'][1:]}, 0.2)",
        line=dict(color=COLORS['primary'])
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                tickvals=[0.2, 0.4, 0.6, 0.8, 1.0],
                ticktext=['20%', '40%', '60%', '80%', '100%']
            )
        ),
        showlegend=False,
        title=title,
        font=dict(size=12)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_price_evolution_chart(price_data: List[Dict]) -> None:
    """
    Crée un graphique d'évolution des prix
    
    Args:
        price_data: Liste des données de prix avec dates
    """
    if not price_data:
        st.warning("Aucune donnée disponible")
        return
    
    dates = [item['date'] for item in price_data]
    prices = [item['price'] for item in price_data]
    
    fig = px.line(
        x=dates,
        y=prices,
        title="Évolution des Prix",
        labels={'x': 'Date', 'y': 'Prix (€)'}
    )
    
    fig.update_traces(line_color=COLORS['primary'])
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Prix (€)",
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_comparison_table(properties: List[Dict]) -> None:
    """
    Crée un tableau de comparaison des propriétés
    
    Args:
        properties: Liste des propriétés à comparer
    """
    if not properties or len(properties) < 2:
        st.warning("Sélectionnez au moins 2 propriétés pour les comparer")
        return
    
    # Préparer les données
    comparison_data = []
    for prop in properties:
        comparison_data.append({
            'Titre': prop['title'],
            'Prix': f"{prop['price']:,}€",
            'Type': prop['property_type'],
            'Surface': f"{prop.get('surface', 'N/A')}m²",
            'Chambres': prop.get('bedrooms', 'N/A'),
            'SdB': prop.get('bathrooms', 'N/A'),
            'Localisation': prop['location']
        })
    
    # Créer le DataFrame et l'afficher
    import pandas as pd
    df = pd.DataFrame(comparison_data)
    st.dataframe(df, use_container_width=True)

def create_search_history_widget():
    """Widget pour afficher l'historique des recherches sauvegardées"""
    user = get_current_user()
    if not user:
        return
    
    try:
        db = get_database()
        saved_searches = db.get_saved_searches(user['id'])
        
        if not saved_searches:
            st.info("Aucune recherche sauvegardée")
            return
        
        st.markdown("#### 💾 Mes Recherches Sauvegardées")
        
        for search in saved_searches:
            with st.expander(f"🔍 {search['name']}", expanded=False):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    filters = search['filters']
                    st.write(f"**Budget:** {filters.get('price_min', 0):,}€ - {filters.get('price_max', 0):,}€")
                    if filters.get('property_type'):
                        st.write(f"**Type:** {filters['property_type']}")
                    if filters.get('location'):
                        st.write(f"**Localisation:** {filters['location']}")
                    
                    alert_status = "🔔 Activées" if search.get('alert_enabled') else "🔕 Désactivées"
                    st.write(f"**Alertes:** {alert_status}")
                
                with col2:
                    if st.button("🔍 Relancer", key=f"rerun_{search['id']}"):
                        st.session_state['current_search_filters'] = filters
                        # Relancer la recherche
                        db = get_database()
                        properties = db.search_properties(filters)
                        st.session_state['current_properties'] = properties
                        st.success(f"{len(properties)} propriétés trouvées")
                    
                    if st.button("🗑️ Supprimer", key=f"delete_{search['id']}"):
                        if db.delete_saved_search(user['id'], search['id']):
                            st.success("Recherche supprimée")
                            st.rerun()
        
    except Exception as e:
        logger.error(f"Erreur widget recherches sauvegardées: {e}")
        st.error("Erreur lors du chargement des recherches sauvegardées")

def create_favorites_widget():
    """Widget pour afficher les propriétés favorites"""
    user = get_current_user()
    if not user:
        return
    
    try:
        db = get_database()
        favorites = db.get_user_favorites(user['id'])
        
        if not favorites:
            st.info("Aucune propriété en favoris")
            return
        
        st.markdown(f"#### ❤️ Mes Favoris ({len(favorites)})")
        
        # Affichage en mode compact
        for favorite in favorites:
            create_property_card(favorite, show_details_button=True, 
                               show_favorite_button=True, compact=True)
            
    except Exception as e:
        logger.error(f"Erreur widget favoris: {e}")
        st.error("Erreur lors du chargement des favoris")

def create_notification_badge(count: int, color: str = COLORS['danger']) -> str:
    """
    Crée un badge de notification
    
    Args:
        count: Nombre à afficher
        color: Couleur du badge
        
    Returns:
        HTML du badge
    """
    if count <= 0:
        return ""
    
    display_count = str(count) if count < 100 else "99+"
    
    return f"""
    <span style="
        background-color: {color};
        color: white;
        border-radius: 50%;
        padding: 0.2rem 0.4rem;
        font-size: 0.7rem;
        font-weight: bold;
        margin-left: 0.5rem;
        display: inline-block;
        min-width: 1.2rem;
        text-align: center;
    ">{display_count}</span>
    """

def create_loading_spinner(text: str = "Chargement...") -> None:
    """Affiche un spinner de chargement avec texte"""
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem;">
        <div style="
            border: 4px solid #f3f3f3;
            border-top: 4px solid {COLORS['primary']};
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 1rem auto;
        "></div>
        <p style="color: #666;">{text}</p>
    </div>
    
    <style>
    @keyframes spin {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}
    </style>
    """, unsafe_allow_html=True)

def create_success_message(title: str, message: str, icon: str = "✅") -> None:
    """Crée un message de succès stylisé"""
    st.markdown(f"""
    <div style="
        background: linear-gradient(90deg, {COLORS['success']}15, {COLORS['success']}05);
        border-left: 4px solid {COLORS['success']};
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    ">
        <h4 style="color: {COLORS['success']}; margin: 0 0 0.5rem 0;">{icon} {title}</h4>
        <p style="margin: 0; color: #333;">{message}</p>
    </div>
    """, unsafe_allow_html=True)

def create_warning_message(title: str, message: str, icon: str = "⚠️") -> None:
    """Crée un message d'avertissement stylisé"""
    st.markdown(f"""
    <div style="
        background: linear-gradient(90deg, {COLORS['warning']}15, {COLORS['warning']}05);
        border-left: 4px solid {COLORS['warning']};
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    ">
        <h4 style="color: {COLORS['warning']}; margin: 0 0 0.5rem 0;">{icon} {title}</h4>
        <p style="margin: 0; color: #333;">{message}</p>
    </div>
    """, unsafe_allow_html=True)

def create_error_message(title: str, message: str, icon: str = "❌") -> None:
    """Crée un message d'erreur stylisé"""
    st.markdown(f"""
    <div style="
        background: linear-gradient(90deg, {COLORS['danger']}15, {COLORS['danger']}05);
        border-left: 4px solid {COLORS['danger']};
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    ">
        <h4 style="color: {COLORS['danger']}; margin: 0 0 0.5rem 0;">{icon} {title}</h4>
        <p style="margin: 0; color: #333;">{message}</p>
    </div>
    """, unsafe_allow_html=True)

def create_feature_comparison_widget(plan_features: Dict[str, List[str]]) -> None:
    """
    Widget de comparaison des fonctionnalités par plan
    
    Args:
        plan_features: Dictionnaire des fonctionnalités par plan
    """
    st.markdown("#### 🔍 Comparaison des Plans")
    
    # Créer un tableau de comparaison
    all_features = set()
    for features in plan_features.values():
        all_features.update(features)
    
    comparison_data = []
    for feature in sorted(all_features):
        row = {'Fonctionnalité': feature}
        for plan, features in plan_features.items():
            row[plan.title()] = "✅" if feature in features else "❌"
        comparison_data.append(row)
    
    import pandas as pd
    df = pd.DataFrame(comparison_data)
    
    # Styliser le dataframe
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

def create_stats_dashboard(stats: Dict[str, Any]) -> None:
    """
    Crée un tableau de bord de statistiques
    
    Args:
        stats: Dictionnaire des statistiques à afficher
    """
    st.markdown("### 📊 Statistiques")
    
    # Métriques principales
    cols = st.columns(4)
    
    metrics = [
        ("Utilisateurs", stats.get('total_users', 0), "👥"),
        ("Propriétés", stats.get('total_properties', 0), "🏠"),
        ("Recherches", stats.get('total_searches', 0), "🔍"),
        ("Favoris", stats.get('total_favorites', 0), "❤️")
    ]
    
    for i, (title, value, icon) in enumerate(metrics):
        with cols[i]:
            create_metric_card(title, f"{value:,}", icon)
    
    # Graphiques additionnels
    if stats.get('property_types_data'):
        col1, col2 = st.columns(2)
        
        with col1:
            # Graphique des types de propriétés
            types_data = stats['property_types_data']
            fig = px.pie(
                values=[item['count'] for item in types_data],
                names=[item['type'] for item in types_data],
                title="Répartition des Types de Biens"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Evolution des prix si données disponibles
            if stats.get('price_evolution'):
                create_price_evolution_chart(stats['price_evolution'])

def create_property_filter_widget(current_filters: Dict = None) -> Dict:
    """
    Widget réutilisable de filtres de propriétés
    
    Args:
        current_filters: Filtres actuels à pré-remplir
        
    Returns:
        Dictionnaire des filtres sélectionnés
    """
    current_filters = current_filters or {}
    
    st.markdown("#### 🎯 Filtres")
    
    # Budget
    budget_range = st.slider(
        "Budget (€)",
        min_value=50000,
        max_value=2000000,
        value=(
            current_filters.get('price_min', 100000),
            current_filters.get('price_max', 500000)
        ),
        step=25000,
        format="%d€"
    )
    
    # Type de propriété
    property_type = st.selectbox(
        "Type de bien",
        options=["Tous"] + PROPERTY_TYPES,
        index=0 if not current_filters.get('property_type') else 
              PROPERTY_TYPES.index(current_filters['property_type']) + 1
    )
    
    # Nombre de pièces
    col1, col2 = st.columns(2)
    
    with col1:
        bedrooms = st.number_input(
            "Chambres min",
            min_value=0,
            max_value=10,
            value=current_filters.get('bedrooms', 1)
        )
    
    with col2:
        bathrooms = st.number_input(
            "SdB min",
            min_value=0,
            max_value=5,
            value=current_filters.get('bathrooms', 1)
        )
    
    # Surface
    surface_min = st.number_input(
        "Surface minimale (m²)",
        min_value=10,
        max_value=1000,
        value=current_filters.get('surface_min', 50),
        step=10
    )
    
    # Localisation
    location = st.text_input(
        "Localisation",
        value=current_filters.get('location', ''),
        placeholder="Ville, quartier..."
    )
    
    return {
        'price_min': budget_range[0],
        'price_max': budget_range[1],
        'property_type': property_type if property_type != "Tous" else None,
        'bedrooms': bedrooms,
        'bathrooms': bathrooms,
        'surface_min': surface_min,
        'location': location if location else None
    }

def create_map_marker(property_data: Dict, map_obj) -> None:
    """
    Ajoute un marker sur la carte pour une propriété
    
    Args:
        property_data: Données de la propriété
        map_obj: Objet carte Folium
    """
    if not (property_data.get('latitude') and property_data.get('longitude')):
        return
    
    # Couleur selon le type de propriété
    from config.settings import MAP_CONFIG
    color = MAP_CONFIG['marker_colors'].get(
        property_data['property_type'].lower(), 
        'blue'
    )
    
    # Popup avec informations
    popup_html = f"""
    <div style="width: 200px; font-family: Arial, sans-serif;">
        <h4 style="margin: 0 0 10px 0; color: {COLORS['primary']};">{property_data['title']}</h4>
        <p style="margin: 5px 0; font-weight: bold; font-size: 16px;">💰 {property_data['price']:,}€</p>
        <p style="margin: 5px 0;">🏠 {property_data['property_type']}</p>
        <p style="margin: 5px 0;">📐 {property_data.get('surface', 'N/A')}m²</p>
        <p style="margin: 5px 0; color: #666;">📍 {property_data['location']}</p>
    </div>
    """
    
    folium.Marker(
        location=[property_data['latitude'], property_data['longitude']],
        popup=folium.Popup(popup_html, max_width=250),
        tooltip=f"{property_data['title']} - {property_data['price']:,}€",
        icon=folium.Icon(color=color, icon='home', prefix='fa')
    ).add_to(map_obj)

# Fonction utilitaire pour formater les devises
def format_currency(amount: float, currency: str = "€") -> str:
    """Formate un montant en devise"""
    return f"{amount:,.0f}{currency}".replace(",", " ")

# Fonction utilitaire pour formater les surfaces  
def format_surface(surface: float) -> str:
    """Formate une surface"""
    return f"{surface:,.0f}m²".replace(",", " ")

# Fonction utilitaire pour obtenir l'emoji d'un type de propriété
def get_property_emoji(property_type: str) -> str:
    """Retourne l'emoji correspondant au type de propriété"""
    emoji_map = {
        'appartement': '🏢',
        'maison': '🏠',
        'studio': '🏠',
        'villa': '🏡',
        'loft': '🏢',
        'duplex': '🏢',
        'triplex': '🏢',
        'penthouse': '🏙️',
        'terrain': '🌳',
        'local commercial': '🏪',
        'bureau': '🏢'
    }
    return emoji_map.get(property_type.lower(), '🏠')