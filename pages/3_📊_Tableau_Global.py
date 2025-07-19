# pages/3_📊_Tableau_Global.py
import streamlit as st
from shared_code import *

st.markdown("<h1 style='text-align: center;'>Tableau de Bord Global</h1>", unsafe_allow_html=True)

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
        return f'background-color: {green_color}' if val > 5 else ''
    def tma_col(val):
        return f'background-color: {blue_clair_color}; color: white' if val > 15 else ''

    columns_to_display = ['Période', "Nom d'Agence", "Temps Moyen d'Operation (MIN)", "Temps Moyen d'Attente (MIN)", "Temps Moyen de Passage(MIN)", 'Capacité', 'Total Tickets', 'Total Traités', 'TotalMobile']
    AGG_display = AGG[columns_to_display]

      # Exemple avec plus de styles pour les en-têtes
    # 1. Définir le style pour les en-têtes (headers)
    header_styles = [{'selector': "th.col_heading", 'props': [('font-weight', 'bold')]}]
    
    styled_agg = AGG_display.style.format("{:.0f}", subset=["Temps Moyen d'Operation (MIN)", "Temps Moyen d'Attente (MIN)", "Temps Moyen de Passage(MIN)"]) \
                                   .applymap(tmo_col, subset=["Temps Moyen d'Operation (MIN)"]) \
                                   .applymap(tma_col, subset=["Temps Moyen d'Attente (MIN)"])\
                                   

    styled_agg=styled_agg.set_table_styles(header_styles)

    st.table(styled_agg)

        