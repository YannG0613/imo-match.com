"""
Page de profil utilisateur pour ImoMatch
"""
import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import logging

from config.settings import PLANS, COLORS, PROPERTY_TYPES, VALIDATION_RULES
from database.manager import get_database
from auth.authentication import auth_manager, get_current_user
from ui.components import create_metric_card, create_radar_chart, create_favorites_widget
from utils.helpers import format_currency, format_date

logger = logging.getLogger(__name__)

def render():
    """Rend la page de profil utilisateur"""
    user = get_current_user()
    if not user:
        st.error("Vous devez être connecté pour accéder à cette page")
        return
    
    st.markdown("# 👤 Mon Profil")
    
    # Tabs pour organiser le contenu
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📝 Informations", 
        "🎯 Préférences", 
        "💳 Abonnement", 
        "❤️ Favoris",
        "⚙️ Paramètres"
    ])
    
    with tab1:
        _render_user_info(user)
    
    with tab2:
        _render_preferences(user)
    
    with tab3:
        _render_subscription(user)
    
    with tab4:
        _render_favorites(user)
    
    with tab5:
        _render_settings(user)

def _render_user_info(user):
    """Section informations personnelles"""
    st.markdown("## 📋 Informations Personnelles")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Formulaire de mise à jour
        with st.form("update_profile"):
            st.markdown("### ✏️ Modifier mes informations")
            
            first_name = st.text_input(
                "Prénom",
                value=user.get('first_name', ''),
                placeholder="Votre prénom"
            )
            
            last_name = st.text_input(
                "Nom",
                value=user.get('last_name', ''),
                placeholder="Votre nom"
            )
            
            email = st.text_input(
                "Email",
                value=user.get('email', ''),
                placeholder="votre.email@example.com",
                help="L'email sert pour la connexion"
            )
            
            phone = st.text_input(
                "Téléphone",
                value=user.get('phone', '') if user.get('phone') else '',
                placeholder="+33 6 12 34 56 78"
            )
            
            col_age, col_prof = st.columns(2)
            
            with col_age:
                age = st.number_input(
                    "Âge",
                    min_value=VALIDATION_RULES['age']['min'],
                    max_value=VALIDATION_RULES['age']['max'],
                    value=user.get('age', 25) if user.get('age') else 25,
                    step=1
                )
            
            with col_prof:
                profession = st.text_input(
                    "Profession",
                    value=user.get('profession', '') if user.get('profession') else '',
                    placeholder="Votre profession"
                )
            
            if st.form_submit_button("💾 Sauvegarder", type="primary", use_container_width=True):
                updates = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'phone': phone if phone else None,
                    'age': age,
                    'profession': profession if profession else None
                }
                
                success, message = auth_manager.update_profile(updates)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
    
    with col2:
        # Informations du compte
        st.markdown("### 📊 Informations du Compte")
        
        # Carte de profil
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['secondary']});
            color: white;
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 1rem;
        ">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">👤</div>
            <h3 style="margin: 0.5rem 0;">{user['first_name']} {user['last_name']}</h3>
            <p style="margin: 0; opacity: 0.9;">{user['email']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Statistiques du compte
        st.markdown("#### 📈 Statistiques")
        
        member_since = format_date(user.get('created_at', ''), 'long')
        st.info(f"**Membre depuis:** {member_since}")
        
        # Plan actuel
        current_plan = PLANS.get(user.get('plan', 'free'), PLANS['free'])
        plan_color = COLORS['success'] if user.get('plan') == 'free' else COLORS['primary']
        
        st.markdown(f"""
        <div style="
            background: {plan_color}15;
            border: 2px solid {plan_color};
            border-radius: 10px;
            padding: 1rem;
            margin: 1rem 0;
        ">
            <h4 style="margin: 0 0 0.5rem 0; color: {plan_color};">Plan Actuel</h4>
            <p style="margin: 0; font-size: 1.1rem; font-weight: bold;">{current_plan['name']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Activité récente
        try:
            _render_user_activity_summary(user)
        except Exception as e:
            logger.error(f"Erreur activité utilisateur: {e}")

def _render_preferences(user):
    """Section préférences de recherche"""
    st.markdown("## 🎯 Mes Préférences de Recherche")
    
    db = get_database()
    current_prefs = db.get_user_preferences(user['id']) or {}
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.form("update_preferences"):
            st.markdown("### 🔍 Critères de Recherche")
            
            # Budget
            st.markdown("#### 💰 Budget")
            col_min, col_max = st.columns(2)
            
            with col_min:
                budget_min = st.number_input(
                    "Budget minimum (€)",
                    min_value=VALIDATION_RULES['price']['min'],
                    max_value=VALIDATION_RULES['price']['max'],
                    value=current_prefs.get('budget_min', 200000),
                    step=25000,
                    format="%d"
                )
            
            with col_max:
                budget_max = st.number_input(
                    "Budget maximum (€)",
                    min_value=VALIDATION_RULES['price']['min'],
                    max_value=VALIDATION_RULES['price']['max'],
                    value=current_prefs.get('budget_max', 500000),
                    step=25000,
                    format="%d"
                )
            
            # Type de propriété
            property_type = st.selectbox(
                "Type de bien préféré",
                options=["Aucune préférence"] + PROPERTY_TYPES,
                index=0 if not current_prefs.get('property_type') else 
                      PROPERTY_TYPES.index(current_prefs['property_type']) + 1
            )
            
            # Caractéristiques
            st.markdown("#### 🏠 Caractéristiques")
            col_bed, col_bath, col_surf = st.columns(3)
            
            with col_bed:
                bedrooms = st.number_input(
                    "Chambres (min)",
                    min_value=0,
                    max_value=10,
                    value=current_prefs.get('bedrooms', 2),
                    step=1
                )
            
            with col_bath:
                bathrooms = st.number_input(
                    "Salles de bain (min)",
                    min_value=0,
                    max_value=5,
                    value=current_prefs.get('bathrooms', 1),
                    step=1
                )
            
            with col_surf:
                surface_min = st.number_input(
                    "Surface min (m²)",
                    min_value=10,
                    max_value=1000,
                    value=current_prefs.get('surface_min', 70),
                    step=10
                )
            
            # Localisation
            location = st.text_input(
                "Localisation préférée",
                value=current_prefs.get('location', ''),
                placeholder="Ex: Antibes, Cannes, Nice..."
            )
            
            # Critères avancés pour utilisateurs premium
            if auth_manager.can_access_feature('advanced_search'):
                st.markdown("#### ⭐ Critères Avancés (Premium)")
                
                advanced_criteria = current_prefs.get('criteria', {})
                
                col1_adv, col2_adv = st.columns(2)
                
                with col1_adv:
                    has_garage = st.checkbox(
                        "Garage souhaité", 
                        value=advanced_criteria.get('has_garage', False)
                    )
                    has_garden = st.checkbox(
                        "Jardin souhaité",
                        value=advanced_criteria.get('has_garden', False)
                    )
                    has_pool = st.checkbox(
                        "Piscine souhaitée",
                        value=advanced_criteria.get('has_pool', False)
                    )
                
                with col2_adv:
                    has_balcony = st.checkbox(
                        "Balcon/Terrasse",
                        value=advanced_criteria.get('has_balcony', False)
                    )
                    furnished = st.checkbox(
                        "Meublé préféré",
                        value=advanced_criteria.get('furnished', False)
                    )
                    elevator = st.checkbox(
                        "Ascenseur requis",
                        value=advanced_criteria.get('elevator', False)
                    )
            
            if st.form_submit_button("💾 Sauvegarder les Préférences", type="primary", use_container_width=True):
                preferences = {
                    'budget_min': budget_min,
                    'budget_max': budget_max,
                    'property_type': property_type if property_type != "Aucune préférence" else None,
                    'bedrooms': bedrooms,
                    'bathrooms': bathrooms,
                    'surface_min': surface_min,
                    'location': location if location else None
                }
                
                # Ajouter critères avancés si disponibles
                if auth_manager.can_access_feature('advanced_search'):
                    preferences['criteria'] = {
                        'has_garage': has_garage,
                        'has_garden': has_garden,
                        'has_pool': has_pool,
                        'has_balcony': has_balcony,
                        'furnished': furnished,
                        'elevator': elevator
                    }
                
                if db.save_user_preferences(user['id'], preferences):
                    st.success("Préférences sauvegardées avec succès !")
                    st.rerun()
                else:
                    st.error("Erreur lors de la sauvegarde")
    
    with col2:
        # Visualisation des préférences actuelles
        if current_prefs:
            st.markdown("### 📊 Aperçu de vos Préférences")
            
            # Graphique radar des critères
            criteria_scores = {
                'Budget': 0.8,
                'Localisation': 0.9 if current_prefs.get('location') else 0.3,
                'Taille': min(1.0, (current_prefs.get('surface_min', 0) / 200)),
                'Chambres': min(1.0, (current_prefs.get('bedrooms', 0) / 5)),
                'Type': 0.8 if current_prefs.get('property_type') else 0.5
            }
            
            create_radar_chart(criteria_scores, "Profil de Recherche")
            
            # Résumé des préférences
            st.markdown("#### 📋 Résumé")
            prefs_summary = []
            
            if current_prefs.get('budget_min') and current_prefs.get('budget_max'):
                prefs_summary.append(f"💰 {format_currency(current_prefs['budget_min'])} - {format_currency(current_prefs['budget_max'])}")
            
            if current_prefs.get('property_type'):
                prefs_summary.append(f"🏠 {current_prefs['property_type']}")
            
            if current_prefs.get('location'):
                prefs_summary.append(f"📍 {current_prefs['location']}")
            
            if current_prefs.get('surface_min'):
                prefs_summary.append(f"📐 Min {current_prefs['surface_min']}m²")
            
            for item in prefs_summary:
                st.write(f"• {item}")

def _render_subscription(user):
    """Section gestion de l'abonnement"""
    st.markdown("## 💳 Mon Abonnement")
    
    current_plan = user.get('plan', 'free')
    plan_info = PLANS.get(current_plan, PLANS['free'])
    
    # Plan actuel
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📋 Plan Actuel")
        
        plan_color = COLORS['success'] if current_plan == 'free' else COLORS['primary']
        
        st.markdown(f"""
        <div style="
            background: {plan_color}15;
            border: 2px solid {plan_color};
            border-radius: 15px;
            padding: 2rem;
            margin: 1rem 0;
        ">
            <h2 style="margin: 0 0 1rem 0; color: {plan_color};">{plan_info['name']}</h2>
            <p style="font-size: 1.5rem; margin: 0 0 1rem 0; color: {plan_color}; font-weight: bold;">
                {plan_info['price']}€/mois
            </p>
            <div style="color: #666;">
                {"<br>".join([f"✅ {feature}" for feature in plan_info['features']])}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Utilisation mensuelle
        if current_plan == 'free':
            searches_used = user.get('searches_this_month', 0)
            max_searches = plan_info['searches_per_month']
            
            progress = searches_used / max_searches if max_searches > 0 else 0
            
            st.markdown("#### 📊 Utilisation ce Mois")
            st.progress(progress)
            st.write(f"**Recherches:** {searches_used}/{max_searches}")
            
            if searches_used >= max_searches * 0.8:
                st.warning("⚠️ Vous approchez de la limite mensuelle !")
    
    with col2:
        st.markdown("### 🚀 Passer au Niveau Supérieur")
        
        # Afficher les autres plans
        for plan_key, plan_data in PLANS.items():
            if plan_key != current_plan:
                
                color = COLORS['primary'] if plan_key == 'premium' else COLORS['secondary']
                
                st.markdown(f"""
                <div style="
                    border: 1px solid {color};
                    border-radius: 10px;
                    padding: 1rem;
                    margin: 1rem 0;
                    text-align: center;
                ">
                    <h4 style="color: {color}; margin: 0 0 0.5rem 0;">{plan_data['name']}</h4>
                    <p style="font-size: 1.2rem; font-weight: bold; margin: 0 0 0.5rem 0;">{plan_data['price']}€/mois</p>
                    <small style="color: #666;">{"<br>".join(plan_data['features'][:3])}</small>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"⬆️ Passer au {plan_data['name']}", key=f"upgrade_{plan_key}", use_container_width=True):
                    success, message = auth_manager.upgrade_plan(plan_key)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
    
    # Historique de facturation (simulé)
    if current_plan != 'free':
        st.markdown("---")
        st.markdown("### 📋 Historique de Facturation")
        
        # Données simulées
        billing_data = [
            {'date': '2024-01-01', 'plan': plan_info['name'], 'montant': plan_info['price'], 'statut': 'Payé'},
            {'date': '2023-12-01', 'plan': plan_info['name'], 'montant': plan_info['price'], 'statut': 'Payé'},
            {'date': '2023-11-01', 'plan': plan_info['name'], 'montant': plan_info['price'], 'statut': 'Payé'},
        ]
        
        df = pd.DataFrame(billing_data)
        df['Date'] = pd.to_datetime(df['date']).dt.strftime('%d/%m/%Y')
        
        st.dataframe(
            df[['Date', 'plan', 'montant', 'statut']],
            column_config={
                'Date': 'Date',
                'plan': 'Plan',
                'montant': st.column_config.NumberColumn('Montant (€)', format='%d €'),
                'statut': 'Statut'
            },
            hide_index=True,
            use_container_width=True
        )

def _render_favorites(user):
    """Section favoris"""
    st.markdown("## ❤️ Mes Propriétés Favorites")
    
    create_favorites_widget()
    
    # Statistiques des favoris
    try:
        db = get_database()
        favorites = db.get_user_favorites(user['id'])
        
        if favorites:
            st.markdown("### 📊 Analyse de mes Favoris")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                avg_price = sum(fav['price'] for fav in favorites) / len(favorites)
                create_metric_card("Prix Moyen", format_currency(avg_price), "💰")
            
            with col2:
                if any(fav.get('surface') for fav in favorites):
                    avg_surface = sum(fav.get('surface', 0) for fav in favorites if fav.get('surface')) / len([f for f in favorites if f.get('surface')])
                    create_metric_card("Surface Moyenne", f"{avg_surface:.0f}m²", "📐")
            
            with col3:
                create_metric_card("Total Favoris", str(len(favorites)), "❤️")
            
            # Répartition par type
            if len(favorites) > 1:
                type_counts = {}
                for fav in favorites:
                    prop_type = fav['property_type']
                    type_counts[prop_type] = type_counts.get(prop_type, 0) + 1
                
                fig = px.pie(
                    values=list(type_counts.values()),
                    names=list(type_counts.keys()),
                    title="Répartition de vos Favoris par Type"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        logger.error(f"Erreur analyse favoris: {e}")

def _render_settings(user):
    """Section paramètres"""
    st.markdown("## ⚙️ Paramètres du Compte")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔒 Sécurité")
        
        # Changement de mot de passe
        with st.expander("🔑 Changer le Mot de Passe"):
            with st.form("change_password"):
                current_password = st.text_input("Mot de passe actuel", type="password")
                new_password = st.text_input("Nouveau mot de passe", type="password")
                confirm_password = st.text_input("Confirmer le nouveau mot de passe", type="password")
                
                if st.form_submit_button("🔒 Changer le Mot de Passe"):
                    success, message = auth_manager.change_password(
                        current_password, new_password, confirm_password
                    )
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
        
        # Export des données
        st.markdown("### 📥 Mes Données")
        
        if st.button("📊 Exporter mes Données (RGPD)", use_container_width=True):
            from utils.helpers import export_user_data
            data = export_user_data(user['id'])
            if data:
                st.download_button(
                    label="💾 Télécharger mes données",
                    data=json.dumps(data, indent=2, ensure_ascii=False),
                    file_name=f"imomatch_data_{user['id']}_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
                st.success("Données exportées avec succès !")
            else:
                st.error("Erreur lors de l'export")
    
    with col2:
        st.markdown("### 🎨 Préférences d'Interface")
        
        # Thème (placeholder pour future implémentation)
        theme = st.selectbox(
            "Thème",
            options=["Clair", "Sombre", "Auto"],
            index=0,
            help="Le thème sombre sera disponible prochainement"
        )
        
        # Langue
        language = st.selectbox(
            "Langue",
            options=["Français", "English"],
            index=0,
            help="Support multilingue à venir"
        )
        
        # Notifications
        st.markdown("### 🔔 Notifications")
        
        email_notifications = st.checkbox("Notifications par email", value=True)
        search_alerts = st.checkbox("Alertes de nouvelles propriétés", value=False)
        newsletter = st.checkbox("Newsletter mensuelle", value=False)
        
        if st.button("💾 Sauvegarder les Préférences", use_container_width=True):
            st.success("Préférences sauvegardées !")
        
        # Zone dangereuse
        st.markdown("---")
        st.markdown("### ⚠️ Zone Dangereuse")
        
        with st.expander("🗑️ Supprimer mon Compte", expanded=False):
            st.error("⚠️ Cette action est irréversible !")
            st.write("Toutes vos données seront définitivement supprimées.")
            
            confirm_deletion = st.text_input(
                "Tapez 'SUPPRIMER' pour confirmer",
                placeholder="SUPPRIMER"
            )
            
            if st.button("🗑️ Supprimer Définitivement", type="primary"):
                if confirm_deletion == "SUPPRIMER":
                    st.error("Fonctionnalité de suppression à implémenter")
                else:
                    st.warning("Veuillez taper 'SUPPRIMER' pour confirmer")

def _render_user_activity_summary(user):
    """Affiche un résumé de l'activité utilisateur"""
    st.markdown("#### 📈 Activité Récente")
    
    try:
        db = get_database()
        
        # Compter les favoris
        favorites_count = len(db.get_user_favorites(user['id']))
        
        # Compter les recherches sauvegardées
        saved_searches_count = len(db.get_saved_searches(user['id']))
        
        # Afficher les métriques
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Favoris", favorites_count)
        
        with col2:
            st.metric("Recherches", saved_searches_count)
        
        # Dernière activité
        last_update = format_date(user.get('updated_at', ''), 'relative')
        st.caption(f"Dernière activité: {last_update}")
        
    except Exception as e:
        logger.error(f"Erreur résumé activité: {e}")
        st.caption("Impossible de charger l'activité")
