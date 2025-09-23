"""
Système d'authentification complet pour ImoMatch
"""
import streamlit as st
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple, List
import re
import logging

logger = logging.getLogger(__name__)

class AuthenticationManager:
    """Gestionnaire d'authentification principal"""
    
    def __init__(self):
        # Initialiser les variables de session si nécessaire
        if 'user' not in st.session_state:
            st.session_state.user = None
        if 'user_authenticated' not in st.session_state:
            st.session_state.user_authenticated = False
    
    def is_authenticated(self) -> bool:
        """Vérifie si l'utilisateur est connecté"""
        return st.session_state.get('user_authenticated', False) and st.session_state.get('user') is not None
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Retourne l'utilisateur actuellement connecté"""
        if self.is_authenticated():
            return st.session_state.user
        return None
    
    def login(self, email: str, password: str) -> Tuple[bool, str]:
        """
        Connecte un utilisateur
        
        Args:
            email: Adresse email
            password: Mot de passe
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            # Validation des entrées
            if not email or not password:
                return False, "Email et mot de passe requis"
            
            if not self._validate_email(email):
                return False, "Format d'email invalide"
            
            # Tentative d'authentification via la base de données
            try:
                from database.manager import get_database
                db = get_database()
                user = db.authenticate_user(email, password)
            except ImportError:
                # Fallback avec utilisateurs de démonstration
                user = self._authenticate_demo_user(email, password)
            
            if user:
                # Connexion réussie
                st.session_state.user = user
                st.session_state.user_authenticated = True
                
                logger.info(f"Connexion réussie pour: {email}")
                return True, f"Bienvenue {user['first_name']} !"
            else:
                logger.warning(f"Tentative de connexion échouée pour: {email}")
                return False, "Email ou mot de passe incorrect"
                
        except Exception as e:
            logger.error(f"Erreur lors de la connexion: {e}")
            return False, "Une erreur s'est produite lors de la connexion"
    
    def register(self, user_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Inscrit un nouvel utilisateur
        
        Args:
            user_data: Données de l'utilisateur
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            # Validation des données
            is_valid, errors = self._validate_registration_data(user_data)
            if not is_valid:
                return False, " • ".join(errors)
            
            # Tentative de création en base de données
            try:
                from database.manager import get_database
                db = get_database()
                
                user_id = db.create_user(
                    email=user_data['email'],
                    password=user_data['password'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    phone=user_data.get('phone'),
                    age=user_data.get('age'),
                    profession=user_data.get('profession'),
                    plan=user_data.get('plan', 'free')
                )
                
                if user_id:
                    logger.info(f"Nouvel utilisateur créé: {user_data['email']}")
                    return True, "Inscription réussie ! Vous pouvez maintenant vous connecter."
                else:
                    return False, "Cette adresse email est déjà utilisée"
                    
            except ImportError:
                # Mode fallback sans base de données
                logger.warning("Base de données non disponible, inscription simulée")
                return True, "Inscription simulée réussie (base de données non configurée)"
                
        except Exception as e:
            logger.error(f"Erreur lors de l'inscription: {e}")
            return False, "Une erreur s'est produite lors de l'inscription"
    
    def logout(self):
        """Déconnecte l'utilisateur"""
        if self.is_authenticated():
            email = st.session_state.user.get('email', 'unknown')
            logger.info(f"Déconnexion de: {email}")
        
        # Nettoyer la session
        st.session_state.user = None
        st.session_state.user_authenticated = False
        
        # Nettoyer d'autres variables de session
        keys_to_remove = ['search_filters', 'current_properties', 'ai_conversation']
        for key in keys_to_remove:
            if key in st.session_state:
                del st.session_state[key]
        
        st.success("Vous avez été déconnecté avec succès")
    
    def update_profile(self, updates: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Met à jour le profil utilisateur
        
        Args:
            updates: Données à mettre à jour
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        if not self.is_authenticated():
            return False, "Vous devez être connecté pour modifier votre profil"
        
        try:
            # Validation des mises à jour
            if 'email' in updates and not self._validate_email(updates['email']):
                return False, "Format d'email invalide"
            
            if 'age' in updates and updates['age']:
                if not (18 <= updates['age'] <= 99):
                    return False, "L'âge doit être entre 18 et 99 ans"
            
            # Mise à jour en base de données
            try:
                from database.manager import get_database
                db = get_database()
                
                user_id = st.session_state.user['id']
                success = db.update_user(user_id, **updates)
                
                if success:
                    # Mettre à jour la session
                    updated_user = db.get_user_by_id(user_id)
                    if updated_user:
                        st.session_state.user = updated_user
                    
                    logger.info(f"Profil mis à jour pour l'utilisateur {user_id}")
                    return True, "Profil mis à jour avec succès !"
                else:
                    return False, "Erreur lors de la mise à jour"
                    
            except ImportError:
                # Mode fallback
                for key, value in updates.items():
                    if key in st.session_state.user:
                        st.session_state.user[key] = value
                
                return True, "Profil mis à jour (mode local)"
                
        except Exception as e:
            logger.error(f"Erreur mise à jour profil: {e}")
            return False, "Une erreur s'est produite lors de la mise à jour"
    
    def change_password(self, current_password: str, new_password: str, 
                       confirm_password: str) -> Tuple[bool, str]:
        """
        Change le mot de passe utilisateur
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        if not self.is_authenticated():
            return False, "Vous devez être connecté"
        
        try:
            # Vérifications
            if not all([current_password, new_password, confirm_password]):
                return False, "Tous les champs sont requis"
            
            if new_password != confirm_password:
                return False, "Les nouveaux mots de passe ne correspondent pas"
            
            if not self._validate_password_strength(new_password):
                return False, "Le mot de passe doit contenir au moins 8 caractères avec majuscules, minuscules et chiffres"
            
            # Vérifier le mot de passe actuel
            current_hash = self._hash_password(current_password)
            if current_hash != st.session_state.user.get('password_hash'):
                return False, "Mot de passe actuel incorrect"
            
            # Mettre à jour en base
            try:
                from database.manager import get_database
                db = get_database()
                
                new_hash = self._hash_password(new_password)
                success = db.update_user(st.session_state.user['id'], password_hash=new_hash)
                
                if success:
                    logger.info(f"Mot de passe changé pour l'utilisateur {st.session_state.user['id']}")
                    return True, "Mot de passe mis à jour avec succès"
                else:
                    return False, "Erreur lors de la mise à jour"
                    
            except ImportError:
                return True, "Changement de mot de passe simulé"
                
        except Exception as e:
            logger.error(f"Erreur changement mot de passe: {e}")
            return False, "Une erreur s'est produite"
    
    def upgrade_plan(self, new_plan: str) -> Tuple[bool, str]:
        """
        Met à niveau le plan utilisateur
        
        Args:
            new_plan: Nouveau plan (premium, professional)
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        if not self.is_authenticated():
            return False, "Vous devez être connecté"
        
        try:
            from config.settings import PLANS
            
            if new_plan not in PLANS:
                return False, "Plan invalide"
            
            # Mise à jour en base
            try:
                from database.manager import get_database
                db = get_database()
                
                user_id = st.session_state.user['id']
                updates = {'plan': new_plan}
                
                # Ajouter date de fin d'essai si applicable
                if new_plan in ['premium', 'professional']:
                    trial_days = PLANS[new_plan].get('trial_days', 0)
                    if trial_days > 0:
                        trial_end = datetime.now() + timedelta(days=trial_days)
                        updates['trial_end_date'] = trial_end.isoformat()
                
                success = db.update_user(user_id, **updates)
                
                if success:
                    # Mettre à jour la session
                    updated_user = db.get_user_by_id(user_id)
                    if updated_user:
                        st.session_state.user = updated_user
                    
                    plan_name = PLANS[new_plan]['name']
                    logger.info(f"Plan mis à niveau vers {new_plan} pour l'utilisateur {user_id}")
                    return True, f"Bienvenue dans le plan {plan_name} !"
                else:
                    return False, "Erreur lors de la mise à niveau"
                    
            except ImportError:
                # Mode fallback
                st.session_state.user['plan'] = new_plan
                plan_name = PLANS[new_plan]['name']
                return True, f"Plan {plan_name} activé (mode local)"
                
        except Exception as e:
            logger.error(f"Erreur mise à niveau plan: {e}")
            return False, "Une erreur s'est produite"
    
    def can_access_feature(self, feature: str) -> bool:
        """
        Vérifie si l'utilisateur peut accéder à une fonctionnalité
        
        Args:
            feature: Nom de la fonctionnalité
            
        Returns:
            bool: True si l'accès est autorisé
        """
        if not self.is_authenticated():
            return False
        
        user_plan = st.session_state.user.get('plan', 'free')
        
        # Fonctionnalités par plan
        features_by_plan = {
            'free': [
                'basic_search', 'view_properties', 'basic_ai', 'favorites'
            ],
            'premium': [
                'basic_search', 'view_properties', 'basic_ai', 'favorites',
                'advanced_search', 'unlimited_search', 'advanced_ai', 
                'notifications', 'save_searches', 'market_insights'
            ],
            'professional': [
                'basic_search', 'view_properties', 'basic_ai', 'favorites',
                'advanced_search', 'unlimited_search', 'advanced_ai',
                'notifications', 'save_searches', 'market_insights',
                'api_access', 'custom_reports', 'priority_support',
                'bulk_operations'
            ]
        }
        
        return feature in features_by_plan.get(user_plan, [])
    
    def get_search_limits(self) -> Dict[str, Any]:
        """
        Retourne les limites de recherche pour l'utilisateur actuel
        
        Returns:
            Dict avec informations sur les limites
        """
        if not self.is_authenticated():
            return {
                'can_search': False, 
                'remaining_searches': 0, 
                'plan_name': 'Non connecté'
            }
        
        user_plan = st.session_state.user.get('plan', 'free')
        
        try:
            from config.settings import PLANS
            plan_info = PLANS.get(user_plan, PLANS['free'])
            
            if user_plan == 'free':
                # Vérifier les limites via la base de données
                try:
                    from database.manager import get_database
                    db = get_database()
                    user_id = st.session_state.user['id']
                    can_search, remaining = db.can_user_search(user_id)
                    
                    return {
                        'can_search': can_search,
                        'remaining_searches': remaining,
                        'plan_name': plan_info['name']
                    }
                except ImportError:
                    # Mode fallback
                    searches_used = st.session_state.get('searches_used', 0)
                    max_searches = plan_info['searches_per_month']
                    remaining = max(0, max_searches - searches_used)
                    
                    return {
                        'can_search': remaining > 0,
                        'remaining_searches': remaining,
                        'plan_name': plan_info['name']
                    }
            else:
                # Plans premium/pro : illimité
                return {
                    'can_search': True,
                    'remaining_searches': -1,  # -1 = illimité
                    'plan_name': plan_info['name']
                }
                
        except ImportError:
            return {
                'can_search': True,
                'remaining_searches': 5,
                'plan_name': 'Gratuit'
            }
    
    def use_search(self) -> bool:
        """
        Enregistre l'utilisation d'une recherche
        
        Returns:
            bool: True si la recherche a pu être utilisée
        """
        if not self.is_authenticated():
            return False
        
        user_plan = st.session_state.user.get('plan', 'free')
        
        # Plans premium/pro : toujours autorisé
        if user_plan in ['premium', 'professional']:
            return True
        
        # Plan gratuit : vérifier les limites
        try:
            from database.manager import get_database
            db = get_database()
            user_id = st.session_state.user['id']
            
            can_search, remaining = db.can_user_search(user_id)
            
            if can_search:
                db.increment_search_count(user_id)
                return True
            else:
                return False
                
        except ImportError:
            # Mode fallback
            searches_used = st.session_state.get('searches_used', 0)
            max_searches = 5  # Limite par défaut
            
            if searches_used < max_searches:
                st.session_state.searches_used = searches_used + 1
                return True
            else:
                return False
    
    # === MÉTHODES PRIVÉES ===
    
    def _authenticate_demo_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authentification avec utilisateurs de démonstration (fallback)"""
        demo_users = {
            'demo.free@imomatch.fr': {
                'id': 1,
                'email': 'demo.free@imomatch.fr',
                'password_hash': self._hash_password('Demo123!'),
                'first_name': 'Demo',
                'last_name': 'Gratuit',
                'plan': 'free',
                'phone': '06.12.34.56.78',
                'age': 30,
                'profession': 'Développeur',
                'created_at': datetime.now().isoformat()
            },
            'demo.premium@imomatch.fr': {
                'id': 2,
                'email': 'demo.premium@imomatch.fr',
                'password_hash': self._hash_password('Demo123!'),
                'first_name': 'Demo',
                'last_name': 'Premium',
                'plan': 'premium',
                'phone': '06.23.45.67.89',
                'age': 35,
                'profession': 'Manager',
                'created_at': datetime.now().isoformat()
            },
            'demo.pro@imomatch.fr': {
                'id': 3,
                'email': 'demo.pro@imomatch.fr',
                'password_hash': self._hash_password('Demo123!'),
                'first_name': 'Demo',
                'last_name': 'Professionnel',
                'plan': 'professional',
                'phone': '06.34.56.78.90',
                'age': 40,
                'profession': 'Agent Immobilier',
                'created_at': datetime.now().isoformat()
            }
        }
        
        user = demo_users.get(email)
        if user and user['password_hash'] == self._hash_password(password):
            return user
        
        return None
    
    def _validate_email(self, email: str) -> bool:
        """Valide le format d'un email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _validate_password_strength(self, password: str) -> bool:
        """Valide la force d'un mot de passe"""
        if len(password) < 8:
            return False
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        
        return has_upper and has_lower and has_digit
    
    def _validate_registration_data(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Valide les données d'inscription"""
        errors = []
        
        # Champs requis
        required_fields = ['email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if not data.get(field):
                field_name = field.replace('_', ' ').title()
                errors.append(f"{field_name} est requis")
        
        # Validation email
        if data.get('email') and not self._validate_email(data['email']):
            errors.append("Format d'email invalide")
        
        # Validation mot de passe
        if data.get('password') and not self._validate_password_strength(data['password']):
            errors.append("Le mot de passe doit contenir au moins 8 caractères avec majuscules, minuscules et chiffres")
        
        # Confirmation mot de passe
        if data.get('password') != data.get('confirm_password'):
            errors.append("Les mots de passe ne correspondent pas")
        
        # Validation âge
        if data.get('age') and not (18 <= data['age'] <= 99):
            errors.append("L'âge doit être entre 18 et 99 ans")
        
        # Validation téléphone
        if data.get('phone'):
            phone_clean = re.sub(r'[^\d+]', '', data['phone'])
            if len(phone_clean) < 10:
                errors.append("Numéro de téléphone invalide")
        
        return len(errors) == 0, errors
    
    def _hash_password(self, password: str) -> str:
        """Hache un mot de passe avec SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()


# === FONCTIONS UTILITAIRES ===

def require_auth(func):
    """Décorateur pour les fonctions nécessitant une authentification"""
    def wrapper(*args, **kwargs):
        if not auth_manager.is_authenticated():
            st.error("Vous devez être connecté pour accéder à cette fonctionnalité")
            st.stop()
        return func(*args, **kwargs)
    return wrapper

def require_plan(required_plan: str):
    """Décorateur pour les fonctions nécessitant un plan spécifique"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not auth_manager.is_authenticated():
                st.error("Vous devez être connecté")
                st.stop()
            
            user_plan = auth_manager.get_current_user().get('plan', 'free')
            plan_hierarchy = {'free': 0, 'premium': 1, 'professional': 2}
            
            if plan_hierarchy.get(user_plan, 0) < plan_hierarchy.get(required_plan, 0):
                st.error(f"Cette fonctionnalité nécessite le plan {required_plan}")
                st.stop()
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# === INSTANCE GLOBALE ===

# Instance globale du gestionnaire d'authentification
auth_manager = AuthenticationManager()

def get_auth_manager() -> AuthenticationManager:
    """Retourne l'instance du gestionnaire d'authentification"""
    return auth_manager

def get_current_user() -> Optional[Dict[str, Any]]:
    """Raccourci pour obtenir l'utilisateur actuel"""
    return auth_manager.get_current_user()

def is_authenticated() -> bool:
    """Raccourci pour vérifier l'authentification"""
    return auth_manager.is_authenticated()

def login_user(email: str, password: str) -> Tuple[bool, str]:
    """Raccourci pour connecter un utilisateur"""
    return auth_manager.login(email, password)

def register_user(user_data: Dict[str, Any]) -> Tuple[bool, str]:
    """Raccourci pour inscrire un utilisateur"""
    return auth_manager.register(user_data)

def logout_user():
    """Raccourci pour déconnecter l'utilisateur"""
    auth_manager.logout()