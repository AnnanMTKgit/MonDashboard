# pages/4_📈_Analyse_par_Agence.py
import streamlit as st
from shared_code import *

st.set_page_config(page_title="Analyse par Agence", layout="wide", page_icon="📈")
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

if df_all_filtered.empty: st.stop()


st.title("📈 Analyse Détaillée par Agence")

tab1, tab2, tab3 = st.tabs(["Performance par Catégorie", "Agences les Plus Lentes", "Agences les Plus Fréquentées"])

with tab1:
    st.header("Catégorisation des Temps d'Attente et d'Opération")
    chart1 = stacked_chart(df_all_filtered, 'TempsAttenteReel', 'NomAgence', "Catégorisation du Temps d'Attente")
    st.altair_chart(chart1, use_container_width=True)
    
    chart2 = stacked_chart(df_all_filtered, 'TempOperation', 'NomAgence', "Catégorisation du Temps d'Opération")
    st.altair_chart(chart2, use_container_width=True)
    
    chart3 = TempsPassage(df_all_filtered)
    st.altair_chart(chart3, use_container_width=True)

with tab2:
    st.header("Analyse des Agences les Plus Lentes")
    fig_attente, _, _, _ = area_graph(df_all_filtered, concern='NomAgence', time='TempsAttenteReel', date_to_bin='Date_Appel', seuil=15, title="Top 5 Agences les Plus Lentes en Temps d'Attente")
    st.plotly_chart(fig_attente, use_container_width=True)
    
    fig_op, _, _, _ = area_graph(df_all_filtered, concern='NomAgence', time='TempOperation', date_to_bin='Date_Fin', seuil=5, title="Top 5 Agences les Plus Lentes en Temps d'Opération")
    st.plotly_chart(fig_op, use_container_width=True)

with tab3:
    st.header("Analyse des Agences les Plus Fréquentées")
    fig1 = top_agence_freq(df_all_filtered, df_queue_filtered, title=['Total Tickets', 'Total Traités'])
    fig2 = top_agence_freq(df_all_filtered, df_queue_filtered, title=['Total Tickets', 'Total Rejetées'], color=['#00CC96', "#EF553B"])
    
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        st.plotly_chart(fig2, use_container_width=True)