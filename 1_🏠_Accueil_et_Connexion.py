# 1_🏠_Accueil_et_Connexion.py
import streamlit as st
from shared_code import get_connection, run_query, SQLQueries, load_and_display_css
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

def show_login_page():
    st.title("Connexion au Dashboard Marlodj")
    
    conn = get_connection()
   
    df_users = run_query(conn, SQLQueries().ProfilQueries)
    st.write(len(df_users))
    users_dict = dict(zip(df_users['UserName'], df_users['MotDePasse']))
    profiles_dict = dict(zip(df_users['UserName'], df_users['Profil']))

    with st.form("login_form"):
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")
        submitted = st.form_submit_button("Se connecter")

        # Dans 1_🏠_Accueil_et_Connexion.py

# ... dans la fonction show_login_page()
        if submitted:
            if users_dict.get(username) == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.user_profile = profiles_dict.get(username)

                # --- NOUVEAU : Initialisation de l'état des filtres ---
                # On le fait ici pour que ça se produise une seule fois après le login.
                if 'start_date' not in st.session_state:
                    st.session_state.start_date = datetime.now().date()
                if 'end_date' not in st.session_state:
                    st.session_state.end_date = datetime.now().date()
                if 'selected_agencies' not in st.session_state:
                    # Charger toutes les agences pour le default
                    all_agencies_df = run_query(conn, SQLQueries().AllAgences)
                    st.session_state.selected_agencies = list(all_agencies_df['NomAgence'].unique())
                # --------------------------------------------------------

                st.rerun()
            else:
                st.error("Nom d'utilisateur ou mot de passe incorrect.")

def show_agent_dashboard():
    """Dashboard spécifique pour les profils 'Caissier' ou 'Clientele'."""
    st.title(f"Bienvenue, {st.session_state.username}")
    st.header(f"Votre Dashboard - Profil : {st.session_state.user_profile}")
    
    # Ici, vous reconstruisez la logique de votre fonction 'option_agent'
    # en utilisant les fonctions de 'shared_code.py'
    st.info("Le dashboard spécifique à l'agent est en cours de construction.")
    # ... ex: appeler des fonctions pour afficher les métriques et graphiques de l'agent
    
    if st.button("Se déconnecter"):
        st.session_state.logged_in = False
        st.rerun()

# Logique principale
if not st.session_state.logged_in:
    show_login_page()
else:
    if st.session_state.user_profile in ['Caissier', 'Clientele']:
        # Masquer la navigation multi-page pour les agents
        st.set_page_config(page_title=f"Dashboard Agent - {st.session_state.username}")
        show_agent_dashboard()
    else:
        # Afficher la page d'accueil pour les Admins/Supervisors
        st.title(f"🏠 Bienvenue sur le Dashboard Marlodj, {st.session_state.username}!")
        st.header("Navigation")
        st.info("Utilisez le menu sur la gauche pour naviguer entre les différentes sections d'analyse.")
        
        # Charger la sidebar commune pour les pages d'analyse
        from shared_code import create_sidebar_filters, AgenceTable
        conn = get_connection()
        df_agences = run_query(conn, SQLQueries().AllAgences)
        create_sidebar_filters(df_agences)
        
        st.subheader("Aperçu rapide")
        st.write("Ceci est la page d'accueil. Les données et analyses détaillées se trouvent dans les pages dédiées.")