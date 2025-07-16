# pages/5_⚙️_Analyse_par_Service.py
import streamlit as st
from shared_code import *
st.markdown("<h1 style='text-align: center;'>Analyse par Service et Type d'Opération</h1>", unsafe_allow_html=True)

st.markdown(""" <style>iframe[title="streamlit_echarts.st_echarts"]{ height: 800px !important } """, unsafe_allow_html=True)
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

tabs=st.tabs(["Temps de traitement moyen par type de service","Types de transactions les plus courantes","Top 10 Types de transactions en nombre de clients"])

with tabs[0]:
    
        
    fig_temps_op = GraphsGlob(df_all_filtered)
    st.plotly_chart(fig_temps_op, use_container_width=True)
    
with tabs[1]:
    fig_top10 = Top10_Type(df_queue_filtered,title="Top10 des Opérations le plus courantes")
    st_echarts(fig_top10,height="600px")
        
with tabs[2]:
    chart_service = stacked_agent2(df_all_filtered, type='Type_Operation', concern='NomService',titre="Total Clients par type de transaction")
    st_echarts(chart_service,height="600px")
    
        
        

