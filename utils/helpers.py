"""
Fonctions utilitaires pour ImoMatch
"""
import streamlit as st
import hashlib
import secrets
import re
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

def init_session_state():
    """Initialise les variables de session par défaut"""
    default_values = {
        'user': None,
        'user_authenticated': False,
        'current_search_filters': {},
        'current_properties': [],
        'ai_conversation': [],
        'theme': 'light',
        'language': 'fr',
        'page_visits': 0
    }
    
    for key, value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = value
    
    # Incrémenter le compteur de visites
    st.session_state.page_visits += 1

def clear_session_state(keys: List[str] = None):
    """
    Nettoie les variables de session
    
    Args:
        keys: Liste des clés à nettoyer. Si None, nettoie tout sauf l'authentification
    """
    if keys is None:
        keys_to_keep = ['user', 'user_authenticated', 'theme', 'language']
        keys = [k for k in st.session_state.keys() if k not in keys_to_keep]
    
    for key in keys:
        if key in st.session_state:
            del st.session_state[key]

def generate_session_token() -> str:
    """Génère un token de session sécurisé"""
    return secrets.token_urlsafe(32)

def hash_password(password: str) -> str:
    """Hache un mot de passe avec SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def validate_email(email: str) -> bool:
    """
    Valide le format d'un email
    
    Args:
        email: Adresse email à valider
        
    Returns:
        bool: True si l'email est valide
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone: str) -> bool:
    """
    Valide le format d'un numéro de téléphone
    
    Args:
        phone: Numéro de téléphone à valider
        
    Returns:
        bool: True si le numéro est valide
    """
    # Nettoyer le numéro
    clean_phone = re.sub(r'[^\d+]', '', phone)
    
    # Vérifier la longueur et le format
    if len(clean_phone) < 10 or len(clean_phone) > 15:
        return False
    
    # Vérifier que c'est bien numérique (avec + optionnel au début)
    return re.match(r'^\+?[\d]+$', clean_phone) is not None

def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Valide la force d'un mot de passe
    
    Args:
        password: Mot de passe à valider
        
    Returns:
        Tuple[bool, str]: (is_valid, message)
    """
    if len(password) < 8:
        return False, "Le mot de passe doit contenir au moins 8 caractères"
    
    if not re.search(r'[A-Z]', password):
        return False, "Le mot de passe doit contenir au moins une majuscule"
    
    if not re.search(r'[a-z]', password):
        return False, "Le mot de passe doit contenir au moins une minuscule"
    
    if not re.search(r'\d', password):
        return False, "Le mot de passe doit contenir au moins un chiffre"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Le mot de passe doit contenir au moins un caractère spécial"
    
    return True, "Mot de passe valide"

def format_currency(amount: float, currency: str = "€", decimal_places: int = 0) -> str:
    """
    Formate un montant en devise
    
    Args:
        amount: Montant à formater
        currency: Symbole de la devise
        decimal_places: Nombre de décimales
        
    Returns:
        str: Montant formaté
    """
    if decimal_places == 0:
        return f"{amount:,.0f} {currency}".replace(",", " ")
    else:
        return f"{amount:,.{decimal_places}f} {currency}".replace(",", " ")

def format_surface(surface: float) -> str:
    """
    Formate une surface
    
    Args:
        surface: Surface à formater
        
    Returns:
        str: Surface formatée
    """
    return f"{surface:,.0f} m²".replace(",", " ")

def format_date(date_str: str, format_type: str = "short") -> str:
    """
    Formate une date
    
    Args:
        date_str: Date au format ISO
        format_type: Type de format ("short", "long", "relative")
        
    Returns:
        str: Date formatée
    """
    try:
        date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        
        if format_type == "short":
            return date_obj.strftime("%d/%m/%Y")
        elif format_type == "long":
            return date_obj.strftime("%d %B %Y à %H:%M")
        elif format_type == "relative":
            return format_relative_time(date_obj)
        else:
            return date_obj.strftime("%d/%m/%Y %H:%M")
            
    except Exception as e:
        logger.error(f"Erreur formatage date {date_str}: {e}")
        return date_str

def format_relative_time(date_obj: datetime) -> str:
    """
    Formate une date de manière relative (il y a X temps)
    
    Args:
        date_obj: Objet datetime
        
    Returns:
        str: Temps relatif formaté
    """
    now = datetime.now()
    if date_obj.tzinfo is not None:
        now = now.replace(tzinfo=date_obj.tzinfo)
    
    diff = now - date_obj
    
    if diff.days > 365:
        years = diff.days // 365
        return f"il y a {years} an{'s' if years > 1 else ''}"
    elif diff.days > 30:
        months = diff.days // 30
        return f"il y a {months} mois"
    elif diff.days > 0:
        return f"il y a {diff.days} jour{'s' if diff.days > 1 else ''}"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"il y a {hours} heure{'s' if hours > 1 else ''}"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"il y a {minutes} minute{'s' if minutes > 1 else ''}"
    else:
        return "à l'instant"

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcule la distance entre deux points GPS (formule de Haversine)
    
    Args:
        lat1, lon1: Coordonnées du premier point
        lat2, lon2: Coordonnées du second point
        
    Returns:
        float: Distance en kilomètres
    """
    import math
    
    # Convertir en radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Formule de Haversine
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Rayon de la Terre en km
    r = 6371
    
    return c * r

def geocode_address(address: str) -> Optional[Tuple[float, float]]:
    """
    Géocode une adresse (version simulée pour cet exemple)
    
    Args:
        address: Adresse à géocoder
        
    Returns:
        Optional[Tuple[float, float]]: (latitude, longitude) ou None
    """
    # Dans une vraie implémentation, utiliser une API de géocodage comme:
    # - Google Maps Geocoding API
    # - OpenStreetMap Nominatim
    # - MapBox Geocoding API
    
    # Coordonnées par défaut pour quelques villes (simulé)
    city_coordinates = {
        'antibes': (43.5804, 7.1225),
        'cannes': (43.5528, 7.0174),
        'nice': (43.7102, 7.2620),
        'monaco': (43.7384, 7.4246),
        'grasse': (43.6584, 6.9225),
        'juan-les-pins': (43.5673, 7.1063),
        'villeneuve-loubet': (43.6395, 7.1289),
        'biot': (43.6284, 7.0962)
    }
    
    address_lower = address.lower()
    for city, coords in city_coordinates.items():
        if city in address_lower:
            return coords
    
    # Coordonnées par défaut (Antibes)
    return (43.5804, 7.1225)

def load_json_file(file_path: str) -> Optional[Dict]:
    """
    Charge un fichier JSON
    
    Args:
        file_path: Chemin vers le fichier JSON
        
    Returns:
        Optional[Dict]: Contenu du fichier ou None
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erreur chargement JSON {file_path}: {e}")
        return None

def save_json_file(data: Dict, file_path: str) -> bool:
    """
    Sauvegarde des données en JSON
    
    Args:
        data: Données à sauvegarder
        file_path: Chemin de sauvegarde
        
    Returns:
        bool: True si succès
    """
    try:
        # Créer le répertoire si nécessaire
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Erreur sauvegarde JSON {file_path}: {e}")
        return False

def sanitize_filename(filename: str) -> str:
    """
    Nettoie un nom de fichier
    
    Args:
        filename: Nom de fichier à nettoyer
        
    Returns:
        str: Nom de fichier nettoyé
    """
    # Remplacer les caractères interdits
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Limiter la longueur
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:255-len(ext)-1] + '.' + ext if ext else name[:255]
    
    return filename

def create_backup_filename(base_name: str, extension: str = 'json') -> str:
    """
    Crée un nom de fichier de sauvegarde avec timestamp
    
    Args:
        base_name: Nom de base
        extension: Extension du fichier
        
    Returns:
        str: Nom de fichier avec timestamp
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_backup_{timestamp}.{extension}"

def parse_search_query(query: str) -> Dict[str, Any]:
    """
    Parse une requête de recherche en langage naturel
    
    Args:
        query: Requête de recherche
        
    Returns:
        Dict[str, Any]: Filtres parsés
    """
    filters = {}
    query_lower = query.lower()
    
    # Extraction du budget
    price_match = re.search(r'(\d+(?:\s?\d+)*)\s*(?:€|euros?)', query_lower)
    if price_match:
        price = int(price_match.group(1).replace(' ', ''))
        filters['price_max'] = price
    
    # Extraction du nombre de pièces
    rooms_match = re.search(r'(\d+)\s*(?:pièces?|chambres?)', query_lower)
    if rooms_match:
        rooms = int(rooms_match.group(1))
        filters['bedrooms'] = rooms
    
    # Extraction de la surface
    surface_match = re.search(r'(\d+)\s*m[²2]', query_lower)
    if surface_match:
        surface = int(surface_match.group(1))
        filters['surface_min'] = surface
    
    # Extraction du type de bien
    from config.settings import PROPERTY_TYPES
    for prop_type in PROPERTY_TYPES:
        if prop_type.lower() in query_lower:
            filters['property_type'] = prop_type
            break
    
    # Extraction de la localisation (villes connues)
    cities = ['antibes', 'cannes', 'nice', 'monaco', 'grasse', 'juan-les-pins']
    for city in cities:
        if city in query_lower:
            filters['location'] = city.title()
            break
    
    return filters

def generate_property_description(property_data: Dict[str, Any]) -> str:
    """
    Génère une description automatique pour une propriété
    
    Args:
        property_data: Données de la propriété
        
    Returns:
        str: Description générée
    """
    description_parts = []
    
    # Introduction basée sur le type
    prop_type = property_data.get('property_type', 'Bien')
    description_parts.append(f"{prop_type} exceptionnel")
    
    # Surface
    if property_data.get('surface'):
        description_parts.append(f"de {property_data['surface']}m²")
    
    # Localisation
    if property_data.get('location'):
        description_parts.append(f"situé à {property_data['location']}")
    
    # Caractéristiques
    characteristics = []
    if property_data.get('bedrooms'):
        characteristics.append(f"{property_data['bedrooms']} chambre{'s' if property_data['bedrooms'] > 1 else ''}")
    if property_data.get('bathrooms'):
        characteristics.append(f"{property_data['bathrooms']} salle{'s' if property_data['bathrooms'] > 1 else ''} de bain")
    
    if characteristics:
        description_parts.append(f"comprenant {', '.join(characteristics)}")
    
    # Équipements
    if property_data.get('features'):
        features = property_data['features'][:3]  # Prendre les 3 premiers
        if features:
            description_parts.append(f"avec {', '.join(features)}")
    
    return ". ".join(description_parts) + "."

def calculate_property_score(property_data: Dict[str, Any], user_preferences: Dict[str, Any]) -> float:
    """
    Calcule un score de compatibilité entre une propriété et les préférences utilisateur
    
    Args:
        property_data: Données de la propriété
        user_preferences: Préférences de l'utilisateur
        
    Returns:
        float: Score entre 0 et 1
    """
    score = 0.0
    total_weight = 0.0
    
    # Poids des différents critères
    weights = {
        'price': 0.3,
        'location': 0.25,
        'property_type': 0.2,
        'surface': 0.15,
        'bedrooms': 0.1
    }
    
    # Score pour le prix
    if user_preferences.get('budget_min') and user_preferences.get('budget_max'):
        property_price = property_data.get('price', 0)
        budget_min = user_preferences['budget_min']
        budget_max = user_preferences['budget_max']
        
        if budget_min <= property_price <= budget_max:
            score += weights['price'] * 1.0
        elif property_price < budget_min:
            # Moins cher que souhaité (bonus partiel)
            score += weights['price'] * 0.8
        else:
            # Plus cher (pénalité selon l'écart)
            excess_ratio = (property_price - budget_max) / budget_max
            penalty = max(0, 1 - excess_ratio)
            score += weights['price'] * penalty
        
        total_weight += weights['price']
    
    # Score pour le type de propriété
    if user_preferences.get('property_type'):
        if property_data.get('property_type') == user_preferences['property_type']:
            score += weights['property_type'] * 1.0
        total_weight += weights['property_type']
    
    # Score pour la surface
    if user_preferences.get('surface_min'):
        property_surface = property_data.get('surface', 0)
        min_surface = user_preferences['surface_min']
        
        if property_surface >= min_surface:
            # Bonus si surface largement supérieure
            bonus = min(1.0, property_surface / min_surface)
            score += weights['surface'] * bonus
        else:
            # Pénalité si surface insuffisante
            penalty = property_surface / min_surface if min_surface > 0 else 0
            score += weights['surface'] * penalty
        
        total_weight += weights['surface']
    
    # Score pour le nombre de chambres
    if user_preferences.get('bedrooms'):
        property_bedrooms = property_data.get('bedrooms', 0)
        desired_bedrooms = user_preferences['bedrooms']
        
        if property_bedrooms >= desired_bedrooms:
            score += weights['bedrooms'] * 1.0
        else:
            penalty = property_bedrooms / desired_bedrooms if desired_bedrooms > 0 else 0
            score += weights['bedrooms'] * penalty
        
        total_weight += weights['bedrooms']
    
    # Score pour la localisation (approximatif)
    if user_preferences.get('location') and property_data.get('location'):
        user_location = user_preferences['location'].lower()
        property_location = property_data['location'].lower()
        
        if user_location in property_location or property_location in user_location:
            score += weights['location'] * 1.0
        else:
            # Score partiel si même département/région (logique simplifiée)
            score += weights['location'] * 0.5
        
        total_weight += weights['location']
    
    # Normaliser le score
    return score / total_weight if total_weight > 0 else 0.0

def log_user_action(user_id: int, action: str, details: Dict[str, Any] = None):
    """
    Log une action utilisateur (pour analytics)
    
    Args:
        user_id: ID de l'utilisateur
        action: Type d'action
        details: Détails additionnels
    """
    try:
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'action': action,
            'details': details or {}
        }
        
        logger.info(f"User action: {json.dumps(log_entry)}")
        
        # Dans une vraie implémentation, sauvegarder en base ou envoyer à un service d'analytics
        
    except Exception as e:
        logger.error(f"Erreur log action utilisateur: {e}")

def export_user_data(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Exporte toutes les données d'un utilisateur (RGPD)
    
    Args:
        user_id: ID de l'utilisateur
        
    Returns:
        Optional[Dict[str, Any]]: Données utilisateur ou None
    """
    try:
        from database.manager import get_database
        db = get_database()
        
        # Récupérer toutes les données utilisateur
        user_data = db.get_user_by_id(user_id)
        if not user_data:
            return None
        
        # Récupérer les préférences
        preferences = db.get_user_preferences(user_id)
        
        # Récupérer les favoris
        favorites = db.get_user_favorites(user_id)
        
        # Récupérer les recherches sauvegardées
        saved_searches = db.get_saved_searches(user_id)
        
        # Assembler toutes les données
        export_data = {
            'user_info': user_data,
            'preferences': preferences,
            'favorites': [{'property_id': fav['id'], 'title': fav['title']} for fav in favorites],
            'saved_searches': saved_searches,
            'export_date': datetime.now().isoformat(),
            'format_version': '1.0'
        }
        
        # Supprimer les données sensibles
        if 'password_hash' in export_data['user_info']:
            del export_data['user_info']['password_hash']
        
        return export_data
        
    except Exception as e:
        logger.error(f"Erreur export données utilisateur {user_id}: {e}")
        return None

def import_sample_properties() -> bool:
    """
    Importe des propriétés d'exemple dans la base de données
    
    Returns:
        bool: True si succès
    """
    try:
        from database.manager import get_database
        db = get_database()
        
        # Propriétés d'exemple
        sample_properties = [
            {
                'title': 'Appartement lumineux centre-ville Antibes',
                'price': 380000,
                'property_type': 'Appartement',
                'bedrooms': 3,
                'bathrooms': 2,
                'surface': 85,
                'location': 'Antibes Centre',
                'latitude': 43.5804,
                'longitude': 7.1225,
                'description': 'Magnifique appartement de 3 pièces en centre-ville d\'Antibes, proche de toutes commodités.',
                'features': ['Balcon', 'Parking', 'Ascenseur', 'Cave'],
                'images': ['https://via.placeholder.com/400x300/FF6B35/FFFFFF?text=Appartement+Antibes'],
                'agent_contact': 'Marie Dubois - 06.12.34.56.78'
            },
            {
                'title': 'Villa avec piscine Juan-les-Pins',
                'price': 850000,
                'property_type': 'Villa',
                'bedrooms': 4,
                'bathrooms': 3,
                'surface': 140,
                'location': 'Juan-les-Pins',
                'latitude': 43.5673,
                'longitude': 7.1063,
                'description': 'Superbe villa avec piscine et jardin, proche des plages de Juan-les-Pins.',
                'features': ['Piscine', 'Jardin', 'Garage', 'Terrasse', 'Barbecue'],
                'images': ['https://via.placeholder.com/400x300/F7931E/FFFFFF?text=Villa+Juan'],
                'agent_contact': 'Pierre Martin - 04.93.12.34.56'
            },
            {
                'title': 'Studio rénové proche plages Cannes',
                'price': 195000,
                'property_type': 'Studio',
                'bedrooms': 0,
                'bathrooms': 1,
                'surface': 28,
                'location': 'Cannes Centre',
                'latitude': 43.5528,
                'longitude': 7.0174,
                'description': 'Studio entièrement rénové à 300m des plages de Cannes.',
                'features': ['Climatisation', 'Kitchenette équipée', 'Balcon'],
                'images': ['https://via.placeholder.com/400x300/FFB84D/FFFFFF?text=Studio+Cannes'],
                'agent_contact': 'Sophie Mercier - 04.92.98.76.54'
            },
            {
                'title': 'Maison familiale avec jardin Nice',
                'price': 620000,
                'property_type': 'Maison',
                'bedrooms': 4,
                'bathrooms': 2,
                'surface': 120,
                'location': 'Nice Est',
                'latitude': 43.7102,
                'longitude': 7.2620,
                'description': 'Belle maison familiale avec grand jardin dans quartier calme de Nice.',
                'features': ['Jardin', 'Garage double', 'Cheminée', 'Buanderie'],
                'images': ['https://via.placeholder.com/400x300/28a745/FFFFFF?text=Maison+Nice'],
                'agent_contact': 'Jean-Claude Riviera - 04.93.87.65.43'
            },
            {
                'title': 'Penthouse vue mer Monaco',
                'price': 2500000,
                'property_type': 'Penthouse',
                'bedrooms': 3,
                'bathrooms': 3,
                'surface': 110,
                'location': 'Monaco Monte-Carlo',
                'latitude': 43.7384,
                'longitude': 7.4246,
                'description': 'Exceptionnel penthouse avec vue panoramique sur la mer et le port de Monaco.',
                'features': ['Vue mer', 'Terrasse 50m²', 'Concierge', 'Cave à vin', 'Parking'],
                'images': ['https://via.placeholder.com/400x300/dc3545/FFFFFF?text=Penthouse+Monaco'],
                'agent_contact': 'Luxury Homes Monaco - 377.93.12.34.56'
            }
        ]
        
        # Ajouter les propriétés
        for prop in sample_properties:
            db.add_property(prop)
        
        logger.info(f"{len(sample_properties)} propriétés d'exemple ajoutées")
        return True
        
    except Exception as e:
        logger.error(f"Erreur import propriétés d'exemple: {e}")
        return False

def clean_expired_data():
    """Nettoie les données expirées de l'application"""
    try:
        from database.manager import get_database
        db = get_database()
        
        # Nettoyer les sessions expirées
        db.cleanup_expired_sessions()
        
        # Réinitialiser les compteurs mensuels si nécessaire
        # (logique à implémenter selon les besoins)
        
        logger.info("Nettoyage des données expirées effectué")
        
    except Exception as e:
        logger.error(f"Erreur nettoyage données expirées: {e}")

def get_app_statistics() -> Dict[str, Any]:
    """
    Récupère les statistiques de l'application
    
    Returns:
        Dict[str, Any]: Statistiques diverses
    """
    try:
        from database.manager import get_database
        db = get_database()
        
        # Statistiques de base
        stats = db.get_statistics()
        
        # Statistiques de session
        session_stats = {
            'current_session_visits': st.session_state.get('page_visits', 0),
            'authenticated': bool(st.session_state.get('user_authenticated')),
            'current_user_plan': None
        }
        
        if st.session_state.get('user'):
            session_stats['current_user_plan'] = st.session_state.user.get('plan', 'free')
        
        stats.update(session_stats)
        return stats
        
    except Exception as e:
        logger.error(f"Erreur récupération statistiques: {e}")
        return {}

def send_notification_email(to_email: str, subject: str, message: str) -> bool:
    """
    Envoie un email de notification (version simulée)
    
    Args:
        to_email: Adresse de destination
        subject: Sujet de l'email
        message: Corps du message
        
    Returns:
        bool: True si succès
    """
    # Dans une vraie implémentation, utiliser un service comme:
    # - SendGrid
    # - Mailgun  
    # - AWS SES
    # - SMTP classique
    
    logger.info(f"Email simulé envoyé à {to_email}: {subject}")
    return True

def create_property_alerts_check():
    """
    Vérifie les nouvelles propriétés correspondant aux alertes utilisateurs
    (À exécuter périodiquement)
    """
    try:
        from database.manager import get_database
        db = get_database()
        
        # Récupérer toutes les recherches avec alertes activées
        # (nécessite une requête SQL personnalisée)
        
        # Pour chaque recherche sauvegardée avec alerte
        # 1. Exécuter la recherche
        # 2. Comparer avec les résultats précédents
        # 3. Envoyer une notification si nouvelles propriétés
        
        logger.info("Vérification des alertes propriétés effectuée")
        
    except Exception as e:
        logger.error(f"Erreur vérification alertes: {e}")

def validate_property_data(property_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Valide les données d'une propriété
    
    Args:
        property_data: Données de la propriété à valider
        
    Returns:
        Tuple[bool, List[str]]: (is_valid, error_messages)
    """
    errors = []
    
    # Champs obligatoires
    required_fields = ['title', 'price', 'property_type', 'location']
    for field in required_fields:
        if not property_data.get(field):
            errors.append(f"Le champ '{field}' est obligatoire")
    
    # Validation du prix
    price = property_data.get('price')
    if price is not None:
        if not isinstance(price, (int, float)) or price <= 0:
            errors.append("Le prix doit être un nombre positif")
    
    # Validation de la surface
    surface = property_data.get('surface')
    if surface is not None:
        if not isinstance(surface, (int, float)) or surface <= 0:
            errors.append("La surface doit être un nombre positif")
    
    # Validation des coordonnées GPS
    lat = property_data.get('latitude')
    lng = property_data.get('longitude')
    if lat is not None and lng is not None:
        if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
            errors.append("Coordonnées GPS invalides")
    
    # Validation du type de propriété
    from config.settings import PROPERTY_TYPES
    if property_data.get('property_type') not in PROPERTY_TYPES:
        errors.append("Type de propriété invalide")
    
    return len(errors) == 0, errors

# Décorateurs utiles
def requires_auth(func):
    """Décorateur pour les fonctions nécessitant une authentification"""
    def wrapper(*args, **kwargs):
        if not st.session_state.get('user_authenticated'):
            st.error("Veuillez vous connecter pour accéder à cette fonctionnalité")
            st.stop()
        return func(*args, **kwargs)
    return wrapper

def requires_plan(required_plan: str):
    """Décorateur pour les fonctions nécessitant un plan spécifique"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not st.session_state.get('user_authenticated'):
                st.error("Veuillez vous connecter")
                st.stop()
            
            user_plan = st.session_state.user.get('plan', 'free')
            plan_hierarchy = {'free': 0, 'premium': 1, 'professional': 2}
            
            if plan_hierarchy.get(user_plan, 0) < plan_hierarchy.get(required_plan, 0):
                st.error(f"Cette fonctionnalité nécessite le plan {required_plan}")
                st.stop()
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def measure_performance(func):
    """Décorateur pour mesurer les performances d'une fonction"""
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        result = func(*args, **kwargs)
        end_time = datetime.now()
        
        duration = (end_time - start_time).total_seconds()
        logger.info(f"Performance {func.__name__}: {duration:.3f}s")
        
        return result
    return wrapper
