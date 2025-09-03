# pages/3_📊_Tableau_Global.py
import streamlit as st
from shared_code import *
from st_aggrid.shared import JsCode


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

st.markdown("<h1 style='text-align: center;'>Tableau de Bord Global</h1>", unsafe_allow_html=True)

st.markdown("<br/><br/>", unsafe_allow_html=True)

Kpi=df_all_filtered.groupby("NomService")["UserName"].nunique().reset_index()
Kpi = Kpi.rename(columns={"UserName": "Nombre_Agents"})



cols = st.columns(len(Kpi))  # une colonne par service
for i, row in Kpi.iterrows():
    with cols[i]:
        st.metric(label="Nombre Agents " + row["NomService"], value=row["Nombre_Agents"])

st.markdown("<br/>", unsafe_allow_html=True)

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
    

    # --- 3. JavaScript for Conditional Formatting ---
    # Use JsCode to define JavaScript functions for cell styling
    # Green background for "Temps Moyen d'Operation (MIN)" > 5
    cellsytle_jscode_operation = JsCode("function(params) {if (params.value > 5) {return {'backgroundColor': '#BBD600'}}return {'backgroundColor': 'white'}};").js_code

    # Blue background for "Temps Moyen d'Attente (MIN)" > 15
    cellsytle_jscode_attente = JsCode("function(params) {if (params.value > 15) {return {'backgroundColor': '#1B698D','color':'white'}}return {'backgroundColor': 'white'}};").js_code

    
    # Build the GridOptions
    gb = GridOptionsBuilder.from_dataframe(AGG)

    # Apply the conditional styling
    gb.configure_column("Temps Moyen d'Operation (MIN)", cellStyle=cellsytle_jscode_operation)
    gb.configure_column("Temps Moyen d'Attente (MIN)", cellStyle=cellsytle_jscode_attente)

    # Configure all columns to be flexible and have a minimum width
    gb.configure_default_column(
        flex=1,
        minWidth=200,
        groupable=True,
        enableRowGroup=True,
        aggFunc='sum',
        editable=False,
        filter=True          # <-- ACTIVER LE FILTRE
       
    )

    # Hide Longitude and Latitude by default (users can unhide from the sidebar)
    gb.configure_column('Longitude', hide=True)
    gb.configure_column('Latitude', hide=True)
    
    




    custom_css = {
    ".ag-theme-alpine.headers1": {
        "--ag-header-height": "30px",
        "--ag-header-foreground-color": "white",
        "--ag-header-background-color": "black",
        "--ag-header-cell-hover-background-color": "rgb(80, 40, 140)",
        "--ag-header-cell-moving-background-color": "rgb(80, 40, 140)",
    },
    ".ag-theme-alpine.headers1 .ag-header": {
        "font-family": "cursive"
    },
    ".ag-theme-alpine.headers1 .ag-header-group-cell": {
        "font-weight": "normal",
        "font-size": "22px"
    },
    ".ag-theme-alpine.headers1 .ag-header-cell": {
        "font-size": "18px"
    }
}


   
    
    # Add other interactive features
    gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren=True)
    gb.configure_side_bar()

    gridOptions = gb.build()

    # Display the AgGrid table
    grid_response=AgGrid(
        AGG,
        height=500,
        gridOptions=gridOptions,
        
        allow_unsafe_jscode=True,
        enable_enterprise_modules=False,
        theme='alpine',
        custom_css=custom_css
)

    

    selected_rows = grid_response['selected_rows']
    
    # 2. If rows are selected, create a new DataFrame and a download button.
    if not selected_rows is None:
        if not selected_rows.empty  :
            # Create a DataFrame from the list of dictionaries.
            selected_df = pd.DataFrame(selected_rows)
            
            # The selected rows include an internal Ag-Grid column, let's drop it.
            # The column is named '_selectedRowNodeInfo'
            selected_df.drop(columns=['_selectedRowNodeInfo'], inplace=True, errors='ignore')
            
            
            st.write("Télécharger en format Excel la sélection:")
            
            buffer = create_excel_buffer(selected_df)
            st.download_button(
            label="📥 Télécharger en Excel",
            data=buffer,
            file_name=f'Selected_{st.session_state.start_date}_to_{st.session_state.end_date}.xlsx',
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        else:
            st.info("Veuillez sélectionner une ou plusieurs lignes dans le tableau pour activer le téléchargement.")
