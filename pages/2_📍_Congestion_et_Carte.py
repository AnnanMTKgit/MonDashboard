# pages/2_📍_Congestion_et_Carte.py
import streamlit as st
from shared_code import (
    get_connection, run_query, SQLQueries, create_sidebar_filters, 
    AgenceTable, create_folium_map, echarts_satisfaction_gauge, current_attente,
    load_and_display_css
)

st.set_page_config(page_title="Congestion et Carte", layout="wide", page_icon="📍")
load_and_display_css()

if not st.session_state.get('logged_in'):
    st.error("Veuillez vous connecter pour accéder à cette page.")
    st.stop()

# --- Chargement des données et filtres ---
conn = get_connection()
df_agences = run_query(conn, SQLQueries().AllAgences)
create_sidebar_filters(df_agences)

df_all = run_query(conn, SQLQueries().AllQueueQueries, params=(st.session_state.start_date, st.session_state.end_date))
df_queue = df_all.copy() # Simplification, df_queue est souvent une version filtrée/spécifique

# --- Filtrage des données basé sur st.session_state ---
df_all_filtered = df_all[df_all['NomAgence'].isin(st.session_state.selected_agencies)] # Et ici
df_queue_filtered = df_queue[df_queue['NomAgence'].isin(st.session_state.selected_agencies)] # Et ici

if df_all_filtered.empty:
    st.warning("Aucune donnée disponible pour la période et les agences sélectionnées.")
    st.stop()

st.title("📍 Congestion et Localisation des Agences")

# --- KPIs ---
_, agg_global = AgenceTable(df_all, df_queue)
agg_global = agg_global[agg_global["Nom d'Agence"].isin(st.session_state.selected_agencies)]

TMO = agg_global["Temps Moyen d'Operation (MIN)"].mean()
TMA = agg_global["Temps Moyen d'Attente (MIN)"].mean()
NMC = agg_global['Total Tickets'].sum()

c1, c2, c3 = st.columns(3)
c1.metric("Temps Moyen d'Opération (MIN)", f"{TMO:.0f}")
c2.metric("Temps Moyen d'Attente (MIN)", f"{TMA:.0f}")
c3.metric("Nombre Total de Clients", f"{NMC:.0f}")

st.divider()

# --- Section Congestion ---
c1, c2 = st.columns([1, 2])

agg_map = agg_global.rename(columns={
    "Nom d'Agence":'NomAgence', 'Capacité':'Capacites', 
    "Temps Moyen d'Operation (MIN)":'Temps_Moyen_Operation',
    "Temps Moyen d'Attente (MIN)":'Temps_Moyen_Attente',
    'Total Traités':'NombreTraites', 'Total Tickets':'NombreTickets',
    'Nbs de Clients en Attente':'AttenteActuel'
})

with c1:
    st.subheader("CONGESTION PAR AGENCE")
    agence_options = agg_map['NomAgence'].unique()
    if len(agence_options) > 0:
        selected_agence_gauge = st.selectbox(
            "Choisir une agence",
            options=agence_options,
            label_visibility="collapsed"
        )
        
        agence_data = agg_map[agg_map['NomAgence'] == selected_agence_gauge]
        if not agence_data.empty:
            queue_length = agence_data['AttenteActuel'].values[0]
            max_length = agence_data['Capacites'].values[0]
            echarts_satisfaction_gauge(queue_length, max_length=max_length, title="Clients en Attente")
            # Ajoutez les métriques par service ici si nécessaire

with c2:
    st.subheader("CARTE DES AGENCES")
    create_folium_map(agg_map)