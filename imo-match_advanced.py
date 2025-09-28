"""
Script de test pour la base de données ImoMatch
À lancer pour vérifier que tout fonctionne
"""
import streamlit as st
from database.manager import DatabaseManager

def test_database():
    st.title("Test Base de Données ImoMatch")
    
    # Initialiser la base
    db = DatabaseManager()
    
    # Test de connexion
    if db.test_connection():
        st.success("Connexion à la base de données réussie")
    else:
        st.error("Problème de connexion à la base de données")
        return
    
    # Ajouter des données d'exemple
    if st.button("Ajouter des données d'exemple"):
        db.add_sample_data()
        st.success("Données d'exemple ajoutées")
    
    # Afficher les propriétés
    st.subheader("Propriétés en base de données")
    
    properties = db.get_all_properties()
    
    if properties:
        st.write(f"Nombre de propriétés : {len(properties)}")
        
        for prop in properties:
            with st.expander(f"{prop['title']} - {prop['price']:,}€"):
                st.write(f"**Type :** {prop['property_type']}")
                st.write(f"**Surface :** {prop['surface']}m²")
                st.write(f"**Chambres :** {prop['bedrooms']}")
                st.write(f"**Localisation :** {prop['location']}")
                st.write(f"**Description :** {prop['description']}")
    else:
        st.warning("Aucune propriété trouvée. Cliquez sur 'Ajouter des données d'exemple'.")

if __name__ == "__main__":
    test_database()
