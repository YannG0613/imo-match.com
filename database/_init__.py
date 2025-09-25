# database/__init__.py
"""Module de gestion de base de données pour ImoMatch"""

try:
    from .manager import *
except ImportError as e:
    print(f"Warning: Could not import manager: {e}")

try:
    from .migrations import *
except ImportError as e:
    print(f"Warning: Could not import migrations: {e}")

# Vous pouvez aussi faire des imports plus spécifiques selon vos besoins :
# from .manager import DatabaseManager, get_connection
# from .migrations import run_migrations
