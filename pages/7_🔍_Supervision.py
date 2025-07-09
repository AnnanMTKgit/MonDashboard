# pages/7_🔍_Supervision.py
import streamlit as st
from shared_code import (
    get_connection, run_query, SQLQueries, create_sidebar_filters, load_and_display_css,
    AgenceTable, area_graph, echarts_satisfaction_gauge, current_attente
)
import pandas as pd

st.set_page_config(page_title="Supervision", layout="wide", page_icon="🔍")
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
df_rh = run_query(conn, SQLQueries().RendezVousQueries, params=(start_date, end_date))

# --- Filtrage des données ---
df_all = df_all[df_all['NomAgence'].isin(selected_agencies)]
df_queue = df_queue[df_queue['NomAgence'].isin(selected_agencies)]
# On ne filtre pas df_rh par agence pour l'instant, car la requête ne contient pas NomAgence.
# Si c'était le cas, il faudrait ajouter un filtre ici.

if df_all.empty:
    st.warning("Aucune donnée disponible pour la période et les agences sélectionnées.")
    st.stop()

st.title("🔍 Supervision des Agences")

# --- Navigation par onglets pour la page de supervision ---
tab1, tab2, tab3 = st.tabs([
    "Monitoring de la Congestion en Grille",
    "Opérations sur Rendez-vous",
    "Évolution des Temps sur la Période"
])


with tab1:
    st.header("État des Files d'Attente en Temps Réel")

    _, agg_global = AgenceTable(df_all, df_queue)
    agg_global = agg_global[agg_global["Nom d'Agence"].isin(selected_agencies)]

    agences_a_afficher = agg_global["Nom d'Agence"].unique()
    num_agences = len(agences_a_afficher)
    
    # Définir le nombre de colonnes, 4 est une bonne valeur pour la lisibilité
    num_cols = 4
    
    # Créer les colonnes dynamiquement
    columns = st.columns(num_cols)

    for i, nom_agence in enumerate(agences_a_afficher):
        col_index = i % num_cols
        with columns[col_index]:
            st.subheader(nom_agence)
            
            agence_data = agg_global[agg_global["Nom d'Agence"] == nom_agence]
            if not agence_data.empty:
                max_cap = agence_data['Capacité'].values[0]
                queue_now = agence_data['Nbs de Clients en Attente'].values[0]
                
                # Jauge de congestion
                echarts_satisfaction_gauge(
                    queue_length=queue_now, 
                    max_length=max_cap if max_cap > 0 else 10, # Éviter une division par zéro
                    key=f"gauge_{i}"
                )
                
                # Métriques par service
                st.markdown("**Clients par Service :**")
                
                # Récupérer les services pour cette agence spécifique
                df_agence_queue = df_queue[df_queue['NomAgence'] == nom_agence]
                services_agence = df_agence_queue['NomService'].unique()
                
                # On ne peut pas mettre des colonnes dans des colonnes facilement en Streamlit
                # On va donc les afficher verticalement.
                for service in services_agence:
                    df_service_queue = df_agence_queue[df_agence_queue['NomService'] == service]
                    attente_service = current_attente(df_service_queue, nom_agence)
                    st.metric(label=f"{service}", value=attente_service)

with tab2:
    st.header("Analyse des Opérations sur Rendez-vous")
    
    if df_rh.empty:
        st.info("Aucune donnée de rendez-vous disponible pour la période sélectionnée.")
    else:
        # Traitement des données de rendez-vous
        df_rh['Date'] = pd.to_datetime(df_rh['HeureReservation']).dt.date
        agg_rh = df_rh.groupby(['Date']).agg(
            Temps_Moyen_Attente=('TempAttenteMoyen', lambda x: round(x.mean() / 60) if not x.empty else 0),
            Rendez_Vous_Traites=('Nom', lambda x: (x == 'Traitée').sum()),
            Rendez_Vous_Rejetes=('Nom', lambda x: (x == 'Rejetée').sum()),
            Rendez_Vous_Passes=('Nom', lambda x: (x == 'Passée').sum()),
            Rendez_Vous_en_Attente=('Nom', lambda x: (x == 'En attente').sum()),
            Total_Rendez_Vous=('HeureReservation', 'count'),
            TotalMobile=('IsMobile', lambda x: int(x.sum()))
        ).reset_index()

        st.dataframe(agg_rh, use_container_width=True)

with tab3:
    st.header("Évolution des Temps Moyen sur la Période Sélectionnée")
    
    fig_attente, _, _, _ = area_graph(
        df_all, 
        concern='NomAgence', 
        time='TempsAttenteReel', 
        date_to_bin='Date_Appel', 
        seuil=15, 
        title="Évolution du Temps d'Attente par Agence"
    )
    st.plotly_chart(fig_attente, use_container_width=True)
    
    fig_operation, _, _, _ = area_graph(
        df_all, 
        concern='NomAgence', 
        time='TempOperation', 
        date_to_bin='Date_Fin', 
        seuil=5, 
        title="Évolution du Temps d'Opération par Agence"
    )
    st.plotly_chart(fig_operation, use_container_width=True)