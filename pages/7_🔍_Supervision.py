# pages/7_🔍_Supervision.py
import streamlit as st
from shared_code import *
import pandas as pd
st.markdown(""" <style>iframe[title="streamlit_echarts.st_echarts"]{ height: 500px !important } """, unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center;'>Supervision des Agences</h1>", unsafe_allow_html=True)
load_and_display_css()

if not st.session_state.get('logged_in'):
    st.error("Veuillez vous connecter pour accéder à cette page.")
    st.stop()




create_sidebar_filters()
conn = get_connection()
df_all = run_query(conn, SQLQueries().AllQueueQueries, params=(st.session_state.start_date, st.session_state.end_date))
df_queue = df_all.copy()
df_rh = run_query(conn, SQLQueries().RendezVousQueries, params=(st.session_state.start_date, st.session_state.end_date))

df_all_filtered = df_all[df_all['NomAgence'].isin(st.session_state.selected_agencies)]
df_queue_filtered = df_queue[df_queue['NomAgence'].isin(st.session_state.selected_agencies)]

if df_all_filtered.empty: 
    st.error("Aucune donnée disponible pour la sélection.")
    st.stop()




# --- Navigation par onglets pour la page de supervision ---
tab1, tab2, tab3 = st.tabs([
    "Monitoring de la Congestion en Grille",
    "Opérations sur Rendez-vous",
    "Évolution des Temps sur la Période"
])


with tab1:
 
    st.markdown("<h1 style='text-align: center;'>État des Files d'Attente en Temps Réel</h1>", unsafe_allow_html=True)
    _, agg_global = AgenceTable(df_all_filtered, df_queue_filtered)
    agg_global = agg_global[agg_global["Nom d'Agence"].isin(st.session_state.selected_agencies)]
    
    agg_global = agg_global.sort_values(by='Nbs de Clients en Attente', ascending=False)
    agences_a_afficher = agg_global["Nom d'Agence"].unique()
    num_agences = len(agences_a_afficher)
    
    # Définir le nombre de colonnes, 4 est une bonne valeur pour la lisibilité
    num_cols = 3
    
    # Créer les colonnes dynamiquement
    columns = st.columns(num_cols)
    
    for i, nom_agence in enumerate(agences_a_afficher):
            col_index = i % num_cols
            
            agence_data = agg_global[agg_global["Nom d'Agence"] == nom_agence]
            if not agence_data.empty:
                max_cap = agence_data['Capacité'].values[0]
                queue_now = agence_data['Nbs de Clients en Attente'].values[0]
                
                
                
                # Récupérer les services pour cette agence spécifique
                df_agence_queue = df_queue_filtered[df_queue_filtered['NomAgence'] == nom_agence]
                services_agence = df_agence_queue['NomService'].unique()
                
                # On ne peut pas mettre des colonnes dans des colonnes facilement en Streamlit
                # On va donc les afficher verticalement.
                service_dict = {}
                for service in services_agence:
                    
                    df_service_queue = df_agence_queue[df_agence_queue['NomService'] == service]
                    attente_service = current_attente(df_service_queue, nom_agence)
                    service_dict[service]=attente_service
                row = {
                    "NomAgence": nom_agence,
                    "Clients en Attente": queue_now,
                    "Services": service_dict,
                    "Status":None
                }
                
                            # --- 2. Load the external CSS file ---
                with open("led.css") as f:
                    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

                row['Status'] = get_status_info(row["Clients en Attente"], capacite=max_cap)

            

            
            

                services_dynamic_html = ""
                if row['Services']:
                    for service_name, client_count in row['Services'].items():
                        
                        services_dynamic_html += f""" <div style="text-align: center;">
                                {service_name}<br>
                                <strong>{client_count}</strong>
                            </div>
                        """
                else:
                    services_dynamic_html = "<div>Aucun service spécifié.</div>"
                
                with columns[i % num_cols]:
                    st.markdown(f"""
                        <div style="
                            background-color: {BackgroundGraphicColor}; 
                            border: 1px solid #444; 
                            border-radius: 10px; 
                            padding: 12px 16px; 
                            margin-bottom: 10px;
                            color: black;
                            min-height: 150px; /* Adjust this value as needed */
                        ">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <strong style="font-size: 16px;">{row['NomAgence']}</strong>
                                <div style="display: flex; align-items: center;">
                                    <span class="status-led {row['Status']}"></span> <span style="font-size: 14px;"></span>
                                </div>
                            </div>
                            <div style="margin-top: 10px; font-size: 14px;">
                                Clients en attente : <strong>{row['Clients en Attente']}</strong><br>
                                Capacité Maximale : <strong>{max_cap}</strong><br>
                                <div style="display: flex; justify-content: space-around; flex-wrap: wrap; margin-top: 10px;">
                                    {services_dynamic_html}
                        </div>
                        """, unsafe_allow_html=True)   
                        


        

with tab2:
    st.header("Pas de données encore disponible")
    
    # if st.session_state.df_RH.empty:
    #     st.info("Aucune donnée de rendez-vous disponible pour la période sélectionnée.")
    # else:
    #     # Traitement des données de rendez-vous
    #     st.session_state.df_RH['Date'] = pd.to_datetime(st.session_state.df_RH['HeureReservation']).dt.date
    #     agg_rh = st.session_state.df_RH.groupby(['Date']).agg(
    #         Temps_Moyen_Attente=('TempAttenteMoyen', lambda x: round(x.mean() / 60) if not x.empty else 0),
    #         Rendez_Vous_Traites=('Nom', lambda x: (x == 'Traitée').sum()),
    #         Rendez_Vous_Rejetes=('Nom', lambda x: (x == 'Rejetée').sum()),
    #         Rendez_Vous_Passes=('Nom', lambda x: (x == 'Passée').sum()),
    #         Rendez_Vous_en_Attente=('Nom', lambda x: (x == 'En attente').sum()),
    #         Total_Rendez_Vous=('HeureReservation', 'count'),
    #         TotalMobile=('IsMobile', lambda x: int(x.sum()))
    #     ).reset_index()

    #     st.dataframe(agg_rh, use_container_width=True)

with tab3:
    
    
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
