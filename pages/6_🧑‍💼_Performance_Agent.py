# pages/6_🧑‍💼_Performance_Agent.py
import streamlit as st
from shared_code import *

# Mettre le minuteur en place dès le début de la page
setup_auto_refresh(interval_minutes=10)



# -----------------------------------------------

st.markdown("<h1 style='text-align: center;'>Performance des Agents</h1>", unsafe_allow_html=True)

st.markdown(""" <style>iframe[title="streamlit_echarts.st_echarts"]{ height: 600px !important } """, unsafe_allow_html=True)
load_and_display_css()

if not st.session_state.get('logged_in'):
    st.error("Veuillez vous connecter pour accéder à cette page.")
    st.stop()

create_sidebar_filters()

# Utiliser les données partagées au lieu de recharger
df = st.session_state.df_main
df_all = df[df['UserName'].notna()].reset_index(drop=True)
df_queue = df.copy()

df_filtered_global = df_all[df_all['NomAgence'].isin(st.session_state.selected_agencies)]
df_filtered_global = df_filtered_global[df_filtered_global['UserName'].notna()]


if df_filtered_global.empty: 
    st.error("Aucune donnée disponible pour la sélection.")
    st.stop()



# --- DataFrame final pour les visualisations ---
df_selection = filter1(df_filtered_global)

if df_selection.empty:
    st.warning("Aucune donnée pour cette sélection de services et d'agents.")
    st.stop()
    
#st.divider()

# --- Onglets de visualisation ---
tab1, tab2, tab3,tab4 = st.tabs(["Performance en Volume", "Performance en Temps","Evolution en Temps par Agent", "Vue par Catégorie"])

with tab1:
    
    #pie_charts = Graphs_pie(df_selection)
    c1, c2, c3 = st.columns(3)
    with c1:
       
        option1=create_pie_chart2(df_selection,title='Traitée')
        st_echarts( options=option1, height="600px",key='pie_1')
        
        # st.plotly_chart(pie_charts[0], use_container_width=True)
    with c2:
        
        option2=create_pie_chart2(df_selection,title='Passée')
        st_echarts( options=option2, height="600px",key="pie_2")
        #st.plotly_chart(pie_charts[1], use_container_width=True)
    with c3:
        
        option3=create_pie_chart2(df_selection,title='Rejetée')
        st_echarts( options=option3, height="600px",key="pie_3")
        #st.plotly_chart(pie_charts[2], use_container_width=True)
    
    

with tab2:
    #bar_charts=Graphs_bar(df_selection)
    #st.plotly_chart(bar_charts[1], use_container_width=True)
    c1, c2, c3 = st.columns(3)
    with c1:
       
        option1=create_bar_chart2(df_selection,status='Traitée')
    
        st_echarts( options=option1, height="600px",key="bar_1")
        
        # st.plotly_chart(pie_charts[0], use_container_width=True)
    with c2:
        
        option2=create_bar_chart2(df_selection,status='Passée',color=green_color)
        st_echarts( options=option2, height="600px",key="bar_2")
        #st.plotly_chart(pie_charts[1], use_container_width=True)
    with c3:
        
        option3=create_bar_chart2(df_selection,status='Rejetée',color=blue_clair_color)
        st_echarts( options=option3, height="600px",key="bar_3")
        #st.plotly_chart(pie_charts[2], use_container_width=True)
    

with tab3:
    line_chart = plot_line_chart(df_selection)
    st.plotly_chart(line_chart, use_container_width=True)


with tab4:
    
   
    option1 = stacked_chart2(df_selection, 'TempOperation', 'UserName', titre="Total des opérations par Agent et par Catégorie")
        
    option2 = stacked_agent2(df_selection, concern='UserName', type='Type_Operation',titre="Top 10 des opérations effectuées par Agent")
    
    figures = [option1, option2]
    total_figures = len(figures)
    if 'current_stacked_agent' not in st.session_state:
        st.session_state.current_stacked_agent = 0


  
    stacked_agent_index = st.session_state.current_stacked_agent

    
    st_echarts(
        options=figures[stacked_agent_index],
        height="600px",
        key=f"area_{stacked_agent_index}" 
    )

    
    # Étape B : Créer les colonnes pour la navigation EN DESSOUS de la figure.
    # On utilise 3 colonnes pour un layout équilibré : [Bouton Précédent | Texte Central | Bouton Suivant]
    col1, col2, col3 = st.columns([2, 1, 2]) # Le ratio donne plus d'espace aux boutons

    with col1:
        # Le bouton est désactivé si on est sur la première figure
        if st.button("◀️ Précédent", use_container_width=True, disabled=(stacked_agent_index == 0),key="stacked_agent_prev"):
            st.session_state.current_stacked_agent -= 1
            st.rerun() # On force le rafraîchissement pour voir le changement

    with col2:
        # Affiche le statut "page / total" au centre.
        # On utilise du Markdown pour centrer le texte.
        st.markdown(
            f"<p style='text-align: center; font-weight: bold;'>Figure {stacked_agent_index + 1} / {total_figures}</p>", 
            unsafe_allow_html=True
        )

    with col3:
        # Le bouton est désactivé si on est sur la dernière figure
        if st.button("Suivant ▶️", use_container_width=True, disabled=(stacked_agent_index>= total_figures - 1),key='area_next'):
            st.session_state.current_stacked_agent += 1
            st.rerun()
