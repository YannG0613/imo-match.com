# database/__init__.py
from .manager import DatabaseManager

# Instance globale pour faciliter l'utilisation
db_manager = DatabaseManager()
