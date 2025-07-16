# pages/4_📈_Analyse_par_Agence.py
import streamlit as st
from shared_code import *
st.markdown("<h1 style='text-align: center;'>Analyse Détaillée par Agence</h1>", unsafe_allow_html=True)
st.markdown(""" <style>iframe[title="streamlit_echarts.st_echarts"]{ height: 500px !important } """, unsafe_allow_html=True)
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




tab1, tab2, tab3 = st.tabs(["Performance par Catégorie", "Agences les Plus Lentes", "Agences les Plus Fréquentées"])

with tab1:
    option1=stacked_chart2(df_all_filtered, 'TempsAttenteReel', 'NomAgence', "Catégorisation du Temps d'Attente")
    option2=stacked_chart2(df_all_filtered, 'TempOperation', 'NomAgence', "Catégorisation du Temps d'Opération")
    figures = [option1, option2]
    total_figures = len(figures)
    if 'current_stack' not in st.session_state:
        st.session_state.current_stack = 0


  
    stack_index = st.session_state.current_stack

    
    st_echarts(
        options=figures[stack_index],
        height="500px",
        key=f"stack_{stack_index}" 
    )

    st.markdown("---") # Ajoute une ligne de séparation pour un look plus propre

    # Étape B : Créer les colonnes pour la navigation EN DESSOUS de la figure.
    # On utilise 3 colonnes pour un layout équilibré : [Bouton Précédent | Texte Central | Bouton Suivant]
    col1, col2, col3 = st.columns([2, 1, 2]) # Le ratio donne plus d'espace aux boutons

    with col1:
        # Le bouton est désactivé si on est sur la première figure
        if st.button("◀️ Précédent", use_container_width=True, disabled=(stack_index == 0),key="stack_prev"):
            st.session_state.current_stack -= 1
            st.rerun() # On force le rafraîchissement pour voir le changement

    with col2:
        # Affiche le statut "page / total" au centre.
        # On utilise du Markdown pour centrer le texte.
        st.markdown(
            f"<p style='text-align: center; font-weight: bold;'>Figure {stack_index + 1} / {total_figures}</p>", 
            unsafe_allow_html=True
        )

    with col3:
        # Le bouton est désactivé si on est sur la dernière figure
        if st.button("Suivant ▶️", use_container_width=True, disabled=(stack_index >= total_figures - 1),key="stack_next"):
            st.session_state.current_stack += 1
            st.rerun()

    # chart1 = stacked_chart(df_all_filtered, 'TempsAttenteReel', 'NomAgence', "Catégorisation du Temps d'Attente")
    # st.altair_chart(chart1, use_container_width=True)
    
    # chart2 = stacked_chart(df_all_filtered, 'TempOperation', 'NomAgence', "Catégorisation du Temps d'Opération")
    # st.altair_chart(chart2, use_container_width=True)
    
    # chart3 = TempsPassage(df_all_filtered)
    # st.altair_chart(chart3, use_container_width=True)

with tab2:
    
    option1=area_graph2(df_all_filtered, concern='NomAgence', time='TempsAttenteReel', date_to_bin='Date_Appel', seuil=15, title="Top 5 des Agences les Plus Lentes en Temps d'Attente")     
    option2=area_graph2(df_all_filtered, concern='NomAgence', time='TempOperation', date_to_bin='Date_Fin', seuil=5, title="Top 5 des Agences les Plus Lentes en Temps d'Opération")
    
    
    figures = [option1, option2]
    total_figures = len(figures)

    
    if 'current_area' not in st.session_state:
        st.session_state.current_area = 0


  
    area_index = st.session_state.current_area

    
    st_echarts(
        options=figures[area_index],
        height="500px",
        key=f"area_{area_index}" 
    )

    st.markdown("---") # Ajoute une ligne de séparation pour un look plus propre

    # Étape B : Créer les colonnes pour la navigation EN DESSOUS de la figure.
    # On utilise 3 colonnes pour un layout équilibré : [Bouton Précédent | Texte Central | Bouton Suivant]
    col1, col2, col3 = st.columns([2, 1, 2]) # Le ratio donne plus d'espace aux boutons

    with col1:
        # Le bouton est désactivé si on est sur la première figure
        if st.button("◀️ Précédent", use_container_width=True, disabled=(area_index == 0),key="area_prev"):
            st.session_state.current_area -= 1
            st.rerun() # On force le rafraîchissement pour voir le changement

    with col2:
        # Affiche le statut "page / total" au centre.
        # On utilise du Markdown pour centrer le texte.
        st.markdown(
            f"<p style='text-align: center; font-weight: bold;'>Figure {area_index + 1} / {total_figures}</p>", 
            unsafe_allow_html=True
        )

    with col3:
        # Le bouton est désactivé si on est sur la dernière figure
        if st.button("Suivant ▶️", use_container_width=True, disabled=(area_index >= total_figures - 1),key='area_next'):
            st.session_state.current_area += 1
            st.rerun()

with tab3:
    
    fig1 = top_agence_freq(df_all_filtered, df_queue_filtered, title=['Total Tickets', 'Total Traités'])
    fig2 = top_agence_freq(df_all_filtered, df_queue_filtered, title=['Total Tickets', 'Total Rejetées'], color=[green_color, blue_color])
    
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        st.plotly_chart(fig2, use_container_width=True)