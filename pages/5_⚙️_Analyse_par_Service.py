# pages/5_⚙️_Analyse_par_Service.py
import streamlit as st
from shared_code import *
st.markdown("<h1 style='text-align: center;'>Analyse par Service et Type d'Opération</h1>", unsafe_allow_html=True)

st.markdown(""" <style>iframe[title="streamlit_echarts.st_echarts"]{ height: 500px !important } """, unsafe_allow_html=True)
load_and_display_css()

if not st.session_state.get('logged_in'):
    st.error("Veuillez vous connecter pour accéder à cette page.")
    st.stop()
create_sidebar_filters()
conn = get_connection()
df = run_query(conn, SQLQueries().AllQueueQueries, params=(st.session_state.start_date, st.session_state.end_date))
df_all = df[df['UserName'].notna()].reset_index(drop=True)
df_queue=df.copy()


df_all_filtered = df_all[df_all['NomAgence'].isin(st.session_state.selected_agencies)]
df_queue_filtered = df_queue[df_queue['NomAgence'].isin(st.session_state.selected_agencies)]

if df_all_filtered.empty: 
    st.error("Aucune donnée disponible pour la sélection.")
    st.stop()

tabs=st.tabs(["Temps de traitement moyen par type de service","Types de transactions les plus courantes","Top 10 Types de transactions en nombre de clients"])

with tabs[0]:
    
        
    option1 = GraphsGlob2(df_all_filtered,"Temps Moyen d'opération par Service")
    st_echarts(option1,height="600px",key="fig_temps_op")
    
with tabs[1]:
    option2 = Top10_Type(df_queue_filtered,title="Top10 des Opérations le plus courantes")
    st_echarts(option2,height="600px",key='fig_top10')
        
with tabs[2]:
    figures=analyse_activity(df_all_filtered, type='Type_Operation', concern='NomService')
    
    

    total_figures = len(figures)

    # Initialiser l'état de la session pour cet onglet spécifique
    if 'carousel_tab3_index' not in st.session_state:
        st.session_state.carousel_tab3_index = 0

    # Récupérer l'index courant
    current_index = st.session_state.carousel_tab3_index

    # S'assurer que l'index ne dépasse pas les limites (sécurité)
    if current_index >= total_figures:
        st.session_state.carousel_tab3_index = 0
        current_index = 0

    # Afficher le titre du graphique courant
    
    st.markdown("<h1 style='text-align: center;font-size:1em;'>Analyse détaillée par Service</h1>", unsafe_allow_html=True)
    # Afficher la figure courante
    st_echarts(
        options=figures[current_index],
        height="500px",
        key=f"carousel_chart_{current_index}" 
    )

    # Créer les colonnes pour la navigation
    col1, col2, col3 = st.columns([2, 1, 2])

    with col1:
        if st.button("◀️ Précédent", use_container_width=True, disabled=(current_index == 0), key="carousel_prev"):
            st.session_state.carousel_tab3_index -= 1
            st.rerun()

    with col2:
        st.markdown(
            f"<p style='text-align: center; font-weight: bold;'>Service {current_index + 1} / {total_figures}</p>", 
            unsafe_allow_html=True
        )

    with col3:
        if st.button("Suivant ▶️", use_container_width=True, disabled=(current_index >= total_figures - 1), key='carousel_next'):
            st.session_state.carousel_tab3_index += 1
            st.rerun()

    
    

