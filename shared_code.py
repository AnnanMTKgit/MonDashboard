# shared_code.py
import streamlit as st
import pandas as pd
import numpy as np
import pyodbc
from datetime import datetime
import folium
from streamlit_folium import st_folium
from streamlit_echarts import st_echarts,JsCode
import altair as alt
import plotly.graph_objects as go
import io 
from openpyxl.utils import get_column_letter ##
from openpyxl.worksheet.table import Table, TableStyleInfo ##
import plotly.express as px

# Variable de couleurs


# --- Configuration Globale du Thème des Graphiques ---
BackgroundGraphicColor = "#FAFAFA"
GraphicPlotColor = "#FFFFFF"
GraphicTitleColor = 'black'
OutsideBarColor = 'black'
InsideBarColor = 'black'





# --- Classes et Fonctions de Connexion BDD (depuis query.py et sql.py) ---

class SQLQueries:
    def __init__(self):
        # ... (copiez votre classe SQLQueries ici)
        self.AllQueueQueries = f""" SELECT u.FirstName,u.LastName,u.UserName,q.Date_Reservation,q.Date_Appel,q.TempAttenteMoyen,DATEDIFF(second, q.Date_Reservation, q.Date_Appel) as TempsAttenteReel,
    q.Date_Fin,DATEDIFF(second, q.Date_Appel, q.Date_Fin) as TempOperation,q.IsMobile,e.Nom ,s.NomService,t.Label as Type_Operation,r.ReservationParHeure,
    r.AgenceId,a.NomAgence,a.Capacites,a.Longitude,a.Latitude ,a.HeureFermeture, rg.Label Region FROM reservation r LEFT JOIN TypeOperation t ON t.Id=r.TypeOperationId LEFT JOIN queue q ON r.id = q.reservationId
    LEFT JOIN Service s ON r.ServiceId = s.Id LEFT JOIN [User] u ON u.Id = q.userId LEFT JOIN Etat e ON e.Id = q.EtatId LEFT JOIN Agence a ON a.Id = r.AgenceId LEFT JOIN Region rg ON rg.Id=a.RegionId
    WHERE Date_Reservation is not NULL and CAST(q.Date_Reservation AS DATE) BETWEEN CAST(? AS datetime) AND CAST(? AS datetime) 
    ORDER BY q.Date_Reservation DESC; """

        self.ProfilQueries = f"""SELECT
      U.[FirstName]
      ,U.[LastName]
      ,U.[PhoneNumber]
      ,U.[UserName]
      ,U.[Token] as MotDePasse
      ,R.Label as Profil
      ,a.NomAgence
  FROM [User] U  LEFT JOIN [Role] R ON U.[RoleId]= R.Id LEFT JOIN Agence a ON a.Id = U.AgenceId"""
       
        self.RendezVousQueries = f"""SELECT RPH.Id
      ,[HeureReservation]
      ,[NumeroHeureReservation]
      ,[HeureAppel]
      ,[Date_Fin]
      ,[Date_Appel]
      ,[ReservationID]
      ,[userId]
      ,[TempAttenteMoyen]
      ,e.Nom
      ,[IsMobile]
      
  FROM [dbo].[ReservationParHeure] RPH LEFT JOIN Etat e ON e.Id = RPH.EtatId
  WHERE HeureReservation is not NULL and CAST(HeureReservation AS DATE) BETWEEN CAST(? AS datetime) AND CAST(? AS datetime) 
  """ 
        
        self.AllAgences = f"""SELECT [Id]
      ,[NomAgence]
      ,[Adresse]
      ,[codeAgence]
      ,[Pays]
      ,[RegionId]
      ,[Longitude]
      ,[Latitude]
      ,[StructureID]
      ,[NbClientByDay]
      ,[Status]
      ,[Capacites]
      ,[Telephone]
      ,[HeureDemarrage]
      ,[HeureFermeture]
      ,[SuspensionActivite]
      ,[ActivationReservation]
      ,[nombreLimitReservation]
  FROM [dbo].[Agence]"""

def create_excel_buffer(df, sheet_name="Sheet1"):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        # Écrire le DataFrame dans Excel
        df.to_excel(writer, index=False, sheet_name=sheet_name)
        worksheet = writer.sheets[sheet_name]

        # Ajuster la largeur des colonnes
        for col_num, column_title in enumerate(df.columns, start=1):
            max_length = max(
                df[column_title].astype(str).map(len).max(),  # Longueur max des données
                len(column_title)  # Longueur du titre de la colonne
            )
            adjusted_width = max_length + 2  # Ajout de marge pour lisibilité
            worksheet.column_dimensions[get_column_letter(col_num)].width = adjusted_width
            
        # Ajouter un style de table
        table = Table(
            displayName="Tableau1",
            ref=worksheet.dimensions  # Dimensions automatiques basées sur les données
        )
        style = TableStyleInfo(
            name="TableStyleMedium9",  # Style prédéfini
            showFirstColumn=False,
            showLastColumn=False,
            showRowStripes=True,  # Bandes alternées
            showColumnStripes=False
        )
        table.tableStyleInfo = style
        worksheet.add_table(table)

    # Réinitialiser le pointeur du buffer
    buffer.seek(0)
    return buffer


# Dans shared_code.py

@st.cache_resource
def get_connection():
    """Crée et met en cache la connexion à la base de données."""
    try:
        server = st.secrets['db_server']
        database = st.secrets['db_database']
        username = st.secrets['db_username']
        password = st.secrets['db_password']
        driver_name = st.secrets['db_driver'] # ex: 'ODBC Driver 17 for SQL Server'

        # FORCER le format correct pour le pilote
        # La chaîne de connexion doit avoir DRIVER={Nom du Pilote}
        # et non DRIVER='{Nom du Pilote};...'
        connection_string = (
            f"DRIVER={{{driver_name}}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password};"
        )
        
        return pyodbc.connect(connection_string, timeout=30)
    
    except Exception as e:
        st.error(f"Erreur de connexion à la base de données: {e}")
        st.info("Veuillez vérifier les points suivants :")
        st.markdown("""
            - Le pilote ODBC pour SQL Server est-il bien installé ? (voir `brew install msodbcsql17`)
            - Les informations dans votre fichier `secrets.toml` sont-elles correctes ?
            - Votre Mac est-il connecté à un réseau qui autorise l'accès au serveur de base de données (vérifiez le pare-feu) ?
        """)
        st.stop()

@st.cache_data(ttl=600) # Cache les données pour 10 minutes
def run_query(_connection, sql, params=None):
    """Exécute une requête SQL et retourne un DataFrame."""
    try:
       
        df = pd.read_sql_query(sql, _connection, index_col=None)
    except pyodbc.Error as pe:
        st.error(f"Error connecting to the database: {pe}")
        df = None
    finally:
        _connection.close()
    
    return  df

# --- Fonctions de Traitement de Données (depuis functions.py) ---

def AgenceTable(df_all,df_queue):

    ########## Journalier ##################
    
    df1=df_all.copy()
    

    df1['Période'] = df1['Date_Reservation'].dt.date
    agg1 = df1.groupby(['Période','NomAgence',"Region", 'Capacites']).agg(
    Temps_Moyen_Operation=('TempOperation', lambda x: np.round(np.mean(x)/60).astype(int)),
    Temps_Moyen_Attente=('TempsAttenteReel', lambda x: np.round(np.mean(x)/60).astype(int)),NombreTraites=('Nom',lambda x: (x == 'Traitée').sum()),NombreRejetee=('Nom',lambda x: (x == 'Rejetée').sum()),NombrePassee=('Nom',lambda x: (x == 'Passée').sum())
).reset_index()
    agg1["Temps Moyen de Passage(MIN)"]=agg1['Temps_Moyen_Attente']+agg1['Temps_Moyen_Operation']
    df2=df_queue.copy()
    df2['Période'] = df2['Date_Reservation'].dt.date
    agg2=df2.groupby(['Période','NomAgence',"Region", 'Capacites','Longitude','Latitude']).agg(NombreTickets=('Date_Reservation', np.count_nonzero),AttenteActuel=("NomAgence",lambda x: current_attente(df2,agence=x.iloc[0],HeureFermeture=df2[df2['NomAgence']==x.iloc[0]]['HeureFermeture'].values[0])),TotalMobile=('IsMobile',lambda x: int(sum(x)))).reset_index()
    
    detail=pd.merge(agg2,agg1,on=['Période','NomAgence',"Region", 'Capacites'],how='outer')
    
    ##### Global ############
    globale=detail.groupby(['NomAgence',"Region", 'Capacites','Longitude','Latitude']).agg(
    Temps_Moyen_Operation=('Temps_Moyen_Operation', lambda x: np.round(np.mean(x)).astype(int)),
    Temps_Moyen_Attente=('Temps_Moyen_Attente', lambda x: np.round(np.mean(x)).astype(int)),NombreTraites=('NombreTraites',lambda x: x.sum()),NombreRejetee=('NombreRejetee',lambda x: x.sum()),NombrePassee=('NombrePassee',lambda x: x.sum()),
    TMP=("Temps Moyen de Passage(MIN)", lambda x: np.round(np.mean(x)).astype(int)),
NombreTickets=('NombreTickets', lambda x: np.sum(x)),AttenteActuel=("AttenteActuel",lambda x: x.sum()),TotalMobile=('TotalMobile',lambda x: int(sum(x)))).reset_index()
    globale["Période"]=f"{df_queue['Date_Reservation'].min().strftime('%Y-%m-%d')} - {df_queue['Date_Reservation'].max().strftime('%Y-%m-%d')}"
    globale["Temps Moyen de Passage(MIN)"]=globale['Temps_Moyen_Attente']+globale['Temps_Moyen_Operation']
    ###########
    
    new_name={'NomAgence':"Nom d'Agence",'Capacites':'Capacité','Temps_Moyen_Operation':"Temps Moyen d'Operation (MIN)",'Temps_Moyen_Attente':"Temps Moyen d'Attente (MIN)",'NombreTraites':'Total Traités','NombreRejetee':'Total Rejetées','NombrePassee':'Total Passées','NombreTickets':'Total Tickets','AttenteActuel':'Nbs de Clients en Attente'}


    detail=detail.rename(columns=new_name)
    globale=globale.rename(columns=new_name)
    

    # order=['Période',"Nom d'Agence", "Temps Moyen d'Operation (MIN)", "Temps Moyen d'Attente (MIN)","Temps Moyen de Passage(MIN)",'Capacité','Total Tickets','Total Traités','Total Rejetées','Total Passées','TotalMobile','Nbs de Clients en Attente','Longitude','Latitude']
    # detail=detail[order]
    # globale=globale[order]
  
    globale=globale.replace(-9223372036854775808, 0)
    detail=detail.replace(-9223372036854775808, 0)
    
   
    return detail,globale
def current_attente(df_queue,agence,HeureFermeture=None):
    current_date = datetime.now().date()
    current_datetime = datetime.now()
   
# Set the time to 6:00 PM on the same day
    if HeureFermeture==None:
        six_pm_datetime = current_datetime.replace(hour=18, minute=0, second=0, microsecond=0)
    else:
        
        time_obj =datetime.strptime(HeureFermeture, "%H:%M").time()
        six_pm_datetime=datetime.combine(current_date, time_obj)

    if current_datetime > six_pm_datetime:
    
        return 0
    else:
        var='En attente'
        
        df = df_queue.query(
        f"(Nom == @var) & (Date_Reservation.dt.strftime('%Y-%m-%d') == '{current_date}') & (NomAgence == @agence)"
    )
        number=len(df)
        return number


# --- Composants UI Partagés ---

def load_and_display_css():
    """Charge le fichier CSS consolidé."""
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def create_sidebar_filters(df_agences):
    """Crée la sidebar avec les filtres communs et retourne les valeurs sélectionnées."""
    st.sidebar.image("assets/logo.png", width=150)
    st.sidebar.title("Tableau de Bord Marlodj")
    
    start_date = st.sidebar.date_input("Date Début", datetime.now().date())
    end_date = st.sidebar.date_input("Date Fin", datetime.now().date())

    if start_date > end_date:
        st.sidebar.error("La date de début ne peut pas être après la date de fin.")
        st.stop()
        
    available_agencies = df_agences['NomAgence'].unique()
    selected_agencies = st.sidebar.multiselect(
        'Agences',
        options=available_agencies,
        default=list(available_agencies)
    )

    st.sidebar.markdown("---")
    st.sidebar.info(f"Utilisateur : {st.session_state.username}")
    if st.sidebar.button("Déconnexion"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()

    st.sidebar.markdown("""
        <div style="position: fixed; bottom: 0; left: 0; width: 17rem; padding: 10px; text-align: center; font-size: 0.9rem;">
            Copyright Obertys 2025
        </div>
    """, unsafe_allow_html=True)

    return start_date, end_date, selected_agencies

# --- Fonctions de Visualisation Partagées ---

@st.cache_data
def create_folium_map(agg):
    legend_html = ''  # Variable pour stocker la légende HTML
    
    df=agg.copy()
    df['Temps_Moyen_Attente']=df['Temps_Moyen_Attente'].fillna(' ')
    # Définition des couleurs uniques par NomAgence
    agences = list(df["NomAgence"].unique())
    couleurs = [
        'blue', 'green', 'purple', 'orange', 'darkred', 'red',
        'cadetblue', 'darkpurple', 'pink', 'lightblue', 'lightgreen', 
        'gray', 'black', 'darkblue'
    ]

    agence_couleur = {
        agence: couleurs[i % len(couleurs)] 
        for i, agence in enumerate(agences)
    }
    # 4. Déterminer la vue initiale de la carte
    if df.empty or df["Latitude"].isnull().all() or df["Longitude"].isnull().all():
        map_location = [14.4974, -14.4524] # Centre du Sénégal
        map_zoom = 6
    else:
        map_location = [df["Latitude"].mean(), df["Longitude"].mean()]
        map_zoom = 7

    # 5. Créer l'objet carte en utilisant la position sauvegardée si elle existe
    m = folium.Map(
        location= map_location,
        zoom_start= map_zoom,
        control_scale=True,
        prefer_canvas=True,
        width="100%",
        height="100%"
    )
    # Générer des polygones et marqueurs par ville
    for ville, group in df.groupby("Region"):
        min_lat, max_lat = group["Latitude"].min(), group["Latitude"].max()
        min_lon, max_lon = group["Longitude"].min(), group["Longitude"].max()

        # Définition du polygone (bounding box)
        polygon_coords = [
            [min_lat, min_lon], [max_lat, min_lon],
            [max_lat, max_lon], [min_lat, max_lon],
            [min_lat, min_lon]
        ]
        folium.Polygon(
            locations=polygon_coords,
            color="black",
            fill=True,
            fill_color="gray",
            fill_opacity=0.2,
            popup=f"Zone: {ville}"
        ).add_to(m)

        # Ajouter les marqueurs avec popups
        for _, row in group.iterrows():
            popup_text = (
                f"<b>Région:</b> {row['Region']}<br>"
                f"<b>Nom Agence:</b> {row['NomAgence']}<br>"
                f"<b>Client en Attente:</b> {row['AttenteActuel']} <br>"
                f"<b>Temps Moyen d'Attente:</b> {row['Temps_Moyen_Attente']} min"
            )

            folium.Marker(
                location=[row["Latitude"], row["Longitude"]],
                tooltip=popup_text,  # Affichage au survol
                popup=folium.Popup(popup_text, max_width=300),
                icon=folium.Icon(color=agence_couleur[row["NomAgence"]], icon="info-sign")
            ).add_to(m)

    return m  


def echarts_satisfaction_gauge(queue_length, title="Client(s) en Attente",max_length=100,key="1"):
    value = int(queue_length)
    max_value = int(max_length)

    

    # Ensure splitNumber is within a reasonable range for ECharts
    final_split_number = 1
    
    # --- Determine Pointer Color based on Gauge Progress ---
    current_percentage = value / max_value
    
    pointer_color = '#FF0000' if value >= max_value else ('white' if current_percentage ==0 else
        '#00CC96' if current_percentage < 0.5 else "#FFA500" if current_percentage < 0.8 else "#EF553B"
    )
    
    status={"white":'Vide','#00CC96':"Modérement occupée",'#FFA500':"Fortement occupée","#EF553B":"Très fortement occupée ",'#FF0000':'Congestionnée'}



    options = {
        "backgroundColor":BackgroundGraphicColor,
        "graphic": [ # <--- Ajout du composant graphique pour le texte
            {
                "type": "text",
                "left": "center",
                "top": "-1%", # Ajustez cette valeur pour positionner le texte
                "style": {
                    "text": status[pointer_color],
                    "font": "20px sans-serif", # Taille et police du texte
                    "fill": pointer_color # Couleur du texte
                },
                "z": 100 # Assure que le texte est au-dessus des autres éléments
            }
        ],
        "series": [
            {
                "type": "gauge",
                "max": max_value,  # Set the maximum value of the gauge
                "splitNumber": final_split_number, # <--- Corrected to use the calculated value
                "radius":'90%', # Hardcoded
                "axisLine": {
                    "lineStyle": {
                        "width": 30, # Hardcoded
                        "color": [
                            [0.5 , '#BEE0F9'],  # 0-50% Green (was Blue)
                            [0.8 , "#BEE0F9"],  # 50-80% Orange (was Yellow)
                            [1  , "#BEE0F9"]     # 80-100% Red (was Green)
                        ]
                    }
                },
                "progress": {
                    "show": True,
                    "width": 30 # Hardcoded
                },
                "detail": {
                    "valueAnimation": True,
                    "formatter": '{value}',
                    "color": 'auto',
                    "fontSize": 50, # Hardcoded
                    "offsetCenter": [0, '70%'] # Hardcoded
                },
                "data": [{"value": value, "name": title}],
                "title": {
                    "show": True,
                    "offsetCenter": [0, '100%'], # Hardcoded
                    "fontSize": 20, # Hardcoded
                   'color': GraphicTitleColor # Hardcoded
                },
                "axisTick": {
                    "show": False
                },
                "splitLine": {
                    "show": False
                },
                "axisLabel": {
                    "show": True,
                    "distance": 10, # Hardcoded
                    "formatter": '{value}',
                   'color': GraphicTitleColor,
                    "fontSize": 15 # Hardcoded
                },
                "itemStyle": {
                    "color": "#1976D2" #pointer_color
                     
                }
            }
        ]
    }
    # Ensure st_echarts is imported
    # from streamlit_echarts import st_echarts
    st_echarts(options=options, height="280px", key=key)


def stacked_chart(data,type:str,concern:str,titre,w=1000,h=400):
    """
    Default values of type:
    'TempsAttenteReel' and 'TempOperation'
    """
    df=data.copy()
    df=df.sample(n=min(5000, len(data)),replace=False)
    df = df.dropna(subset=[type])

    top_categories=['0-5min','5-10min','>10min']
    color_scale = alt.Scale(
        domain=top_categories,  # The top categories you want to color specifically
        range=['#00CC96',"#FFA500","#EF553B"]   # Replace with the colors you want to assign to each category
    ) 
      
    if concern=='UserName':
        x='Agent(s)'
    else:
        x='Agence(s)'
    if type=='TempsAttenteReel' or concern=='NomAgence':
        
        df['Categorie'] = df[type].apply(lambda x: 
        '0-5min' if 0 <= np.round(x/60).astype(int) <= 5 else 
        '5-10min' if 5 < np.round(x/60).astype(int) <= 10 else 
        '>10min'
    )
        df=df.groupby([f'{concern}', 'Categorie']).size().reset_index(name='Count')
        
       
        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X(f'{concern}:O', title=f'{x}'),
            y=alt.Y('Count:Q', title='Nombre'),
            color=alt.Color('Categorie:N', title='Queue',sort=top_categories,scale=color_scale),
            order=alt.Order('Categorie:N',title='Queue')  # Ensures the stacking order
        ).properties(
            width=1000,
            height=400,
            title={
        "text": f"{titre} par {x}",
        "anchor": "middle",
        "fontSize": 16,
        "font": "Helvetica",
       'color': GraphicTitleColor
    }
       
            
        ).configure(
    background=BackgroundGraphicColor   # Set the background color for the entire figure
)
    else:
        
        df['Type_Operation'] = df['Type_Operation'].fillna('Inconnu')
        # Ensure Categorie is correctly assigned based on TempOperation (in minutes)
        df[type] = df[type].apply(lambda x: np.round(x / 60).astype(int))

        df['Categorie'] = df[type].apply(
            lambda x: 
            '0-5min' if 0 <= x <= 5 else 
            '5-10min' if 5 < x <= 10 else 
            '>10min'
        )
  
        


        # Group by UserName and Categorie, count the occurrences
        df_count = df.groupby([f'{concern}', 'Categorie']).size().reset_index(name='Count')

        # Calculate the top 2 TypeOperation and corresponding TempOperation (now in minutes) per UserName and Categorie
        # top_operations = df.groupby([f'{concern}', 'Categorie', 'Type_Operation'])[type].agg(
        #     lambda x: np.round(x.mean()).astype(int)
        # ).reset_index(name=type)
        #top_operations = top_operations.sort_values([f'{concern}', 'Categorie', type], ascending=[True, True, False])

        top_operations = df.groupby(['UserName', 'Categorie', 'Type_Operation', type]).size().reset_index(name='OperationCount')
        top_operations = top_operations.sort_values(['UserName', 'Categorie', type], ascending=[True, True, False])
        top_operations = top_operations.groupby([f'{concern}', 'Categorie']).head(5)
        
        if len(top_operations)==0:
            chart = alt.Chart(top_operations).mark_bar().encode(
            x=alt.X(f'{concern}:O', title=f'{x}'),
            y=alt.Y('Count:Q', title='Nombre par Categorie'),
            color=alt.Color('Categorie:N', title='Queue',sort=top_categories,scale=color_scale),
            order=alt.Order('Categorie:N',title='Queue'),  # Ensures the stacking order
            tooltip=[
                alt.Tooltip('UserName:O', title=f'{x}'),
                alt.Tooltip('Count:Q', title='Nombre'),
                alt.Tooltip('Categorie:N', title='Queue'),
                alt.Tooltip('TopOperations:N', title='5 premières opérations')
            ]
        ).properties(
            width=1000,
            height=400,
         title={
        "text": f"{titre} par {x}",
        "anchor": "middle",
        "fontSize": 16,
        "font": "Helvetica",
       'color': GraphicTitleColor
    }
        ).configure(
    background=BackgroundGraphicColor   # Set the background color for the entire figure
) 
            return chart

        # Combine the TypeOperation, TempOperation, and OperationCount into a single string for tooltips
        top_operations['TopOperations'] = top_operations.apply(
    lambda row: f"{row['Type_Operation']} ({row[type]} min, {row['OperationCount']} fois)", axis=1
)
        top_operations = top_operations.groupby([f'{concern}', 'Categorie'])['TopOperations'].apply(lambda x: ', '.join(x)).reset_index()
        #top_operations = top_operations.groupby([f'{concern}', 'Categorie'])['TopOperations'].apply(lambda x: '\n'.join(x)).reset_index()
        #top_operations = top_operations.groupby([f'{concern}', 'Categorie'])['TopOperations'].apply(lambda x: '\n'.join([f"({op}, {count} fois)" for op, count in x.value_counts().items()])).reset_index()

        #st.table(top_operations)
        
        # Merge the top operations back with the count dataframe
        df_final = pd.merge(df_count, top_operations, on=[f'{concern}', 'Categorie'], how='left')
        #st.dataframe(df_final)
        # Create the Altair chart with tooltips

        chart = alt.Chart(df_final).mark_bar().encode(
            x=alt.X(f'{concern}:O', title=f'{x}'),
            y=alt.Y('Count:Q', title='Nombre par Categorie'),
            color=alt.Color('Categorie:N', title='Queue',sort=top_categories,scale=color_scale),
            order=alt.Order('Categorie:N',title='Queue'),  # Ensures the stacking order
            tooltip=[
                alt.Tooltip('UserName:O', title=f'{x}'),
                alt.Tooltip('Count:Q', title='Nombre'),
                alt.Tooltip('Categorie:N', title='Queue'),
                alt.Tooltip('TopOperations:N', title='5 premières opérations')
            ]
        ).properties(
            width=w,
            height=h,
         title={
        "text": f"{titre}",
        "anchor": "middle",
        "fontSize": 16,
        "font": "Helvetica",
       'color': GraphicTitleColor
    }
        ).configure(
    background=BackgroundGraphicColor   # Set the background color for the entire figure
)
    return chart

def TempsPassage(data):
    """
    Default values of type:
    'TempsAttenteReel' and 'TempOperation'
    """
    df=data.copy()
    df=df.sample(n=min(5000, len(data)),replace=False)
    df['TempsAttenteReel'] = df['TempsAttenteReel'].dropna()
    df['TempOperation'] = df['TempOperation'].dropna()
    df['TempsPassage']=df['TempsAttenteReel']+df['TempOperation']
    
    
    df['Categorie'] = df['TempsPassage'].apply(lambda x: 
    '0-30min' if 0 <= np.round(x/60).astype(int) <= 30 else 
    '30min-1h' if 30 < np.round(x/60).astype(int) <= 60 else 
    '>1h'
)
    df=df.groupby(['NomAgence', 'Categorie']).size().reset_index(name='Count')
    top_categories=['0-30min','30min-1h','>1h']
    color_scale = alt.Scale(
        domain=top_categories,  # The top categories you want to color specifically
        range=['#00CC96',"#FFA500","#EF553B"]  # Replace with the colors you want to assign to each category
    )
        
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X(f'NomAgence:O', title=f'Agence(s)'),
        y=alt.Y('Count:Q', title='Nombre par Categorie'),
        color=alt.Color('Categorie:N',title='Queue',sort=top_categories,scale=color_scale),
        order=alt.Order('Categorie:N',title='Queue')  # Ensures the stacking order
    ).properties(
        width=1000,
        height=400,
        title={
    "text": f"Répartition en trois du Temps de Passage par Agence",
    "anchor": "middle",
    "fontSize": 16,
    "font": "Helvetica",
   'color': GraphicTitleColor
}
        
        ).configure(
    background=BackgroundGraphicColor   # Set the background color for the entire figure
)
    return chart


def assign_to_bin(date,bins):
    date = pd.Timestamp(date).normalize()  # Convert string date to Timestamp and normalize (ignore time)
    for start, end in bins:
        start_date = pd.Timestamp(start).normalize()
        end_date = pd.Timestamp(end).normalize()
        if start_date <= date <= end_date:
            return f"{start_date.date()} to {end_date.date()}"
    return None   
def get_time_bins(min_date, max_date, bin_type):
    start_date = min_date
    time_bins = []

    if bin_type == 'Mois':
        offset = pd.DateOffset(months=1)
    elif bin_type == 'Semaine':
        offset = pd.DateOffset(weeks=1)
    elif bin_type == 'Annee':
        offset = pd.DateOffset(years=1)
    else:
        raise ValueError("bin_type must be 'month', 'week', or 'year'")

    while start_date <= max_date:
        if bin_type == 'Semaine':
            end_date = start_date + pd.DateOffset(days=6)
        else:
            end_date = (start_date + offset) - pd.DateOffset(days=1)

        # Ensure the end date does not exceed the max_date
        if end_date > max_date:
            end_date = max_date

        time_bins.append((start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))

        # Move to the next bin
        start_date = end_date + pd.DateOffset(days=1)

    return time_bins


def area_graph(data,concern='UserName',time='TempOperation',date_to_bin='Date_Fin',seuil=5,title='Courbe',w=1000,couleur=None):
    df=data.copy()
    df=df.dropna(subset=[date_to_bin])

    # Convert columns to datetime
    df['Date_Reservation'] = pd.to_datetime(df['Date_Reservation'])
    df[date_to_bin] = pd.to_datetime(df[date_to_bin])


    # Calculate the difference between the min and max dates
    min_date = df['Date_Reservation'].min()
    max_date = df['Date_Reservation'].max()
    date_diff = (max_date - min_date).days

    # Define the Time_Bin intervals based on the date difference
    if date_diff == 0:
        time_bin_labels = ['7-8h', '8-9h', '9-10h', '10-11h', '11-12h', 
                           '12-13h', '13-14h', '14-15h', '15-16h', '16-17h', '17-18h']
        unit, df['Time_Bin'] = 'Heure', pd.cut(df[date_to_bin].dt.hour, bins=range(7, 19), labels=time_bin_labels, right=False)
        df['Time_Bin'] = pd.Categorical(df['Time_Bin'], categories=time_bin_labels, ordered=True)
    elif 1 <= date_diff <=7:
        unit, df['Time_Bin'], complete_dates = 'Jour', df[date_to_bin].dt.day, range(min_date.day, max_date.day + 1)
    else:
        unit = ['Semaine', 'Mois', 'Annee'][int(date_diff > 84) + int(date_diff > 365)]
        bins = get_time_bins(min_date, max_date, unit)
        df['Time_Bin'] = df[date_to_bin].apply(lambda x: assign_to_bin(x, bins))


    # Group by Nom_Agence and Time_Bin, and calculate the average TempAttente
    #grouped_data = df.groupby([concern, 'Time_Bin'])[[time]].agg(( lambda x: np.round(np.mean(x)/60).astype(int))).reset_index()

    grouped_data = df.groupby([concern, 'Time_Bin'])[[time]].agg(lambda x: np.round(np.nanmean(x) / 60).astype(int)).reset_index()
    
    
    if len(grouped_data)==0:
        fig=go.Figure()
        fig.update_layout(
        title={
        'text': title,
        'x': 0.5,  # Center the title
        'xanchor': 'center'
             
        },plot_bgcolor=GraphicPlotColor,paper_bgcolor=BackgroundGraphicColor,
        xaxis_title=f'Intervalle de Temps en {unit}',
        yaxis_title='Temp Moyen (minutes)',
        template='plotly_dark',
        legend_title=concern,width=1000,
         xaxis=dict(
            tickvals=df['Time_Bin'].unique()  # Only show unique Time_Bin values present in agency_data
        )

    )
        return fig

    # Select the top 5 agencies with the largest area under the curve
    if len(df['NomAgence'].unique())==1 and concern=='UserName':
        top_agences=grouped_data[concern].unique()
    else:
        top_agences =grouped_data.groupby(concern)[time].sum().nlargest(5).index.tolist()
    


    # Create a DataFrame with all combinations of agencies and time bins
    if unit=="Jour":
        all_combinations = pd.MultiIndex.from_product([top_agences, sorted(complete_dates)], names=[concern, 'Time_Bin']).to_frame(index=False)
    else:
        
        all_combinations = pd.MultiIndex.from_product([top_agences, sorted(df['Time_Bin'].dropna().unique())], names=[concern, 'Time_Bin']).to_frame(index=False)

    all_combinations = pd.merge(all_combinations, grouped_data, on=[concern, 'Time_Bin'], how='left').fillna(0)
    
    
   
    # Create a figure with go.Figure
    fig = go.Figure()

    # Add traces for each agency
    for agence in top_agences:
        agency_data = all_combinations[all_combinations[concern] == agence]
        if unit=='Heure':
            agency_data = agency_data.sort_values(by='Time_Bin', key=lambda x: pd.Categorical(x, categories=time_bin_labels, ordered=True))
        fig.add_trace(go.Scatter(
            x=agency_data['Time_Bin'],
            y=agency_data[time],
            mode='lines+markers',
            fill='tozeroy',
            name=agence,
            line=dict(color=couleur) if couleur is not None else None,  # Set the color of the curve here
            marker=dict(color=couleur)if couleur is not None else None,
            showlegend=True
        ))
    
    # Update layout for better visualization
    fig.update_layout(
        title={
        'text': title,
        'x': 0.5,  # Center the title
        'xanchor': 'center'
             
        },plot_bgcolor=GraphicPlotColor,paper_bgcolor=BackgroundGraphicColor,
        xaxis_title=f'Intervalle de Temps en {unit}',
        yaxis_title='Temp Moyen (minutes)',
        template='plotly_dark',
        legend_title=concern,width=w,
         xaxis=dict(
            tickvals=all_combinations['Time_Bin'].unique()  # Only show unique Time_Bin values present in agency_data
        )

    )
    # Ajouter une ligne horizontale avec une couleur différente des courbes
    
    if unit=="Heure":
        h=all_combinations.sort_values(by='Time_Bin', key=lambda x: pd.Categorical(x, categories=time_bin_labels, ordered=True))
        h=list(h['Time_Bin'].unique())
        if len(h)!=0:
            a,b=h[0],h[-1]
        else:
            a,b=0,0
    else:
        a,b=all_combinations['Time_Bin'].min(),all_combinations['Time_Bin'].max()
    fig.add_shape(
        type="line",
        x0=a,  # Début de la ligne sur l'axe x
        x1=b,  # Fin de la ligne sur l'axe x
        y0=seuil,  # Position de la ligne sur l'axe y
        y1=seuil,  # Même que y0 pour que la ligne soit horizontale
        line=dict(color="yellow", width=2, dash="dot")  # Couleur différente (ici, noir)
    )
    
    # Display the chart in Streamlit
    return fig,a,b,seuil

def top_agence_freq(df_all,df_queue,title,color=['#00CC96',"#FFA500"]): 
    _,agg=AgenceTable(df_all,df_queue)
    agg=agg[["Nom d'Agence",title[0],title[1]]]
    

    top_counts0=agg[["Nom d'Agence",title[0]]]
    top_counts0=top_counts0.sort_values(by=title[0], ascending=False)
    top_counts0=top_counts0.head(5)
    top_counts0=top_counts0.rename(columns={title[0]:'Total'})
    top_counts0['Statut']=title[0].split(' ')[1]
    

    top_counts1=agg[["Nom d'Agence",title[1]]]
    top_counts1=top_counts1.sort_values(by=title[1], ascending=False)
    top_counts1=top_counts1.head(5)
    top_counts1=top_counts1.rename(columns={title[1]:'Total'})
    top_counts1['Statut']=title[1].split(' ')[1]
    
    
    top_counts = pd.concat([top_counts0, top_counts1], axis=0)
    
    fig = px.funnel(top_counts, x='Total', y="Nom d'Agence",color='Statut',color_discrete_sequence=color)
    fig.update_layout(title={
        'text': f'{title[0]} vs {title[1]}',
        'x': 0.5,  # Center the title
        'xanchor': 'center' # Set your desired color
        
        },plot_bgcolor=GraphicPlotColor,paper_bgcolor=BackgroundGraphicColor,
                  xaxis=dict(title='tt',tickfont=dict(size=10)),
                  yaxis=dict(title="Nom d'Agence"))
    return fig

def GraphsGlob(df_all):
    

    df=df_all.copy()
    df['TempOperation']=df['TempOperation'].fillna(0)
    df = df.groupby(by=['NomService']).agg(
    TempOperation=('TempOperation', lambda x: np.round(np.mean(x)/60).astype(int))).reset_index()


    fig_tempOp_1 = go.Figure()
   
    fig_tempOp_1.add_trace(go.Bar(go.Bar(x=df['NomService'],y=df['TempOperation'],orientation='v',text=df['TempOperation'],width=[0.6] * len(df['NomService']) , # Réduire la largeur de la barre
    textposition='inside',showlegend=False,marker=dict(color='#4169E1')
    )))


    fig_tempOp_1.update_layout(title={
        'text': "Temps Moyen d'Opération par Type de Service",
        'x': 0.5,  # Centers the title horizontally
        'xanchor': 'center',  # Ensures proper alignment
        'yanchor': 'top'  # Aligns the title vertically
    },
        xaxis=(dict(tickmode='linear')),width=400,height=400,
        plot_bgcolor=GraphicPlotColor,paper_bgcolor=BackgroundGraphicColor,
                             yaxis=(dict(title='Temps (min)',showgrid=False)))
     

    return fig_tempOp_1

def stacked_service(data,type:str,concern:str,titre="Nombre de type d'opération par Service"):
    """
    Default values of type:
    'TempsAttenteReel' and 'TempOperation'
    """
    df=data.copy()
    df=df.sample(n=min(5000, len(data)),replace=False)
    df[concern] = df[concern].apply(lambda x: 'Inconnu' if pd.isnull(x) else x)
    
    df=df.groupby([f'{type}', f'{concern}']).size().reset_index(name='Count')
    
    n=len(df[concern].unique()) 

    top_categories=df.groupby([f'{concern}'])['Count'].sum().nlargest(53).reset_index()[f'{concern}'].to_list()
    
    colors = ['#00CC96',"#FFA500","#EF553B","#FF5733", "#33FF57", "#3357FF", "#FF33A1", "#33FFF0","#FF8333", "#33FF83", "#8C33FF", "#FF3385", "#3385FF",
    "#FFBD33", "#33FFBD", "#8CFF33", "#FF33B8", "#33FFCC","#B833FF", "#FF336D", "#3385FF", "#FF8333", "#33A1FF","#FF5733", "#33FF57", "#3357FF", "#FF33A1", "#33FFF0",
    "#FF8333", "#33FF83", "#8C33FF", "#FF3385", "#3385FF","#FFD433", "#33FFD4", "#BD33FF", "#FF33BD", "#33FF99","#FF33B8", "#33A1FF", "#FFBD33", "#33D4FF", "#FF33D4",
    "#FF5733", "#33FF57", "#3357FF", "#FF33A1", "#33FFF0","#FF8333", "#33FF83", "#8C33FF", "#FF3385", "#3385FF"
]
    color_scale = alt.Scale(
        domain=top_categories,  # The top categories you want to color specifically
        range=colors   # Replace with the colors you want to assign to each category
    )


    


    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X(f'{type}:O', title='Service'),
        y=alt.Y('Count:Q', title='Nombre par Categorie'),
        color=alt.Color(f'{concern}:N', title="Type d'Opération" ,sort=top_categories,scale=color_scale   # Apply specific colors to the top three categories
        ),
        order=alt.Order('Count:N', title="Type d'Opération",sort='descending')  # Ensures the stacking order
    ).properties(
        width=600,height=400,
         title={
        "text": f"{titre}",
        "anchor": "middle",
        "fontSize": 16,
        "font": "Helvetica",
       'color': GraphicTitleColor
    }
    
    ).configure(
    background=BackgroundGraphicColor   # Set the background color for the entire figure
)
    return chart

def stacked_agent(data,type:str,concern:str,titre="Nombre de type d'opération par Agent",w=1000,h=400):
    """
    Default values of type:
    'TempsAttenteReel' and 'TempOperation'
    """
    df=data.copy()
    df=df.sample(n=min(5000, len(data)),replace=False)
    df[concern] = df[concern].apply(lambda x: 'Inconnu' if pd.isnull(x) else x)
    
    df=df.groupby([f'{type}', f'{concern}']).size().reset_index(name='Count')
    
    top_categories=df.groupby([f'{concern}'])['Count'].sum().nlargest(53).reset_index()[f'{concern}'].to_list()
    
    colors = ['#00CC96',"#FFA500","#EF553B","#FF5733", "#33FF57", "#3357FF", "#FF33A1", "#33FFF0","#FF8333", "#33FF83", "#8C33FF", "#FF3385", "#3385FF",
    "#FFBD33", "#33FFBD", "#8CFF33", "#FF33B8", "#33FFCC","#B833FF", "#FF336D", "#3385FF", "#FF8333", "#33A1FF","#FF5733", "#33FF57", "#3357FF", "#FF33A1", "#33FFF0",
    "#FF8333", "#33FF83", "#8C33FF", "#FF3385", "#3385FF","#FFD433", "#33FFD4", "#BD33FF", "#FF33BD", "#33FF99","#FF33B8", "#33A1FF", "#FFBD33", "#33D4FF", "#FF33D4",
    "#FF5733", "#33FF57", "#3357FF", "#FF33A1", "#33FFF0","#FF8333", "#33FF83", "#8C33FF", "#FF3385", "#3385FF"
]
    color_scale = alt.Scale(
        domain=top_categories,  # The top categories you want to color specifically
        range=colors   # Replace with the colors you want to assign to each category
    )
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X(f'{type}:O', title='Agent(s)'),
        y=alt.Y('Count:Q', title='Nombre par Categorie'),
        color=alt.Color(f'{concern}:N', title="Type d'Opération",sort=top_categories,scale=color_scale),
        order=alt.Order(f'Count:N', title="Type d'Opération",sort='descending')  # Ensures the stacking order
    ).properties(
        width=w,
        height=h,
        title={
        "text": f"{titre}",
        "anchor": "middle",
        "fontSize": 16,
        "font": "Helvetica",
       'color': GraphicTitleColor
    }
       
    ).configure(
    background=BackgroundGraphicColor   # Set the background color for the entire figure
)

    return chart

def Top10_Type(df_queue):
    df=df_queue.copy()
    df['Type_Operation'] = df['Type_Operation'].apply(lambda x: 'Inconnu' if pd.isnull(x) else x)

    
    top_counts = df['Type_Operation'].value_counts().reset_index()
    top_counts=top_counts.sort_values(by='Type_Operation', ascending=False)
    top_counts=top_counts.head(10)
    top_counts = top_counts.iloc[::-1]
    
    
    fig = go.Figure()
    if top_counts.empty==False:
        valmax=top_counts['Type_Operation'].max()
        
        dfmax=top_counts[top_counts['Type_Operation'].apply(lambda x:(x>=100) and (valmax-x<=100))]
    
        dfmin=top_counts[top_counts['Type_Operation'].apply(lambda x:(x<100) or (valmax-x>100))]
    # Ajouter les barres pour les valeurs < 100
        
        # Ajouter les barres pour les valeurs >= 100
        fig.add_trace(go.Bar(go.Bar(x=dfmin['Type_Operation'], y=dfmin['index'],orientation='h',text=dfmin['Type_Operation'],
        textposition='outside',showlegend=False,textfont=dict(color=OutsideBarColor),marker=dict(color='#00CC96'))
        ))
        fig.add_trace(go.Bar(go.Bar(x=dfmax['Type_Operation'], y=dfmax['index'],orientation='h',text=dfmax['Type_Operation'],
        textposition='inside',showlegend=False,textfont=dict(color=InsideBarColor),marker=dict(color='#00CC96'))
        ))

    fig.update_layout(title={
        'text': "Top 10 Type d'Opération en nombre de clients",
        'x': 0.5,  # Centers the title horizontally
        'xanchor': 'center',  # Ensures proper alignment
        'yanchor': 'top'  # Aligns the title vertically
    },plot_bgcolor=GraphicPlotColor,paper_bgcolor=BackgroundGraphicColor,
                  xaxis=dict(title='Nombre de Clients',tickfont=dict(size=10)),width=400,height=400,margin=dict(l=150, r=50, t=50, b=150),
                  yaxis=dict(title='Type'))
    
    return fig


# Plotting with Plotly
def find_highest_peak(df, person):
        df_person = df[df['UserName'] == person]
        max_row = df_person.loc[df_person['count'].idxmax()]
        return max_row['Date_Reservation']
def find_value_peak(df, person):
        df_person = df[df['UserName'] == person]
        return df_person['count'].max()



def plot_line_chart(df):
    if len(df['Date_Reservation'].dt.date.unique())==1:

        grouped = df.groupby('UserName').size().reset_index(name='count')
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=grouped['UserName'],
            y=grouped['count'],
            mode='lines+markers+text',
            text=grouped.apply(lambda row: f" {row['count']}", axis=1),
            textposition='top center',
            marker=dict(size=10,color='#4169E1'),
            name='Total Count'
            

        ))

        fig.update_layout(
            xaxis=dict(title='Agent(s)',tickfont=dict(size=10)),
            yaxis=dict(title="Nombre d'Opération"),margin=dict(l=150, r=20, t=30, b=150),
            title={
        'text': "Nombre d'Opération par Agent",
        'x': 0.5,  # Center the title
        'xanchor': 'center',
             'font': {
            'color': GraphicTitleColor  # Set your desired color
        }}
        ,plot_bgcolor=GraphicPlotColor,paper_bgcolor=BackgroundGraphicColor,
            showlegend=False,height=500
        )
        
    
    else:

        df['date'] = df['Date_Reservation'].dt.date

        filtered_df = df

        # Agréger les données par jour et par personne
        aggregated_df = filtered_df.groupby(['UserName', 'date']).size().reset_index(name='count')
        
        aggregated_df['Date_Reservation'] = aggregated_df['UserName'] + ' = ' + aggregated_df['date'].astype(str)
       
        # Récupération des dates des pics les plus élevés pour chaque personne
        peak_dates = {person: find_highest_peak(aggregated_df, person) for person in aggregated_df['UserName'].unique()}

        # Filtrage des dates d'abscisse pour n'afficher que les dates des pics
        peak_date_strings = [date for date in peak_dates.values()]
        
        agg=aggregated_df.loc[aggregated_df.groupby('UserName')['count'].idxmax()]

        # Créer le graphique
        
        fig = px.line(aggregated_df, x='Date_Reservation', y='count', color='UserName',line_group='UserName', title='Nombre d\'Opération par Agent', markers=True)
        fig.update_xaxes(
        tickmode='array',
        tickvals=[date for date in peak_dates.values()],
        ticktext=peak_date_strings
       )  
    
        fig.add_trace(go.Scatter(
            x=agg['Date_Reservation'],
            y=agg['count'],
            mode='text',
            text=agg.apply(lambda row: f" {row['count']}", axis=1),
            textposition='top center',
            marker=dict(size=10,color='#4169E1'),
            showlegend=False

        ))
        

        fig.update_layout(
            xaxis_title='Date de Pick de Client par Agent',
            yaxis_title='Nombre d\'Opérations',
            xaxis_tickangle=-45,plot_bgcolor=GraphicPlotColor,paper_bgcolor=BackgroundGraphicColor,
           
            height=500

        )
    return fig 

def create_bar_chart(df, status, title):
    
    df_filtered = df[df['Nom'] == status]
    top = df_filtered.groupby(by=['UserName']).agg(TempOperation=('TempOperation',lambda x: np.round(np.mean(x)/60))).reset_index()
    top=top.sort_values(by='TempOperation', ascending=True)

    fig = go.Figure()
    if top.empty==False:
        
        valmax=top['TempOperation'].max()
        
        dfmax=top[top['TempOperation'].apply(lambda x:(x>=10) and (valmax-x<=10))]
    
        dfmin=top[top['TempOperation'].apply(lambda x:(x<10) or (valmax-x>10))]
        
        fig.add_trace(go.Bar(go.Bar(x=dfmin['TempOperation'], y=dfmin['UserName'],orientation='h',text=dfmin['TempOperation'],
        textposition='outside',showlegend=False,marker=dict(color='#00CC96'),textfont=dict(color=OutsideBarColor))
        ))
        fig.add_trace(go.Bar(go.Bar(x=dfmax['TempOperation'], y=dfmax['UserName'],orientation='h',text=dfmax['TempOperation'],
        textposition='inside',showlegend=False,marker=dict(color='#00CC96'),textfont=dict(color=InsideBarColor))
        ))

    
        
    fig.update_layout(
    title={
        'text': f'Temps Moyen<br>Opération {status}',  # Utilisez <br> pour gérer la coupure en ligne
        'x': 0.5,  # Center the title
        'xanchor': 'center',
             'font': {
            'color': GraphicTitleColor  # Set your desired color
        }
        },
        margin={'t': 60},
    xaxis_title='Temps en minutes',
    yaxis_title='Agents',
    font=dict(
        family="Arial, sans-serif",
        size=12,
        color="white"
    ),
    plot_bgcolor=GraphicPlotColor,paper_bgcolor=BackgroundGraphicColor,
    xaxis=dict(
        showgrid=False
    
    ),height=500,
    yaxis=dict(
        showgrid=False,
    )
)   
    fig.update_traces(hovertemplate='%{label}: %{value}<extra></extra>')
    return fig
    

def create_pie_chart(df, title):

    df=df[df['Nom']==title]
    top = df.groupby(by=['UserName'])['Nom'].count().reset_index()
    

    fig = go.Figure()
   
    
    if top.empty==False:
        top['LabelWithNbs'] = top['UserName'] + ' (' + top['Nom'].round(2).astype(str) + ')'

        fig.add_trace(go.Pie(
            labels=top['LabelWithNbs'],
            values=top['Nom'],
            pull=[0.1 if i == 1 else 0 for i in range(len(top))],  # Pull out the second slice ('B')
            marker=dict(colors = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA',"#FFA500", '#19D3F3', '#FF6692', '#B6E880','#FF97FF', '#FECB52'], line=dict(color='#FFFFFF', width=2)),
            textinfo='percent' ,textposition= 'inside'
        ))
    #fig = px.pie(top, values='Nom', names='UserName',color_discrete_sequence=['#636EFA', '#EF553B', '#00CC96', '#AB63FA','#FFA15A', '#19D3F3', '#FF6692', '#B6E880','#FF97FF', '#FECB52'], title=f'Personnes {title}s Par Agent')
    
    

    # Update layout for aesthetics
    fig.update_layout(
        title={
        'text': f'Personnes {title}s<br>Par Agent',
        'x': 0.5,  # Center the title
        'xanchor': 'center',
             'font': {
            'color': GraphicTitleColor  # Set your desired color
        }
        }
        ,
        legend=dict(
        title="Legend",
        itemsizing='constant',
        font=dict(size=10)
    ),height=500,
        annotations=[dict(text='', x=0.5, y=0.5, font_size=12, showarrow=False)],
        showlegend=True,
        paper_bgcolor=BackgroundGraphicColor,
        plot_bgcolor=GraphicPlotColor
    )


    fig.update_traces(hovertemplate='%{label}: %{value}<extra></extra>')
    return fig

def Graphs_pie(df_selected):
    pie=[
        create_pie_chart(df_selected, 'Traitée'),
        #create_pie_chart(df_selection, 'En attente'),
        create_pie_chart(df_selected, 'Passée'),
        create_pie_chart(df_selected, 'Rejetée')
    ]
    return pie

def Graphs_bar(df_selected):
    
    
    figs = [
        create_bar_chart(df_selected, 'Traitée', 'TempOperation/Traitée'),
        #create_bar_chart(df_selection, 'En Attente', 'En attente'),
        create_bar_chart(df_selected, 'Passée', 'TempOperation/Passée'),
        create_bar_chart(df_selected, 'Rejetée', 'TempOperation/Rejetée')
    ]
    config = {
    'staticPlot': True,  # Disable all interactive features
    'displayModeBar': False  # Hide the mode bar (but still offer the download button via Streamlit)
}
    return figs