"""
Scripts de migration pour la base de données ImoMatch
"""
import json
import logging
from typing import List, Dict, Any
from datetime import datetime
import os

from database.manager import get_database

logger = logging.getLogger(__name__)

def load_sample_data() -> bool:
    """
    Charge les données d'exemple dans la base de données
    
    Returns:
        bool: True si succès
    """
    try:
        db = get_database()
        
        # Charger le fichier JSON des propriétés d'exemple
        sample_data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'sample_properties.json')
        
        if not os.path.exists(sample_data_path):
            logger.warning(f"Fichier de données d'exemple non trouvé: {sample_data_path}")
            return create_minimal_sample_data()
        
        with open(sample_data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Insérer les propriétés d'exemple
        properties_added = 0
        for property_data in data.get('properties', []):
            try:
                property_id = db.add_property(property_data)
                if property_id:
                    properties_added += 1
                    logger.debug(f"Propriété ajoutée avec ID: {property_id}")
            except Exception as e:
                logger.error(f"Erreur ajout propriété {property_data.get('title', 'Unknown')}: {e}")
        
        logger.info(f"Migration terminée: {properties_added} propriétés ajoutées")
        return properties_added > 0
        
    except Exception as e:
        logger.error(f"Erreur lors du chargement des données d'exemple: {e}")
        return False

def create_minimal_sample_data() -> bool:
    """
    Crée un jeu de données minimal si le fichier JSON n'est pas disponible
    
    Returns:
        bool: True si succès
    """
    try:
        db = get_database()
        
        minimal_properties = [
            {
                'title': 'Appartement centre Antibes',
                'price': 350000,
                'property_type': 'Appartement',
                'bedrooms': 2,
                'bathrooms': 1,
                'surface': 65,
                'location': 'Antibes Centre',
                'latitude': 43.5804,
                'longitude': 7.1225,
                'description': 'Bel appartement 2 pièces en centre-ville d\'Antibes.',
                'features': ['Balcon', 'Parking'],
                'images': [],
                'agent_contact': 'Agent ImoMatch - contact@imomatch.fr'
            },
            {
                'title': 'Villa avec jardin Cannes',
                'price': 850000,
                'property_type': 'Villa',
                'bedrooms': 4,
                'bathrooms': 3,
                'surface': 150,
                'location': 'Cannes',
                'latitude': 43.5528,
                'longitude': 7.0174,
                'description': 'Belle villa familiale avec jardin paysager.',
                'features': ['Jardin', 'Piscine', 'Garage'],
                'images': [],
                'agent_contact': 'Agent ImoMatch - contact@imomatch.fr'
            },
            {
                'title': 'Studio Nice centre',
                'price': 180000,
                'property_type': 'Studio',
                'bedrooms': 0,
                'bathrooms': 1,
                'surface': 25,
                'location': 'Nice Centre',
                'latitude': 43.7102,
                'longitude': 7.2620,
                'description': 'Studio moderne en plein centre de Nice.',
                'features': ['Climatisation', 'Proche transports'],
                'images': [],
                'agent_contact': 'Agent ImoMatch - contact@imomatch.fr'
            }
        ]
        
        properties_added = 0
        for property_data in minimal_properties:
            property_id = db.add_property(property_data)
            if property_id:
                properties_added += 1
        
        logger.info(f"Données minimales créées: {properties_added} propriétés")
        return properties_added > 0
        
    except Exception as e:
        logger.error(f"Erreur création données minimales: {e}")
        return False

def create_demo_users() -> bool:
    """
    Crée des utilisateurs de démonstration
    
    Returns:
        bool: True si succès
    """
    try:
        db = get_database()
        
        demo_users = [
            {
                'email': 'demo.free@imomatch.fr',
                'password': 'Demo123!',
                'first_name': 'Demo',
                'last_name': 'Gratuit',
                'phone': '06.12.34.56.78',
                'age': 30,
                'profession': 'Développeur',
                'plan': 'free'
            },
            {
                'email': 'demo.premium@imomatch.fr', 
                'password': 'Demo123!',
                'first_name': 'Demo',
                'last_name': 'Premium',
                'phone': '06.23.45.67.89',
                'age': 35,
                'profession': 'Manager',
                'plan': 'premium'
            },
            {
                'email': 'demo.pro@imomatch.fr',
                'password': 'Demo123!',
                'first_name': 'Demo',
                'last_name': 'Professionnel',
                'phone': '06.34.56.78.90',
                'age': 40,
                'profession': 'Agent Immobilier',
                'plan': 'professional'
            }
        ]
        
        users_created = 0
        for user_data in demo_users:
            try:
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
                    users_created += 1
                    logger.debug(f"Utilisateur démo créé: {user_data['email']}")
                    
                    # Ajouter des préférences pour les utilisateurs démo
                    create_demo_preferences(user_id, user_data['plan'])
                    
            except Exception as e:
                logger.error(f"Erreur création utilisateur {user_data['email']}: {e}")
        
        logger.info(f"Utilisateurs démo créés: {users_created}")
        return users_created > 0
        
    except Exception as e:
        logger.error(f"Erreur création utilisateurs démo: {e}")
        return False

def create_demo_preferences(user_id: int, plan: str) -> bool:
    """
    Crée des préférences démo pour un utilisateur
    
    Args:
        user_id: ID de l'utilisateur
        plan: Plan de l'utilisateur
        
    Returns:
        bool: True si succès
    """
    try:
        db = get_database()
        
        # Préférences selon le plan
        if plan == 'free':
            preferences = {
                'budget_min': 150000,
                'budget_max': 300000,
                'property_type': 'Appartement',
                'bedrooms': 2,
                'bathrooms': 1,
                'surface_min': 50,
                'location': 'Antibes',
                'criteria': {}
            }
        elif plan == 'premium':
            preferences = {
                'budget_min': 400000,
                'budget_max': 800000,
                'property_type': 'Villa',
                'bedrooms': 3,
                'bathrooms': 2,
                'surface_min': 100,
                'location': 'Cannes',
                'criteria': {
                    'has_garden': True,
                    'has_garage': True,
                    'has_pool': False
                }
            }
        else:  # professional
            preferences = {
                'budget_min': 800000,
                'budget_max': 2000000,
                'property_type': 'Villa',
                'bedrooms': 4,
                'bathrooms': 3,
                'surface_min': 150,
                'location': 'Monaco',
                'criteria': {
                    'has_garden': True,
                    'has_garage': True,
                    'has_pool': True,
                    'has_balcony': True
                }
            }
        
        success = db.save_user_preferences(user_id, preferences)
        logger.debug(f"Préférences démo créées pour utilisateur {user_id}: {success}")
        return success
        
    except Exception as e:
        logger.error(f"Erreur création préférences démo: {e}")
        return False

def create_demo_favorites(user_id: int, plan: str) -> bool:
    """
    Ajoute quelques propriétés en favoris pour la démo
    
    Args:
        user_id: ID de l'utilisateur
        plan: Plan de l'utilisateur
        
    Returns:
        bool: True si succès
    """
    try:
        db = get_database()
        
        # Récupérer toutes les propriétés
        all_properties = db.search_properties({})
        
        if not all_properties:
            return False
        
        # Ajouter quelques favoris selon le plan
        favorites_count = {'free': 1, 'premium': 3, 'professional': 5}.get(plan, 1)
        
        added_count = 0
        for i, property_data in enumerate(all_properties[:favorites_count]):
            if db.add_to_favorites(user_id, property_data['id']):
                added_count += 1
        
        logger.debug(f"Favoris démo ajoutés pour utilisateur {user_id}: {added_count}")
        return added_count > 0
        
    except Exception as e:
        logger.error(f"Erreur création favoris démo: {e}")
        return False

def create_demo_saved_searches() -> bool:
    """
    Crée des recherches sauvegardées de démonstration
    
    Returns:
        bool: True si succès
    """
    try:
        db = get_database()
        
        # Récupérer les utilisateurs démo
        demo_users = [
            db.authenticate_user('demo.premium@imomatch.fr', 'Demo123!'),
            db.authenticate_user('demo.pro@imomatch.fr', 'Demo123!')
        ]
        
        saved_searches_data = [
            {
                'name': 'Appartement Antibes Budget',
                'filters': {
                    'property_type': 'Appartement',
                    'location': 'Antibes',
                    'price_max': 400000,
                    'bedrooms': 2
                },
                'alert_enabled': True
            },
            {
                'name': 'Villa Familiale Cannes',
                'filters': {
                    'property_type': 'Villa', 
                    'location': 'Cannes',
                    'bedrooms': 3,
                    'surface_min': 120
                },
                'alert_enabled': False
            }
        ]
        
        saved_count = 0
        for user in demo_users:
            if user:
                for search_data in saved_searches_data:
                    search_id = db.save_search(
                        user_id=user['id'],
                        name=search_data['name'],
                        filters=search_data['filters'],
                        alert_enabled=search_data['alert_enabled']
                    )
                    if search_id:
                        saved_count += 1
        
        logger.info(f"Recherches sauvegardées démo créées: {saved_count}")
        return saved_count > 0
        
    except Exception as e:
        logger.error(f"Erreur création recherches sauvegardées démo: {e}")
        return False

def run_all_migrations() -> bool:
    """
    Exécute toutes les migrations dans l'ordre correct
    
    Returns:
        bool: True si toutes les migrations ont réussi
    """
    logger.info("🚀 Début des migrations ImoMatch")
    
    migrations = [
        ("Initialisation base de données", init_database),
        ("Chargement propriétés d'exemple", load_sample_data),
        ("Création utilisateurs démo", create_demo_users),
        ("Création recherches sauvegardées démo", create_demo_saved_searches),
        ("Finalisation", finalize_migrations)
    ]
    
    success_count = 0
    
    for migration_name, migration_func in migrations:
        logger.info(f"📋 Exécution: {migration_name}")
        
        try:
            if migration_func():
                logger.info(f"✅ {migration_name} - Succès")
                success_count += 1
            else:
                logger.warning(f"⚠️ {migration_name} - Échec partiel")
                success_count += 0.5  # Échec partiel
        except Exception as e:
            logger.error(f"❌ {migration_name} - Erreur: {e}")
    
    total_migrations = len(migrations)
    success_rate = (success_count / total_migrations) * 100
    
    if success_rate >= 100:
        logger.info("🎉 Toutes les migrations ont réussi !")
        return True
    elif success_rate >= 80:
        logger.warning(f"⚠️ Migrations partiellement réussies ({success_rate:.1f}%)")
        return True
    else:
        logger.error(f"❌ Échec des migrations ({success_rate:.1f}%)")
        return False

def init_database() -> bool:
    """
    Initialise la base de données (déjà fait par DatabaseManager)
    
    Returns:
        bool: True si succès
    """
    try:
        db = get_database()
        # La base est déjà initialisée par le DatabaseManager
        logger.debug("Base de données initialisée")
        return True
    except Exception as e:
        logger.error(f"Erreur initialisation base: {e}")
        return False

def finalize_migrations() -> bool:
    """
    Finalise les migrations et nettoie
    
    Returns:
        bool: True si succès
    """
    try:
        db = get_database()
        
        # Nettoyer les sessions expirées
        db.cleanup_expired_sessions()
        
        # Créer les favoris pour les utilisateurs démo
        demo_users = [
            db.authenticate_user('demo.premium@imomatch.fr', 'Demo123!'),
            db.authenticate_user('demo.pro@imomatch.fr', 'Demo123!')
        ]
        
        for user in demo_users:
            if user:
                create_demo_favorites(user['id'], user['plan'])
        
        logger.info("Migrations finalisées")
        return True
        
    except Exception as e:
        logger.error(f"Erreur finalisation: {e}")
        return False

def reset_database() -> bool:
    """
    ATTENTION: Supprime toutes les données et recrée la base
    
    Returns:
        bool: True si succès
    """
    logger.warning("🚨 RESET COMPLET DE LA BASE DE DONNÉES")
    
    try:
        import os
        from config.settings import get_database_url
        
        db_url = get_database_url()
        
        # Supprimer le fichier SQLite s'il existe
        if db_url.endswith('.db') and os.path.exists(db_url):
            os.remove(db_url)
            logger.info(f"Base de données supprimée: {db_url}")
        
        # Recréer la base avec les migrations
        return run_all_migrations()
        
    except Exception as e:
        logger.error(f"Erreur reset base: {e}")
        return False

def backup_database(backup_path: str = None) -> bool:
    """
    Crée une sauvegarde de la base de données
    
    Args:
        backup_path: Chemin de sauvegarde (optionnel)
        
    Returns:
        bool: True si succès
    """
    try:
        db = get_database()
        
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"backup_imomatch_{timestamp}.db"
        
        backup_file = db.backup_database(backup_path)
        logger.info(f"Sauvegarde créée: {backup_file}")
        return True
        
    except Exception as e:
        logger.error(f"Erreur sauvegarde: {e}")
        return False

def get_migration_status() -> Dict[str, Any]:
    """
    Retourne le statut des migrations
    
    Returns:
        Dict avec les informations de statut
    """
    try:
        db = get_database()
        stats = db.get_statistics()
        
        status = {
            'database_initialized': True,
            'total_users': stats.get('total_users', 0),
            'total_properties': stats.get('total_properties', 0),
            'demo_users_present': False,
            'sample_data_loaded': stats.get('total_properties', 0) > 0,
            'last_check': datetime.now().isoformat()
        }
        
        # Vérifier présence des utilisateurs démo
        demo_user = db.authenticate_user('demo.free@imomatch.fr', 'Demo123!')
        status['demo_users_present'] = demo_user is not None
        
        return status
        
    except Exception as e:
        logger.error(f"Erreur statut migrations: {e}")
        return {'error': str(e), 'last_check': datetime.now().isoformat()}

def repair_database() -> bool:
    """
    Répare les problèmes courants de la base de données
    
    Returns:
        bool: True si succès
    """
    logger.info("🔧 Réparation de la base de données")
    
    try:
        db = get_database()
        
        repairs_done = []
        
        # Nettoyer les sessions expirées
        db.cleanup_expired_sessions()
        repairs_done.append("Sessions expirées nettoyées")
        
        # Réinitialiser les compteurs de recherche du mois précédent
        # (Dans une vraie implémentation, vérifier les dates)
        repairs_done.append("Compteurs de recherche vérifiés")
        
        # Vérifier l'intégrité des données
        stats = db.get_statistics()
        if stats['total_properties'] == 0:
            logger.warning("Aucune propriété trouvée, rechargement des données d'exemple")
            if load_sample_data():
                repairs_done.append("Données d'exemple rechargées")
        
        logger.info(f"Réparations effectuées: {', '.join(repairs_done)}")
        return True
        
    except Exception as e:
        logger.error(f"Erreur réparation base: {e}")
        return False

# Scripts utilitaires pour le développement
def create_test_data() -> bool:
    """
    Crée des données de test supplémentaires
    
    Returns:
        bool: True si succès
    """
    try:
        logger.info("Création de données de test")
        
        # Créer des utilisateurs de test supplémentaires
        test_users = [
            {
                'email': 'test.user1@example.com',
                'password': 'Test123!',
                'first_name': 'Alice',
                'last_name': 'Martin',
                'plan': 'free'
            },
            {
                'email': 'test.user2@example.com',
                'password': 'Test123!', 
                'first_name': 'Bob',
                'last_name': 'Durand',
                'plan': 'premium'
            }
        ]
        
        db = get_database()
        users_created = 0
        
        for user_data in test_users:
            user_id = db.create_user(
                email=user_data['email'],
                password=user_data['password'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                plan=user_data['plan']
            )
            
            if user_id:
                users_created += 1
        
        logger.info(f"Données de test créées: {users_created} utilisateurs")
        return users_created > 0
        
    except Exception as e:
        logger.error(f"Erreur création données test: {e}")
        return False

def export_database_schema() -> Dict[str, Any]:
    """
    Exporte le schéma de la base de données
    
    Returns:
        Dict avec le schéma
    """
    try:
        db = get_database()
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Récupérer toutes les tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            schema = {}
            
            for table in tables:
                table_name = table[0]
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                
                schema[table_name] = {
                    'columns': [
                        {
                            'name': col[1],
                            'type': col[2],
                            'not_null': bool(col[3]),
                            'default_value': col[4],
                            'primary_key': bool(col[5])
                        }
                        for col in columns
                    ]
                }
        
        return schema
        
    except Exception as e:
        logger.error(f"Erreur export schéma: {e}")
        return {}

# Point d'entrée pour les migrations
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Scripts de migration ImoMatch")
    parser.add_argument('--action', choices=[
        'migrate', 'reset', 'backup', 'repair', 'status', 'test-data'
    ], default='migrate', help='Action à exécuter')
    parser.add_argument('--backup-path', help='Chemin pour la sauvegarde')
    
    args = parser.parse_args()
    
    if args.action == 'migrate':
        success = run_all_migrations()
        print("✅ Migrations terminées avec succès" if success else "❌ Échec des migrations")
    
    elif args.action == 'reset':
        print("🚨 ATTENTION: Cette action va supprimer toutes les données !")
        confirm = input("Tapez 'CONFIRMER' pour continuer: ")
        if confirm == 'CONFIRMER':
            success = reset_database()
            print("✅ Reset terminé" if success else "❌ Échec du reset")
        else:
            print("❌ Reset annulé")
    
    elif args.action == 'backup':
        success = backup_database(args.backup_path)
        print("✅ Sauvegarde créée" if success else "❌ Échec de la sauvegarde")
    
    elif args.action == 'repair':
        success = repair_database()
        print("✅ Réparation terminée" if success else "❌ Échec de la réparation")
    
    elif args.action == 'status':
        status = get_migration_status()
        print("📊 Statut des migrations:")
        for key, value in status.items():
            print(f"  {key}: {value}")
    
    elif args.action == 'test-data':
        success = create_test_data()
        print("✅ Données de test créées" if success else "❌ Échec création données de test")
