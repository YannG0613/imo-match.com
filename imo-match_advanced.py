# imomatch_app.py
import streamlit as st
import pandas as pd

# -------------------------------
# Bases de données simulées
# -------------------------------
if "acheteurs" not in st.session_state:
    st.session_state.acheteurs = []

if "vendeurs" not in st.session_state:
    st.session_state.vendeurs = []

if "pros" not in st.session_state:
    st.session_state.pros = []


# -------------------------------
# Fonction de calcul du score
# -------------------------------
def calcul_score(acheteur, vendeur):
    score = 0
    if acheteur["localisation"].lower() == vendeur["localisation"].lower():
        score += 30
    if vendeur["prix"] <= acheteur["budget"]:
        score += 30
    if acheteur["type_bien"] == vendeur["type_bien"]:
        score += 20
    if vendeur["surface"] >= acheteur["surface_min"]:
        score += 20
    return score


# -------------------------------
# Interface principale
# -------------------------------
st.title("🏡 imoMatch – Prototype")
st.markdown("### Un Demandeur, Un Logement, Une Vente")

mode = st.radio("Vous êtes :", ["Acquéreur / Locataire", "Vendeur / Bailleur", "Professionnel / Intermédiaire"])

# -------------------------------
# Formulaire Acheteur / Locataire
# -------------------------------
if mode == "Acquéreur / Locataire":
    st.subheader("Formulaire Acquéreur / Locataire")
    nom = st.text_input("Nom")
    budget = st.number_input("Budget maximum (€)", 10000, 2000000, step=1000)
    localisation = st.text_input("Localisation souhaitée")
    type_bien = st.selectbox("Type de bien recherché", ["Appartement", "Maison"])
    surface_min = st.number_input("Surface minimale (m²)", 10, 500, step=5)
    style_vie = st.text_area("Style de vie / Préférences (facultatif)")

    if st.button("Soumettre ma recherche"):
        acheteur = {
            "nom": nom,
            "budget": budget,
            "localisation": localisation,
            "type_bien": type_bien,
            "surface_min": surface_min,
            "style_vie": style_vie
        }
        st.session_state.acheteurs.append(acheteur)
        st.success("✅ Profil acheteur ajouté avec succès !")

    if st.session_state.vendeurs:
        st.subheader("🔎 Mes recommandations")
        for vendeur in st.session_state.vendeurs:
            score = calcul_score(acheteur, vendeur)
            st.write(f"🏠 {vendeur['nom_bien']} à {vendeur['localisation']} – "
                     f"Prix: {vendeur['prix']} € – Surface: {vendeur['surface']} m² – "
                     f"**Score: {score}%**")

# -------------------------------
# Formulaire Vendeur / Bailleur
# -------------------------------
elif mode == "Vendeur / Bailleur":
    st.subheader("Formulaire Vendeur / Bailleur")
    nom_bien = st.text_input("Nom du bien (ex: Appartement T3 centre-ville)")
    prix = st.number_input("Prix (€)", 10000, 2000000, step=1000)
    localisation = st.text_input("Localisation du bien")
    type_bien = st.selectbox("Type de bien", ["Appartement", "Maison"])
    surface = st.number_input("Surface (m²)", 10, 500, step=5)
    souhaits = st.text_area("Souhaits particuliers (facultatif)")

    if st.button("Soumettre mon bien"):
        vendeur = {
            "nom_bien": nom_bien,
            "prix": prix,
            "localisation": localisation,
            "type_bien": type_bien,
            "surface": surface,
            "souhaits": souhaits
        }
        st.session_state.vendeurs.append(vendeur)
        st.success("✅ Bien ajouté avec succès !")

    if st.session_state.acheteurs:
        st.subheader("🔎 Acquéreurs correspondants")
        for acheteur in st.session_state.acheteurs:
            score = calcul_score(acheteur, vendeur)
            st.write(f"👤 {acheteur['nom']} – Budget: {acheteur['budget']} € – "
                     f"Surface min: {acheteur['surface_min']} m² – "
                     f"**Score: {score}%**")

# -------------------------------
# Formulaire Professionnel
# -------------------------------
elif mode == "Professionnel / Intermédiaire":
    st.subheader("Formulaire Professionnel / Intermédiaire")
    nom = st.text_input("Nom / Agence")
    domaine = st.text_input("Domaine d’activité (transaction, location, gestion...)")
    zone = st.text_input("Zone géographique d’intervention")

    if st.button("Soumettre mon profil"):
        pro = {"nom": nom, "domaine": domaine, "zone": zone}
        st.session_state.pros.append(pro)
        st.success("✅ Profil professionnel ajouté avec succès !")

    if st.session_state.acheteurs and st.session_state.vendeurs:
        st.subheader("🔎 Transactions potentielles")
        for acheteur in st.session_state.acheteurs:
            for vendeur in st.session_state.vendeurs:
                score = calcul_score(acheteur, vendeur)
                if score >= 60:  # seuil pour afficher une transaction intéressante
                    st.write(f"👤 Acheteur {acheteur['nom']} ↔ 🏠 {vendeur['nom_bien']} "
                             f"(Score: {score}%)")
