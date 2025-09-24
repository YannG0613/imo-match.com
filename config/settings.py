"""
Configuration générale de l'application ImoMatch
"""
import os
from typing import Dict, Any

# Couleurs de l'application
COLORS = {
    "primary": "#FF6B35",      # Orange principal
    "secondary": "#F7931E",    # Orange secondaire  
    "accent": "#FFB84D",       # Orange clair
    "success": "#28a745",      # Vert succès
    "warning": "#ffc107",      # Jaune attention
    "danger": "#dc3545",       # Rouge erreur
    "dark": "#343a40",         # Gris foncé
    "light": "#f8f9fa"         # Gris clair
}

# Plans tarifaires
PLANS = {
    "free": {
        "name": "Gratuit",
        "searches_per_month": 5,
        "price": 0,
        "features": [
            "5 recherches par mois",
            "Support de base",
            "Accès limité à l'IA"
        ]
    },
    "premium": {
        "name": "Premium",
        "searches_per_month": -1,  # Illimité
        "price": 29,
        "trial_days": 14,
        "features": [
            "Recherches illimitées",
            "IA avancée", 
            "Support prioritaire",
            "Notifications en temps réel",
            "Essai gratuit 14 jours"
        ]
    },
    "professional": {
        "name": "Professionnel",
        "searches_per_month": -1,  # Illimité
        "price": 99,
        "features": [
            "Toutes les fonctionnalités Premium",
            "Accès API",
            "Rapports personnalisés",
            "Support dédié"
        ]
    }
}

# Types de propriétés
PROPERTY_TYPES = [
    "Appartement",
    "Maison", 
    "Studio",
    "Loft",
    "Villa",
    "Duplex",
    "Triplex",
    "Penthouse",
    "Terrain",
    "Local commercial",
    "Bureau"
]

# Configuration de l'application
APP_CONFIG = {
    "name": "ImoMatch",
    "version": "1.0.0",
    "description": "Application immobilière avec IA",
    "author": "YannG0613",
    "email": "support@imomatch.fr",
    "url": "https://imo-match.streamlit.app"
}

# Configuration Streamlit
STREAMLIT_CONFIG = {
    "page_title": "ImoMatch - Immobilier IA",
    "page_icon": "🏠",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
    "menu_items": {
        'Get Help': 'https://docs.imomatch.fr',
        'Report a bug': 'mailto:support@imomatch.fr',
        'About': f"# {APP_CONFIG['name']} v{APP_CONFIG['version']}\n{APP_CONFIG['description']}"
    }
}

# Configuration de la base de données
DATABASE_CONFIG = {
    "sqlite": {
        "path": "imomatch.db",
        "check_same_thread": False
    },
    "postgresql": {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5432"),
        "database": os.getenv("DB_NAME", "imomatch"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", "")
    }
}

# Configuration OpenAI
OPENAI_CONFIG = {
    "api_key": os.getenv("OPENAI_API_KEY"),
    "model": "gpt-3.5-turbo",
    "max_tokens": 500,
    "temperature": 0.7
}

# Configuration des cartes
MAP_CONFIG = {
    "default_location": [43.5804, 7.1225],  # Antibes, France
    "default_zoom": 12,
    "tile_layer": "OpenStreetMap",
    "marker_colors": {
        "appartement": "blue",
        "maison": "green", 
        "studio": "orange",
        "villa": "red"
    }
}

# Limites et validations
VALIDATION_RULES = {
    "price": {
        "min": 50000,
        "max": 10000000
    },
    "surface": {
        "min": 10,
        "max": 1000
    },
    "bedrooms": {
        "min": 0,
        "max": 10
    },
    "bathrooms": {
        "min": 0,
        "max": 5
    },
    "age": {
        "min": 18,
        "max": 99
    }
}

# Messages et textes
MESSAGES = {
    "welcome": "Bienvenue sur ImoMatch ! 🏠",
    "login_required": "Veuillez vous connecter pour accéder à cette fonctionnalité.",
    "search_limit_reached": "Limite de recherches atteinte. Passez au plan Premium !",
    "profile_updated": "Profil mis à jour avec succès !",
    "property_saved": "Propriété ajoutée aux favoris ❤️",
    "error_generic": "Une erreur s'est produite. Veuillez réessayer."
}

# Configuration des notifications (future implémentation)
NOTIFICATION_CONFIG = {
    "email": {
        "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
        "smtp_port": int(os.getenv("SMTP_PORT", "587")),
        "username": os.getenv("EMAIL_USERNAME"),
        "password": os.getenv("EMAIL_PASSWORD")
    },
    "push": {
        "service_account_key": os.getenv("FIREBASE_KEY_PATH")
    }
}

# Configuration pour le développement
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
TESTING = os.getenv("TESTING", "False").lower() == "true"

def get_database_url() -> str:
    """Retourne l'URL de la base de données selon l'environnement"""
    db_type = os.getenv("DB_TYPE", "sqlite")
    
    if db_type == "sqlite":
        return DATABASE_CONFIG["sqlite"]["path"]
    elif db_type == "postgresql":
        config = DATABASE_CONFIG["postgresql"]
        return f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
    else:
        raise ValueError(f"Type de base de données non supporté: {db_type}")

def get_color_scheme(theme: str = "light") -> Dict[str, str]:
    """Retourne le schéma de couleurs selon le thème"""
    if theme == "dark":
        return {
            **COLORS,
            "background": "#1e1e1e",
            "surface": "#2d2d2d",
            "text": "#ffffff"
        }
    else:
        return {
            **COLORS,
            "background": "#ffffff",
            "surface": "#f8f9fa",
            "text": "#343a40"
        }
