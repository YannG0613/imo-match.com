"""
Agent IA conversationnel pour ImoMatch
"""
import logging
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from config.settings import OPENAI_CONFIG, PROPERTY_TYPES
from database.manager import get_database
from utils.helpers import parse_search_query, calculate_property_score

logger = logging.getLogger(__name__)

class ImoMatchAI:
    """Agent IA conversationnel pour l'assistance immobilière"""
    
    def __init__(self):
        self.db = get_database()
        self.conversation_context = {}
        self.user_profiles = {}
        
        # Templates de réponses
        self.response_templates = {
            'greeting': [
                "Bonjour ! Je suis votre assistant IA immobilier. Comment puis-je vous aider dans votre recherche ?",
                "Salut ! Prêt(e) à trouver le bien immobilier de vos rêves ? Je suis là pour vous accompagner !",
                "Hello ! En quoi puis-je vous aider pour votre projet immobilier ?"
            ],
            'search_help': [
                "Je peux vous aider à affiner votre recherche. Quel type de bien vous intéresse ?",
                "Dites-moi vos critères : budget, localisation, type de bien... Je m'occupe du reste !",
                "Décrivez-moi votre bien idéal, je vais vous trouver les meilleures options !"
            ],
            'budget_advice': [
                "Pour votre budget, je recommande de prévoir 10% supplémentaires pour les frais.",
                "Avec ce budget, vous avez plusieurs options intéressantes. Voulez-vous que je vous montre ?",
                "Votre budget est réaliste pour cette zone. Je peux vous proposer des biens correspondants."
            ]
        }
    
    def process_message(self, user_id: int, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Traite un message utilisateur et génère une réponse
        
        Args:
            user_id: ID de l'utilisateur
            message: Message de l'utilisateur
            context: Contexte de la conversation
            
        Returns:
            Dict contenant la réponse et les actions suggérées
        """
        try:
            # Mettre à jour le contexte utilisateur
            self._update_user_context(user_id, message, context)
            
            # Analyser l'intention du message
            intent = self._analyze_intent(message)
            
            # Générer la réponse selon l'intention
            response = self._generate_response(user_id, message, intent, context)
            
            # Suggérer des actions
            suggested_actions = self._suggest_actions(user_id, intent, context)
            
            # Log de l'interaction
            self._log_interaction(user_id, message, response, intent)
            
            return {
                'response': response,
                'intent': intent,
                'suggested_actions': suggested_actions,
                'context_updated': True
            }
            
        except Exception as e:
            logger.error(f"Erreur traitement message IA: {e}")
            return {
                'response': "Désolé, je rencontre un problème technique. Pouvez-vous reformuler votre question ?",
                'intent': 'error',
                'suggested_actions': [],
                'context_updated': False
            }
    
    def get_property_recommendations(self, user_id: int, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Génère des recommandations de propriétés personnalisées
        
        Args:
            user_id: ID de l'utilisateur
            context: Contexte de conversation
            
        Returns:
            Liste des propriétés recommandées avec explications
        """
        try:
            # Récupérer le profil utilisateur
            user_preferences = self.db.get_user_preferences(user_id)
            user_context = self.user_profiles.get(user_id, {})
            
            # Construire les critères de recherche
            search_criteria = self._build_search_criteria(user_preferences, user_context, context)
            
            # Rechercher des propriétés
            properties = self.db.search_properties(search_criteria)
            
            # Évaluer et expliquer chaque propriété
            explained_properties = []
            
            for prop in properties:
                explanation = self._explain_recommendation(prop, user_preferences, user_context)
                
                explained_properties.append({
                    'property': prop,
                    'recommendation_score': calculate_property_score(prop, user_preferences or {}),
                    'explanation': explanation,
                    'pros': self._extract_pros(prop, user_preferences),
                    'cons': self._extract_cons(prop, user_preferences)
                })
            
            # Trier par score de recommandation
            explained_properties.sort(key=lambda x: x['recommendation_score'], reverse=True)
            
            return explained_properties[:5]  # Top 5
            
        except Exception as e:
            logger.error(f"Erreur recommandations IA: {e}")
            return []
    
    def analyze_property_match(self, property_id: int, user_id: int) -> Dict[str, Any]:
        """
        Analyse la compatibilité entre une propriété et un utilisateur
        
        Args:
            property_id: ID de la propriété
            user_id: ID de l'utilisateur
            
        Returns:
            Analyse détaillée de la compatibilité
        """
        try:
            # Récupérer la propriété et les préférences
            property_data = self.db.get_property_by_id(property_id)
            user_preferences = self.db.get_user_preferences(user_id)
            
            if not property_data:
                return {'error': 'Propriété introuvable'}
            
            # Calculer le score de compatibilité
            compatibility_score = calculate_property_score(property_data, user_preferences or {})
            
            # Analyser chaque critère
            criteria_analysis = self._analyze_criteria_match(property_data, user_preferences)
            
            # Générer un résumé IA
            ai_summary = self._generate_property_summary(property_data, compatibility_score, criteria_analysis)
            
            # Suggérer des améliorations ou alternatives
            suggestions = self._suggest_property_improvements(property_data, user_preferences)
            
            return {
                'compatibility_score': compatibility_score,
                'score_category': self._categorize_score(compatibility_score),
                'criteria_analysis': criteria_analysis,
                'ai_summary': ai_summary,
                'suggestions': suggestions,
                'decision_factors': self._identify_decision_factors(property_data, user_preferences)
            }
            
        except Exception as e:
            logger.error(f"Erreur analyse compatibilité: {e}")
            return {'error': 'Erreur lors de l\'analyse'}
    
    def get_market_insights(self, location: str = None, user_id: int = None) -> Dict[str, Any]:
        """
        Fournit des insights sur le marché immobilier
        
        Args:
            location: Localisation à analyser
            user_id: ID de l'utilisateur pour personnaliser
            
        Returns:
            Insights de marché personnalisés
        """
        try:
            # Récupérer les données de marché
            from search.engine import get_search_engine
            search_engine = get_search_engine()
            
            market_stats = search_engine.get_market_stats(location)
            market_trends = search_engine.get_market_trends(location)
            
            # Personnaliser selon l'utilisateur
            if user_id:
                user_preferences = self.db.get_user_preferences(user_id)
                personalized_insights = self._personalize_market_insights(
                    market_stats, market_trends, user_preferences
                )
            else:
                personalized_insights = self._generate_general_insights(market_stats, market_trends)
            
            return {
                'market_stats': market_stats,
                'trends': market_trends,
                'insights': personalized_insights,
                'recommendations': self._generate_market_recommendations(market_trends, user_id),
                'timing_advice': self._generate_timing_advice(market_trends)
            }
            
        except Exception as e:
            logger.error(f"Erreur insights marché: {e}")
            return {'error': 'Impossible d\'analyser le marché actuellement'}
    
    def chat_about_property(self, property_id: int, user_question: str, user_id: int) -> str:
        """
        Répond à des questions spécifiques sur une propriété
        
        Args:
            property_id: ID de la propriété
            user_question: Question de l'utilisateur
            user_id: ID de l'utilisateur
            
        Returns:
            Réponse détaillée sur la propriété
        """
        try:
            property_data = self.db.get_property_by_id(property_id)
            if not property_data:
                return "Désolé, je ne trouve pas cette propriété."
            
            # Analyser la question pour identifier le sujet
            question_intent = self._analyze_property_question(user_question)
            
            # Générer une réponse contextuelle
            response = self._generate_property_response(
                property_data, user_question, question_intent, user_id
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Erreur chat propriété: {e}")
            return "Je rencontre un problème pour répondre à votre question. Pouvez-vous la reformuler ?"
    
    # === MÉTHODES PRIVÉES ===
    
    def _update_user_context(self, user_id: int, message: str, context: Dict[str, Any] = None):
        """Met à jour le contexte utilisateur"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                'messages': [],
                'preferences_mentioned': {},
                'search_intent': None,
                'last_interaction': None
            }
        
        profile = self.user_profiles[user_id]
        profile['messages'].append({
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'context': context
        })
        
        # Garder seulement les 10 derniers messages
        profile['messages'] = profile['messages'][-10:]
        
        # Extraire les préférences mentionnées
        mentioned_prefs = self._extract_preferences_from_message(message)
        profile['preferences_mentioned'].update(mentioned_prefs)
        
        profile['last_interaction'] = datetime.now().isoformat()
    
    def _analyze_intent(self, message: str) -> str:
        """Analyse l'intention du message utilisateur"""
        message_lower = message.lower()
        
        # Intentions de salutation
        if any(word in message_lower for word in ['bonjour', 'salut', 'hello', 'bonsoir']):
            return 'greeting'
        
        # Intentions de recherche
        if any(word in message_lower for word in ['cherche', 'recherche', 'trouve', 'veux', 'besoin']):
            return 'search'
        
        # Intentions de questions sur budget
        if any(word in message_lower for word in ['budget', 'prix', 'coût', 'combien', 'cher']):
            return 'budget'
        
        # Intentions de questions sur localisation
        if any(word in message_lower for word in ['où', 'quartier', 'zone', 'localisation', 'secteur']):
            return 'location'
        
        # Intentions de questions sur caractéristiques
        if any(word in message_lower for word in ['chambre', 'pièce', 'surface', 'm²', 'garage', 'jardin']):
            return 'features'
        
        # Intentions de conseils
        if any(word in message_lower for word in ['conseil', 'recommande', 'suggère', 'aide']):
            return 'advice'
        
        # Intention de comparaison
        if any(word in message_lower for word in ['compare', 'différence', 'mieux', 'versus']):
            return 'comparison'
        
        # Intention de feedback
        if any(word in message_lower for word in ['merci', 'parfait', 'bien', 'excellent', 'nul', 'mauvais']):
            return 'feedback'
        
        return 'general'
    
    def _generate_response(self, user_id: int, message: str, intent: str, context: Dict[str, Any] = None) -> str:
        """Génère une réponse selon l'intention"""
        
        if intent == 'greeting':
            return self._get_random_template('greeting')
        
        elif intent == 'search':
            return self._handle_search_intent(user_id, message, context)
        
        elif intent == 'budget':
            return self._handle_budget_intent(user_id, message, context)
        
        elif intent == 'location':
            return self._handle_location_intent(user_id, message, context)
        
        elif intent == 'features':
            return self._handle_features_intent(user_id, message, context)
        
        elif intent == 'advice':
            return self._handle_advice_intent(user_id, message, context)
        
        elif intent == 'comparison':
            return self._handle_comparison_intent(user_id, message, context)
        
        elif intent == 'feedback':
            return self._handle_feedback_intent(user_id, message, context)
        
        else:
            return self._handle_general_intent(user_id, message, context)
    
    def _handle_search_intent(self, user_id: int, message: str, context: Dict[str, Any] = None) -> str:
        """Gère les intentions de recherche"""
        # Extraire les critères du message
        criteria = parse_search_query(message)
        
        if criteria:
            criteria_text = []
            if criteria.get('property_type'):
                criteria_text.append(f"type: {criteria['property_type']}")
            if criteria.get('location'):
                criteria_text.append(f"à {criteria['location']}")
            if criteria.get('price_max'):
                criteria_text.append(f"jusqu'à {criteria['price_max']:,}€")
            if criteria.get('bedrooms'):
                criteria_text.append(f"au moins {criteria['bedrooms']} chambres")
            
            if criteria_text:
                return f"Je comprends que vous cherchez un bien avec les critères suivants: {', '.join(criteria_text)}. Voulez-vous que je lance une recherche avec ces critères ?"
        
        return "Pour vous aider dans votre recherche, pouvez-vous me préciser : le type de bien, votre budget, et la localisation souhaitée ?"
    
    def _handle_budget_intent(self, user_id: int, message: str, context: Dict[str, Any] = None) -> str:
        """Gère les questions sur le budget"""
        # Extraire le budget mentionné
        budget_match = re.search(r'(\d+(?:\s?\d+)*)\s*(?:€|euros?|k€)', message)
        
        if budget_match:
            budget_str = budget_match.group(1).replace(' ', '')
            budget = int(budget_str)
            
            if 'k€' in budget_match.group(0):
                budget *= 1000
            
            # Conseils selon le budget
            if budget < 200000:
                return f"Avec un budget de {budget:,}€, je vous conseille de regarder les studios et petits appartements, ou d'élargir votre zone de recherche aux villes périphériques."
            elif budget < 500000:
                return f"Votre budget de {budget:,}€ vous permet d'accéder à de beaux appartements 2-3 pièces ou petites maisons selon la localisation."
            elif budget < 1000000:
                return f"Avec {budget:,}€, vous avez accès à de très belles propriétés : appartements spacieux, maisons avec jardin, voire des villas selon la zone."
            else:
                return f"Votre budget de {budget:,}€ vous ouvre toutes les possibilités ! Vous pouvez viser des propriétés d'exception avec vue mer, grandes villas, ou biens d'investissement."
        
        return "Pour vous donner des conseils sur le budget, pouvez-vous me dire quelle somme vous souhaitez investir ?"
    
    def _handle_location_intent(self, user_id: int, message: str, context: Dict[str, Any] = None) -> str:
        """Gère les questions sur la localisation"""
        # Villes connues de la Côte d'Azur
        cities_mentioned = []
        known_cities = ['antibes', 'cannes', 'nice', 'monaco', 'juan-les-pins', 'grasse', 'valbonne', 'mougins']
        
        for city in known_cities:
            if city in message.lower():
                cities_mentioned.append(city.title())
        
        if cities_mentioned:
            city = cities_mentioned[0]
            return self._get_city_advice(city)
        
        return "Pour vous conseiller sur la localisation, dites-moi quelles villes vous intéressent ou quels sont vos critères (proximité plage, centre-ville, transports...) ?"
    
    def _get_city_advice(self, city: str) -> str:
        """Donne des conseils spécifiques à une ville"""
        city_advice = {
            'Antibes': "Antibes offre un parfait équilibre entre charme historique et modernité. Le Vieil Antibes est idéal pour l'authenticité, Juan-les-Pins pour la proximité des plages.",
            'Cannes': "Cannes est réputée pour son prestige et ses plages. Le centre-ville est animé, la Croisette luxueuse. Attention aux prix élevés pendant le Festival.",
            'Nice': "Nice combine vie culturelle riche et climat méditerranéen. Vieux Nice pour le charme, Cimiez pour la tranquillité, le port pour la modernité.",
            'Monaco': "Monaco offre sécurité et prestations d'exception mais les prix sont très élevés. Idéal pour l'investissement de prestige.",
            'Grasse': "Grasse propose un excellent rapport qualité-prix avec l'avantage de l'arrière-pays tout en restant proche de la côte."
        }
        
        return city_advice.get(city, f"{city} est une excellente région pour investir dans l'immobilier. Voulez-vous des informations spécifiques sur cette zone ?")
    
    def _handle_advice_intent(self, user_id: int, message: str, context: Dict[str, Any] = None) -> str:
        """Gère les demandes de conseils"""
        user_preferences = self.db.get_user_preferences(user_id)
        
        if user_preferences:
            advice_parts = []
            
            # Conseils sur le budget
            if user_preferences.get('budget_max'):
                budget = user_preferences['budget_max']
                advice_parts.append(f"Avec votre budget de {budget:,}€, pensez à prévoir 10% supplémentaires pour les frais de notaire et d'agence.")
            
            # Conseils sur la localisation
            if user_preferences.get('location'):
                location = user_preferences['location']
                advice_parts.append(f"Pour {location}, je recommande de visiter à différents moments (jour/soir, semaine/weekend) pour bien évaluer l'environnement.")
            
            # Conseils généraux
            advice_parts.append("N'hésitez pas à négocier le prix, surtout si le bien est sur le marché depuis longtemps.")
            
            return " ".join(advice_parts)
        
        return "Voici mes conseils généraux : définissez clairement vos critères, visitez plusieurs biens pour comparer, et n'hésitez pas à faire une contre-offre. Voulez-vous des conseils plus spécifiques ?"
    
    def _suggest_actions(self, user_id: int, intent: str, context: Dict[str, Any] = None) -> List[Dict[str, str]]:
        """Suggère des actions à l'utilisateur"""
        actions = []
        
        if intent == 'search':
            actions.extend([
                {'type': 'search', 'label': '🔍 Lancer la recherche', 'action': 'start_search'},
                {'type': 'preferences', 'label': '⚙️ Définir mes préférences', 'action': 'set_preferences'}
            ])
        
        elif intent == 'budget':
            actions.extend([
                {'type': 'calculator', 'label': '🧮 Calculer ma capacité d\'emprunt', 'action': 'loan_calculator'},
                {'type': 'market', 'label': '📊 Voir les prix du marché', 'action': 'market_stats'}
            ])
        
        elif intent == 'location':
            actions.extend([
                {'type': 'map', 'label': '🗺️ Explorer sur la carte', 'action': 'show_map'},
                {'type': 'comparison', 'label': '⚖️ Comparer les quartiers', 'action': 'compare_areas'}
            ])
        
        elif intent == 'advice':
            actions.extend([
                {'type': 'recommendations', 'label': '💡 Voir mes recommandations', 'action': 'show_recommendations'},
                {'type': 'checklist', 'label': '✅ Checklist achat immobilier', 'action': 'show_checklist'}
            ])
        
        # Actions génériques toujours disponibles
        actions.extend([
            {'type': 'favorites', 'label': '❤️ Mes favoris', 'action': 'show_favorites'},
            {'type': 'help', 'label': '❓ Plus d\'aide', 'action': 'show_help'}
        ])
        
        return actions
    
    def _extract_preferences_from_message(self, message: str) -> Dict[str, Any]:
        """Extrait les préférences mentionnées dans le message"""
        preferences = {}
        message_lower = message.lower()
        
        # Budget
        budget_match = re.search(r'(\d+(?:\s?\d+)*)\s*(?:€|euros?|k€)', message)
        if budget_match:
            budget = int(budget_match.group(1).replace(' ', ''))
            if 'k€' in budget_match.group(0):
                budget *= 1000
            preferences['budget_max'] = budget
        
        # Type de propriété
        for prop_type in PROPERTY_TYPES:
            if prop_type.lower() in message_lower:
                preferences['property_type'] = prop_type
                break
        
        # Nombre de chambres
        bedrooms_match = re.search(r'(\d+)\s*(?:chambres?|ch\.?)', message_lower)
        if bedrooms_match:
            preferences['bedrooms'] = int(bedrooms_match.group(1))
        
        # Surface
        surface_match = re.search(r'(\d+)\s*m[²2]', message_lower)
        if surface_match:
            preferences['surface_min'] = int(surface_match.group(1))
        
        return preferences
    
    def _build_search_criteria(self, user_preferences: Dict[str, Any], 
                              user_context: Dict[str, Any], 
                              context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Construit les critères de recherche depuis les préférences et le contexte"""
        criteria = {}
        
        # Préférences explicites
        if user_preferences:
            criteria.update({
                'price_min': user_preferences.get('budget_min'),
                'price_max': user_preferences.get('budget_max'),
                'property_type': user_preferences.get('property_type'),
                'bedrooms': user_preferences.get('bedrooms'),
                'bathrooms': user_preferences.get('bathrooms'),
                'surface_min': user_preferences.get('surface_min'),
                'location': user_preferences.get('location')
            })
        
        # Préférences déduites du contexte
        context_prefs = user_context.get('preferences_mentioned', {})
        for key, value in context_prefs.items():
            if key not in criteria or criteria[key] is None:
                criteria[key] = value
        
        # Nettoyer les valeurs None
        criteria = {k: v for k, v in criteria.items() if v is not None}
        
        return criteria
    
    def _explain_recommendation(self, property_data: Dict[str, Any], 
                               user_preferences: Dict[str, Any], 
                               user_context: Dict[str, Any]) -> str:
        """Explique pourquoi une propriété est recommandée"""
        explanations = []
        
        # Correspondance budget
        if user_preferences and user_preferences.get('budget_max'):
            budget = user_preferences['budget_max']
            price = property_data.get('price', 0)
            if price <= budget:
                if price <= budget * 0.9:
                    explanations.append("Prix attractif par rapport à votre budget")
                else:
                    explanations.append("Dans votre budget")
        
        # Correspondance type
        if user_preferences and user_preferences.get('property_type'):
            if property_data.get('property_type') == user_preferences['property_type']:
                explanations.append("Correspond exactement à votre type de bien recherché")
        
        # Correspondance localisation
        if user_preferences and user_preferences.get('location'):
            user_location = user_preferences['location'].lower()
            prop_location = property_data.get('location', '').lower()
            if user_location in prop_location:
                explanations.append("Localisation parfaite selon vos préférences")
        
        # Caractéristiques attractives
        features = property_data.get('features', [])
        attractive_features = ['Piscine', 'Vue mer', 'Garage', 'Jardin', 'Terrasse']
        found_features = [f for f in features if f in attractive_features]
        if found_features:
            explanations.append(f"Équipements de qualité : {', '.join(found_features[:2])}")
        
        if not explanations:
            explanations.append("Propriété intéressante selon vos critères généraux")
        
        return ". ".join(explanations) + "."
    
    def _extract_pros(self, property_data: Dict[str, Any], user_preferences: Dict[str, Any]) -> List[str]:
        """Extrait les points positifs d'une propriété"""
        pros = []
        
        # Prix compétitif
        if user_preferences and user_preferences.get('budget_max'):
            if property_data.get('price', 0) <= user_preferences['budget_max'] * 0.85:
                pros.append("Prix très attractif")
        
        # Grande surface
        surface = property_data.get('surface', 0)
        if surface >= 100:
            pros.append("Grande surface")
        
        # Équipements premium
        features = property_data.get('features', [])
        premium_features = ['Piscine', 'Vue mer', 'Garage', 'Jardin', 'Terrasse', 'Climatisation']
        found_premium = [f for f in features if f in premium_features]
        if found_premium:
            pros.extend(found_premium[:3])
        
        # Localisation prisée
        location = property_data.get('location', '').lower()
        prime_areas = ['centre', 'plage', 'mer', 'port']
        if any(area in location for area in prime_areas):
            pros.append("Localisation privilégiée")
        
        return pros[:4]  # Maximum 4 pros
    
    def _extract_cons(self, property_data: Dict[str, Any], user_preferences: Dict[str, Any]) -> List[str]:
        """Extrait les points négatifs potentiels d'une propriété"""
        cons = []
        
        # Prix élevé
        if user_preferences and user_preferences.get('budget_max'):
            if property_data.get('price', 0) > user_preferences['budget_max'] * 0.95:
                cons.append("Prix proche de votre budget maximum")
        
        # Surface limitée
        surface = property_data.get('surface', 0)
        if surface > 0 and surface < 50:
            cons.append("Surface relativement petite")
        
        # Manque d'équipements
        features = property_data.get('features', [])
        if len(features) < 3:
            cons.append("Équipements limités")
        
        # Étage élevé sans ascenseur (simulé)
        # Dans une vraie impl, avoir ces infos en BDD
        
        return cons[:3]  # Maximum 3 cons
    
    def _get_random_template(self, template_type: str) -> str:
        """Retourne un template aléatoire"""
        import random
        templates = self.response_templates.get(template_type, ["Je peux vous aider !"])
        return random.choice(templates)
    
    def _log_interaction(self, user_id: int, message: str, response: str, intent: str):
        """Log l'interaction pour l'amélioration de l'IA"""
        log_entry = {
            'user_id': user_id,
            'message': message,
            'response': response,
            'intent': intent,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"AI Interaction: {json.dumps(log_entry)}")
        
        # Dans une vraie implémentation, sauvegarder en base pour entraînement
    
    def _handle_general_intent(self, user_id: int, message: str, context: Dict[str, Any] = None) -> str:
        """Gère les intentions générales"""
        return "Je suis là pour vous aider dans votre recherche immobilière. Vous pouvez me poser des questions sur les biens, les prix, les quartiers, ou me dire ce que vous recherchez !"
    
    def _handle_comparison_intent(self, user_id: int, message: str, context: Dict[str, Any] = None) -> str:
        """Gère les demandes de comparaison"""
        return "Pour comparer des biens, vous pouvez me donner les IDs des propriétés ou me décrire les options que vous hésitez. Je vous aiderai à analyser les avantages et inconvénients de chacune."
    
    def _handle_features_intent(self, user_id: int, message: str, context: Dict[str, Any] = None) -> str:
        """Gère les questions sur les caractéristiques"""
        return "Pour les caractéristiques des biens, je peux vous expliquer l'importance de chaque critère : nombre de pièces, surface, exposition, équipements... Que voulez-vous savoir précisément ?"
    
    def _handle_feedback_intent(self, user_id: int, message: str, context: Dict[str, Any] = None) -> str:
        """Gère le feedback utilisateur"""
        if any(word in message.lower() for word in ['merci', 'parfait', 'bien', 'excellent']):
            return "Je suis ravi de vous avoir aidé ! N'hésitez pas si vous avez d'autres questions."
        else:
            return "Je suis désolé si ma réponse ne vous convenait pas. Pouvez-vous me dire comment je peux mieux vous aider ?"


# Instance globale de l'agent IA
ai_agent = ImoMatchAI()

def get_ai_agent() -> ImoMatchAI:
    """Retourne l'instance de l'agent IA"""
    return ai_agent
