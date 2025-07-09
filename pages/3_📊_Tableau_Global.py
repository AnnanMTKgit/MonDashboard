# pages/3_📊_Tableau_Global.py
import streamlit as st
from shared_code import (
    get_connection, run_query, SQLQueries, create_sidebar_filters,
    AgenceTable, create_excel_buffer, load_and_display_css
)

st.set_page_config(page_title="Tableau Global", layout="wide", page_icon="📊")
load_and_display_css()

if not st.session_state.get('logged_in'):
    st.error("Veuillez vous connecter pour accéder à cette page.")
    st.stop()

# --- Chargement des données et filtres ---
conn = get_connection()
df_agences = run_query(conn, SQLQueries().AllAgences)
create_sidebar_filters(df_agences)

df_all = run_query(conn, SQLQueries().AllQueueQueries, params=(st.session_state.start_date, st.session_state.end_date))
df_queue = df_all.copy()

if df_all.empty or not st.session_state.selected_agencies:
    st.warning("Aucune donnée disponible pour la période et les agences sélectionnées.")
    st.stop()

# --- Filtrage des données ---
# --- Filtrage des données basé sur st.session_state ---
df_all_filtered = df_all[df_all['NomAgence'].isin(st.session_state.selected_agencies)] # Et ici
df_queue_filtered = df_queue[df_queue['NomAgence'].isin(st.session_state.selected_agencies)] # Et ici

if df_all_filtered.empty:
    st.warning("Aucune donnée disponible pour la période et les agences sélectionnées.")
    st.stop()

st.title("📊 Tableau de Bord Global")
st.markdown("Statistiques agrégées pour la période et les agences sélectionnées.")

# --- Affichage du tableau ---
_, AGG = AgenceTable(df_all_filtered, df_queue_filtered )


if not AGG.empty:
    st.markdown(f"### Statistiques Globales par Agence")
    
    # Bouton de téléchargement
    buffer = create_excel_buffer(AGG)
    st.download_button(
        label="📥 Télécharger en Excel",
        data=buffer,
        file_name=f'Global_{st.session_state.start_date}_to_{st.session_state.end_date}.xlsx',
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # Appliquer le style
    def tmo_col(val):
        return 'background-color: #50C878' if val <= 5 else ''
    def tma_col(val):
        return 'background-color: #EF553B' if val > 15 else ''

    columns_to_display = ['Période', "Nom d'Agence", "Temps Moyen d'Operation (MIN)", "Temps Moyen d'Attente (MIN)", "Temps Moyen de Passage(MIN)", 'Capacité', 'Total Tickets', 'Total Traités', 'TotalMobile']
    AGG_display = AGG[columns_to_display]
    
    styled_agg = AGG_display.style.format("{:.0f}", subset=["Temps Moyen d'Operation (MIN)", "Temps Moyen d'Attente (MIN)", "Temps Moyen de Passage(MIN)"]) \
                                   .applymap(tmo_col, subset=["Temps Moyen d'Operation (MIN)"]) \
                                   .applymap(tma_col, subset=["Temps Moyen d'Attente (MIN)"])

    st.dataframe(styled_agg, use_container_width=True)

else:
    st.info("Aucune donnée à afficher dans le tableau global pour cette sélection.")