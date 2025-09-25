"""Module footer pour ImoMatch"""
import streamlit as st

def show_footer():
    """Affiche le footer de l'application"""
    st.markdown("---")
    
    # Footer avec colonnes
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("### Support")
        st.markdown("- [Contact](mailto:contact@imomatch.fr)")
        st.markdown("- [FAQ](#)")
        st.markdown("- [Aide](#)")
    
    with col2:
        st.markdown("### Documentation")
        st.markdown("- [Guide d'utilisation](#)")
        st.markdown("- [API](#)")
        st.markdown("- [Développeurs](#)")
    
    with col3:
        st.markdown("### Légal")
        st.markdown("- [CGU](#)")
        st.markdown("- [Confidentialité](#)")
        st.markdown("- [Cookies](#)")
    
    with col4:
        st.markdown("### À propos")
        st.markdown("- [Notre équipe](#)")
        st.markdown("- [Carrières](#)")
        st.markdown("- [Blog](#)")
    
    # Copyright
    st.markdown("""
    <div style='text-align: center; margin-top: 2rem; padding: 1rem; background-color: #f0f2f6; border-radius: 10px;'>
        <p style='margin: 0; opacity: 0.8; font-size: 0.9rem;'>
            © 2024 ImoMatch. Tous droits réservés.
        </p>
        <p style='margin: 0.5rem 0 0 0; opacity: 0.6; font-size: 0.8rem;'>
            Fait en France avec ❤️ pour l'immobilier
        </p>
    </div>
    """, unsafe_allow_html=True)
