# pages/7_🔍_Supervision.py
import streamlit as st
from shared_code import *
import pandas as pd

# Mettre le minuteur en place dès le début de la page
setup_auto_refresh(interval_minutes=10)


st.markdown(""" <style>iframe[title="streamlit_echarts.st_echarts"]{ height: 500px !important } """, unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center;'>Supervision des Agences</h1>", unsafe_allow_html=True)
load_and_display_css()

if not st.session_state.get('logged_in'):
    st.error("Veuillez vous connecter pour accéder à cette page.")
    st.stop()




create_sidebar_filters()
conn = get_connection()
df = run_query(conn, SQLQueries().AllQueueQueries, params=(st.session_state.start_date, st.session_state.end_date))
df_all = df[df['UserName'].notna()].reset_index(drop=True)
df_queue=df.copy()

df_rh = run_query(conn, SQLQueries().RendezVousQueries, params=(st.session_state.start_date, st.session_state.end_date))

df_all_filtered = df_all[df_all['NomAgence'].isin(st.session_state.selected_agencies)]
df_queue_filtered = df_queue[df_queue['NomAgence'].isin(st.session_state.selected_agencies)]

if df_all_filtered.empty: 
    st.error("Aucune donnée disponible pour la sélection.")
    st.stop()



# --- 1. Configuration des onglets et de l'état de session ---
SUPERVISION_TABS = [
    "Monitoring de la Congestion",
    "Opérations sur Rendez-vous",
    "Évolution des Temps sur la Période",
    "Prédiction de l'Affluence future"
]

if 'active_supervision_tab_index' not in st.session_state:
    st.session_state.active_supervision_tab_index = 0
if 'current_area' not in st.session_state: # Pour le carrousel de l'onglet 3
    st.session_state.current_area = 0

# --- 2. Préparation des figures pour les onglets ---
# Seul l'onglet 3 a un carrousel, nous préparons donc ses figures à l'avance.
figures_tab3 = [
    area_graph2(df_all_filtered, concern='NomAgence', time='TempsAttenteReel', date_to_bin='Date_Appel', seuil=15, title="Top 5 des Agences les Plus Lentes en Temps d'Attente"),
    area_graph2(df_all_filtered, concern='NomAgence', time='TempOperation', date_to_bin='Date_Fin', seuil=5, title="Top 5 des Agences les Plus Lentes en Temps d'Opération")
]
total_figures_tab3 = len(figures_tab3)

# --- 3. Affichage du menu de navigation ---
selected_tab = option_menu(
    menu_title=None,
    options=SUPERVISION_TABS,
    icons=['binoculars-fill', 'calendar-check', 'graph-up-arrow', 'magic'],
    orientation="horizontal",
    default_index=st.session_state.active_supervision_tab_index,
    styles={
        "container": {"padding": "0!important", "background-color": "white", "border-bottom": "1px solid #333"},
        "icon": {"color": "black", "font-size": "18px"},
        "nav-link": {"font-size": "16px", "text-align": "center", "margin": "0px", "color": "black"},
        "nav-link-selected": {"background-color": "#013447", "color": "white", "border-bottom": "3px solid #013447"},
    }
)

# --- 4. Affichage du contenu de l'onglet sélectionné ---
# L'ensemble de votre code original est copié ici, dans la structure if/elif.


if selected_tab == SUPERVISION_TABS[0]:

    # --- Définir les styles au début pour la lisibilité ---
    online_card_style = """
        background-color: #F8F9F9; 
        border: 1px solid #D5D8DC; 
        border-radius: 10px; 
        padding: 12px 16px; 
        margin-bottom: 10px;
        color: black;
        min-height: 170px;
    """
    offline_card_style = """
        background-color: #FEF2F2; 
        border: 1px solid #F8C6C6; 
        border-radius: 10px; 
        padding: 12px 16px; 
        margin-bottom: 10px;
        color: black;
        min-height: 170px;
    """
    section_title_style = """
        text-align: center; 
        width: 100%; 
        margin-top: 10px; 
        margin-bottom: 20px;
        color: #555555;
        font-size: 1.5em; 
        font-weight: 500;
    """
    st.markdown("""
        <style>
            /* Cible le conteneur créé par st.columns */
            [data-testid="stHorizontalBlock"] {
                /* Réduit l'espace en dessous de la grille */
                margin-bottom: 0px; 
            }
        </style>
        """, unsafe_allow_html=True)

     



    st.markdown("<h1 style='text-align: center;font-size:2em;'>État des Files d'Attente en Temps Réel</h1>", unsafe_allow_html=True)
    _, agg_global = AgenceTable(df_all_filtered, df_queue_filtered)
   
    agg_global = agg_global[agg_global["Nom d'Agence"].isin(st.session_state.selected_agencies)]
    if not agg_global.empty:
        st.markdown(f"<h3 style='{section_title_style}'>Agences en Lignes</h3>", unsafe_allow_html=True)
        
    agg_global = agg_global.sort_values(by='Nbs de Clients en Attente', ascending=False)
    agences_a_afficher = agg_global["Nom d'Agence"].unique()
    num_agences = len(agences_a_afficher)
    
    # Définir le nombre de colonnes, 4 est une bonne valeur pour la lisibilité
    num_cols = 3
    
    # Créer les colonnes dynamiquement
    j=0
    
    agences_a_afficher=list(agences_a_afficher)
    #agences_a_afficher.extend(st.session_state.offline_agencies_in_scope)
    


    # Chargez les styles UNE SEULE FOIS au début, avant toute boucle.
    try:
        with open("led.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("Le fichier 'led.css' est manquant.")
    # --- SECTION 1 : AGENCES CONNECTÉES ---
    # Créez des colonnes spécifiquement pour cette section
    columns_online = st.columns(num_cols)

    # Boucle uniquement sur les agences en ligne
    for i, nom_agence in enumerate(agences_a_afficher):
        col_index = i % num_cols
        
        agence_data = agg_global[agg_global["Nom d'Agence"] == nom_agence]
        
        # Votre logique de récupération de données reste la même
        max_cap = agence_data['Capacité'].values[0]
        queue_now = agence_data['Nbs de Clients en Attente'].values[0]
        df_agence_queue = df_queue_filtered[df_queue_filtered['NomAgence'] == nom_agence]
        services_agence = df_agence_queue['NomService'].unique()
        
        service_dict = {}
        for service in services_agence:
            df_service_queue = df_agence_queue[df_agence_queue['NomService'] == service]
            attente_service = current_attente(df_service_queue, nom_agence)
            service_dict[service]=attente_service
            
        row = {
            "NomAgence": nom_agence,
            "Clients en Attente": queue_now,
            "Services": service_dict,
            "Status": get_status_info(queue_now, capacite=max_cap)
        }
        
        # with open("led.css") as f:
        #     st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

        services_dynamic_html = ""
        if row['Services']:
            for service_name, client_count in row['Services'].items():
                services_dynamic_html += f"""<div style="text-align: center; margin: 0 5px;">
                        {service_name}<br><strong>{client_count}</strong>
                    </div>"""
        else:
            services_dynamic_html = "<div>Aucun service spécifié.</div>"
        
        with columns_online[col_index]:
            st.markdown(f"""
                            <div style="
                                background-color: {BackgroundGraphicColor}; 
                                border: 1px solid #D5D8DC; 
                                border-radius: 10px; 
                                padding: 12px 16px; 
                                margin-bottom: 10px;
                                color: black;
                                min-height: 170px;
                            ">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <strong style="font-size: 16px;">{row['NomAgence']}</strong>
                                    <div style="display: flex; align-items: center;">
                                        <span class="status-led {row['Status']}"><span class="tooltiptext"></span></span> <span style="font-size: 14px;"></span>
                                    </div>
                                </div>
                                <div style="margin-top: 10px; font-size: 14px;">
                                    Clients en attente : <strong>{row['Clients en Attente']}</strong><br>
                                    Capacité Maximale : <strong>{max_cap}</strong><br>
                                    <div style="display: flex; justify-content: space-around; flex-wrap: wrap; margin-top: 10px;">
                                        {services_dynamic_html}
                            </div>
                            """, unsafe_allow_html=True)
            
    st.divider()
    # --- TITRE DE LA SECTION ---
    # Affichez le titre ici, en pleine largeur, entre les deux grilles.
    if st.session_state.offline_agencies_in_scope:
        st.markdown(f"<h3 style='{section_title_style}'>Agences Hors Lignes</h3>", unsafe_allow_html=True)

    # --- SECTION 2 : AGENCES HORS LIGNE ---
    # Créez un NOUVEL ensemble de colonnes pour garantir un alignement parfait
    columns_offline = st.columns(num_cols)

    # Boucle uniquement sur les agences hors ligne
    for i, nom_agence in enumerate(st.session_state.offline_agencies_in_scope):
        col_index = i % num_cols
        
        with columns_offline[col_index]:
            try:
                max_cap = st.session_state.all_agence_Region.loc[st.session_state.all_agence_Region['NomAgence']==nom_agence, 'Capacites'].values[0]
                max_cap = int(max_cap)
            except (IndexError, ValueError):
                max_cap = "N/A"

            st.markdown(f"""
                <div style="{offline_card_style}">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <strong style="font-size: 16px;">{nom_agence}</strong>
                    </div>
                    <div style="margin-top: 10px; font-size: 14px;">
                        Capacité Maximale : <strong>{max_cap}</strong>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
        

elif selected_tab == SUPERVISION_TABS[1]:
    st.markdown("---")
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

elif selected_tab == SUPERVISION_TABS[2]:
    st.markdown("---")
    
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

    #st.markdown("---") # Ajoute une ligne de séparation pour un look plus propre

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

elif selected_tab == SUPERVISION_TABS[3]:
    # st.title("📈 Prédiction de l'Affluence des Agences")
    # --- Exécution du pipeline ---
    model, scaler = load_model_and_scaler() 
    

    df_actual=df_queue_filtered[["Date_Reservation","Date_Appel","Date_Fin","NomAgence"]]
    
    yesterday = st.session_state.end_date - timedelta(days=1)
    
    is_today = (st.session_state.end_date == datetime.now().date())
    
    if is_today:
        

        df_past = run_query(conn, SQLQueries().AllQueueQueries, params=(yesterday,yesterday))

        df_past = df_past[df_past['NomAgence'].isin(st.session_state.selected_agencies)]
        df_past = df_past[["Date_Reservation","Date_Appel","Date_Fin","NomAgence"]]
        # --- Exécution du pipeline ---
        df_observed, df_predictions, current_time = run_prediction_pipeline(df_actual, df_past)

        if df_observed is not None and df_predictions is not None:
            
            # --- ÉTAPE 1 : Préparer TOUTES les configurations de graphiques (inchangé) ---
            all_agencies = df_predictions.index.get_level_values('NomAgence').unique().tolist()
            figures_options = [] # Liste pour stocker les options de chaque graphique

            for agency in all_agencies:
                observed_agency_data = df_observed.loc[agency]
                predicted_agency_data = df_predictions.loc[agency]
                
                # ... (votre logique de préparation des données pour le graphique : past_data, future_data, etc.)
                display_start_time = current_time - pd.Timedelta(hours=23)
                past_data = observed_agency_data.loc[display_start_time:current_time]['nb_attente']
                future_data = predicted_agency_data['prediction']
                dates_list = past_data.index.strftime('%Y-%m-%d %Hh').tolist() + future_data.index.strftime('%Y-%m-%d %Hh').tolist()
                past_values = np.round(past_data.values, 2).tolist()
                future_values = np.round(future_data.values, 2).tolist()
                prediction_start_index = len(past_values)
                # Le libellé sur l'axe X à cet index
                # On ajoute une sécurité pour éviter un IndexError si future_data est vide
                prediction_start_label = dates_list[prediction_start_index] if prediction_start_index < len(dates_list) else None
                options = {
                    # On peut simplifier le titre car le nom de l'agence sera au-dessus du graphique
                    #'title': {'text': "Observé vs. Prédit", 'left': 'center', 'textStyle': {'fontSize': 14}},
                    "tooltip": {"trigger": "axis"},
                    "legend": {"data": ["Affluence observée", "Affluence Prédite"], "left": "center", "top": 30},
                    "xAxis": {"type": "category", "data": dates_list},
                    "yAxis": {"type": "value", "name": "Moyenne"},
                    
                    "series": [
                    {
                        "name": "Affluence observée", "type": "line", "data": past_values,
                        "lineStyle": {"color": "#3398DB", "width": 3}, "itemStyle": {"color": "#3398DB"},
                        
                    },
                    {
                        "name": "Affluence Prédite", "type": "line", 
                        "data": [None] * len(past_values) + future_values,
                        "lineStyle": {"color": "#FF5733", "type": "dashed", "width": 3}, 
                        "itemStyle": {"color": "#FF5733"},
                        # --- C'EST ICI QUE L'ON AJOUTE LA LIGNE VERTICALE ---
            'markLine': {
                'symbol': 'none',  # Pour ne pas avoir de flèches au bout de la ligne
                'data': [
                    {
                        'xAxis': prediction_start_label, # On positionne la ligne sur la bonne date/heure
                        'lineStyle': {
                            'color': 'green',      # Une couleur grise discrète
                            'type': 'dashed',   # En pointillé
                            'width': 2
                        },
                        'label': {
                            'show': True,
                            'position': 'end', 
                            # Le texte à afficher
                            'formatter': 'Début de Prédiction', 
                            'color': 'green',
                            'fontSize': 12,
                            'fontWeight': 'bold',
                            'backgroundColor': 'white', 
                            'padding': [2, 4],            
                            'borderRadius': 3          
                        }
                    }
                ]
            } if prediction_start_label else {} # On n'ajoute la ligne que si le label existe
                    },
                
                
                ],
                   "visualMap": {
                    "top": 50, "right": 10, "show": False,
                    "pieces": [{"gt": 0, "lte": len(past_values) -1, "color": "#3398DB"},
                            {"gte": len(past_values), "color": "#FF5733"}],
                    "outOfRange": {"color": "#999"}
                },
                    "grid": {"left": "10%", "right": "5%", "top": "20%", "bottom": "20%"} # Ajuster pour laisser de la place
                }
                figures_options.append(options)

            # --- ÉTAPE 2 : NOUVELLE LOGIQUE D'AFFICHAGE EN GRILLE ---
            total_figures = len(figures_options)

            if total_figures > 0:
                st.markdown("---")
                # Ajouter un contrôle pour que l'utilisateur choisisse la disposition
                num_columns = 2
                # st.number_input(
                #     'Nombre de graphiques par ligne :', 
                #     min_value=1, 
                #     max_value=4, 
                #     value=2, 
                #     step=1
                # )
                
                # Boucler par "lignes" de graphiques
                for i in range(0, total_figures, num_columns):
                    
                    cols = st.columns(num_columns)
                    
                    # Récupérer le sous-ensemble de graphiques pour cette ligne
                    row_figures_options = figures_options[i : i + num_columns]
                    row_agencies = all_agencies[i : i + num_columns]
                    
                    # Remplir chaque colonne avec un graphique
                    for j, col in enumerate(cols):
                        if j < len(row_figures_options): # S'assurer de ne pas dépasser pour la dernière ligne
                            with col:
                                # Afficher le nom de l'agence en titre
                                
                                st.markdown(f"<h1 style='text-align: center;font-size:1em;'>{row_agencies[j]}</h1>", unsafe_allow_html=True)
                                # Afficher le graphique
                                st_echarts(
                                    options=row_figures_options[j],
                                    height="500px",
                                    key=f"grid_chart_{row_agencies[j]}" # Clé unique et stable
                                )
                                
            else:               
                st.warning("Aucun graphique à afficher.")

        else:
            st.error("Impossible de générer les prédictions.")
        

        
    else:
        st.info(f"Pas de Prédictions Futures")
        st.markdown(f"<h1 style='text-align: center;font-size:2em;'>Affluence observées lors de la dernière journée ouvrable ({df_actual['Date_Reservation'].max().date()})</h1>", unsafe_allow_html=True)
        
        
        # Pour la vue historique, on ne veut que les données de la journée sélectionnée.
        df_to_process = df_queue_filtered[df_queue_filtered['Date_Reservation'].dt.date == df_actual['Date_Reservation'].max().date()]
        
        if df_to_process.empty:
            st.warning(f"Aucune donnée disponible")
        else:
            # On utilise une fonction simple, cachée, juste pour le prétraitement.
            
            df_historical = get_historical_data(df_to_process)
            
            if df_historical is not None:
                agencies = df_historical.index.get_level_values(0).unique().tolist()
                # MODIFICATION : On place aussi ce multiselect dans une colonne
                col1, col2 = st.columns([20, 80])
                with col1:
                    selected_agency = st.selectbox("Sélectionnez une agence", agencies)
            
            
            
                with col2:
                    
                    
                    agency_data = df_historical.loc[selected_agency]
                    
                    options = { "title": {"text": f"{selected_agency}", "left": "center"},
                        "tooltip": {"trigger": "axis"},
                        "xAxis": {"type": "category", "data": agency_data.index.strftime('%Hh').tolist()},
                        "yAxis": {"type": "value", "name": "Affluence Moyenne"},
                        "series": [{"name": "Affluence observée", "type": "line", "data": np.round(agency_data['nb_attente'].values, 0).tolist(), "color": "#3398DB"}],
                        "dataZoom": [{"type": "inside"}, {"type": "slider"}],
                    }
                        
                    st_echarts(options=options, height="500px")
                