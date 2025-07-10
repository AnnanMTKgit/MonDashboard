# pages/5_⚙️_Analyse_par_Service.py
import streamlit as st
from shared_code import *
st.markdown("<h1 style='text-align: center;'>Analyse par Service et Type d'Opération</h1>", unsafe_allow_html=True)

load_and_display_css()

if not st.session_state.get('logged_in'):
    st.error("Veuillez vous connecter pour accéder à cette page.")
    st.stop()
create_sidebar_filters()
conn = get_connection()
df_all = run_query(conn, SQLQueries().AllQueueQueries, params=(st.session_state.start_date, st.session_state.end_date))
df_queue = df_all.copy()

df_all_filtered = df_all[df_all['NomAgence'].isin(st.session_state.selected_agencies)]
df_queue_filtered = df_queue[df_queue['NomAgence'].isin(st.session_state.selected_agencies)]

if df_all_filtered.empty: 
    st.error("Aucune donnée disponible pour la sélection.")
    st.stop()


col1, col2 = st.columns(2)

with col1:
    
    fig_temps_op = GraphsGlob(df_all_filtered)
    st.plotly_chart(fig_temps_op, use_container_width=True)
    
    chart_service = stacked_service(df_all_filtered, type='NomService', concern='Type_Operation')
    st.altair_chart(chart_service, use_container_width=True)

with col2:
    
    fig_top10 = Top10_Type(df_queue_filtered)
    st.plotly_chart(fig_top10, use_container_width=True)

