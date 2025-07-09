# pages/6_🧑‍💼_Performance_Agent.py
import streamlit as st
from shared_code import (
    get_connection, run_query, SQLQueries, create_sidebar_filters, load_and_display_css,
    stacked_chart, stacked_agent, plot_line_chart, Graphs_pie, Graphs_bar
)

st.set_page_config(page_title="Performance Agent", layout="wide", page_icon="🧑‍💼")
load_and_display_css()

if not st.session_state.get('logged_in'):
    st.error("Veuillez vous connecter pour accéder à cette page.")
    st.stop()

# --- Chargement des données et filtres globaux ---
conn = get_connection()
df_agences = run_query(conn, SQLQueries().AllAgences)
start_date, end_date, selected_agencies = create_sidebar_filters(df_agences)

df_all_raw = run_query(conn, SQLQueries().AllQueueQueries, params=(start_date, end_date))
df_all = df_all_raw[df_all_raw['NomAgence'].isin(selected_agencies)]
df_all = df_all[df_all['UserName'].notna()].reset_index(drop=True)

if df_all.empty:
    st.warning("Aucun agent n'a de données pour la période et les agences sélectionnées.")
    st.stop()

st.title("🧑‍💼 Performance des Agents")

# --- Filtres spécifiques à la page ---
st.subheader("Filtres d'Analyse")
col_filter1, col_filter2 = st.columns(2)

with col_filter1:
    selected_services = st.multiselect(
        'Filtrer par Services',
        options=df_all['NomService'].unique(),
        default=list(df_all['NomService'].unique())
    )

df_filtered_by_service = df_all[df_all['NomService'].isin(selected_services)]

with col_filter2:
    selected_users = st.multiselect(
        'Filtrer par Agents',
        options=df_filtered_by_service['UserName'].unique(),
        default=list(df_filtered_by_service['UserName'].unique())
    )

# --- DataFrame final pour les visualisations ---
df_selection = df_filtered_by_service[df_filtered_by_service['UserName'].isin(selected_users)]

if df_selection.empty:
    st.warning("Aucune donnée pour cette sélection de services et d'agents.")
    st.stop()
    
st.divider()

# --- Onglets de visualisation ---
tab1, tab2, tab3 = st.tabs(["Performance en Volume", "Performance en Temps", "Vue par Catégorie"])

with tab1:
    st.header("Performance en Nombre de Clients Traités")
    pie_charts = Graphs_pie(df_selection)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.plotly_chart(pie_charts[0], use_container_width=True)
    with c2:
        st.plotly_chart(pie_charts[1], use_container_width=True)
    with c3:
        st.plotly_chart(pie_charts[2], use_container_width=True)
    
    st.header("Évolution du Nombre d'Opérations par Agent")
    line_chart = plot_line_chart(df_selection)
    st.plotly_chart(line_chart, use_container_width=True)

with tab2:
    st.header("Performance en Temps Moyen de Traitement (par statut)")
    bar_charts = Graphs_bar(df_selection)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.plotly_chart(bar_charts[0], use_container_width=True)
    with c2:
        st.plotly_chart(bar_charts[1], use_container_width=True)
    with c3:
        st.plotly_chart(bar_charts[2], use_container_width=True)

with tab3:
    st.header("Détail par Catégorie de Temps et Type d'Opération")
    fig1 = stacked_chart(df_selection, 'TempOperation', 'UserName', "Catégorisation du Temps d'opération")
    st.altair_chart(fig1, use_container_width=True)
    fig2 = stacked_agent(df_selection, type='UserName', concern='Type_Operation')
    st.altair_chart(fig2, use_container_width=True)