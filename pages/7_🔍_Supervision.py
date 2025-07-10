# pages/7_🔍_Supervision.py
import streamlit as st
from shared_code import *
import pandas as pd

st.set_page_config(page_title="Supervision", layout="wide", page_icon="🔍")
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

st.title("🔍 Supervision des Agences")

# --- Navigation par onglets pour la page de supervision ---
tab1, tab2, tab3 = st.tabs([
    "Monitoring de la Congestion en Grille",
    "Opérations sur Rendez-vous",
    "Évolution des Temps sur la Période"
])


with tab1:
    st.header("État des Files d'Attente en Temps Réel")

    _, agg_global = AgenceTable(df_all_filtered, df_queue_filtered)
    agg_global = agg_global[agg_global["Nom d'Agence"].isin(st.session_state.selected_agencies)]

    agences_a_afficher = agg_global["Nom d'Agence"].unique()
    num_agences = len(agences_a_afficher)
    
    # Définir le nombre de colonnes, 4 est une bonne valeur pour la lisibilité
    num_cols = 3
    
    # Créer les colonnes dynamiquement
    columns = st.columns(num_cols)
    
    for i, nom_agence in enumerate(agences_a_afficher):
            data=[]
            col_index = i % num_cols
            with columns[col_index]:
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
            "Detail par service": service_dict
            
        }
            data.append(row)
            data=pd.DataFrame(data)  
            
            

            data['Statut'] = data['Clients en Attente'].apply(lambda clients: get_status(clients, capacite=max_cap))

            

            data = data.sort_values(by="Clients en Attente", ascending=False)
            c=columns[col_index].columns(len(data))
            for index, row in data.iterrows():
                services_string = " | ".join([f"{service} : {val}" for service, val in row["Detail par service"].items()])

                # Ligne complète à afficher
                # c[index].markdown(f"""
                # <div style="padding: 8px; margin-bottom: 8px; border-bottom: 1px solid #ddd;">
                #     <strong>{row["NomAgence"]}</strong> {row['Statut']}<br>
                #     Clients en Attente : <strong>{row['Clients en Attente']}</strong>, {services_string}
                # </div>
                # """, unsafe_allow_html=True)
                
                
                c[index].markdown(f"""
                <div style="
                    background-color: #111; 
                    border: 1px solid #444; 
                    border-radius: 10px; 
                    padding: 12px 16px; 
                    margin-bottom: 10px;
                    color: white;
                    min-height: 150px;  /* Ajuste cette valeur selon ton besoin */
                ">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <strong style="font-size: 16px;">{row['NomAgence']}</strong>
                        <div style="display: flex; align-items: center;">
                            <span style="
                                width: 12px; 
                                height: 12px; 
                                background-color: black; 
                                border-radius: 50%; 
                                display: inline-block; 
                                margin-right: 6px;
                            "></span>
                            <span style="font-size: 14px;">{row['Statut']}</span>
                        </div>
                    </div>
                    <div style="margin-top: 10px; font-size: 14px;">
                        Clients en attente : <strong>{row['Clients en Attente']}</strong><br>
                        {services_string}
                    </div>
                </div>
                """, unsafe_allow_html=True)


        

with tab2:
    st.header("Analyse des Opérations sur Rendez-vous")
    
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
    st.header("Évolution des Temps Moyen sur la Période Sélectionnée")
    
    fig_attente, _, _, _ = area_graph(
        df_all_filtered, 
        concern='NomAgence', 
        time='TempsAttenteReel', 
        date_to_bin='Date_Appel', 
        seuil=15, 
        title="Évolution du Temps d'Attente par Agence"
    )
    st.plotly_chart(fig_attente, use_container_width=True)
    
    fig_operation, _, _, _ = area_graph(
        df_all_filtered, 
        concern='NomAgence', 
        time='TempOperation', 
        date_to_bin='Date_Fin', 
        seuil=5, 
        title="Évolution du Temps d'Opération par Agence"
    )
    st.plotly_chart(fig_operation, use_container_width=True)