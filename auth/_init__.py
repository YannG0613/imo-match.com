# auth/__init__.py
"""Module d'authentification pour ImoMatch"""

try:
    from .authentication import *
except ImportError as e:
    print(f"Warning: Could not import authentication: {e}")

# Vous pouvez aussi faire des imports plus spécifiques :
# from .authentication import login_user, logout_user, create_user, verify_password
