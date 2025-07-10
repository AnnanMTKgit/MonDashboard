# pages/6_🧑‍💼_Performance_Agent.py
import streamlit as st
from shared_code import *


st.markdown("<h1 style='text-align: center;'>Performance des Agents</h1>", unsafe_allow_html=True)
load_and_display_css()

if not st.session_state.get('logged_in'):
    st.error("Veuillez vous connecter pour accéder à cette page.")
    st.stop()

create_sidebar_filters()
conn = get_connection()
df_all = run_query(conn, SQLQueries().AllQueueQueries, params=(st.session_state.start_date, st.session_state.end_date))

df_filtered_global = df_all[df_all['NomAgence'].isin(st.session_state.selected_agencies)]
df_filtered_global = df_filtered_global[df_filtered_global['UserName'].notna()]


if df_filtered_global.empty: 
    st.error("Aucune donnée disponible pour la sélection.")
    st.stop()


# --- Filtres spécifiques à la page ---
st.sidebar.subheader("Filtres d'Analyse")



# --- DataFrame final pour les visualisations ---
df_selection = filter1(df_filtered_global)

if df_selection.empty:
    st.warning("Aucune donnée pour cette sélection de services et d'agents.")
    st.stop()
    
#st.divider()

# --- Onglets de visualisation ---
tab1, tab2, tab3 = st.tabs(["Performance en Volume", "Performance en Temps", "Vue par Catégorie"])

with tab1:
    
    pie_charts = Graphs_pie(df_selection)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.plotly_chart(pie_charts[0], use_container_width=True)
    with c2:
        st.plotly_chart(pie_charts[1], use_container_width=True)
    with c3:
        st.plotly_chart(pie_charts[2], use_container_width=True)
    
    
    line_chart = plot_line_chart(df_selection)
    st.plotly_chart(line_chart, use_container_width=True)

with tab2:
    
    bar_charts = Graphs_bar(df_selection)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.plotly_chart(bar_charts[0], use_container_width=True)
    with c2:
        st.plotly_chart(bar_charts[1], use_container_width=True)
    with c3:
        st.plotly_chart(bar_charts[2], use_container_width=True)

with tab3:
    
    fig1 = stacked_chart(df_selection, 'TempOperation', 'UserName', "Catégorisation du Temps d'opération")
    st.altair_chart(fig1, use_container_width=True)
    fig2 = stacked_agent(df_selection, type='UserName', concern='Type_Operation')
    st.altair_chart(fig2, use_container_width=True)