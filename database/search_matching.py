"""
Algorithmes de matching utilisateur/propriétés pour ImoMatch
"""
import logging
import math
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime

from utils.helpers import calculate_distance
from database.manager import get_database

logger = logging.getLogger(__name__)

class PropertyMatcher:
    """Classe pour le matching de propriétés selon les préférences utilisateur"""
    
    def __init__(self):
        self.db = get_database()
        self.weight_config = {
            'price': 0.25,
            'location': 0.20,
            'property_type': 0.15,
            'surface': 0.15,
            'bedrooms': 0.10,
            'bathrooms': 0.05,
            'features': 0.10
        }
    
    def calculate_match_score(self, property_data: Dict[str, Any], 
                             user_preferences: Dict[str, Any],
                             user_behavior: Dict[str, Any] = None) -> float:
        """
        Calcule le score de compatibilité entre une propriété et un utilisateur
        
        Args:
            property_data: Données de la propriété
            user_preferences: Préférences explicites de l'utilisateur
            user_behavior: Données comportementales (historique, favoris)
            
        Returns:
            float: Score entre 0 et 1
        """
        try:
            total_score = 0.0
            total_weight = 0.0
            
            # Score prix
            price_score, price_weight = self._calculate_price_score(
                property_data, user_preferences
            )
            total_score += price_score * price_weight
            total_weight += price_weight
            
            # Score localisation
            location_score, location_weight = self._calculate_location_score(
                property_data, user_preferences
            )
            total_score += location_score * location_weight
            total_weight += location_weight
            
            # Score type de propriété
            type_score, type_weight = self._calculate_type_score(
                property_data, user_preferences
            )
            total_score += type_score * type_weight
            total_weight += type_weight
            
            # Score surface
            surface_score, surface_weight = self._calculate_surface_score(
                property_data, user_preferences
            )
            total_score += surface_score * surface_weight
            total_weight += surface_weight
            
            # Score chambres
            bedrooms_score, bedrooms_weight = self._calculate_bedrooms_score(
                property_data, user_preferences
            )
            total_score += bedrooms_score * bedrooms_weight
            total_weight += bedrooms_weight
            
            # Score salles de bain
            bathrooms_score, bathrooms_weight = self._calculate_bathrooms_score(
                property_data, user_preferences
            )
            total_score += bathrooms_score * bathrooms_weight
            total_weight += bathrooms_weight
            
            # Score équipements
            features_score, features_weight = self._calculate_features_score(
                property_data, user_preferences
            )
            total_score += features_score * features_weight
            total_weight += features_weight
            
            # Bonus comportemental
            if user_behavior:
                behavior_bonus = self._calculate_behavior_bonus(
                    property_data, user_behavior
                )
                total_score += behavior_bonus * 0.1
                total_weight += 0.1
            
            # Normaliser le score
            final_score = total_score / total_weight if total_weight > 0 else 0.0
            
            return min(1.0, max(0.0, final_score))
            
        except Exception as e:
            logger.error(f"Erreur calcul score matching: {e}")
            return 0.0
    
    def find_matches(self, user_id: int, limit: int = 10, 
                    min_score: float = 0.3) -> List[Dict[str, Any]]:
        """
        Trouve les meilleures correspondances pour un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            limit: Nombre maximum de résultats
            min_score: Score minimum requis
            
        Returns:
            Liste des propriétés avec scores
        """
        try:
            # Récupérer les préférences utilisateur
            user_preferences = self.db.get_user_preferences(user_id)
            if not user_preferences:
                logger.warning(f"Pas de préférences pour l'utilisateur {user_id}")
                return []
            
            # Récupérer le comportement utilisateur
            user_behavior = self._get_user_behavior(user_id)
            
            # Récupérer toutes les propriétés disponibles
            all_properties = self.db.search_properties({'is_available': True})
            
            # Calculer les scores
            scored_properties = []
            
            for property_data in all_properties:
                score = self.calculate_match_score(
                    property_data, user_preferences, user_behavior
                )
                
                if score >= min_score:
                    property_data['match_score'] = score
                    property_data['match_explanation'] = self._generate_match_explanation(
                        property_data, user_preferences, score
                    )
                    scored_properties.append(property_data)
            
            # Trier par score décroissant
            scored_properties.sort(key=lambda x: x['match_score'], reverse=True)
            
            return scored_properties[:limit]
            
        except Exception as e:
            logger.error(f"Erreur recherche matches: {e}")
            return []
    
    def get_similar_properties(self, reference_property_id: int, 
                              limit: int = 5) -> List[Dict[str, Any]]:
        """
        Trouve des propriétés similaires à une propriété de référence
        
        Args:
            reference_property_id: ID de la propriété de référence
            limit: Nombre de propriétés similaires à retourner
            
        Returns:
            Liste des propriétés similaires
        """
        try:
            # Récupérer la propriété de référence
            reference = self.db.get_property_by_id(reference_property_id)
            if not reference:
                return []
            
            # Récupérer toutes les autres propriétés
            all_properties = self.db.search_properties({'is_available': True})
            other_properties = [p for p in all_properties if p['id'] != reference_property_id]
            
            # Calculer la similarité
            similar_properties = []
            
            for property_data in other_properties:
                similarity_score = self._calculate_property_similarity(
                    reference, property_data
                )
                
                if similarity_score > 0.3:  # Seuil de similarité
                    property_data['similarity_score'] = similarity_score
                    similar_properties.append(property_data)
            
            # Trier par similarité décroissante
            similar_properties.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            return similar_properties[:limit]
            
        except Exception as e:
            logger.error(f"Erreur propriétés similaires: {e}")
            return []
    
    # === MÉTHODES PRIVÉES DE CALCUL DE SCORES ===
    
    def _calculate_price_score(self, property_data: Dict, user_preferences: Dict) -> Tuple[float, float]:
        """Calcule le score de prix"""
        weight = self.weight_config['price']
        
        property_price = property_data.get('price', 0)
        user_budget_min = user_preferences.get('budget_min', 0)
        user_budget_max = user_preferences.get('budget_max', float('inf'))
        
        if user_budget_max == 0:
            return 0.5, weight  # Score neutre si pas de budget défini
        
        if user_budget_min <= property_price <= user_budget_max:
            # Dans le budget : score selon la position dans la fourchette
            if user_budget_max > user_budget_min:
                position = (property_price - user_budget_min) / (user_budget_max - user_budget_min)
                # Score max au milieu de la fourchette
                score = 1.0 - abs(position - 0.5) * 0.4
            else:
                score = 1.0
        elif property_price < user_budget_min:
            # Moins cher que souhaité (bonus)
            ratio = property_price / user_budget_min if user_budget_min > 0 else 1
            score = 0.8 + (1.0 - ratio) * 0.2  # Score entre 0.8 et 1.0
        else:
            # Plus cher que le budget (pénalité)
            excess_ratio = (property_price - user_budget_max) / user_budget_max
            score = max(0.0, 0.5 - excess_ratio * 0.5)
        
        return score, weight
    
    def _calculate_location_score(self, property_data: Dict, user_preferences: Dict) -> Tuple[float, float]:
        """Calcule le score de localisation"""
        weight = self.weight_config['location']
        
        property_location = property_data.get('location', '').lower()
        preferred_location = user_preferences.get('location', '').lower()
        
        if not preferred_location:
            return 0.5, weight  # Score neutre si pas de préférence
        
        # Correspondance exacte
        if preferred_location in property_location:
            return 1.0, weight
        
        # Correspondance partielle (même ville/région)
        location_words = preferred_location.split()
        property_words = property_location.split()
        
        matches = sum(1 for word in location_words if word in property_words)
        partial_score = matches / len(location_words) if location_words else 0
        
        return partial_score * 0.8, weight  # Score réduit pour correspondance partielle
    
    def _calculate_type_score(self, property_data: Dict, user_preferences: Dict) -> Tuple[float, float]:
        """Calcule le score de type de propriété"""
        weight = self.weight_config['property_type']
        
        property_type = property_data.get('property_type', '')
        preferred_type = user_preferences.get('property_type', '')
        
        if not preferred_type:
            return 0.5, weight  # Score neutre si pas de préférence
        
        if property_type == preferred_type:
            return 1.0, weight
        
        # Types similaires (logique métier)
        similar_types = {
            'Appartement': ['Studio', 'Duplex', 'Triplex', 'Penthouse'],
            'Maison': ['Villa', 'Mas'],
            'Villa': ['Maison'],
            'Studio': ['Appartement']
        }
        
        if preferred_type in similar_types:
            if property_type in similar_types[preferred_type]:
                return 0.7, weight
        
        return 0.2, weight  # Score faible pour types différents
    
    def _calculate_surface_score(self, property_data: Dict, user_preferences: Dict) -> Tuple[float, float]:
        """Calcule le score de surface"""
        weight = self.weight_config['surface']
        
        property_surface = property_data.get('surface', 0)
        min_surface = user_preferences.get('surface_min', 0)
        
        if min_surface == 0:
            return 0.5, weight  # Score neutre si pas de préférence
        
        if property_surface >= min_surface:
            # Bonus si surface largement supérieure
            excess_ratio = (property_surface - min_surface) / min_surface
            score = min(1.0, 0.8 + excess_ratio * 0.2)
            return score, weight
        else:
            # Pénalité si surface insuffisante
            deficit_ratio = property_surface / min_surface
            return deficit_ratio * 0.6, weight
    
    def _calculate_bedrooms_score(self, property_data: Dict, user_preferences: Dict) -> Tuple[float, float]:
        """Calcule le score de nombre de chambres"""
        weight = self.weight_config['bedrooms']
        
        property_bedrooms = property_data.get('bedrooms', 0)
        desired_bedrooms = user_preferences.get('bedrooms', 0)
        
        if desired_bedrooms == 0:
            return 0.5, weight
        
        if property_bedrooms >= desired_bedrooms:
            return 1.0, weight
        elif property_bedrooms == desired_bedrooms - 1:
            return 0.7, weight  # Une chambre en moins : score acceptable
        else:
            return 0.3, weight  # Trop peu de chambres
    
    def _calculate_bathrooms_score(self, property_data: Dict, user_preferences: Dict) -> Tuple[float, float]:
        """Calcule le score de nombre de salles de bain"""
        weight = self.weight_config['bathrooms']
        
        property_bathrooms = property_data.get('bathrooms', 0)
        desired_bathrooms = user_preferences.get('bathrooms', 0)
        
        if desired_bathrooms == 0:
            return 0.5, weight
        
        if property_bathrooms >= desired_bathrooms:
            return 1.0, weight
        else:
            ratio = property_bathrooms / desired_bathrooms if desired_bathrooms > 0 else 0
            return ratio * 0.8, weight
    
    def _calculate_features_score(self, property_data: Dict, user_preferences: Dict) -> Tuple[float, float]:
        """Calcule le score des équipements"""
        weight = self.weight_config['features']
        
        property_features = set(property_data.get('features', []))
        desired_criteria = user_preferences.get('criteria', {})
        
        if not desired_criteria:
            return 0.5, weight
        
        # Compter les critères satisfaits
        satisfied_criteria = 0
        total_criteria = 0
        
        feature_mapping = {
            'has_garage': 'Garage',
            'has_garden': 'Jardin',
            'has_pool': 'Piscine',
            'has_balcony': ['Balcon', 'Terrasse'],
            'furnished': 'Meublé'
        }
        
        for criterion, desired in desired_criteria.items():
            if desired and criterion in feature_mapping:
                total_criteria += 1
                feature_names = feature_mapping[criterion]
                
                if isinstance(feature_names, list):
                    if any(fname in property_features for fname in feature_names):
                        satisfied_criteria += 1
                else:
                    if feature_names in property_features:
                        satisfied_criteria += 1
        
        if total_criteria == 0:
            return 0.5, weight
        
        score = satisfied_criteria / total_criteria
        return score, weight
    
    def _calculate_behavior_bonus(self, property_data: Dict, user_behavior: Dict) -> float:
        """Calcule un bonus basé sur le comportement utilisateur"""
        bonus = 0.0
        
        # Bonus si propriété similaire aux favoris
        favorite_types = user_behavior.get('favorite_property_types', {})
        property_type = property_data.get('property_type', '')
        
        if property_type in favorite_types:
            # Plus l'utilisateur a de favoris de ce type, plus le bonus est important
            type_count = favorite_types[property_type]
            total_favorites = sum(favorite_types.values())
            bonus += (type_count / total_favorites) * 0.2 if total_favorites > 0 else 0
        
        # Bonus si localisation populaire dans les recherches
        searched_locations = user_behavior.get('searched_locations', {})
        property_location = property_data.get('location', '').lower()
        
        for searched_loc, count in searched_locations.items():
            if searched_loc.lower() in property_location:
                bonus += min(0.1, count * 0.02)  # Max 0.1 bonus
                break
        
        return min(0.3, bonus)  # Bonus maximum de 0.3
    
    def _calculate_property_similarity(self, prop1: Dict, prop2: Dict) -> float:
        """Calcule la similarité entre deux propriétés"""
        similarity_score = 0.0
        
        # Similarité de prix (±20%)
        price1, price2 = prop1.get('price', 0), prop2.get('price', 0)
        if price1 > 0 and price2 > 0:
            price_diff = abs(price1 - price2) / max(price1, price2)
            price_sim = max(0, 1 - price_diff / 0.2) * 0.3
            similarity_score += price_sim
        
        # Même type de propriété
        if prop1.get('property_type') == prop2.get('property_type'):
            similarity_score += 0.25
        
        # Similarité de surface (±30%)
        surface1, surface2 = prop1.get('surface', 0), prop2.get('surface', 0)
        if surface1 > 0 and surface2 > 0:
            surface_diff = abs(surface1 - surface2) / max(surface1, surface2)
            surface_sim = max(0, 1 - surface_diff / 0.3) * 0.2
            similarity_score += surface_sim
        
        # Même nombre de chambres
        if prop1.get('bedrooms') == prop2.get('bedrooms'):
            similarity_score += 0.15
        
        # Proximité géographique
        if (prop1.get('latitude') and prop1.get('longitude') and 
            prop2.get('latitude') and prop2.get('longitude')):
            
            distance = calculate_distance(
                prop1['latitude'], prop1['longitude'],
                prop2['latitude'], prop2['longitude']
            )
            
            # Similarité max si distance < 5km
            geo_sim = max(0, 1 - distance / 10) * 0.1
            similarity_score += geo_sim
        
        return min(1.0, similarity_score)
    
    def _get_user_behavior(self, user_id: int) -> Dict[str, Any]:
        """Récupère les données comportementales de l'utilisateur"""
        try:
            behavior = {}
            
            # Analyser les favoris
            favorites = self.db.get_user_favorites(user_id)
            if favorites:
                favorite_types = {}
                for fav in favorites:
                    prop_type = fav['property_type']
                    favorite_types[prop_type] = favorite_types.get(prop_type, 0) + 1
                
                behavior['favorite_property_types'] = favorite_types
            
            # Analyser les recherches sauvegardées
            saved_searches = self.db.get_saved_searches(user_id)
            if saved_searches:
                searched_locations = {}
                for search in saved_searches:
                    filters = search.get('filters', {})
                    location = filters.get('location', '')
                    if location:
                        searched_locations[location] = searched_locations.get(location, 0) + 1
                
                behavior['searched_locations'] = searched_locations
            
            return behavior
            
        except Exception as e:
            logger.error(f"Erreur récupération comportement utilisateur {user_id}: {e}")
            return {}
    
    def _generate_match_explanation(self, property_data: Dict, 
                                   user_preferences: Dict, score: float) -> str:
        """Génère une explication du matching"""
        explanations = []
        
        # Explication prix
        property_price = property_data.get('price', 0)
        budget_max = user_preferences.get('budget_max', 0)
        
        if budget_max and property_price <= budget_max:
            if property_price <= budget_max * 0.8:
                explanations.append("Prix très attractif")
            else:
                explanations.append("Dans votre budget")
        
        # Explication type
        if property_data.get('property_type') == user_preferences.get('property_type'):
            explanations.append("Type de bien idéal")
        
        # Explication localisation
        property_location = property_data.get('location', '').lower()
        preferred_location = user_preferences.get('location', '').lower()
        if preferred_location and preferred_location in property_location:
            explanations.append("Localisation parfaite")
        
        # Score global
        if score >= 0.8:
            explanations.insert(0, "Excellente correspondance")
        elif score >= 0.6:
            explanations.insert(0, "Bonne correspondance")
        else:
            explanations.insert(0, "Correspondance acceptable")
        
        return " • ".join(explanations) if explanations else "Correspondance selon vos critères"


class CollaborativeFilter:
    """Filtrage collaboratif pour les recommandations"""
    
    def __init__(self):
        self.db = get_database()
    
    def get_collaborative_recommendations(self, user_id: int, 
                                        limit: int = 10) -> List[Dict[str, Any]]:
        """
        Recommandations basées sur les utilisateurs similaires
        
        Args:
            user_id: ID de l'utilisateur
            limit: Nombre de recommandations
            
        Returns:
            Liste des propriétés recommandées
        """
        try:
            # Trouver des utilisateurs similaires
            similar_users = self._find_similar_users(user_id)
            
            if not similar_users:
                return []
            
            # Récupérer les favoris des utilisateurs similaires
            recommended_properties = {}
            
            for similar_user_id, similarity_score in similar_users:
                user_favorites = self.db.get_user_favorites(similar_user_id)
                
                for favorite in user_favorites:
                    prop_id = favorite['id']
                    if prop_id not in recommended_properties:
                        recommended_properties[prop_id] = {
                            'property': favorite,
                            'recommendation_score': 0.0,
                            'recommender_count': 0
                        }
                    
                    recommended_properties[prop_id]['recommendation_score'] += similarity_score
                    recommended_properties[prop_id]['recommender_count'] += 1
            
            # Exclure les propriétés déjà en favoris de l'utilisateur
            user_favorites = self.db.get_user_favorites(user_id)
            user_favorite_ids = {fav['id'] for fav in user_favorites}
            
            recommendations = [
                data for prop_id, data in recommended_properties.items()
                if prop_id not in user_favorite_ids
            ]
            
            # Trier par score et prendre les meilleures
            recommendations.sort(
                key=lambda x: x['recommendation_score'], 
                reverse=True
            )
            
            return [rec['property'] for rec in recommendations[:limit]]
            
        except Exception as e:
            logger.error(f"Erreur recommandations collaboratives: {e}")
            return []
    
    def _find_similar_users(self, user_id: int, limit: int = 10) -> List[Tuple[int, float]]:
        """Trouve des utilisateurs similaires basés sur les préférences et favoris"""
        try:
            target_user_prefs = self.db.get_user_preferences(user_id)
            target_user_favorites = self.db.get_user_favorites(user_id)
            
            if not target_user_prefs and not target_user_favorites:
                return []
            
            # Récupérer tous les autres utilisateurs
            # (Dans une vraie implémentation, optimiser cette requête)
            similar_users = []
            
            # Logique simplifiée : comparer les préférences
            # Dans une vraie implémentation, utiliser des algorithmes plus sophistiqués
            
            return similar_users[:limit]
            
        except Exception as e:
            logger.error(f"Erreur recherche utilisateurs similaires: {e}")
            return []


# Instance globale
property_matcher = PropertyMatcher()
collaborative_filter = CollaborativeFilter()

def get_property_matcher() -> PropertyMatcher:
    """Retourne l'instance du matcher"""
    return property_matcher

def get_collaborative_filter() -> CollaborativeFilter:
    """Retourne l'instance du filtre collaboratif"""
    return collaborative_filter