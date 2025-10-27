# pages/4_📈_Analyse_par_Agence.py
import streamlit as st
from shared_code import *

# Mettre le minuteur en place dès le début de la page
setup_auto_refresh(interval_minutes=10)



st.markdown("<h1 style='text-align: center;'>Analyse Détaillée par Agence</h1>", unsafe_allow_html=True)
st.markdown(""" <style>iframe[title="streamlit_echarts.st_echarts"]{ height: 500px !important } """, unsafe_allow_html=True)
load_and_display_css()

if not st.session_state.get('logged_in'):
    st.error("Veuillez vous connecter pour accéder à cette page.")
    st.stop()

create_sidebar_filters()

# Utiliser les données partagées au lieu de recharger
df = st.session_state.df_main
df_all = df[df['UserName'].notna()].reset_index(drop=True)
df_queue = df.copy()

df_all_filtered = df_all[df_all['NomAgence'].isin(st.session_state.selected_agencies)]
df_queue_filtered = df_queue[df_queue['NomAgence'].isin(st.session_state.selected_agencies)]

if df_all_filtered.empty: 
    st.error("Aucune donnée disponible pour la sélection.")
    st.stop()



# --- 1. Configuration des onglets et de l'état de session ---
TABS = ["Performance par Catégorie", "Agences les Plus Lentes", "Agences les Plus Fréquentées"]

if 'active_tab_index' not in st.session_state:
    st.session_state.active_tab_index = 0
if 'current_stack' not in st.session_state: # Carrousel de l'onglet 1
    st.session_state.current_stack = 0
if 'current_area' not in st.session_state: # Carrousel de l'onglet 2
    st.session_state.current_area = 0

# --- 2. Préparation des figures pour chaque onglet ---
# Il est préférable de définir les figures avant la logique d'affichage
# pour que la logique de défilement finale connaisse le nombre total de figures.

# Figures pour l'onglet 1
figures_tab1 = [
    stacked_chart2(df_all_filtered, 'TempsAttenteReel', 'NomAgence', "Catégorisation du Temps d'Attente"),
    stacked_chart2(df_all_filtered, 'TempOperation', 'NomAgence', "Catégorisation du Temps d'Opération")
]
total_figures_tab1 = len(figures_tab1)

# Figures pour l'onglet 2
figures_tab2 = [
    area_graph2(df_all_filtered, concern='NomAgence', time='TempsAttenteReel', date_to_bin='Date_Appel', seuil=15, title="Top 5 des Agences les Plus Lentes en Temps d'Attente"),
    area_graph2(df_all_filtered, concern='NomAgence', time='TempOperation', date_to_bin='Date_Fin', seuil=5, title="Top 5 des Agences les Plus Lentes en Temps d'Opération")
]
total_figures_tab2 = len(figures_tab2)

# --- 3. Affichage du menu de navigation (remplace st.tabs) ---
selected_tab = option_menu(
    menu_title=None,
    options=TABS,
    icons=['bar-chart-line', 'speedometer2', 'people-fill'], # Icônes pour chaque onglet
    orientation="horizontal",
    default_index=st.session_state.active_tab_index, # Contrôle l'onglet actif
    styles={
        "container": {"padding": "0!important", "background-color": "#fafafa", "border-bottom": "1px solid #ddd"},
        "icon": {"color": "#6c757d", "font-size": "18px"}, 
        "nav-link": {"font-size": "16px", "text-align": "center", "margin":"0px", "--hover-color": "#eee"},
        # Le style que vous aviez dans votre image (ligne rouge sous l'onglet actif)
        "nav-link-selected": {"background-color": "transparent", "color": "#e74c3c", "border-bottom": "3px solid #e74c3c"},
    }
)

# --- 4. Affichage du contenu de l'onglet sélectionné ---
if selected_tab == TABS[0]:
    stack_index = st.session_state.current_stack
    st_echarts(options=figures_tab1[stack_index], height="500px", key=f"stack_{stack_index}")

    col1, col2, col3 = st.columns([2, 1, 2])
    with col1:
        if st.button("◀️ Précédent", use_container_width=True, disabled=(stack_index == 0), key="stack_prev"):
            st.session_state.current_stack -= 1
            st.rerun()
    with col2:
        st.markdown(f"<p style='text-align: center; font-weight: bold;'>Figure {stack_index + 1} / {total_figures_tab1}</p>", unsafe_allow_html=True)
    with col3:
        if st.button("Suivant ▶️", use_container_width=True, disabled=(stack_index >= total_figures_tab1 - 1), key="stack_next"):
            st.session_state.current_stack += 1
            st.rerun()

elif selected_tab == TABS[1]:
    area_index = st.session_state.current_area
    st_echarts(options=figures_tab2[area_index], height="500px", key=f"area_{area_index}")

    col1, col2, col3 = st.columns([2, 1, 2])
    with col1:
        if st.button("◀️ Précédent", use_container_width=True, disabled=(area_index == 0), key="area_prev"):
            st.session_state.current_area -= 1
            st.rerun()
    with col2:
        st.markdown(f"<p style='text-align: center; font-weight: bold;'>Figure {area_index + 1} / {total_figures_tab2}</p>", unsafe_allow_html=True)
    with col3:
        if st.button("Suivant ▶️", use_container_width=True, disabled=(area_index >= total_figures_tab2 - 1), key='area_next'):
            st.session_state.current_area += 1
            st.rerun()

elif selected_tab == TABS[2]:
    fig1 = top_agence_freq(df_all_filtered, df_queue_filtered, title=['Total Tickets', 'Total Traités'])
    fig2 = top_agence_freq(df_all_filtered, df_queue_filtered, title=['Total Tickets', 'Total Rejetées'], color=[green_color, blue_color])
    
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        st.plotly_chart(fig2, use_container_width=True)

