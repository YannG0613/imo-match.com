"""
Moteur de recherche avancé pour ImoMatch
"""
import logging
from typing import Dict, List, Any, Optional, Tuple
import re
from datetime import datetime

from database.manager import get_database
from utils.helpers import calculate_distance, geocode_address, parse_search_query, calculate_property_score

logger = logging.getLogger(__name__)

class SearchEngine:
    """Moteur de recherche principal pour les propriétés"""
    
    def __init__(self):
        self.db = get_database()
    
    def search(self, filters: Dict[str, Any], user_preferences: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Effectue une recherche de propriétés
        
        Args:
            filters: Filtres de recherche
            user_preferences: Préférences utilisateur pour le scoring
            
        Returns:
            List[Dict[str, Any]]: Liste des propriétés trouvées
        """
        try:
            # Recherche de base en BDD
            properties = self.db.search_properties(filters)
            
            # Enrichir avec des calculs
            enriched_properties = []
            
            for prop in properties:
                enriched_prop = prop.copy()
                
                # Calculer le score de compatibilité si préférences fournies
                if user_preferences:
                    enriched_prop['compatibility_score'] = calculate_property_score(prop, user_preferences)
                
                # Calculer le prix/m²
                if prop.get('surface') and prop.get('surface') > 0:
                    enriched_prop['price_per_m2'] = prop['price'] / prop['surface']
                
                # Enrichir les informations de localisation
                enriched_prop = self._enrich_location_data(enriched_prop)
                
                enriched_properties.append(enriched_prop)
            
            # Appliquer les filtres avancés
            filtered_properties = self._apply_advanced_filters(enriched_properties, filters)
            
            # Trier les résultats
            sorted_properties = self._sort_results(filtered_properties, filters, user_preferences)
            
            logger.info(f"Recherche effectuée: {len(filtered_properties)} résultats")
            return sorted_properties
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche: {e}")
            return []
    
    def search_by_query(self, query: str, user_preferences: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Recherche par requête en langage naturel
        
        Args:
            query: Requête en langage naturel
            user_preferences: Préférences utilisateur
            
        Returns:
            List[Dict[str, Any]]: Propriétés trouvées
        """
        try:
            # Parser la requête en filtres
            filters = parse_search_query(query)
            
            # Ajouter les préférences utilisateur comme filtres de base
            if user_preferences:
                base_filters = {
                    'price_min': user_preferences.get('budget_min'),
                    'price_max': user_preferences.get('budget_max'),
                    'property_type': user_preferences.get('property_type'),
                    'bedrooms': user_preferences.get('bedrooms'),
                    'surface_min': user_preferences.get('surface_min'),
                    'location': user_preferences.get('location')
                }
                
                # Fusionner avec les filtres parsés (les filtres parsés ont priorité)
                for key, value in base_filters.items():
                    if key not in filters and value is not None:
                        filters[key] = value
            
            return self.search(filters, user_preferences)
            
        except Exception as e:
            logger.error(f"Erreur recherche par requête: {e}")
            return []
    
    def get_similar_properties(self, property_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Trouve des propriétés similaires à une propriété donnée
        
        Args:
            property_id: ID de la propriété de référence
            limit: Nombre maximum de résultats
            
        Returns:
            List[Dict[str, Any]]: Propriétés similaires
        """
        try:
            # Récupérer la propriété de référence
            reference_property = self.db.get_property_by_id(property_id)
            if not reference_property:
                return []
            
            # Créer des filtres basés sur la propriété de référence
            filters = {
                'property_type': reference_property['property_type'],
                'price_min': int(reference_property['price'] * 0.7),  # ±30% du prix
                'price_max': int(reference_property['price'] * 1.3),
                'bedrooms': reference_property.get('bedrooms'),
                'limit': limit + 5  # Plus de résultats pour filtrer ensuite
            }
            
            # Rechercher les propriétés similaires
            similar_properties = self.db.search_properties(filters)
            
            # Exclure la propriété de référence
            similar_properties = [p for p in similar_properties if p['id'] != property_id]
            
            # Calculer la similarité et trier
            scored_properties = []
            
            for prop in similar_properties:
                similarity_score = self._calculate_similarity(reference_property, prop)
                prop['similarity_score'] = similarity_score
                scored_properties.append(prop)
            
            # Trier par score de similarité et prendre les meilleurs
            scored_properties.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            return scored_properties[:limit]
            
        except Exception as e:
            logger.error(f"Erreur recherche propriétés similaires: {e}")
            return []
    
    def get_search_suggestions(self, partial_query: str, limit: int = 10) -> List[Dict[str, str]]:
        """
        Propose des suggestions de recherche basées sur une requête partielle
        
        Args:
            partial_query: Début de requête
            limit: Nombre de suggestions
            
        Returns:
            List[Dict[str, str]]: Suggestions avec types
        """
        suggestions = []
        query_lower = partial_query.lower()
        
        try:
            # Suggestions de localisation
            locations = self._get_location_suggestions(query_lower)
            suggestions.extend([{'text': loc, 'type': 'location'} for loc in locations[:3]])
            
            # Suggestions de type de propriété
            from config.settings import PROPERTY_TYPES
            type_suggestions = [t for t in PROPERTY_TYPES if query_lower in t.lower()]
            suggestions.extend([{'text': t, 'type': 'property_type'} for t in type_suggestions[:3]])
            
            # Suggestions de prix
            price_suggestions = self._get_price_suggestions(query_lower)
            suggestions.extend([{'text': p, 'type': 'price'} for p in price_suggestions[:2]])
            
            # Suggestions de recherches populaires
            popular_searches = self._get_popular_searches(query_lower)
            suggestions.extend([{'text': s, 'type': 'popular'} for s in popular_searches[:2]])
            
            return suggestions[:limit]
            
        except Exception as e:
            logger.error(f"Erreur suggestions de recherche: {e}")
            return []
    
    def get_market_stats(self, location: str = None, property_type: str = None) -> Dict[str, Any]:
        """
        Récupère des statistiques de marché
        
        Args:
            location: Localisation pour filtrer
            property_type: Type de propriété pour filtrer
            
        Returns:
            Dict[str, Any]: Statistiques de marché
        """
        try:
            filters = {}
            
            if location:
                filters['location'] = location
            if property_type:
                filters['property_type'] = property_type
            
            properties = self.db.search_properties(filters)
            
            if not properties:
                return {}
            
            prices = [p['price'] for p in properties]
            surfaces = [p.get('surface', 0) for p in properties if p.get('surface')]
            
            stats = {
                'total_properties': len(properties),
                'average_price': sum(prices) / len(prices) if prices else 0,
                'min_price': min(prices) if prices else 0,
                'max_price': max(prices) if prices else 0,
                'median_price': sorted(prices)[len(prices) // 2] if prices else 0,
                'average_surface': sum(surfaces) / len(surfaces) if surfaces else 0,
                'average_price_per_m2': 0
            }
            
            if surfaces and stats['average_surface'] > 0:
                stats['average_price_per_m2'] = stats['average_price'] / stats['average_surface']
            
            # Répartition par nombre de chambres
            bedroom_distribution = {}
            for prop in properties:
                bedrooms = prop.get('bedrooms', 0)
                bedroom_distribution[bedrooms] = bedroom_distribution.get(bedrooms, 0) + 1
            
            stats['bedroom_distribution'] = bedroom_distribution
            
            return stats
            
        except Exception as e:
            logger.error(f"Erreur statistiques marché: {e}")
            return {}
    
    # === MÉTHODES PRIVÉES ===
    
    def _apply_advanced_filters(self, properties: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Applique des filtres avancés aux propriétés"""
        filtered = properties.copy()
        
        # Filtre par distance si coordonnées fournies
        if filters.get('center_lat') and filters.get('center_lng') and filters.get('radius_km'):
            center_lat = filters['center_lat']
            center_lng = filters['center_lng']
            radius = filters['radius_km']
            
            filtered = [
                prop for prop in filtered
                if prop.get('latitude') and prop.get('longitude') and
                calculate_distance(center_lat, center_lng, prop['latitude'], prop['longitude']) <= radius
            ]
        
        # Filtre par prix/m²
        if filters.get('max_price_per_m2'):
            max_price_per_m2 = filters['max_price_per_m2']
            filtered = [
                prop for prop in filtered
                if prop.get('price_per_m2', float('inf')) <= max_price_per_m2
            ]
        
        # Filtre par équipements requis
        required_features = filters.get('required_features', [])
        if required_features:
            filtered = [
                prop for prop in filtered
                if all(feature in prop.get('features', []) for feature in required_features)
            ]
        
        # Filtre par année de construction
        if filters.get('min_year_built'):
            min_year = filters['min_year_built']
            # Simulé - dans une vraie impl, avoir ce champ en BDD
            filtered = [
                prop for prop in filtered
                if prop.get('year_built', 2000) >= min_year
            ]
        
        return filtered
    
    def _sort_results(self, properties: List[Dict[str, Any]], filters: Dict[str, Any], 
                     user_preferences: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Trie les résultats selon les critères"""
        
        sort_by = filters.get('sort_by', 'relevance')
        
        if sort_by == 'price_asc':
            return sorted(properties, key=lambda x: x.get('price', 0))
        elif sort_by == 'price_desc':
            return sorted(properties, key=lambda x: x.get('price', 0), reverse=True)
        elif sort_by == 'surface_desc':
            return sorted(properties, key=lambda x: x.get('surface', 0), reverse=True)
        elif sort_by == 'date_desc':
            return sorted(properties, key=lambda x: x.get('created_at', ''), reverse=True)
        elif sort_by == 'price_per_m2_asc':
            return sorted(properties, key=lambda x: x.get('price_per_m2', float('inf')))
        elif sort_by == 'compatibility' and user_preferences:
            return sorted(properties, key=lambda x: x.get('compatibility_score', 0), reverse=True)
        else:  # relevance par défaut
            # Tri par score de compatibilité puis par date
            if user_preferences:
                return sorted(properties, 
                            key=lambda x: (x.get('compatibility_score', 0), x.get('created_at', '')), 
                            reverse=True)
            else:
                return sorted(properties, key=lambda x: x.get('created_at', ''), reverse=True)
    
    def _calculate_similarity(self, prop1: Dict[str, Any], prop2: Dict[str, Any]) -> float:
        """Calcule la similarité entre deux propriétés"""
        score = 0.0
        
        # Similarité de prix (±20% = score max)
        price1, price2 = prop1.get('price', 0), prop2.get('price', 0)
        if price1 > 0 and price2 > 0:
            price_diff = abs(price1 - price2) / max(price1, price2)
            price_score = max(0, 1 - (price_diff / 0.2))  # Score max si différence ≤ 20%
            score += price_score * 0.3
        
        # Similarité de surface
        surface1, surface2 = prop1.get('surface', 0), prop2.get('surface', 0)
        if surface1 > 0 and surface2 > 0:
            surface_diff = abs(surface1 - surface2) / max(surface1, surface2)
            surface_score = max(0, 1 - (surface_diff / 0.3))
            score += surface_score * 0.2
        
        # Même type de propriété
        if prop1.get('property_type') == prop2.get('property_type'):
            score += 0.2
        
        # Même nombre de chambres
        if prop1.get('bedrooms') == prop2.get('bedrooms'):
            score += 0.15
        
        # Proximité géographique
        if (prop1.get('latitude') and prop1.get('longitude') and 
            prop2.get('latitude') and prop2.get('longitude')):
            distance = calculate_distance(
                prop1['latitude'], prop1['longitude'],
                prop2['latitude'], prop2['longitude']
            )
            # Score max si distance < 5km
            geo_score = max(0, 1 - (distance / 10))
            score += geo_score * 0.15
        
        return min(1.0, score)
    
    def _enrich_location_data(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrichit les données de localisation d'une propriété"""
        
        # Si pas de coordonnées, essayer de les obtenir
        if not property_data.get('latitude') or not property_data.get('longitude'):
            location = property_data.get('location')
            if location:
                coords = geocode_address(location)
                if coords:
                    property_data['latitude'], property_data['longitude'] = coords
        
        # Extraire ville et département de la localisation
        location = property_data.get('location', '')
        if location:
            parts = location.split(',')
            if len(parts) >= 2:
                property_data['city'] = parts[0].strip()
                property_data['district'] = parts[1].strip()
            else:
                property_data['city'] = location.strip()
        
        return property_data
    
    def _get_location_suggestions(self, query: str) -> List[str]:
        """Récupère des suggestions de localisation"""
        common_locations = [
            'Antibes', 'Cannes', 'Nice', 'Monaco', 'Juan-les-Pins',
            'Grasse', 'Valbonne', 'Mougins', 'Biot', 'Villeneuve-Loubet',
            'Cagnes-sur-Mer', 'Saint-Laurent-du-Var', 'Mandelieu-la-Napoule'
        ]
        
        return [loc for loc in common_locations if query in loc.lower()]
    
    def _get_price_suggestions(self, query: str) -> List[str]:
        """Suggère des fourchettes de prix"""
        if 'prix' in query or 'budget' in query or '€' in query:
            return [
                'Budget jusqu\'à 300 000€',
                'Budget 300 000€ - 500 000€',
                'Budget 500 000€ - 1M€',
                'Budget plus de 1M€'
            ]
        return []
    
    def _get_popular_searches(self, query: str) -> List[str]:
        """Retourne des recherches populaires"""
        popular_searches = [
            'Appartement 3 pièces Antibes',
            'Villa avec piscine Cannes',
            'Studio centre-ville Nice',
            'Maison jardin Juan-les-Pins',
            'Penthouse vue mer Monaco',
            'Appartement terrasse Grasse'
        ]
        
        return [search for search in popular_searches if any(word in search.lower() for word in query.split())]


class SmartSearchEngine(SearchEngine):
    """Version avancée du moteur de recherche avec IA"""
    
    def __init__(self):
        super().__init__()
        self.search_history = []
    
    def smart_search(self, query: str, user_id: int, user_preferences: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Recherche intelligente avec apprentissage des préférences
        
        Args:
            query: Requête de recherche
            user_id: ID de l'utilisateur
            user_preferences: Préférences utilisateur
            
        Returns:
            List[Dict[str, Any]]: Résultats optimisés
        """
        try:
            # Enregistrer la recherche
            self._log_search(user_id, query)
            
            # Analyser l'historique de recherche de l'utilisateur
            user_patterns = self._analyze_user_patterns(user_id)
            
            # Adapter les filtres basés sur les patterns
            base_filters = parse_search_query(query)
            enhanced_filters = self._enhance_filters_with_patterns(base_filters, user_patterns, user_preferences)
            
            # Effectuer la recherche
            properties = self.search(enhanced_filters, user_preferences)
            
            # Appliquer le machine learning pour le ranking
            ranked_properties = self._apply_ml_ranking(properties, user_patterns, user_preferences)
            
            return ranked_properties
            
        except Exception as e:
            logger.error(f"Erreur recherche intelligente: {e}")
            # Fallback sur la recherche classique
            return self.search_by_query(query, user_preferences)
    
    def get_personalized_recommendations(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Génère des recommandations personnalisées basées sur l'historique
        
        Args:
            user_id: ID de l'utilisateur
            limit: Nombre de recommandations
            
        Returns:
            List[Dict[str, Any]]: Propriétés recommandées
        """
        try:
            # Analyser les préférences de l'utilisateur
            user_preferences = self.db.get_user_preferences(user_id)
            user_favorites = self.db.get_user_favorites(user_id)
            user_patterns = self._analyze_user_patterns(user_id)
            
            # Créer un profil utilisateur consolidé
            consolidated_profile = self._create_user_profile(user_preferences, user_favorites, user_patterns)
            
            # Générer des filtres de recommandation
            recommendation_filters = self._generate_recommendation_filters(consolidated_profile)
            
            # Rechercher des propriétés
            candidates = self.search(recommendation_filters, user_preferences)
            
            # Exclure les propriétés déjà en favoris
            favorite_ids = {fav['id'] for fav in user_favorites}
            candidates = [prop for prop in candidates if prop['id'] not in favorite_ids]
            
            # Scorer et trier les candidats
            scored_candidates = []
            for prop in candidates:
                score = self._calculate_recommendation_score(prop, consolidated_profile)
                prop['recommendation_score'] = score
                scored_candidates.append(prop)
            
            # Trier par score et diversifier les résultats
            scored_candidates.sort(key=lambda x: x['recommendation_score'], reverse=True)
            diversified_results = self._diversify_results(scored_candidates, limit)
            
            return diversified_results
            
        except Exception as e:
            logger.error(f"Erreur recommandations personnalisées: {e}")
            return []
    
    def get_market_trends(self, location: str = None, period_months: int = 12) -> Dict[str, Any]:
        """
        Analyse les tendances de marché
        
        Args:
            location: Localisation pour analyser
            period_months: Période d'analyse en mois
            
        Returns:
            Dict[str, Any]: Tendances de marché
        """
        try:
            # Dans une vraie implémentation, analyser les données historiques
            # Ici, on simule avec des données statiques
            
            base_stats = self.get_market_stats(location)
            
            # Simuler l'évolution des prix (données factices)
            trends = {
                'current_stats': base_stats,
                'price_evolution': {
                    'trend': 'hausse',  # 'hausse', 'baisse', 'stable'
                    'percentage_change': 5.2,  # % sur la période
                    'monthly_data': [
                        {'month': '2024-01', 'avg_price': 4200},
                        {'month': '2024-02', 'avg_price': 4180},
                        {'month': '2024-03', 'avg_price': 4220},
                        {'month': '2024-04', 'avg_price': 4250},
                        {'month': '2024-05', 'avg_price': 4400},
                        {'month': '2024-06', 'avg_price': 4420},
                    ]
                },
                'demand_indicators': {
                    'search_volume_change': 15.3,
                    'time_on_market_days': 45,
                    'competition_level': 'élevé'  # 'faible', 'modéré', 'élevé'
                },
                'predictions': {
                    'next_3_months': 'hausse_moderee',
                    'confidence': 0.78
                }
            }
            
            return trends
            
        except Exception as e:
            logger.error(f"Erreur analyse tendances marché: {e}")
            return {}
    
    # === MÉTHODES PRIVÉES POUR IA ===
    
    def _log_search(self, user_id: int, query: str):
        """Enregistre une recherche pour l'apprentissage"""
        search_entry = {
            'user_id': user_id,
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'filters': parse_search_query(query)
        }
        
        self.search_history.append(search_entry)
        
        # Dans une vraie implémentation, sauvegarder en base
        logger.info(f"Recherche enregistrée pour utilisateur {user_id}: {query}")
    
    def _analyze_user_patterns(self, user_id: int) -> Dict[str, Any]:
        """Analyse les patterns de recherche d'un utilisateur"""
        user_searches = [s for s in self.search_history if s['user_id'] == user_id]
        
        if not user_searches:
            return {}
        
        patterns = {
            'preferred_locations': {},
            'preferred_types': {},
            'price_ranges': [],
            'search_frequency': len(user_searches),
            'recent_queries': [s['query'] for s in user_searches[-5:]]
        }
        
        # Analyser les localisations préférées
        for search in user_searches:
            location = search['filters'].get('location')
            if location:
                patterns['preferred_locations'][location] = patterns['preferred_locations'].get(location, 0) + 1
        
        # Analyser les types préférés
        for search in user_searches:
            prop_type = search['filters'].get('property_type')
            if prop_type:
                patterns['preferred_types'][prop_type] = patterns['preferred_types'].get(prop_type, 0) + 1
        
        # Analyser les fourchettes de prix
        for search in user_searches:
            if search['filters'].get('price_max'):
                patterns['price_ranges'].append(search['filters']['price_max'])
        
        return patterns
    
    def _enhance_filters_with_patterns(self, base_filters: Dict[str, Any], 
                                     patterns: Dict[str, Any], 
                                     user_preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """Enrichit les filtres avec les patterns utilisateur"""
        enhanced = base_filters.copy()
        
        # Si pas de localisation spécifiée, utiliser les préférences
        if not enhanced.get('location') and patterns.get('preferred_locations'):
            # Prendre la localisation la plus recherchée
            most_searched_location = max(patterns['preferred_locations'], 
                                       key=patterns['preferred_locations'].get)
            enhanced['location'] = most_searched_location
        
        # Si pas de type spécifié, utiliser les préférences
        if not enhanced.get('property_type') and patterns.get('preferred_types'):
            most_preferred_type = max(patterns['preferred_types'], 
                                    key=patterns['preferred_types'].get)
            enhanced['property_type'] = most_preferred_type
        
        # Ajuster les fourchettes de prix basées sur l'historique
        if patterns.get('price_ranges') and not enhanced.get('price_max'):
            avg_max_price = sum(patterns['price_ranges']) / len(patterns['price_ranges'])
            enhanced['price_max'] = int(avg_max_price * 1.1)  # +10% de marge
        
        return enhanced
    
    def _apply_ml_ranking(self, properties: List[Dict[str, Any]], 
                         patterns: Dict[str, Any], 
                         user_preferences: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Applique un ranking basé sur le machine learning"""
        
        scored_properties = []
        
        for prop in properties:
            # Score de base (compatibilité avec préférences)
            base_score = prop.get('compatibility_score', 0.5)
            
            # Bonus basé sur les patterns historiques
            pattern_bonus = 0.0
            
            # Bonus si localisation correspond aux préférences historiques
            prop_location = prop.get('city', prop.get('location', ''))
            if patterns.get('preferred_locations'):
                for loc, count in patterns['preferred_locations'].items():
                    if loc.lower() in prop_location.lower():
                        pattern_bonus += (count / max(patterns['preferred_locations'].values())) * 0.2
            
            # Bonus si type correspond aux préférences historiques
            if patterns.get('preferred_types'):
                prop_type = prop.get('property_type', '')
                type_preference = patterns['preferred_types'].get(prop_type, 0)
                if type_preference > 0:
                    max_type_count = max(patterns['preferred_types'].values())
                    pattern_bonus += (type_preference / max_type_count) * 0.15
            
            # Score final
            final_score = min(1.0, base_score + pattern_bonus)
            prop['ml_score'] = final_score
            
            scored_properties.append(prop)
        
        # Trier par score ML
        return sorted(scored_properties, key=lambda x: x['ml_score'], reverse=True)
    
    def _create_user_profile(self, preferences: Dict[str, Any], 
                           favorites: List[Dict[str, Any]], 
                           patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Crée un profil utilisateur consolidé"""
        
        profile = {
            'explicit_preferences': preferences or {},
            'implicit_preferences': {},
            'behavior_patterns': patterns
        }
        
        # Analyser les favoris pour extraire les préférences implicites
        if favorites:
            favorite_types = {}
            favorite_locations = {}
            price_range = []
            
            for fav in favorites:
                # Types préférés
                prop_type = fav['property_type']
                favorite_types[prop_type] = favorite_types.get(prop_type, 0) + 1
                
                # Localisations préférées
                location = fav.get('city', fav.get('location', ''))
                favorite_locations[location] = favorite_locations.get(location, 0) + 1
                
                # Fourchette de prix
                price_range.append(fav['price'])
            
            profile['implicit_preferences'] = {
                'favorite_types': favorite_types,
                'favorite_locations': favorite_locations,
                'price_range': {
                    'min': min(price_range) if price_range else 0,
                    'max': max(price_range) if price_range else 0,
                    'avg': sum(price_range) / len(price_range) if price_range else 0
                }
            }
        
        return profile
    
    def _generate_recommendation_filters(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Génère des filtres pour les recommandations"""
        filters = {}
        
        explicit = profile.get('explicit_preferences', {})
        implicit = profile.get('implicit_preferences', {})
        
        # Budget basé sur explicite et implicite
        budget_sources = []
        if explicit.get('budget_max'):
            budget_sources.append(explicit['budget_max'])
        if implicit.get('price_range', {}).get('avg'):
            budget_sources.append(implicit['price_range']['avg'] * 1.2)  # +20% de marge
        
        if budget_sources:
            filters['price_max'] = int(max(budget_sources))
        
        # Type de propriété le plus préféré
        type_preferences = {}
        if explicit.get('property_type'):
            type_preferences[explicit['property_type']] = 10  # Poids fort
        
        if implicit.get('favorite_types'):
            for prop_type, count in implicit['favorite_types'].items():
                type_preferences[prop_type] = type_preferences.get(prop_type, 0) + count
        
        if type_preferences:
            most_preferred = max(type_preferences, key=type_preferences.get)
            filters['property_type'] = most_preferred
        
        # Autres critères explicites
        for key in ['bedrooms', 'bathrooms', 'surface_min', 'location']:
            if explicit.get(key):
                filters[key] = explicit[key]
        
        return filters
    
    def _calculate_recommendation_score(self, property_data: Dict[str, Any], 
                                      profile: Dict[str, Any]) -> float:
        """Calcule le score de recommandation d'une propriété"""
        score = 0.0
        
        explicit = profile.get('explicit_preferences', {})
        implicit = profile.get('implicit_preferences', {})
        
        # Score basé sur les préférences explicites
        if explicit:
            explicit_score = calculate_property_score(property_data, explicit)
            score += explicit_score * 0.6  # 60% du score
        
        # Score basé sur les favoris historiques
        if implicit.get('favorite_types'):
            prop_type = property_data.get('property_type', '')
            type_count = implicit['favorite_types'].get(prop_type, 0)
            max_type_count = max(implicit['favorite_types'].values()) if implicit['favorite_types'] else 1
            type_score = type_count / max_type_count
            score += type_score * 0.25  # 25% du score
        
        # Score basé sur la fourchette de prix historique
        if implicit.get('price_range', {}).get('avg'):
            avg_price = implicit['price_range']['avg']
            prop_price = property_data.get('price', 0)
            
            if avg_price > 0:
                price_diff = abs(prop_price - avg_price) / avg_price
                price_score = max(0, 1 - price_diff)  # Score inversement proportionnel à la différence
                score += price_score * 0.15  # 15% du score
        
        return min(1.0, score)
    
    def _diversify_results(self, properties: List[Dict[str, Any]], limit: int) -> List[Dict[str, Any]]:
        """Diversifie les résultats pour éviter la monotonie"""
        if len(properties) <= limit:
            return properties
        
        diversified = []
        used_types = set()
        used_locations = set()
        
        # Phase 1: Prendre les meilleurs de chaque type/localisation
        for prop in properties:
            if len(diversified) >= limit:
                break
                
            prop_type = prop.get('property_type', '')
            prop_location = prop.get('city', prop.get('location', ''))
            
            # Favoriser la diversité de types et localisations
            type_penalty = 0.1 * len([p for p in diversified if p.get('property_type') == prop_type])
            location_penalty = 0.05 * len([p for p in diversified if p.get('city') == prop_location])
            
            adjusted_score = prop.get('recommendation_score', 0) - type_penalty - location_penalty
            prop['adjusted_score'] = adjusted_score
            
            diversified.append(prop)
        
        # Phase 2: Retrier par score ajusté et prendre les meilleurs
        diversified.sort(key=lambda x: x.get('adjusted_score', 0), reverse=True)
        
        return diversified[:limit]


# Instance globale du moteur de recherche
search_engine = SmartSearchEngine()

def get_search_engine() -> SmartSearchEngine:
    """Retourne l'instance du moteur de recherche"""
    return search_engine