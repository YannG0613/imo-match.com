"""
Fonctions de validation pour ImoMatch
"""
import re
import logging
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, date
from email_validator import validate_email, EmailNotValidError

from config.settings import VALIDATION_RULES, PROPERTY_TYPES

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Exception levée lors d'erreurs de validation"""
    pass

class FieldValidator:
    """Validateur pour les champs individuels"""
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """
        Valide un email
        
        Returns:
            Tuple[bool, str]: (is_valid, message)
        """
        if not email:
            return False, "Email requis"
        
        try:
            # Utilise la librairie email-validator pour une validation robuste
            valid = validate_email(email)
            return True, "Email valide"
        except EmailNotValidError as e:
            return False, f"Email invalide: {str(e)}"
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:
        """
        Valide un mot de passe selon les règles de sécurité
        
        Returns:
            Tuple[bool, str]: (is_valid, message)
        """
        if not password:
            return False, "Mot de passe requis"
        
        if len(password) < 8:
            return False, "Le mot de passe doit contenir au moins 8 caractères"
        
        if len(password) > 128:
            return False, "Le mot de passe ne peut pas dépasser 128 caractères"
        
        # Vérifier la présence de différents types de caractères
        has_lower = bool(re.search(r'[a-z]', password))
        has_upper = bool(re.search(r'[A-Z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
        
        strength_score = sum([has_lower, has_upper, has_digit, has_special])
        
        if strength_score < 3:
            missing = []
            if not has_lower:
                missing.append("minuscules")
            if not has_upper:
                missing.append("majuscules")
            if not has_digit:
                missing.append("chiffres")
            if not has_special:
                missing.append("caractères spéciaux")
            
            return False, f"Le mot de passe doit contenir: {', '.join(missing)}"
        
        return True, "Mot de passe fort"
    
    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, str]:
        """
        Valide un numéro de téléphone
        
        Returns:
            Tuple[bool, str]: (is_valid, message)
        """
        if not phone:
            return True, "Téléphone optionnel"  # Le téléphone est optionnel
        
        # Nettoyer le numéro (supprimer espaces, tirets, points)
        cleaned_phone = re.sub(r'[^\d+]', '', phone)
        
        # Patterns pour différents formats
        patterns = [
            r'^\+33[1-9]\d{8}$',  # Format international français
            r'^0[1-9]\d{8}$',     # Format national français
            r'^\+\d{10,15}$',     # Format international générique
            r'^\d{10}$'           # 10 chiffres simple
        ]
        
        for pattern in patterns:
            if re.match(pattern, cleaned_phone):
                return True, "Téléphone valide"
        
        return False, "Format de téléphone invalide (ex: 06 12 34 56 78 ou +33 6 12 34 56 78)"
    
    @staticmethod
    def validate_age(age: int) -> Tuple[bool, str]:
        """
        Valide un âge
        
        Returns:
            Tuple[bool, str]: (is_valid, message)
        """
        if not isinstance(age, int):
            return False, "L'âge doit être un nombre entier"
        
        min_age = VALIDATION_RULES['age']['min']
        max_age = VALIDATION_RULES['age']['max']
        
        if age < min_age:
            return False, f"Vous devez avoir au moins {min_age} ans"
        
        if age > max_age:
            return False, f"L'âge maximum accepté est {max_age} ans"
        
        return True, "Âge valide"
    
    @staticmethod
    def validate_name(name: str, field_name: str = "nom") -> Tuple[bool, str]:
        """
        Valide un nom ou prénom
        
        Returns:
            Tuple[bool, str]: (is_valid, message)
        """
        if not name:
            return False, f"{field_name.title()} requis"
        
        name = name.strip()
        
        if len(name) < 2:
            return False, f"Le {field_name} doit contenir au moins 2 caractères"
        
        if len(name) > 50:
            return False, f"Le {field_name} ne peut pas dépasser 50 caractères"
        
        # Vérifier que le nom ne contient que des lettres, espaces, tirets et apostrophes
        if not re.match(r"^[a-zA-ZÀ-ÿ\s'-]+$", name):
            return False, f"Le {field_name} ne peut contenir que des lettres, espaces, tirets et apostrophes"
        
        return True, f"{field_name.title()} valide"

class PropertyValidator:
    """Validateur pour les données de propriétés"""
    
    @staticmethod
    def validate_price(price: float) -> Tuple[bool, str]:
        """Valide un prix de propriété"""
        if not isinstance(price, (int, float)):
            return False, "Le prix doit être un nombre"
        
        if price <= 0:
            return False, "Le prix doit être positif"
        
        min_price = VALIDATION_RULES['price']['min']
        max_price = VALIDATION_RULES['price']['max']
        
        if price < min_price:
            return False, f"Le prix minimum est {min_price:,}€"
        
        if price > max_price:
            return False, f"Le prix maximum est {max_price:,}€"
        
        return True, "Prix valide"
    
    @staticmethod
    def validate_surface(surface: float) -> Tuple[bool, str]:
        """Valide une surface de propriété"""
        if not isinstance(surface, (int, float)):
            return False, "La surface doit être un nombre"
        
        if surface <= 0:
            return False, "La surface doit être positive"
        
        min_surface = VALIDATION_RULES['surface']['min']
        max_surface = VALIDATION_RULES['surface']['max']
        
        if surface < min_surface:
            return False, f"La surface minimum est {min_surface}m²"
        
        if surface > max_surface:
            return False, f"La surface maximum est {max_surface}m²"
        
        return True, "Surface valide"
    
    @staticmethod
    def validate_property_type(property_type: str) -> Tuple[bool, str]:
        """Valide un type de propriété"""
        if not property_type:
            return False, "Type de propriété requis"
        
        if property_type not in PROPERTY_TYPES:
            return False, f"Type de propriété invalide. Types acceptés: {', '.join(PROPERTY_TYPES)}"
        
        return True, "Type de propriété valide"
    
    @staticmethod
    def validate_rooms(rooms: int, room_type: str = "chambres") -> Tuple[bool, str]:
        """Valide le nombre de pièces"""
        if not isinstance(rooms, int):
            return False, f"Le nombre de {room_type} doit être un nombre entier"
        
        if rooms < 0:
            return False, f"Le nombre de {room_type} ne peut pas être négatif"
        
        max_rooms = VALIDATION_RULES.get('bedrooms', {}).get('max', 10) if room_type == "chambres" else 5
        
        if rooms > max_rooms:
            return False, f"Le nombre maximum de {room_type} est {max_rooms}"
        
        return True, f"Nombre de {room_type} valide"
    
    @staticmethod
    def validate_coordinates(latitude: float, longitude: float) -> Tuple[bool, str]:
        """Valide des coordonnées GPS"""
        if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
            return False, "Les coordonnées doivent être des nombres"
        
        if not (-90 <= latitude <= 90):
            return False, "La latitude doit être entre -90 et 90"
        
        if not (-180 <= longitude <= 180):
            return False, "La longitude doit être entre -180 et 180"
        
        return True, "Coordonnées valides"
    
    @staticmethod
    def validate_year_built(year: int) -> Tuple[bool, str]:
        """Valide une année de construction"""
        if not isinstance(year, int):
            return False, "L'année de construction doit être un nombre entier"
        
        current_year = datetime.now().year
        
        if year < 1800:
            return False, "L'année de construction ne peut pas être antérieure à 1800"
        
        if year > current_year + 2:
            return False, f"L'année de construction ne peut pas être supérieure à {current_year + 2}"
        
        return True, "Année de construction valide"

class FormValidator:
    """Validateur pour les formulaires complets"""
    
    @staticmethod
    def validate_user_registration(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Valide les données d'inscription utilisateur
        
        Returns:
            Tuple[bool, List[str]]: (is_valid, error_messages)
        """
        errors = []
        
        # Validation des champs obligatoires
        required_fields = ['email', 'password', 'confirm_password', 'first_name', 'last_name']
        for field in required_fields:
            if not data.get(field):
                field_display = field.replace('_', ' ').title()
                errors.append(f"{field_display} est requis")
        
        # Validation de l'email
        if data.get('email'):
            is_valid, message = FieldValidator.validate_email(data['email'])
            if not is_valid:
                errors.append(message)
        
        # Validation du mot de passe
        if data.get('password'):
            is_valid, message = FieldValidator.validate_password(data['password'])
            if not is_valid:
                errors.append(message)
        
        # Confirmation du mot de passe
        if data.get('password') and data.get('confirm_password'):
            if data['password'] != data['confirm_password']:
                errors.append("Les mots de passe ne correspondent pas")
        
        # Validation du prénom
        if data.get('first_name'):
            is_valid, message = FieldValidator.validate_name(data['first_name'], "prénom")
            if not is_valid:
                errors.append(message)
        
        # Validation du nom
        if data.get('last_name'):
            is_valid, message = FieldValidator.validate_name(data['last_name'], "nom")
            if not is_valid:
                errors.append(message)
        
        # Validation du téléphone (optionnel)
        if data.get('phone'):
            is_valid, message = FieldValidator.validate_phone(data['phone'])
            if not is_valid:
                errors.append(message)
        
        # Validation de l'âge (optionnel)
        if data.get('age'):
            is_valid, message = FieldValidator.validate_age(data['age'])
            if not is_valid:
                errors.append(message)
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_property_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Valide les données d'une propriété
        
        Returns:
            Tuple[bool, List[str]]: (is_valid, error_messages)
        """
        errors = []
        
        # Champs obligatoires
        required_fields = ['title', 'price', 'property_type', 'location']
        for field in required_fields:
            if not data.get(field):
                field_display = field.replace('_', ' ').title()
                errors.append(f"{field_display} est requis")
        
        # Validation du prix
        if data.get('price'):
            is_valid, message = PropertyValidator.validate_price(data['price'])
            if not is_valid:
                errors.append(message)
        
        # Validation du type de propriété
        if data.get('property_type'):
            is_valid, message = PropertyValidator.validate_property_type(data['property_type'])
            if not is_valid:
                errors.append(message)
        
        # Validation de la surface
        if data.get('surface'):
            is_valid, message = PropertyValidator.validate_surface(data['surface'])
            if not is_valid:
                errors.append(message)
        
        # Validation du nombre de chambres
        if data.get('bedrooms') is not None:
            is_valid, message = PropertyValidator.validate_rooms(data['bedrooms'], "chambres")
            if not is_valid:
                errors.append(message)
        
        # Validation du nombre de salles de bain
        if data.get('bathrooms') is not None:
            is_valid, message = PropertyValidator.validate_rooms(data['bathrooms'], "salles de bain")
            if not is_valid:
                errors.append(message)
        
        # Validation des coordonnées GPS
        if data.get('latitude') is not None and data.get('longitude') is not None:
            is_valid, message = PropertyValidator.validate_coordinates(
                data['latitude'], data['longitude']
            )
            if not is_valid:
                errors.append(message)
        
        # Validation de l'année de construction
        if data.get('year_built'):
            is_valid, message = PropertyValidator.validate_year_built(data['year_built'])
            if not is_valid:
                errors.append(message)
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_search_preferences(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Valide les préférences de recherche
        
        Returns:
            Tuple[bool, List[str]]: (is_valid, error_messages)
        """
        errors = []
        
        # Validation de la fourchette de prix
        price_min = data.get('budget_min')
        price_max = data.get('budget_max')
        
        if price_min is not None:
            is_valid, message = PropertyValidator.validate_price(price_min)
            if not is_valid:
                errors.append(f"Prix minimum: {message}")
        
        if price_max is not None:
            is_valid, message = PropertyValidator.validate_price(price_max)
            if not is_valid:
                errors.append(f"Prix maximum: {message}")
        
        if price_min is not None and price_max is not None:
            if price_min > price_max:
                errors.append("Le prix minimum ne peut pas être supérieur au prix maximum")
        
        # Validation du type de propriété
        if data.get('property_type'):
            is_valid, message = PropertyValidator.validate_property_type(data['property_type'])
            if not is_valid:
                errors.append(message)
        
        # Validation de la surface minimum
        if data.get('surface_min'):
            is_valid, message = PropertyValidator.validate_surface(data['surface_min'])
            if not is_valid:
                errors.append(f"Surface minimum: {message}")
        
        # Validation du nombre de chambres
        if data.get('bedrooms') is not None:
            is_valid, message = PropertyValidator.validate_rooms(data['bedrooms'], "chambres")
            if not is_valid:
                errors.append(message)
        
        # Validation du nombre de salles de bain
        if data.get('bathrooms') is not None:
            is_valid, message = PropertyValidator.validate_rooms(data['bathrooms'], "salles de bain")
            if not is_valid:
                errors.append(message)
        
        return len(errors) == 0, errors

class DataSanitizer:
    """Classe pour nettoyer et normaliser les données"""
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = None) -> str:
        """Nettoie une chaîne de caractères"""
        if not value:
            return ""
        
        # Supprimer les espaces en début/fin
        cleaned = value.strip()
        
        # Supprimer les caractères de contrôle
        cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', cleaned)
        
        # Limiter la longueur si spécifiée
        if max_length and len(cleaned) > max_length:
            cleaned = cleaned[:max_length]
        
        return cleaned
    
    @staticmethod
    def sanitize_email(email: str) -> str:
        """Nettoie et normalise un email"""
        if not email:
            return ""
        
        # Convertir en minuscules et supprimer les espaces
        cleaned = email.lower().strip()
        
        # Supprimer les caractères non autorisés (garder seulement les caractères valides pour email)
        cleaned = re.sub(r'[^a-z0-9@._-]', '', cleaned)
        
        return cleaned
    
    @staticmethod
    def sanitize_phone(phone: str) -> str:
        """Nettoie et normalise un numéro de téléphone"""
        if not phone:
            return ""
        
        # Supprimer tous les caractères sauf chiffres et +
        cleaned = re.sub(r'[^\d+]', '', phone)
        
        # Normaliser le format français
        if cleaned.startswith('0') and len(cleaned) == 10:
            cleaned = '+33' + cleaned[1:]
        elif cleaned.startswith('33') and len(cleaned) == 11:
            cleaned = '+' + cleaned
        
        return cleaned
    
    @staticmethod
    def sanitize_location(location: str) -> str:
        """Nettoie et normalise une localisation"""
        if not location:
            return ""
        
        # Nettoyer la chaîne
        cleaned = DataSanitizer.sanitize_string(location, 100)
        
        # Capitaliser correctement (première lettre de chaque mot)
        cleaned = ' '.join(word.capitalize() for word in cleaned.split())
        
        return cleaned
    
    @staticmethod
    def sanitize_numeric(value: Any, value_type: type = int) -> Optional[Any]:
        """Nettoie et convertit une valeur numérique"""
        if value is None or value == '':
            return None
        
        try:
            if value_type == int:
                return int(float(value))  # float() d'abord pour gérer "123.0"
            elif value_type == float:
                return float(value)
        except (ValueError, TypeError):
            return None
        
        return value

def validate_and_sanitize_user_data(raw_data: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """
    Valide et nettoie les données utilisateur
    
    Returns:
        Tuple[Dict[str, Any], List[str]]: (cleaned_data, error_messages)
    """
    errors = []
    cleaned_data = {}
    
    # Nettoyer les données
    if 'email' in raw_data:
        cleaned_data['email'] = DataSanitizer.sanitize_email(raw_data['email'])
    
    if 'first_name' in raw_data:
        cleaned_data['first_name'] = DataSanitizer.sanitize_string(raw_data['first_name'], 50)
    
    if 'last_name' in raw_data:
        cleaned_data['last_name'] = DataSanitizer.sanitize_string(raw_data['last_name'], 50)
    
    if 'phone' in raw_data:
        cleaned_data['phone'] = DataSanitizer.sanitize_phone(raw_data['phone'])
    
    if 'age' in raw_data:
        cleaned_data['age'] = DataSanitizer.sanitize_numeric(raw_data['age'], int)
    
    if 'profession' in raw_data:
        cleaned_data['profession'] = DataSanitizer.sanitize_string(raw_data['profession'], 100)
    
    # Garder le mot de passe tel quel (sera hashé plus tard)
    if 'password' in raw_data:
        cleaned_data['password'] = raw_data['password']
    
    if 'confirm_password' in raw_data:
        cleaned_data['confirm_password'] = raw_data['confirm_password']
    
    # Valider les données nettoyées
    is_valid, validation_errors = FormValidator.validate_user_registration(cleaned_data)
    errors.extend(validation_errors)
    
    return cleaned_data, errors

def validate_and_sanitize_property_data(raw_data: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """
    Valide et nettoie les données de propriété
    
    Returns:
        Tuple[Dict[str, Any], List[str]]: (cleaned_data, error_messages)
    """
    errors = []
    cleaned_data = {}
    
    # Nettoyer les données
    if 'title' in raw_data:
        cleaned_data['title'] = DataSanitizer.sanitize_string(raw_data['title'], 200)
    
    if 'price' in raw_data:
        cleaned_data['price'] = DataSanitizer.sanitize_numeric(raw_data['price'], float)
    
    if 'property_type' in raw_data:
        cleaned_data['property_type'] = DataSanitizer.sanitize_string(raw_data['property_type'], 50)
    
    if 'location' in raw_data:
        cleaned_data['location'] = DataSanitizer.sanitize_location(raw_data['location'])
    
    if 'surface' in raw_data:
        cleaned_data['surface'] = DataSanitizer.sanitize_numeric(raw_data['surface'], float)
    
    if 'bedrooms' in raw_data:
        cleaned_data['bedrooms'] = DataSanitizer.sanitize_numeric(raw_data['bedrooms'], int)
    
    if 'bathrooms' in raw_data:
        cleaned_data['bathrooms'] = DataSanitizer.sanitize_numeric(raw_data['bathrooms'], int)
    
    if 'latitude' in raw_data:
        cleaned_data['latitude'] = DataSanitizer.sanitize_numeric(raw_data['latitude'], float)
    
    if 'longitude' in raw_data:
        cleaned_data['longitude'] = DataSanitizer.sanitize_numeric(raw_data['longitude'], float)
    
    if 'description' in raw_data:
        cleaned_data['description'] = DataSanitizer.sanitize_string(raw_data['description'], 2000)
    
    if 'year_built' in raw_data:
        cleaned_data['year_built'] = DataSanitizer.sanitize_numeric(raw_data['year_built'], int)
    
    # Valider les données nettoyées
    is_valid, validation_errors = FormValidator.validate_property_data(cleaned_data)
    errors.extend(validation_errors)
    
    return cleaned_data, errors

# Fonction utilitaire pour la validation rapide
def quick_validate(value: Any, validator_func, *args, **kwargs) -> bool:
    """Validation rapide qui retourne seulement True/False"""
    try:
        is_valid, _ = validator_func(value, *args, **kwargs)
        return is_valid
    except Exception:
        return False