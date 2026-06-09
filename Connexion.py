# 1_🏠_Accueil_et_Connexion.py
import streamlit as st
from shared_code import *
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Accueil - Marlodj Dashboard",
    page_icon="🏠",
    layout="wide"
)






load_and_display_css()

# Initialisation de l'état de session
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.user_profile = None
    st.session_state.df_RH=None
    st.session_state.all_agencies=None
    

def initialize_filters():
    all_agencies_df = load_agencies_from_api()
    st.session_state.start_date = datetime.now().date()
    st.session_state.end_date = datetime.now().date()
    st.session_state.selected_agencies = list(all_agencies_df['NomAgence'].unique())



def show_login_page():
    st.title("Connexion au Dashboard Marlodj")

    with st.form("login_form"):
        email    = st.text_input("Email")
        password = st.text_input("Mot de passe", type="password")
        submitted = st.form_submit_button("Se connecter")

        if submitted:
            try:
                resp = requests.post(
                    _API_LOGIN_URL,
                    json={"email": email, "password": password},
                    verify=False, timeout=10,
                )
                if resp.status_code == 200:
                    data  = resp.json()
                    user  = data.get("user", {})
                    role  = user.get("role", "").lower()
                    st.session_state.logged_in    = True
                    st.session_state.username     = user.get("name", email)
                    st.session_state.api_token    = data.get("token", "")
                    st.session_state.user_profile = (
                        "Admin" if role in ("admin", "super_admin", "superadmin") else "Caissier"
                    )
                    initialize_filters()
                    st.rerun()
                else:
                    st.error("Email ou mot de passe incorrect.")
            except Exception as e:
                st.error(f"Erreur de connexion à l'API : {e}")

# Main logic

def show_agent_dashboard():
    """Dashboard spécifique pour les profils 'Caissier' ou 'Clientele'."""
    st.sidebar.title(f"Bienvenue, {st.session_state.username}")
    st.sidebar.header(f"Votre Dashboard - Profil : {st.session_state.user_profile}")
    
    df_queue=st.session_state.df.copy()
    username=st.session_state.username
    df_all_service=df_queue.query('UserName==@username')

    if df_all_service.empty:
        st.warning(f"L'agent {username} n'a de données pour la période sélectionnée.")
        st.stop()
    else:
        service=df_all_service["NomService"].iloc[0]
        df_queue_service=df_queue.query('NomService==@service')
        option_agent(df_all_service,df_queue_service)
    if st.sidebar.button("Se déconnecter"):
        st.session_state.logged_in = False
        st.rerun()

# Logique principale
if not st.session_state.logged_in:
    show_login_page()
else:

    
                
    if st.session_state.user_profile in ['Caissier', 'Clientele']:
        # Masquer la navigation multi-page pour les agents
        create_sidebar_filters()
        st.set_page_config(page_title=f"Dashboard Agent - {st.session_state.username}")
        show_agent_dashboard()
    else:
        
        #st.sidebar.info(f"{st.session_state.username}")
        st.title(f"Bienvenue sur le Dashboard Marlodj, {st.session_state.username}!")
        st.info("Utilisez le menu sur la gauche pour naviguer entre les différentes sections d'analyse.")