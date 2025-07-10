import streamlit as st

st.title(f"👋 À bientôt {st.session_state.username}! Vous êtes déconnecté.")
for key in list(st.session_state.keys()):
    del st.session_state[key]
    