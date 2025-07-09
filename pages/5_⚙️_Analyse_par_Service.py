# pages/5_⚙️_Analyse_par_Service.py
import streamlit as st
from shared_code import (
    get_connection, run_query, SQLQueries, create_sidebar_filters, load_and_display_css,
    GraphsGlob, stacked_service, Top10_Type
)

st.set_page_config(page_title="Analyse par Service", layout="wide", page_icon="⚙️")
load_and_display_css()

if not st.session_state.get('logged_in'):
    st.error("Veuillez vous connecter pour accéder à cette page.")
    st.stop()

# --- Chargement des données et filtres ---
conn = get_connection()
df_agences = run_query(conn, SQLQueries().AllAgences)
start_date, end_date, selected_agencies = create_sidebar_filters(df_agences)

df_all = run_query(conn, SQLQueries().AllQueueQueries, params=(start_date, end_date))
df_queue = df_all.copy()

# --- Filtrage des données ---
df_all = df_all[df_all['NomAgence'].isin(selected_agencies)]
df_queue = df_queue[df_queue['NomAgence'].isin(selected_agencies)]

if df_all.empty:
    st.warning("Aucune donnée disponible pour la période et les agences sélectionnées.")
    st.stop()

st.title("⚙️ Analyse par Service et Type d'Opération")

col1, col2 = st.columns(2)

with col1:
    st.header("Performance par Service")
    fig_temps_op = GraphsGlob(df_all)
    st.plotly_chart(fig_temps_op, use_container_width=True)
    
    chart_service = stacked_service(df_all, type='NomService', concern='Type_Operation')
    st.altair_chart(chart_service, use_container_width=True)

with col2:
    st.header("Analyse des Types d'Opérations")
    fig_top10 = Top10_Type(df_queue)
    st.plotly_chart(fig_top10, use_container_width=True)

