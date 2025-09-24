"""
Gestionnaire de base de données pour ImoMatch
"""
import sqlite3
import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
import logging
from contextlib import contextmanager

from config.settings import DATABASE_CONFIG, DEBUG

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gestionnaire principal de la base de données"""
    
    def __init__(self, db_path: str = "imomatch.db"):
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager pour les connexions à la base de données"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row  # Pour accéder aux colonnes par nom
        try:
            yield conn
        except Exception as e:
            conn.rollback()
            logger.error(f"Erreur base de données: {e}")
            raise
        finally:
            conn.close()
    
    def init_database(self):
        """Initialise la base de données avec toutes les tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Table des utilisateurs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    phone TEXT,
                    age INTEGER,
                    profession TEXT,
                    plan TEXT DEFAULT 'free',
                    trial_end_date TEXT,
                    searches_this_month INTEGER DEFAULT 0,
                    last_search_reset TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table des préférences utilisateur
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    budget_min INTEGER,
                    budget_max INTEGER,
                    property_type TEXT,
                    bedrooms INTEGER,
                    bathrooms INTEGER,
                    surface_min INTEGER,
                    location TEXT,
                    criteria TEXT,  -- JSON
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Table des propriétés
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS properties (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    price INTEGER NOT NULL,
                    property_type TEXT NOT NULL,
                    bedrooms INTEGER,
                    bathrooms INTEGER,
                    surface INTEGER,
                    location TEXT NOT NULL,
                    latitude REAL,
                    longitude REAL,
                    description TEXT,
                    features TEXT,  -- JSON
                    images TEXT,    -- JSON (URLs)
                    agent_contact TEXT,
                    is_available BOOLEAN DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table des favoris
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_favorites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    property_id INTEGER NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (property_id) REFERENCES properties (id),
                    UNIQUE(user_id, property_id)
                )
            ''')
            
            # Table des recherches sauvegardées
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS saved_searches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    filters TEXT NOT NULL,  -- JSON
                    alert_enabled BOOLEAN DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Table des sessions (pour l'authentification)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    session_token TEXT UNIQUE NOT NULL,
                    expires_at TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            conn.commit()
            logger.info("Base de données initialisée avec succès")
    
    # === GESTION DES UTILISATEURS ===
    
    def create_user(self, email: str, password: str, first_name: str, 
                   last_name: str, **kwargs) -> Optional[int]:
        """Crée un nouvel utilisateur"""
        password_hash = self._hash_password(password)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO users (email, password_hash, first_name, last_name, 
                                     phone, age, profession, plan)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    email, password_hash, first_name, last_name,
                    kwargs.get('phone'), kwargs.get('age'), 
                    kwargs.get('profession'), kwargs.get('plan', 'free')
                ))
                conn.commit()
                user_id = cursor.lastrowid
                logger.info(f"Utilisateur créé avec ID: {user_id}")
                return user_id
            except sqlite3.IntegrityError:
                logger.warning(f"Email déjà existant: {email}")
                return None
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authentifie un utilisateur"""
        password_hash = self._hash_password(password)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM users 
                WHERE email = ? AND password_hash = ?
            ''', (email, password_hash))
            
            user = cursor.fetchone()
            return dict(user) if user else None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Récupère un utilisateur par son ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            user = cursor.fetchone()
            return dict(user) if user else None
    
    def update_user(self, user_id: int, **kwargs) -> bool:
        """Met à jour les informations d'un utilisateur"""
        if not kwargs:
            return False
            
        # Construction de la requête dynamique
        set_clause = ', '.join([f"{key} = ?" for key in kwargs.keys()])
        set_clause += ', updated_at = ?'
        
        values = list(kwargs.values()) + [datetime.now().isoformat(), user_id]
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                UPDATE users 
                SET {set_clause}
                WHERE id = ?
            ''', values)
            conn.commit()
            return cursor.rowcount > 0
    
    # === GESTION DES PRÉFÉRENCES ===
    
    def save_user_preferences(self, user_id: int, preferences: Dict[str, Any]) -> bool:
        """Sauvegarde les préférences utilisateur"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Vérifier si des préférences existent déjà
            cursor.execute('SELECT id FROM user_preferences WHERE user_id = ?', (user_id,))
            existing = cursor.fetchone()
            
            if existing:
                # Mise à jour
                cursor.execute('''
                    UPDATE user_preferences 
                    SET budget_min = ?, budget_max = ?, property_type = ?,
                        bedrooms = ?, bathrooms = ?, surface_min = ?,
                        location = ?, criteria = ?, updated_at = ?
                    WHERE user_id = ?
                ''', (
                    preferences.get('budget_min'),
                    preferences.get('budget_max'),
                    preferences.get('property_type'),
                    preferences.get('bedrooms'),
                    preferences.get('bathrooms'),
                    preferences.get('surface_min'),
                    preferences.get('location'),
                    json.dumps(preferences.get('criteria', {})),
                    datetime.now().isoformat(),
                    user_id
                ))
            else:
                # Création
                cursor.execute('''
                    INSERT INTO user_preferences 
                    (user_id, budget_min, budget_max, property_type, bedrooms,
                     bathrooms, surface_min, location, criteria)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    preferences.get('budget_min'),
                    preferences.get('budget_max'),
                    preferences.get('property_type'),
                    preferences.get('bedrooms'),
                    preferences.get('bathrooms'),
                    preferences.get('surface_min'),
                    preferences.get('location'),
                    json.dumps(preferences.get('criteria', {}))
                ))
            
            conn.commit()
            return True
    
    def get_user_preferences(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Récupère les préférences utilisateur"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM user_preferences WHERE user_id = ?', (user_id,))
            prefs = cursor.fetchone()
            
            if prefs:
                prefs_dict = dict(prefs)
                if prefs_dict.get('criteria'):
                    prefs_dict['criteria'] = json.loads(prefs_dict['criteria'])
                return prefs_dict
            return None
    
    # === GESTION DES PROPRIÉTÉS ===
    
    def add_property(self, property_data: Dict[str, Any]) -> int:
        """Ajoute une nouvelle propriété"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO properties 
                (title, price, property_type, bedrooms, bathrooms, surface,
                 location, latitude, longitude, description, features, images, agent_contact)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                property_data['title'],
                property_data['price'],
                property_data['property_type'],
                property_data.get('bedrooms'),
                property_data.get('bathrooms'),
                property_data.get('surface'),
                property_data['location'],
                property_data.get('latitude'),
                property_data.get('longitude'),
                property_data.get('description'),
                json.dumps(property_data.get('features', [])),
                json.dumps(property_data.get('images', [])),
                property_data.get('agent_contact')
            ))
            conn.commit()
            return cursor.lastrowid
    
    def search_properties(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Recherche des propriétés selon les filtres"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM properties WHERE is_available = 1"
            params = []
            
            # Application des filtres
            if filters.get('price_min'):
                query += " AND price >= ?"
                params.append(filters['price_min'])
            
            if filters.get('price_max'):
                query += " AND price <= ?"
                params.append(filters['price_max'])
            
            if filters.get('property_type'):
                query += " AND property_type = ?"
                params.append(filters['property_type'])
            
            if filters.get('bedrooms'):
                query += " AND bedrooms >= ?"
                params.append(filters['bedrooms'])
            
            if filters.get('bathrooms'):
                query += " AND bathrooms >= ?"
                params.append(filters['bathrooms'])
            
            if filters.get('surface_min'):
                query += " AND surface >= ?"
                params.append(filters['surface_min'])
            
            if filters.get('location'):
                query += " AND location LIKE ?"
                params.append(f"%{filters['location']}%")
            
            query += " ORDER BY created_at DESC"
            
            if filters.get('limit'):
                query += " LIMIT ?"
                params.append(filters['limit'])
            
            cursor.execute(query, params)
            properties = cursor.fetchall()
            
            result = []
            for prop in properties:
                prop_dict = dict(prop)
                if prop_dict.get('features'):
                    prop_dict['features'] = json.loads(prop_dict['features'])
                if prop_dict.get('images'):
                    prop_dict['images'] = json.loads(prop_dict['images'])
                result.append(prop_dict)
            
            return result
    
    def get_property_by_id(self, property_id: int) -> Optional[Dict[str, Any]]:
        """Récupère une propriété par son ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM properties WHERE id = ?', (property_id,))
            prop = cursor.fetchone()
            
            if prop:
                prop_dict = dict(prop)
                if prop_dict.get('features'):
                    prop_dict['features'] = json.loads(prop_dict['features'])
                if prop_dict.get('images'):
                    prop_dict['images'] = json.loads(prop_dict['images'])
                return prop_dict
            return None
    
    # === GESTION DES FAVORIS ===
    
    def add_to_favorites(self, user_id: int, property_id: int) -> bool:
        """Ajoute une propriété aux favoris"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO user_favorites (user_id, property_id)
                    VALUES (?, ?)
                ''', (user_id, property_id))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                # Déjà en favoris
                return False
    
    def remove_from_favorites(self, user_id: int, property_id: int) -> bool:
        """Retire une propriété des favoris"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM user_favorites 
                WHERE user_id = ? AND property_id = ?
            ''', (user_id, property_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_user_favorites(self, user_id: int) -> List[Dict[str, Any]]:
        """Récupère les favoris d'un utilisateur"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.* FROM properties p
                INNER JOIN user_favorites uf ON p.id = uf.property_id
                WHERE uf.user_id = ?
                ORDER BY uf.created_at DESC
            ''', (user_id,))
            
            properties = cursor.fetchall()
            result = []
            for prop in properties:
                prop_dict = dict(prop)
                if prop_dict.get('features'):
                    prop_dict['features'] = json.loads(prop_dict['features'])
                if prop_dict.get('images'):
                    prop_dict['images'] = json.loads(prop_dict['images'])
                result.append(prop_dict)
            
            return result
    
    def is_favorite(self, user_id: int, property_id: int) -> bool:
        """Vérifie si une propriété est en favoris"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 1 FROM user_favorites 
                WHERE user_id = ? AND property_id = ?
            ''', (user_id, property_id))
            return cursor.fetchone() is not None
    
    # === GESTION DES RECHERCHES SAUVEGARDÉES ===
    
    def save_search(self, user_id: int, name: str, filters: Dict[str, Any], 
                   alert_enabled: bool = False) -> int:
        """Sauvegarde une recherche"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO saved_searches (user_id, name, filters, alert_enabled)
                VALUES (?, ?, ?, ?)
            ''', (user_id, name, json.dumps(filters), alert_enabled))
            conn.commit()
            return cursor.lastrowid
    
    def get_saved_searches(self, user_id: int) -> List[Dict[str, Any]]:
        """Récupère les recherches sauvegardées d'un utilisateur"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM saved_searches 
                WHERE user_id = ? 
                ORDER BY created_at DESC
            ''', (user_id,))
            
            searches = cursor.fetchall()
            result = []
            for search in searches:
                search_dict = dict(search)
                search_dict['filters'] = json.loads(search_dict['filters'])
                result.append(search_dict)
            
            return result
    
    def delete_saved_search(self, user_id: int, search_id: int) -> bool:
        """Supprime une recherche sauvegardée"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM saved_searches 
                WHERE id = ? AND user_id = ?
            ''', (search_id, user_id))
            conn.commit()
            return cursor.rowcount > 0
    
    # === GESTION DES LIMITES DE RECHERCHE ===
    
    def can_user_search(self, user_id: int) -> Tuple[bool, int]:
        """Vérifie si l'utilisateur peut effectuer une recherche"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False, 0
        
        # Les utilisateurs premium/pro ont des recherches illimitées
        if user['plan'] in ['premium', 'professional']:
            return True, -1
        
        # Pour les utilisateurs gratuits, vérifier les limites mensuelles
        now = datetime.now()
        last_reset = user.get('last_search_reset')
        
        # Réinitialiser le compteur si on est dans un nouveau mois
        if not last_reset or datetime.fromisoformat(last_reset).month != now.month:
            self.reset_monthly_searches(user_id)
            return True, 4  # 4 recherches restantes après cette utilisation
        
        searches_used = user.get('searches_this_month', 0)
        from config.settings import PLANS
        max_searches = PLANS['free']['searches_per_month']
        
        if searches_used >= max_searches:
            return False, 0
        
        return True, max_searches - searches_used - 1
    
    def increment_search_count(self, user_id: int):
        """Incrémente le compteur de recherches pour un utilisateur"""
        now = datetime.now()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users 
                SET searches_this_month = searches_this_month + 1,
                    last_search_reset = ?
                WHERE id = ?
            ''', (now.isoformat(), user_id))
            conn.commit()
    
    def reset_monthly_searches(self, user_id: int):
        """Réinitialise le compteur mensuel de recherches"""
        now = datetime.now()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users 
                SET searches_this_month = 0,
                    last_search_reset = ?
                WHERE id = ?
            ''', (now.isoformat(), user_id))
            conn.commit()
    
    # === MÉTHODES UTILITAIRES ===
    
    def _hash_password(self, password: str) -> str:
        """Hache un mot de passe avec SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Récupère des statistiques générales"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Nombre total d'utilisateurs
            cursor.execute('SELECT COUNT(*) FROM users')
            total_users = cursor.fetchone()[0]
            
            # Nombre total de propriétés
            cursor.execute('SELECT COUNT(*) FROM properties WHERE is_available = 1')
            total_properties = cursor.fetchone()[0]
            
            # Répartition par plan
            cursor.execute('''
                SELECT plan, COUNT(*) as count 
                FROM users 
                GROUP BY plan
            ''')
            plan_distribution = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Prix moyen des propriétés
            cursor.execute('SELECT AVG(price) FROM properties WHERE is_available = 1')
            avg_price = cursor.fetchone()[0] or 0
            
            # Types de propriétés les plus populaires
            cursor.execute('''
                SELECT property_type, COUNT(*) as count 
                FROM properties 
                WHERE is_available = 1 
                GROUP BY property_type 
                ORDER BY count DESC 
                LIMIT 5
            ''')
            popular_types = [{'type': row[0], 'count': row[1]} for row in cursor.fetchall()]
            
            return {
                'total_users': total_users,
                'total_properties': total_properties,
                'plan_distribution': plan_distribution,
                'average_price': round(avg_price, 2),
                'popular_property_types': popular_types
            }
    
    def cleanup_expired_sessions(self):
        """Nettoie les sessions expirées"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM user_sessions 
                WHERE expires_at < ?
            ''', (datetime.now().isoformat(),))
            conn.commit()
            logger.info(f"Supprimé {cursor.rowcount} sessions expirées")
    
    def backup_database(self, backup_path: str = None) -> str:
        """Crée une sauvegarde de la base de données"""
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"backup_imomatch_{timestamp}.db"
        
        with self.get_connection() as source:
            backup = sqlite3.connect(backup_path)
            source.backup(backup)
            backup.close()
        
        logger.info(f"Sauvegarde créée: {backup_path}")
        return backup_path


# Singleton pour l'instance de base de données
_db_instance = None

def get_database() -> DatabaseManager:
    """Retourne l'instance singleton de la base de données"""
    global _db_instance
    if _db_instance is None:
        from config.settings import get_database_url
        _db_instance = DatabaseManager(get_database_url())
    return _db_instance
