# pages/3_📊_Tableau_Global.py
import streamlit as st
from shared_code import *
from st_aggrid.shared import JsCode
import pandas as pd

# Mettre le minuteur en place dès le début de la page
setup_auto_refresh(interval_minutes=10)
st.markdown(""" <style>iframe[title="streamlit_echarts.st_echarts"]{ height: 500px !important } """, unsafe_allow_html=True)
load_and_display_css()

if not st.session_state.get('logged_in'):
    st.error("Veuillez vous connecter pour accéder à cette page.")
    st.stop()

create_sidebar_filters()

# Utiliser les données partagées au lieu de recharger
df = st.session_state.df_main
df_all = df[df['UserName'].notna()].reset_index(drop=True)
df_queue = df.copy()

df_all_filtered = df_all[df_all['NomAgence'].isin(st.session_state.selected_agencies)]
df_queue_filtered = df_queue[df_queue['NomAgence'].isin(st.session_state.selected_agencies)]

if df_all_filtered.empty:
    st.error("Aucune donnée disponible pour la sélection.")
    st.stop()

st.markdown("<h1 style='text-align: center;font-size:1.5em;'>Tableau Global</h1>", unsafe_allow_html=True)
st.markdown("<br/>", unsafe_allow_html=True)

# --- Configuration des onglets avec option_menu ---
GLOBAL_TABS = ["Statistiques Agences & Réseau", "Données Brutes"]

# Si c'est le premier chargement de l'application, on définit l'onglet par défaut
if 'active_global_tab' not in st.session_state:
    st.session_state.active_global_tab = GLOBAL_TABS[0]

# Affichage du menu
selected_tab = option_menu(
    menu_title=None,
    options=GLOBAL_TABS,
    icons=['table', 'database-gear'],
    orientation="horizontal",
    # On force l'index basé sur la chaîne de caractères enregistrée
    default_index=GLOBAL_TABS.index(st.session_state.active_global_tab),
    styles={
        "container": {"padding": "0!important", "background-color": "white", "border-bottom": "1px solid #333"},
        "icon": {"color": "black", "font-size": "18px"},
        "nav-link": {"font-size": "16px", "text-align": "center", "margin": "0px", "color": "black"},
        "nav-link-selected": {"background-color": "#013447", "color": "white", "border-bottom": "3px solid #013447"},
    }
)

# On mémorise immédiatement l'onglet textuel sélectionné par l'utilisateur
# if st.session_state.active_global_tab != selected_tab:
#     st.session_state.active_global_tab = selected_tab
#     st.rerun()

st.markdown("<br/>", unsafe_allow_html=True)

# ==============================================================================
# --- ONGLET 1 : STATISTIQUES AGENCES & RÉSEAU ---
# ==============================================================================
if selected_tab == GLOBAL_TABS[0]:
    
    # Affichage des KPIs d'agents
    Kpi = df_all_filtered.groupby("NomService")["UserName"].nunique().reset_index()
    Kpi = Kpi.rename(columns={"UserName": "Nombre_Agents"})

    if not Kpi.empty:
        cols = st.columns(len(Kpi))  # une colonne par service
        for i, row in Kpi.iterrows():
            with cols[i]:
                st.metric(label="Nombre Agents " + row["NomService"], value=row["Nombre_Agents"])

    st.markdown("<br/>", unsafe_allow_html=True)
    
    # --- Préparation des tableaux ---
    (
        agence_mensuel,
        agence_global,
        reseau_mensuel,
        reseau_global
    ) = AgenceTable2(df_all_filtered, df_queue_filtered)

    view_options = {
        "Statistiques Globales par Agence": (agence_global, "Global_Agence"),
        "Statistiques Mensuelles par Agence": (agence_mensuel, "Mensuel_Agence"),
        "Statistiques Globales du Réseau ": (reseau_global, "Global_Reseau"),
        "Statistiques Mensuelles du Réseau ": (reseau_mensuel, "Mensuel_Reseau"),
    }

    selected_view_name = st.selectbox(
        "Choisissez la vue à afficher :",
        options=list(view_options.keys())
    )

    df_to_display, file_prefix = view_options[selected_view_name]
    # --- NOUVEAU : SUPPRESSION DES COLONNES INDÉSIRABLES ---
    # Ajoutez ici le nom exact des colonnes que vous ne voulez pas afficher
    colonnes_a_supprimer = ['Clients en Attente Actuelle'] 
    
    # On supprime uniquement si les colonnes existent dans le DataFrame sélectionné
    # (Sécurité pour éviter les plantages entre les vues Agence et Réseau)
    df_to_display = df_to_display.drop(
        columns=[col for col in colonnes_a_supprimer if col in df_to_display.columns], 
        errors='ignore'
    )


    if not df_to_display.empty:
        st.markdown(f"### {selected_view_name}")
        
        buffer = create_excel_buffer(df_to_display)
        st.download_button(
            label="📥 Télécharger la vue actuelle en Excel",
            data=buffer,
            file_name=f'{file_prefix}_{st.session_state.start_date}_to_{st.session_state.end_date}.xlsx',
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        cellsytle_jscode_operation = JsCode("function(params) {if (params.value > 5) {return {'backgroundColor': '#BBD600'}}return {'backgroundColor': 'white'}};").js_code
        cellsytle_jscode_attente = JsCode("function(params) {if (params.value > 15) {return {'backgroundColor': '#1B698D','color':'white'}}return {'backgroundColor': 'white'}};").js_code

        gb = GridOptionsBuilder.from_dataframe(df_to_display)
        gb.configure_column("Temps Moyen d'Operation (MIN)", cellStyle=cellsytle_jscode_operation)
        gb.configure_column("Temps Moyen d'Attente (MIN)", cellStyle=cellsytle_jscode_attente)

        gb.configure_default_column(
            flex=1,
            minWidth=180,
            groupable=True,
            enableRowGroup=True,
            aggFunc='sum',
            editable=False,
            filter=True
        )
        
        if 'Longitude' in df_to_display.columns:
            gb.configure_column('Longitude', hide=True)
        if 'Latitude' in df_to_display.columns:
            gb.configure_column('Latitude', hide=True)

        custom_css = {
            ".ag-theme-alpine.headers1": {
                "--ag-header-height": "30px",
                "--ag-header-foreground-color": "white",
                "--ag-header-background-color": "black",
                "--ag-header-cell-hover-background-color": "rgb(80, 40, 140)",
                "--ag-header-cell-moving-background-color": "rgb(80, 40, 140)",
            },
            ".ag-theme-alpine.headers1 .ag-header": {"font-family": "cursive"},
            ".ag-theme-alpine.headers1 .ag-header-group-cell": {"font-weight": "normal", "font-size": "22px"},
            ".ag-theme-alpine.headers1 .ag-header-cell": {"font-size": "18px"}
        }
        
        gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren=True)
        gb.configure_side_bar()
        gridOptions = gb.build()

        grid_response = AgGrid(
            df_to_display,
            height=500,
            gridOptions=gridOptions,
            allow_unsafe_jscode=True,
            enable_enterprise_modules=False,
            theme='alpine',
            custom_css=custom_css
        )

        selected_rows = grid_response['selected_rows']
        if selected_rows is not None and not selected_rows.empty:
            selected_df = pd.DataFrame(selected_rows)
            selected_df.drop(columns=['_selectedRowNodeInfo'], inplace=True, errors='ignore')
            
            st.write("Télécharger la sélection en format Excel :")
            buffer_selected = create_excel_buffer(selected_df)
            st.download_button(
                label="📥 Télécharger la sélection",
                data=buffer_selected,
                file_name=f'Selection_{file_prefix}_{st.session_state.start_date}_to_{st.session_state.end_date}.xlsx',
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key='download_selected'
            )
        else:
            st.info("Sélectionnez une ou plusieurs lignes dans le tableau pour télécharger une sélection.")
    else:
        st.warning(f"Aucune donnée disponible pour la vue : '{selected_view_name}'.")

# ==============================================================================
# --- ONGLET 2 : VISUALISATION ET EXPORT DES DONNÉES BRUTES ---
# ==============================================================================
elif selected_tab == GLOBAL_TABS[1]:
    st.markdown("### 🔍 Analyse & Export des Données Brutes")
    
    if not df_queue_filtered.empty:
        # Forcer le calcul propre sur le dataframe actuellement filtré par la sidebar
        total_lignes = int(df_queue_filtered.shape[0])
        
        # Affichage sans espaceur complexe pour éviter les bugs de chaînes
        st.metric(label="Nombre total de lignes filtrées", value=f"{total_lignes}")
        st.markdown("<br/>", unsafe_allow_html=True)
        
        all_columns = list(df_queue_filtered.columns)
        
        # Colonnes pré-sélectionnées par défaut
        default_cols = [col for col in [
    'UserName', 'FirstName', 'LastName', 'Date_Reservation', 
    'Date_Appel', 'Date_Fin', 'TempAttenteMoyen', 'TempsAttenteReel', 
    'TempOperation', 'Nom', 'NomService', 'TypeOperationId', 
    'AgenceId', 'NomAgence',"Capacites",'Region',"IsMobile",'HeureFermeture', 'Longitude', 'Latitude'
] if col in all_columns]
        if not default_cols:
            default_cols = all_columns[:5]

        # Multi-sélecteur de colonnes
        selected_cols = st.multiselect(
            "Sélectionnez les colonnes brutes à afficher et exporter :",
            options=all_columns,
            default=default_cols
        )
        
        if selected_cols:
            df_brute_visu = df_queue_filtered[selected_cols]
            
            # Bouton de téléchargement CSV placé au-dessus du tableau
            csv_data = df_brute_visu.to_csv(index=False, sep=';').encode('utf-8-sig')
            st.download_button(
                label="📥 Télécharger les colonnes sélectionnées en CSV",
                data=csv_data,
                file_name=f'Donnees_Brutes_{st.session_state.start_date}_to_{st.session_state.end_date}.csv',
                mime='text/csv',
                key='download_csv_brute'
            )
            
            st.markdown("<br/>", unsafe_allow_html=True)
            # Affichage de l'aperçu
            st.dataframe(df_brute_visu, use_container_width=True)
        else:
            st.warning("Veuillez sélectionner au moins une colonne.")
    else:
        st.info("Aucune donnée brute disponible pour la sélection actuelle.")