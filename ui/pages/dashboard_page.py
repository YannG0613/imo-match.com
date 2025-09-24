"""
Tableau de bord utilisateur pour ImoMatch
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import logging

from config.settings import COLORS, PLANS
from database.manager import get_database
from auth.authentication import get_current_user
from ui.components import (
    create_metric_card, 
    create_radar_chart, 
    create_search_history_widget,
    create_favorites_widget
)
from utils.helpers import format_currency, calculate_property_score

logger = logging.getLogger(__name__)

def render():
    """Rend le tableau de bord utilisateur"""
    user = get_current_user()
    if not user:
        st.error("Vous devez être connecté pour accéder au tableau de bord")
        return
    
    st.markdown("# 📊 Tableau de Bord")
    
    # Vue d'ensemble
    _render_overview(user)
    
    st.markdown("---")
    
    # Layout en colonnes
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Graphiques et analyses
        _render_analytics(user)
        _render_recommendations(user)
    
    with col2:
        # Widgets latéraux
        _render_quick_actions(user)
        _render_recent_activity(user)

def _render_overview(user):
    """Vue d'ensemble avec métriques principales"""
    st.markdown("### 📈 Vue d'Ensemble")
    
    try:
        db = get_database()
        
        # Récupérer les données
        favorites = db.get_user_favorites(user['id'])
        saved_searches = db.get_saved_searches(user['id'])
        user_preferences = db.get_user_preferences(user['id'])
        
        # Métriques principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            create_metric_card(
                title="Favoris",
                value=str(len(favorites)),
                icon="❤️",
                color=COLORS['danger']
            )
        
        with col2:
            create_metric_card(
                title="Recherches Sauvées",
                value=str(len(saved_searches)),
                icon="💾",
                color=COLORS['primary']
            )
        
        with col3:
            # Calculer le budget moyen des favoris
            if favorites:
                avg_price = sum(fav['price'] for fav in favorites) / len(favorites)
                create_metric_card(
                    title="Prix Moyen Favoris",
                    value=f"{avg_price/1000:.0f}k€",
                    icon="💰",
                    color=COLORS['success']
                )
            else:
                create_metric_card(
                    title="Budget Cible",
                    value=f"{(user_preferences.get('budget_max', 500000))/1000:.0f}k€" if user_preferences else "Non défini",
                    icon="🎯",
                    color=COLORS['warning']
                )
        
        with col4:
            # Nombre de recherches restantes
            plan = user.get('plan', 'free')
            if plan == 'free':
                searches_used = user.get('searches_this_month', 0)
                max_searches = PLANS['free']['searches_per_month']
                remaining = max_searches - searches_used
                create_metric_card(
                    title="Recherches Restantes",
                    value=str(remaining),
                    icon="🔍",
                    color=COLORS['warning'] if remaining <= 2 else COLORS['primary']
                )
            else:
                create_metric_card(
                    title="Recherches",
                    value="Illimitées",
                    icon="∞",
                    color=COLORS['success']
                )
    
    except Exception as e:
        logger.error(f"Erreur vue d'ensemble: {e}")
        st.error("Impossible de charger la vue d'ensemble")

def _render_analytics(user):
    """Section analytics avec graphiques"""
    st.markdown("### 📊 Analyses")
    
    try:
        db = get_database()
        favorites = db.get_user_favorites(user['id'])
        user_preferences = db.get_user_preferences(user['id'])
        
        if not favorites:
            st.info("Ajoutez des propriétés en favoris pour voir des analyses détaillées")
            return
        
        # Onglets pour différentes analyses
        tab1, tab2, tab3 = st.tabs(["📈 Prix", "📍 Localisation", "🏠 Caractéristiques"])
        
        with tab1:
            _render_price_analysis(favorites, user_preferences)
        
        with tab2:
            _render_location_analysis(favorites)
        
        with tab3:
            _render_characteristics_analysis(favorites)
    
    except Exception as e:
        logger.error(f"Erreur analytics: {e}")
        st.error("Impossible de charger les analyses")

def _render_price_analysis(favorites, user_preferences):
    """Analyse des prix des favoris"""
    prices = [fav['price'] for fav in favorites]
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Histogramme des prix
        fig_hist = px.histogram(
            x=prices,
            nbins=10,
            title="Répartition des Prix de vos Favoris",
            labels={'x': 'Prix (€)', 'y': 'Nombre de propriétés'}
        )
        fig_hist.update_traces(marker_color=COLORS['primary'])
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        # Statistiques des prix
        st.markdown("#### 📊 Statistiques des Prix")
        
        min_price = min(prices)
        max_price = max(prices)
        avg_price = sum(prices) / len(prices)
        median_price = sorted(prices)[len(prices) // 2]
        
        st.metric("Prix Minimum", format_currency(min_price))
        st.metric("Prix Maximum", format_currency(max_price))
        st.metric("Prix Moyen", format_currency(avg_price))
        st.metric("Prix Médian", format_currency(median_price))
        
        # Comparaison avec les préférences
        if user_preferences and user_preferences.get('budget_max'):
            budget_max = user_preferences['budget_max']
            over_budget = sum(1 for p in prices if p > budget_max)
            if over_budget > 0:
                st.warning(f"⚠️ {over_budget} favoris dépassent votre budget max")

def _render_location_analysis(favorites):
    """Analyse des localisations"""
    locations = [fav['location'] for fav in favorites]
    location_counts = {}
    
    for location in locations:
        # Simplifier la localisation (prendre la ville principale)
        city = location.split(',')[0].strip()
        location_counts[city] = location_counts.get(city, 0) + 1
    
    if len(location_counts) > 1:
        # Graphique en secteurs des localisations
        fig_pie = px.pie(
            values=list(location_counts.values()),
            names=list(location_counts.keys()),
            title="Répartition de vos Favoris par Ville"
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("Vos favoris sont tous dans la même ville")
    
    # Top des villes
    st.markdown("#### 🏆 Vos Villes Préférées")
    sorted_cities = sorted(location_counts.items(), key=lambda x: x[1], reverse=True)
    
    for i, (city, count) in enumerate(sorted_cities[:5]):
        emoji = ["🥇", "🥈", "🥉", "🏅", "🏅"][min(i, 4)]
        st.write(f"{emoji} **{city}**: {count} propriété{'s' if count > 1 else ''}")

def _render_characteristics_analysis(favorites):
    """Analyse des caractéristiques"""
    
    # Préparer les données
    surfaces = [fav.get('surface', 0) for fav in favorites if fav.get('surface')]
    bedrooms = [fav.get('bedrooms', 0) for fav in favorites if fav.get('bedrooms')]
    types = [fav['property_type'] for fav in favorites]
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Répartition par type
        if types:
            type_counts = {}
            for prop_type in types:
                type_counts[prop_type] = type_counts.get(prop_type, 0) + 1
            
            fig_bar = px.bar(
                x=list(type_counts.keys()),
                y=list(type_counts.values()),
                title="Types de Propriétés Préférées",
                labels={'x': 'Type', 'y': 'Nombre'}
            )
            fig_bar.update_traces(marker_color=COLORS['secondary'])
            st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        # Distribution des surfaces
        if surfaces:
            fig_surface = px.box(
                y=surfaces,
                title="Distribution des Surfaces",
                labels={'y': 'Surface (m²)'}
            )
            fig_surface.update_traces(marker_color=COLORS['accent'])
            st.plotly_chart(fig_surface, use_container_width=True)
        
        # Statistiques des chambres
        if bedrooms:
            st.markdown("#### 🛏️ Chambres")
            bedroom_counts = {}
            for bed in bedrooms:
                bedroom_counts[bed] = bedroom_counts.get(bed, 0) + 1
            
            for bed_count, properties in sorted(bedroom_counts.items()):
                st.write(f"**{bed_count} chambres**: {properties} propriété{'s' if properties > 1 else ''}")

def _render_recommendations(user):
    """Section recommandations personnalisées"""
    st.markdown("### 🎯 Recommandations Personnalisées")
    
    try:
        db = get_database()
        user_preferences = db.get_user_preferences(user['id'])
        favorites = db.get_user_favorites(user['id'])
        
        if not user_preferences and not favorites:
            st.info("Définissez vos préférences ou ajoutez des favoris pour recevoir des recommandations")
            return
        
        # Rechercher des propriétés similaires
        search_filters = {}
        
        if user_preferences:
            search_filters.update({
                'price_min': user_preferences.get('budget_min'),
                'price_max': user_preferences.get('budget_max'),
                'property_type': user_preferences.get('property_type'),
                'bedrooms': user_preferences.get('bedrooms'),
                'surface_min': user_preferences.get('surface_min'),
                'location': user_preferences.get('location')
            })
        
        # Rechercher des propriétés recommandées
        recommended_properties = db.search_properties({
            **search_filters,
            'limit': 6
        })
        
        # Filtrer celles qui ne sont pas déjà en favoris
        favorite_ids = {fav['id'] for fav in favorites}
        recommended_properties = [
            prop for prop in recommended_properties 
            if prop['id'] not in favorite_ids
        ]
        
        if recommended_properties:
            st.markdown("#### 🌟 Propriétés Recommandées pour Vous")
            
            # Calculer les scores de compatibilité
            if user_preferences:
                for prop in recommended_properties:
                    prop['compatibility_score'] = calculate_property_score(prop, user_preferences)
                
                # Trier par score
                recommended_properties.sort(key=lambda x: x.get('compatibility_score', 0), reverse=True)
            
            # Afficher les 3 meilleures recommandations
            cols = st.columns(3)
            
            for i, prop in enumerate(recommended_properties[:3]):
                with cols[i]:
                    # Score de compatibilité
                    score = prop.get('compatibility_score', 0)
                    score_color = COLORS['success'] if score > 0.8 else COLORS['warning'] if score > 0.6 else COLORS['danger']
                    
                    st.markdown(f"""
                    <div style="
                        border: 2px solid {score_color};
                        border-radius: 10px;
                        padding: 1rem;
                        margin-bottom: 1rem;
                    ">
                        <h4 style="margin: 0 0 0.5rem 0;">{prop['title'][:30]}...</h4>
                        <p style="font-size: 1.1rem; font-weight: bold; color: {score_color}; margin: 0.5rem 0;">
                            {format_currency(prop['price'])}
                        </p>
                        <p style="margin: 0.2rem 0;">📍 {prop['location']}</p>
                        <p style="margin: 0.2rem 0;">📐 {prop.get('surface', 'N/A')}m²</p>
                        <div style="background: {score_color}; color: white; padding: 0.3rem; border-radius: 5px; text-align: center; margin-top: 0.5rem;">
                            Compatibilité: {score*100:.0f}%
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col_btn1, col_btn2 = st.columns(2)
                    
                    with col_btn1:
                        if st.button("👁️ Voir", key=f"see_{prop['id']}", use_container_width=True):
                            # Logique pour voir les détails
                            st.info("Détails de la propriété")
                    
                    with col_btn2:
                        if st.button("❤️ Favori", key=f"fav_{prop['id']}", use_container_width=True):
                            if db.add_to_favorites(user['id'], prop['id']):
                                st.success("Ajouté aux favoris !")
                                st.rerun()
        else:
            st.info("Aucune nouvelle recommandation pour le moment. Affinez vos préférences !")
        
        # Conseils d'amélioration du profil
        _render_profile_improvement_tips(user_preferences, favorites)
    
    except Exception as e:
        logger.error(f"Erreur recommandations: {e}")
        st.error("Impossible de charger les recommandations")

def _render_profile_improvement_tips(user_preferences, favorites):
    """Conseils pour améliorer le profil utilisateur"""
    st.markdown("#### 💡 Conseils pour Améliorer vos Recommandations")
    
    tips = []
    
    if not user_preferences:
        tips.append("🎯 Définissez vos préférences de recherche dans votre profil")
    
    if len(favorites) < 3:
        tips.append("❤️ Ajoutez plus de propriétés en favoris pour affiner nos recommandations")
    
    if user_preferences:
        if not user_preferences.get('location'):
            tips.append("📍 Précisez une localisation préférée")
        
        if not user_preferences.get('property_type'):
            tips.append("🏠 Choisissez un type de bien préféré")
    
    if tips:
        for tip in tips:
            st.write(f"• {tip}")
    else:
        st.success("✅ Votre profil est bien configuré pour recevoir des recommandations pertinentes !")

def _render_quick_actions(user):
    """Actions rapides dans la sidebar"""
    st.markdown("### ⚡ Actions Rapides")
    
    # Nouvelle recherche
    if st.button("🔍 Nouvelle Recherche", use_container_width=True, type="primary"):
        st.switch_page("search_page")
    
    # Modifier préférences
    if st.button("⚙️ Mes Préférences", use_container_width=True):
        st.switch_page("profile_page")
    
    # Upgrade plan (si gratuit)
    if user.get('plan') == 'free':
        st.markdown("---")
        st.markdown("### 🚀 Passez au Premium")
        
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #FF6B35, #F7931E);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            text-align: center;
            margin: 1rem 0;
        ">
            <h4 style="margin: 0 0 0.5rem 0;">✨ Premium</h4>
            <p style="margin: 0 0 0.5rem 0;">29€/mois</p>
            <small>Recherches illimitées<br>IA avancée<br>Support prioritaire</small>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("⬆️ Passer au Premium", use_container_width=True):
            st.switch_page("profile_page")

def _render_recent_activity(user):
    """Activité récente"""
    st.markdown("### 📋 Activité Récente")
    
    try:
        db = get_database()
        
        # Favoris récents (3 derniers)
        favorites = db.get_user_favorites(user['id'])
        recent_favorites = favorites[:3] if favorites else []
        
        if recent_favorites:
            st.markdown("#### ❤️ Favoris Récents")
            for fav in recent_favorites:
                st.markdown(f"""
                <div style="
                    border-left: 3px solid {COLORS['danger']};
                    padding: 0.5rem;
                    margin: 0.5rem 0;
                    background: #f8f9fa;
                ">
                    <strong>{fav['title'][:40]}...</strong><br>
                    <small>💰 {format_currency(fav['price'])} • 📍 {fav['location']}</small>
                </div>
                """, unsafe_allow_html=True)
        
        # Recherches sauvegardées récentes
        saved_searches = db.get_saved_searches(user['id'])
        recent_searches = saved_searches[:2] if saved_searches else []
        
        if recent_searches:
            st.markdown("#### 💾 Recherches Récentes")
            for search in recent_searches:
                alert_icon = "🔔" if search.get('alert_enabled') else "🔕"
                st.markdown(f"{alert_icon} **{search['name']}**")
        
        if not recent_favorites and not recent_searches:
            st.info("Aucune activité récente")
    
    except Exception as e:
        logger.error(f"Erreur activité récente: {e}")
        st.error("Impossible de charger l'activité récente")

def _render_market_insights():
    """Insights sur le marché (fonctionnalité premium)"""
    user = get_current_user()
    
    if user.get('plan') not in ['premium', 'professional']:
        st.markdown("### 📈 Insights Marché (Premium)")
        st.info("Passez au plan Premium pour accéder aux analyses de marché détaillées")
        return
    
    st.markdown("### 📈 Insights Marché")
    
    # Données simulées pour les insights marché
    market_data = {
        'evolution_prix': [
            {'mois': 'Jan 2024', 'prix_moyen': 4500},
            {'mois': 'Fév 2024', 'prix_moyen': 4600},
            {'mois': 'Mar 2024', 'prix_moyen': 4550},
            {'mois': 'Avr 2024', 'prix_moyen': 4700},
        ],
        'tendances': {
            'hausse': ['Antibes Centre', 'Cannes Croisette'],
            'stable': ['Juan-les-Pins', 'Nice Est'],
            'baisse': ['Grasse Centre']
        }
    }
    
    # Graphique d'évolution des prix
    df_prices = pd.DataFrame(market_data['evolution_prix'])
    fig_market = px.line(
        df_prices, 
        x='mois', 
        y='prix_moyen',
        title='Évolution Prix/m² - Côte d\'Azur',
        labels={'prix_moyen': 'Prix moyen (€/m²)', 'mois': 'Mois'}
    )
    fig_market.update_traces(line_color=COLORS['primary'])
    st.plotly_chart(fig_market, use_container_width=True)
    
    # Tendances par zone
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 📈 En Hausse")
        for zone in market_data['tendances']['hausse']:
            st.write(f"🔴 {zone}")
    
    with col2:
        st.markdown("#### ➡️ Stable")
        for zone in market_data['tendances']['stable']:
            st.write(f"🟡 {zone}")
    
    with col3:
        st.markdown("#### 📉 En Baisse")
        for zone in market_data['tendances']['baisse']:
            st.write(f"🟢 {zone}")

# Ajout de la fonctionnalité insights marché dans le dashboard principal
def render_with_insights():
    """Version étendue du dashboard avec insights marché"""
    render()
    
    st.markdown("---")
    _render_market_insights()