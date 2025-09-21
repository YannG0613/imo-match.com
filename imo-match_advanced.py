 # Ajoutons au prototype une couche IA simple

import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression

# -------------------------------
# Bases simulées en mémoire
# -------------------------------
if "acheteurs" not in st.session_state:
    st.session_state.acheteurs = []
if "vendeurs" not in st.session_state:
    st.session_state.vendeurs = []

# -------------------------------
# Fonction indicateurs prédictifs
# -------------------------------
def indicateurs_acheteur(acheteur, vendeur):
    # Exemple d'indicateurs simples
    prix_ok = 1 if vendeur["prix"] <= acheteur["budget"] else 0
    surf_ok = 1 if vendeur["surface"] >= acheteur["surface_min"] else 0
    loc_ok = 1 if acheteur["localisation"].lower() == vendeur["localisation"].lower() else 0
    type_ok = 1 if acheteur["type_bien"] == vendeur["type_bien"] else 0
    return [prix_ok, surf_ok, loc_ok, type_ok]

def score_transaction(acheteur, vendeur):
    X = np.array([indicateurs_acheteur(acheteur, vendeur)])
    # petit modèle ML pré-entraîné fictif
    model = LogisticRegression()
    # entraînement rapide sur données factices
    X_train = np.array([[1,1,1,1],[1,0,1,0],[0,1,1,0],[0,0,0,0]])
    y_train = [1,1,0,0]  # 1 = transaction probable, 0 = improbable
    model.fit(X_train, y_train)
    proba = model.predict_proba(X)[0][1]
    return round(proba*100, 1)

# -------------------------------
# Interface
# -------------------------------
st.title("🏡 imoMatcheeeee – Prototype IA")
mode = st.radio("Vous êtes :", ["Acquéreur / Locataire", "Vendeur / Bailleur"])

if mode == "Acquéreur / Locataire":
    st.subheader("Profil Acquéreur")
    nom = st.text_input("Nom")
    age = st.number_input("Âge", 18, 99, step=1)
    situation = st.selectbox("Situation familiale", ["Seul", "Couple", "Famille"])
    budget = st.number_input("Budget max (€)", 50000, 2000000, step=5000)
    localisation = st.text_input("Localisation souhaitée")
    type_bien = st.selectbox("Type de bien", ["Appartement", "Maison"])
    surface_min = st.number_input("Surface minimale (m²)", 10, 300, step=5)
    mode_vie = st.selectbox("Style de vie", ["Urbain", "Périurbain", "Campagne", "Télétravail"])

    if st.button("Soumettre mon profil"):
        acheteur = {
            "nom": nom,
            "age": age,
            "situation": situation,
            "budget": budget,
            "localisation": localisation,
            "type_bien": type_bien,
            "surface_min": surface_min,
            "mode_vie": mode_vie
        }
        st.session_state.acheteurs.append(acheteur)
        st.success("Profil acheteur enregistré ✅")

    if st.session_state.vendeurs:
        st.subheader("Mes recommandations IA")
        for vendeur in st.session_state.vendeurs:
            proba = score_transaction(acheteur, vendeur)
            st.write(f"🏠 {vendeur['nom_bien']} ({vendeur['localisation']}, {vendeur['surface']} m², {vendeur['prix']} €) "
                     f"→ **Probabilité de match : {proba}%**")

elif mode == "Vendeur / Bailleur":
    st.subheader("Profil Vendeur")
    nom_bien = st.text_input("Nom du bien")
    prix = st.number_input("Prix (€)", 50000, 2000000, step=5000)
    localisation = st.text_input("Localisation")
    type_bien = st.selectbox("Type de bien", ["Appartement", "Maison"])
    surface = st.number_input("Surface (m²)", 10, 300, step=5)
    cible = st.selectbox("Acheteur cible", ["Famille", "Investisseur", "Etudiant", "Sans préférence"])

    if st.button("Soumettre mon bien"):
        vendeur = {
            "nom_bien": nom_bien,
            "prix": prix,
            "localisation": localisation,
            "type_bien": type_bien,
            "surface": surface,
            "cible": cible
        }
        st.session_state.vendeurs.append(vendeur)
        st.success("Bien enregistré ✅")

    if st.session_state.acheteurs:
        st.subheader("Acheteurs potentiels")
        for acheteur in st.session_state.acheteurs:
            proba = score_transaction(acheteur, vendeur)
            st.write(f"👤 {acheteur['nom']} ({acheteur['situation']}, budget {acheteur['budget']} €) "
                     f"→ **Probabilité de match : {proba}%**")
