import streamlit as st

def show_footer():
    footer = """
    <div style="border-top: 1px solid rgba(255,255,255,0.2); padding-top: 1rem; margin-top: 1rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; max-width: 800px; margin: 0 auto;">
            <div>
                <div style="font-weight: bold; margin-bottom: 0.5rem;">ImoMatch v1.0.0</div>
                <div style="opacity: 0.8; font-size: 0.9rem;">
                    © 2024 YannG0613. Tous droits réservés.
                </div>
            </div>
            <div style="text-align: right;">
                <div style="margin-bottom: 0.5rem;">🇫🇷 Fait en France</div>
                <div style="opacity: 0.8; font-size: 0.8rem;">
                    Avec ❤️ pour l'immobilier
                </div>
            </div>
        </div>
    </div>
    """
    st.markdown(footer, unsafe_allow_html=True)