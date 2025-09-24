"""
Pages d'authentification (connexion/inscription) pour ImoMatch
"""
import streamlit as st
from datetime import datetime
import logging

from config.settings import COLORS, PLANS, APP_CONFIG
from auth.authentication import auth_manager
from utils.helpers import validate_email, validate_phone, validate_password_strength

logger = logging.getLogger(__name__)

def render():
    """Rend les pages d'authentification"""
    
    # Si l'utilisateur est déjà connecté, rediriger
    if auth_manager.is_authenticated():
        st.success("Vous êtes déjà connecté !")
        st.info("Utilisez la navigation pour accéder aux autres pages")
        return
    
    st.markdown("# 🔑 Authentification")
    
    # Tabs pour connexion et inscription
    tab1, tab2 = st.tabs(["🔓 Connexion", "📝 Inscription"])
    
    with tab1:
        _render_login_form()
    
    with tab2:
        _render_register_form()
    
    # Section informations
    _render_auth_info()

def _render_login_form():
    """Formulaire de connexion"""
    st.markdown("## 🔓 Se Connecter")
    
    with st.form("login_form"):
        st.markdown("### Accédez à votre compte")
        
        email = st.text_input(
            "Email",
            placeholder="votre.email@example.com",
            help="Adresse email utilisée lors de l'inscription"
        )
        
        password = st.text_input(
            "Mot de passe",
            type="password",
            placeholder="Votre mot de passe"
        )
        
        # Option "Se souvenir de moi"
        remember_me = st.checkbox("Se souvenir de moi")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            login_button = st.form_submit_button(
                "🔑 Se Connecter", 
                type="primary", 
                use_container_width=True
            )
        
        with col2:
            forgot_password = st.form_submit_button(
                "🤔 Mot de passe oublié ?",
                use_container_width=True
            )
        
        if login_button:
            if not email or not password:
                st.error("Veuillez remplir tous les champs")
            elif not validate_email(email):
                st.error("Format d'email invalide")
            else:
                # Tentative de connexion
                success, message = auth_manager.login(email, password)
                
                if success:
                    st.success(message)
                    st.balloons()  # Animation de succès
                    
                    # Redirection automatique après connexion
                    st.info("Redirection en cours...")
                    st.rerun()
                else:
                    st.error(message)
        
        if forgot_password:
            _render_forgot_password()

def _render_register_form():
    """Formulaire d'inscription"""
    st.markdown("## 📝 Créer un Compte")
    
    with st.form("register_form"):
        st.markdown("### Rejoignez ImoMatch gratuitement")
        
        # Informations personnelles
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input(
                "Prénom *",
                placeholder="Jean",
                help="Champ obligatoire"
            )
        
        with col2:
            last_name = st.text_input(
                "Nom *",
                placeholder="Dupont",
                help="Champ obligatoire"
            )
        
        # Email et téléphone
        email = st.text_input(
            "Email *",
            placeholder="jean.dupont@example.com",
            help="Votre email servira pour la connexion"
        )
        
        phone = st.text_input(
            "Téléphone",
            placeholder="+33 6 12 34 56 78",
            help="Optionnel - pour être contacté par les agents"
        )
        
        # Informations supplémentaires
        col3, col4 = st.columns(2)
        
        with col3:
            age = st.number_input(
                "Âge",
                min_value=18,
                max_value=99,
                value=30,
                step=1
            )
        
        with col4:
            profession = st.text_input(
                "Profession",
                placeholder="Ex: Ingénieur, Médecin...",
                help="Optionnel"
            )
        
        # Mots de passe
        password = st.text_input(
            "Mot de passe *",
            type="password",
            placeholder="Minimum 8 caractères",
            help="Doit contenir majuscules, minuscules et chiffres"
        )
        
        confirm_password = st.text_input(
            "Confirmer le mot de passe *",
            type="password",
            placeholder="Retapez votre mot de passe"
        )
        
        # Validation du mot de passe en temps réel
        if password:
            is_valid, message = validate_password_strength(password)
            if is_valid:
                st.success(f"✅ {message}")
            else:
                st.error(f"❌ {message}")
        
        # Choix du plan
        st.markdown("### 💳 Choisissez votre Plan")
        
        plan_choice = st.radio(
            "Plan initial",
            options=["free", "premium"],
            format_func=lambda x: f"{PLANS[x]['name']} - {PLANS[x]['price']}€/mois" if x != 'free' else f"{PLANS[x]['name']} - Gratuit",
            index=0,
            help="Vous pourrez changer de plan à tout moment"
        )
        
        # Afficher les avantages du plan sélectionné
        selected_plan = PLANS[plan_choice]
        st.markdown(f"**Avantages du plan {selected_plan['name']}:**")
        for feature in selected_plan['features']:
            st.write(f"✅ {feature}")
        
        if plan_choice == 'premium':
            st.info(f"🎁 Essai gratuit de {selected_plan.get('trial_days', 14)} jours !")
        
        # Conditions d'utilisation
        st.markdown("---")
        
        terms_accepted = st.checkbox(
            "J'accepte les Conditions d'Utilisation et la Politique de Confidentialité *",
            help="Obligatoire pour créer un compte"
        )
        
        newsletter = st.checkbox(
            "Je souhaite recevoir les actualités ImoMatch par email",
            value=False
        )
        
        # Bouton d'inscription
        register_button = st.form_submit_button(
            "🚀 Créer mon Compte",
            type="primary",
            use_container_width=True
        )
        
        if register_button:
            # Validation des données
            errors = []
            
            if not first_name or not last_name or not email or not password or not confirm_password:
                errors.append("Les champs marqués * sont obligatoires")
            
            if email and not validate_email(email):
                errors.append("Format d'email invalide")
            
            if phone and not validate_phone(phone):
                errors.append("Format de téléphone invalide")
            
            if password:
                is_valid, message = validate_password_strength(password)
                if not is_valid:
                    errors.append(message)
            
            if password != confirm_password:
                errors.append("Les mots de passe ne correspondent pas")
            
            if not terms_accepted:
                errors.append("Vous devez accepter les conditions d'utilisation")
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                # Tentative d'inscription
                user_data = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'password': password,
                    'confirm_password': confirm_password,
                    'phone': phone if phone else None,
                    'age': age,
                    'profession': profession if profession else None,
                    'plan': plan_choice
                }
                
                success, message = auth_manager.register(user_data)
                
                if success:
                    st.success(message)
                    st.balloons()
                    st.info("Vous pouvez maintenant vous connecter avec vos identifiants")
                    
                    # Passer automatiquement à l'onglet connexion
                    st.session_state['auth_tab'] = 'login'
                    st.rerun()
                else:
                    st.error(message)

def _render_forgot_password():
    """Section mot de passe oublié"""
    st.markdown("### 🤔 Mot de Passe Oublié")
    
    with st.expander("Réinitialiser mon mot de passe", expanded=True):
        forgot_email = st.text_input(
            "Entrez votre email",
            placeholder="votre.email@example.com"
        )
        
        if st.button("📧 Envoyer le lien de réinitialisation"):
            if not forgot_email:
                st.error("Veuillez entrer votre email")
            elif not validate_email(forgot_email):
                st.error("Format d'email invalide")
            else:
                # Dans une vraie implémentation, envoyer un email
                st.success(f"Si un compte existe avec l'email {forgot_email}, un lien de réinitialisation a été envoyé.")
                logger.info(f"Demande de réinitialisation mot de passe pour: {forgot_email}")

def _render_auth_info():
    """Section informative sur l'authentification"""
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔒 Sécurité")
        
        st.markdown("""
        **Nous protégeons vos données:**
        
        - 🔐 Mots de passe chiffrés
        - 🛡️ Sessions sécurisées  
        - 📱 Protection contre les fraudes
        - 🔒 Conformité RGPD
        """)
    
    with col2:
        st.markdown("### ❓ Besoin d'Aide ?")
        
        st.markdown(f"""
        **Support disponible:**
        
        - 📧 Email: support@imomatch.fr
        - 📞 Téléphone: +33 1 23 45 67 89
        - 💬 Chat en ligne (Premium)
        - 📚 [Documentation]({APP_CONFIG['url']}/help)
        """)
    
    # Statistiques de confiance
    st.markdown("### 📊 Ils nous font confiance")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Utilisateurs", "1,250+", "↗️ +15%")
    
    with col2:
        st.metric("Propriétés", "5,800+", "↗️ +22%")
    
    with col3:
        st.metric("Matches", "980+", "↗️ +31%")
    
    with col4:
        st.metric("Satisfaction", "4.8/5", "⭐")

def _render_social_login():
    """Connexion via réseaux sociaux (placeholder pour future implémentation)"""
    st.markdown("### 🌐 Connexion Rapide")
    
    # Placeholder pour la connexion sociale
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔵 Google", use_container_width=True, disabled=True):
            st.info("Connexion Google - Bientôt disponible")
    
    with col2:
        if st.button("📘 Facebook", use_container_width=True, disabled=True):
            st.info("Connexion Facebook - Bientôt disponible")
    
    with col3:
        if st.button("🐦 Twitter", use_container_width=True, disabled=True):
            st.info("Connexion Twitter - Bientôt disponible")
    
    st.caption("Connexions sociales disponibles prochainement")

def _render_demo_accounts():
    """Section comptes de démonstration (pour testing)"""
    if not st.secrets.get("DEMO_MODE", False):
        return
    
    st.markdown("---")
    st.markdown("### 🧪 Comptes de Démonstration")
    
    st.warning("⚠️ Mode démonstration activé - Environnement de test")
    
    demo_accounts = [
        {
            'name': 'Utilisateur Gratuit',
            'email': 'demo.free@imomatch.fr',
            'password': 'Demo123!',
            'plan': 'free'
        },
        {
            'name': 'Utilisateur Premium',
            'email': 'demo.premium@imomatch.fr',
            'password': 'Demo123!',
            'plan': 'premium'
        },
        {
            'name': 'Utilisateur Pro',
            'email': 'demo.pro@imomatch.fr',
            'password': 'Demo123!',
            'plan': 'professional'
        }
    ]
    
    for account in demo_accounts:
        with st.expander(f"👤 {account['name']} ({account['plan'].title()})"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.code(f"Email: {account['email']}\nMot de passe: {account['password']}")
            
            with col2:
                if st.button(f"🔑 Connexion Rapide", key=f"demo_{account['plan']}"):
                    success, message = auth_manager.login(account['email'], account['password'])
                    if success:
                        st.success(f"Connecté en tant que {account['name']}")
                        st.rerun()
                    else:
                        st.error("Erreur de connexion démo")

def _render_plan_comparison():
    """Comparaison détaillée des plans"""
    st.markdown("---")
    st.markdown("### 📊 Comparaison des Plans")
    
    # Créer un tableau de comparaison
    features_comparison = {
        'Fonctionnalité': [
            'Recherches par mois',
            'Accès IA basique',
            'Accès IA avancée',
            'Recherches sauvegardées',
            'Alertes automatiques',
            'Support client',
            'Cartes interactives',
            'Analyse de marché',
            'API Access',
            'Rapports personnalisés',
            'Essai gratuit'
        ],
        'Gratuit': [
            '5 recherches',
            '✅',
            '❌',
            '3 maximum',
            '❌',
            'Email uniquement',
            'Limité',
            '❌',
            '❌',
            '❌',
            '❌'
        ],
        'Premium (29€/mois)': [
            'Illimitées',
            '✅',
            '✅',
            'Illimitées',
            '✅',
            'Prioritaire',
            'Complet',
            '✅',
            '❌',
            'Basiques',
            '14 jours'
        ],
        'Professionnel (99€/mois)': [
            'Illimitées',
            '✅',
            '✅',
            'Illimitées',
            '✅',
            'Dédié',
            'Complet',
            '✅',
            '✅',
            'Avancés',
            '30 jours'
        ]
    }
    
    import pandas as pd
    df_comparison = pd.DataFrame(features_comparison)
    
    # Styliser le DataFrame
    st.dataframe(
        df_comparison,
        use_container_width=True,
        hide_index=True
    )
    
    # Call-to-action pour chaque plan
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 1rem; border: 2px solid #28a745; border-radius: 10px;">
            <h4 style="color: #28a745;">Plan Gratuit</h4>
            <p>Parfait pour commencer</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🆓 Commencer Gratuitement", use_container_width=True):
            # Scrolling vers le formulaire d'inscription
            st.info("👆 Utilisez le formulaire d'inscription ci-dessus")
    
    with col2:
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; border: 2px solid {COLORS['primary']}; border-radius: 10px; background: {COLORS['primary']}15;">
            <h4 style="color: {COLORS['primary']};">Plan Premium</h4>
            <p>Le plus populaire</p>
            <div style="background: {COLORS['primary']}; color: white; padding: 0.3rem; border-radius: 5px; margin: 0.5rem 0;">
                ⭐ RECOMMANDÉ
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("✨ Essai Premium Gratuit", use_container_width=True, type="primary"):
            st.info("👆 Sélectionnez 'Premium' dans le formulaire d'inscription")
    
    with col3:
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; border: 2px solid {COLORS['secondary']}; border-radius: 10px;">
            <h4 style="color: {COLORS['secondary']};">Plan Professionnel</h4>
            <p>Pour les professionnels</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🏢 Découvrir Pro", use_container_width=True):
            st.info("👆 Sélectionnez 'Premium' dans l'inscription, vous pourrez upgrader ensuite")

def _render_testimonials():
    """Témoignages utilisateurs"""
    st.markdown("---")
    st.markdown("### 💬 Témoignages")
    
    testimonials = [
        {
            'name': 'Marie L.',
            'plan': 'Premium',
            'text': 'Grâce à ImoMatch, j\'ai trouvé l\'appartement de mes rêves à Cannes en 2 semaines !',
            'rating': 5
        },
        {
            'name': 'Pierre M.',
            'plan': 'Professionnel',
            'text': 'L\'IA de recommandation est impressionnante. Mes clients sont très satisfaits.',
            'rating': 5
        },
        {
            'name': 'Sophie R.',
            'plan': 'Gratuit',
            'text': 'Interface intuitive et résultats pertinents, même avec le plan gratuit.',
            'rating': 4
        }
    ]
    
    cols = st.columns(len(testimonials))
    
    for i, testimonial in enumerate(testimonials):
        with cols[i]:
            stars = '⭐' * testimonial['rating']
            
            st.markdown(f"""
            <div style="
                border: 1px solid #ddd;
                border-radius: 10px;
                padding: 1rem;
                margin: 0.5rem 0;
                background: white;
            ">
                <div style="text-align: center; margin-bottom: 1rem;">
                    <div style="font-size: 3rem;">👤</div>
                    <strong>{testimonial['name']}</strong><br>
                    <small>{testimonial['plan']}</small>
                </div>
                <p style="font-style: italic; text-align: center;">"{testimonial['text']}"</p>
                <div style="text-align: center;">{stars}</div>
            </div>
            """, unsafe_allow_html=True)

def _render_faq():
    """FAQ sur l'authentification"""
    st.markdown("---")
    st.markdown("### ❓ Questions Fréquentes")
    
    faqs = [
        {
            'question': 'Comment changer de plan après inscription ?',
            'answer': 'Vous pouvez changer de plan à tout moment depuis votre profil utilisateur. Les changements sont effectifs immédiatement.'
        },
        {
            'question': 'Puis-je annuler mon abonnement Premium ?',
            'answer': 'Oui, vous pouvez annuler à tout moment. Votre accès Premium reste actif jusqu\'à la fin de la période payée.'
        },
        {
            'question': 'Mes données sont-elles sécurisées ?',
            'answer': 'Absolument. Nous utilisons un chiffrement de niveau bancaire et respectons le RGPD. Vos données ne sont jamais partagées avec des tiers.'
        },
        {
            'question': 'Comment fonctionne l\'essai gratuit Premium ?',
            'answer': 'L\'essai gratuit de 14 jours vous donne accès à toutes les fonctionnalités Premium. Aucun engagement, vous pouvez annuler avant la fin.'
        },
        {
            'question': 'Que se passe-t-il si je dépasse mes limites de recherche ?',
            'answer': 'Avec le plan gratuit, vous devrez attendre le mois suivant ou passer au Premium. Nous vous préviendrons avant d\'atteindre la limite.'
        }
    ]
    
    for faq in faqs:
        with st.expander(f"❓ {faq['question']}"):
            st.write(faq['answer'])

# Fonction principale améliorée avec toutes les sections
def render_complete():
    """Version complète des pages d'authentification avec toutes les fonctionnalités"""
    
    # Si l'utilisateur est déjà connecté
    if auth_manager.is_authenticated():
        user = auth_manager.get_current_user()
        st.success(f"Connecté en tant que {user['first_name']} {user['last_name']}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🏠 Aller à l'Accueil", use_container_width=True, type="primary"):
                st.switch_page("home_page")
        
        with col2:
            if st.button("🚪 Se Déconnecter", use_container_width=True):
                auth_manager.logout()
                st.rerun()
        return
    
    # Header de la page d'authentification
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem 0; background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['secondary']}); border-radius: 15px; margin-bottom: 2rem; color: white;">
        <h1 style="font-size: 2.5rem; margin-bottom: 1rem;">🔑 Rejoignez ImoMatch</h1>
        <p style="font-size: 1.2rem; opacity: 0.9;">Trouvez votre bien immobilier idéal avec l'IA</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Onglets principaux
    tab1, tab2 = st.tabs(["🔓 Connexion", "📝 Inscription"])
    
    with tab1:
        _render_login_form()
        _render_social_login()
        _render_demo_accounts()
    
    with tab2:
        _render_register_form()
    
    # Sections informatives
    _render_plan_comparison()
    _render_testimonials()
    _render_auth_info()
    _render_faq()

# Alias pour la compatibilité
render_extended = render_complete
