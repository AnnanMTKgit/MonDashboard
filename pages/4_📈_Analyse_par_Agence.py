# pages/4_📈_Analyse_par_Agence.py
import streamlit as st
from shared_code import (
    get_connection, run_query, SQLQueries, create_sidebar_filters, load_and_display_css,
    AgenceTable, stacked_chart, TempsPassage, area_graph, top_agence_freq
)

st.set_page_config(page_title="Analyse par Agence", layout="wide", page_icon="📈")
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

st.title("📈 Analyse Détaillée par Agence")

tab1, tab2, tab3 = st.tabs(["Performance par Catégorie", "Agences les Plus Lentes", "Agences les Plus Fréquentées"])

with tab1:
    st.header("Catégorisation des Temps d'Attente et d'Opération")
    chart1 = stacked_chart(df_all, 'TempsAttenteReel', 'NomAgence', "Catégorisation du Temps d'Attente")
    st.altair_chart(chart1, use_container_width=True)
    
    chart2 = stacked_chart(df_all, 'TempOperation', 'NomAgence', "Catégorisation du Temps d'Opération")
    st.altair_chart(chart2, use_container_width=True)
    
    chart3 = TempsPassage(df_all)
    st.altair_chart(chart3, use_container_width=True)

with tab2:
    st.header("Analyse des Agences les Plus Lentes")
    fig_attente, _, _, _ = area_graph(df_all, concern='NomAgence', time='TempsAttenteReel', date_to_bin='Date_Appel', seuil=15, title="Top 5 Agences les Plus Lentes en Temps d'Attente")
    st.plotly_chart(fig_attente, use_container_width=True)
    
    fig_op, _, _, _ = area_graph(df_all, concern='NomAgence', time='TempOperation', date_to_bin='Date_Fin', seuil=5, title="Top 5 Agences les Plus Lentes en Temps d'Opération")
    st.plotly_chart(fig_op, use_container_width=True)

with tab3:
    st.header("Analyse des Agences les Plus Fréquentées")
    fig1 = top_agence_freq(df_all, df_queue, title=['Total Tickets', 'Total Traités'])
    fig2 = top_agence_freq(df_all, df_queue, title=['Total Tickets', 'Total Rejetées'], color=['#00CC96', "#EF553B"])
    
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        st.plotly_chart(fig2, use_container_width=True)