# shared_code.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import warnings
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from streamlit_folium import st_folium 
warnings.filterwarnings('ignore')
from streamlit_option_menu import option_menu
import time
import plotly.graph_objects as go
from streamlit.components.v1 import html
import pydeck as pdk
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import plotly.io as pio
import copy
import pyodbc
import altair as alt
import seaborn as sns
import plotly.figure_factory as ff
import plotly.subplots as sp
import io 
import folium
from datetime import datetime, timedelta
from openpyxl.utils import get_column_letter ##
from openpyxl.worksheet.table import Table, TableStyleInfo ##
import base64
from streamlit_echarts import st_echarts,JsCode
import math

# Variable de couleurs


# --- Configuration Globale du Thème des Graphiques ---
BackgroundGraphicColor = "white"
GraphicPlotColor = "#FFFFFF"
GraphicTitleColor = 'black'
OutsideBarColor = 'black'
InsideBarColor = 'white'

#### COLOR SPECIFIQUE A  ECOBANK###
blue_color="#022737"
green_color="#BBD600"
blue_clair_color= "#1B698D"

# colors=[blue_color,blue_clair_color,green_color,"#FF5733", "#33FF57", "#3357FF", "#FF33A1", "#33FFF0","#FF8333", "#33FF83", "#8C33FF", "#FF3385", "#3385FF",
#     "#FFBD33", "#33FFBD", "#8CFF33", "#FF33B8", "#33FFCC","#B833FF", "#FF336D", "#3385FF", "#FF8333", "#33A1FF","#FF5733", "#33FF57", "#3357FF", "#FF33A1", "#33FFF0",
#     "#FF8333", "#33FF83", "#8C33FF", "#FF3385", "#3385FF","#FFD433", "#33FFD4", "#BD33FF", "#FF33BD", "#33FF99","#FF33B8", "#33A1FF", "#FFBD33", "#33D4FF", "#FF33D4",
#     "#FF5733", "#33FF57", "#3357FF", "#FF33A1", "#33FFF0","#FF8333", "#33FF83", "#8C33FF", "#FF3385", "#3385FF"
# ]

# palette non panacher
palette_colors= ["#022737", "#083A53", "#104D6F", "#17608B", "#1B698D", "#2E86AB", "#4F9DBA", "#70B4C9", "#90CDD8", "#B0E4E7", "#D0FBFB", "#E6FCFC", "#6E7C00", "#879A00", "#A1B800", "#BBD600", "#C7DD2A", "#D3E455", "#E0EC80", "#EDF3AA", "#F6F9D5", "#2F3E46", "#4A5A63", "#65767F", "#80919C", "#9AABB8", "#B5C5D3", "#D0E0EE", "#EBF5FF", "#4C3A5A", "#6D557C", "#8E709E", "#A17FAB", "#B48ECC", "#C29AD4", "#D0A7DC", "#DDA4E3", "#00796B", "#00897B", "#26A69A", "#4DB6AC", "#80CBC4", "#B2DFDB", "#E0F2F1", "#B75D28", "#D18A00", "#E5A000", "#F7B42C", "#FFC954", "#FFDDA1", "#FFECC2", "#D4C5A3", "#E3D5B8", "#F2E5CC", "#C7007D", "#E0409A", "#F97FBA", "#FFAFD8", "#FFD6E9"]
Simple_pallette=[blue_color,blue_clair_color,green_color]
# Palette panacher 
# palette_colors=['#022737', '#BBD600', '#4C3A5A', '#083A53', '#A1B800', '#6D557C', '#104D6F', '#879A00', '#8E709E', '#17608B', '#6E7C00', '#A17FAB', '#1B698D', '#C7DD2A', '#B48ECC', '#2E86AB', '#D3E455', '#C29AD4', '#4F9DBA', '#E0EC80', '#D0A7DC', '#70B4C9', '#EDF3AA', '#DDA4E3', '#90CDD8', '#F6F9D5', '#D0FBFB', '#B0E4E7', '#D18A00', '#EBF5FF', '#2F3E46', '#E5A000', '#D4C5A3', '#4A5A63', '#F7B42C', '#E3D5B8', '#65767F', '#FFC954', '#F2E5CC', '#80919C', '#FFDDA1', '#FFECC2', '#9AABB8', '#C7007D', '#80CBC4', '#B5C5D3', '#E0409A', '#B2DFDB', '#00796B', '#F97FBA', '#E0F2F1', '#00897B', '#FFAFD8', '#90CDD8', '#26A69A', '#FFD6E9', '#B0E4E7', '#4DB6AC', '#B75D28', '#D0FBFB']
data_visualization_colors = [
    "#3498DB",  # Bleu Azur
    "#48C9B0",  # Vert Menthe
    "#013447",  # Corail Doux
    blue_color,  # Orange Safran
    "#8E7CC3",  # Lavande
    "#2A9D8F",  # Vert Marin
    "#F7C181",  # Pêche Claire
    "#5DADE2",  # Bleu Ciel
    blue_clair_color,  # Vieux Rose
    "#AF7AC5",  # Mauve
    green_color,  # Jaune Tournesol
    "#586F7C",  # Gris Ardoise
]


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
            f"DRIVER={driver_name};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f'PORT=1433;'
            f"UID={username};"
            f"PWD={password};"
        )
        
        return pyodbc.connect(connection_string)
    
    except Exception as e:
        st.error(f"Erreur de connexion à la base de données: {e}")
        st.info("Veuillez vérifier les points suivants :")
        st.markdown("""
            - Le pilote ODBC pour SQL Server est-il bien installé ? (voir `brew install msodbcsql17`)
            - Les informations dans votre fichier `secrets.toml` sont-elles correctes ?
            - Votre Mac est-il connecté à un réseau qui autorise l'accès au serveur de base de données (vérifiez le pare-feu) ?
        """)
        st.stop()


def run_query(_connection, sql, params=None):
    """
    Exécute une requête SQL en utilisant une connexion existante 
    et retourne un DataFrame Pandas.
    NE FERME PAS LA CONNEXION.
    """
    try:
        # Exécuter la requête et retourner le résultat
        df = pd.read_sql_query(sql, _connection, params=params)
        return df
    except Exception as e:
        st.error(f"Erreur lors de l'exécution de la requête : {e}")
        return pd.DataFrame() # Retourner un DataFrame vide en cas d'erreur

# --- Fonctions de Traitement de Données (depuis functions.py) ---

def AgenceTable(df_all, df_queue):
    
    # Créer des copies pour ne pas modifier les dataframes originaux
    df1 = df_all.copy()
    df2 = df_queue.copy()

    # S'assurer que les colonnes de date sont bien au format datetime
    df1['Date_Reservation'] = pd.to_datetime(df1['Date_Reservation'])
    df2['Date_Reservation'] = pd.to_datetime(df2['Date_Reservation'])
    
    ########## Journalier ##################
    df1['Période'] = df1['Date_Reservation'].dt.date
    
    # Étape 1: Agréger sans forcer la conversion en int. Les résultats seront des floats.
    agg1 = df1.groupby(['Période', 'NomAgence', "Region", 'Capacites']).agg(
        Temps_Moyen_Operation=('TempOperation', lambda x: np.mean(x) / 60),
        Temps_Moyen_Attente=('TempsAttenteReel', lambda x: np.mean(x) / 60),
        NombreTraites=('Nom', lambda x: (x == 'Traitée').sum()),
        NombreRejetee=('Nom', lambda x: (x == 'Rejetée').sum()),
        NombrePassee=('Nom', lambda x: (x == 'Passée').sum())
    ).reset_index()

    df2['Période'] = df2['Date_Reservation'].dt.date
    agg2 = df2.groupby(['Période', 'NomAgence', "Region", 'Capacites', 'Longitude', 'Latitude']).agg(
        NombreTickets=('Date_Reservation', 'count'), # 'count' est plus direct que np.count_nonzero
        AttenteActuel=("NomAgence", lambda x: current_attente(df2, agence=x.iloc[0], HeureFermeture=df2[df2['NomAgence']==x.iloc[0]]['HeureFermeture'].values[0])),
        TotalMobile=('IsMobile', 'sum')
    ).reset_index()
    
    # La fusion outer peut créer des NaN, c'est normal
    detail = pd.merge(agg2, agg1, on=['Période', 'NomAgence', "Region", 'Capacites'], how='outer')
    
    # Étape 2: Remplacer les NaN créés par 0. C'est ici la clé.
    # On cible les colonnes numériques qui peuvent avoir des valeurs manquantes.
    cols_to_fill = [
        'Temps_Moyen_Operation', 'Temps_Moyen_Attente', 'NombreTraites', 
        'NombreRejetee', 'NombrePassee', 'NombreTickets', 'TotalMobile'
    ]
    for col in cols_to_fill:
        if col in detail.columns:
            detail[col] = detail[col].fillna(0)

    # Calculer le temps de passage après avoir rempli les NaN
    detail["Temps Moyen de Passage(MIN)"] = detail['Temps_Moyen_Attente'] + detail['Temps_Moyen_Operation']

    ##### Global ############
    # Agrégation globale à partir du dataframe 'detail' déjà nettoyé
    globale = detail.groupby(['NomAgence', "Region", 'Capacites', 'Longitude', 'Latitude']).agg(
        Temps_Moyen_Operation=('Temps_Moyen_Operation', 'mean'),
        Temps_Moyen_Attente=('Temps_Moyen_Attente', 'mean'),
        NombreTraites=('NombreTraites', 'sum'),
        NombreRejetee=('NombreRejetee', 'sum'),
        NombrePassee=('NombrePassee', 'sum'),
        NombreTickets=('NombreTickets', 'sum'),
        AttenteActuel=('AttenteActuel', 'last'), # 'last' ou 'mean' selon la logique désirée
        TotalMobile=('TotalMobile', 'sum')
    ).reset_index()

    # Recalculer le temps de passage pour la vue globale
    globale["Temps Moyen de Passage(MIN)"] = globale['Temps_Moyen_Attente'] + globale['Temps_Moyen_Operation']
    
    # Définir la période pour la vue globale
    if not df_queue.empty:
        globale["Période"] = f"{df_queue['Date_Reservation'].min().strftime('%Y-%m-%d')} - {df_queue['Date_Reservation'].max().strftime('%Y-%m-%d')}"
    else:
        globale["Période"] = "N/A"

    ########### Conversion finale et renommage ###########
    
    # Liste des colonnes à arrondir et convertir en entier
    cols_to_int = [
        'Temps_Moyen_Operation', 'Temps_Moyen_Attente', 'Temps Moyen de Passage(MIN)',
        'NombreTraites', 'NombreRejetee', 'NombrePassee', 'NombreTickets', 'TotalMobile'
    ]

    for col in cols_to_int:
        if col in detail.columns:
            detail[col] = np.round(detail[col]).astype(int)
        if col in globale.columns:
            globale[col] = np.round(globale[col]).astype(int)

    new_name = {
        'NomAgence': "Nom d'Agence",
        'Capacites': 'Capacité',
        'Temps_Moyen_Operation': "Temps Moyen d'Operation (MIN)",
        'Temps_Moyen_Attente': "Temps Moyen d'Attente (MIN)",
        'NombreTraites': 'Total Traités',
        'NombreRejetee': 'Total Rejetées',
        'NombrePassee': 'Total Passées',
        'NombreTickets': 'Total Tickets',
        'AttenteActuel': 'Nbs de Clients en Attente',
        'TotalMobile': 'TotalMobile' # Renommage suggéré
    }

    detail = detail.rename(columns=new_name)
    globale = globale.rename(columns=new_name)

    # Mettre les colonnes dans l'ordre souhaité
    order = [
        'Période', "Nom d'Agence", 'Region', "Temps Moyen d'Operation (MIN)", 
        "Temps Moyen d'Attente (MIN)", "Temps Moyen de Passage(MIN)", 
        'Capacité', 'Total Tickets', 'Total Traités', 'Total Rejetées', 
        'Total Passées', 'TotalMobile', 'Nbs de Clients en Attente', 
        'Longitude', 'Latitude'
    ]
    
    # Filtrer les colonnes pour ne garder que celles qui existent dans les dataframes
    detail_order = [col for col in order if col in detail.columns]
    globale_order = [col for col in order if col in globale.columns]

    detail = detail[detail_order]
    globale = globale[globale_order]
   
    return detail, globale









# def AgenceTable(df_all,df_queue):

#     ########## Journalier ##################
    
#     df1=df_all.copy()
    
    
#     df1['Période'] = df1['Date_Reservation'].dt.date
#     agg1 = df1.groupby(['Période','NomAgence',"Region", 'Capacites']).agg(
#     Temps_Moyen_Operation=('TempOperation', lambda x: np.round(np.mean(x)/60).astype(int)),
#     Temps_Moyen_Attente=('TempsAttenteReel', lambda x: np.round(np.mean(x)/60).astype(int)),NombreTraites=('Nom',lambda x: (x == 'Traitée').sum()),NombreRejetee=('Nom',lambda x: (x == 'Rejetée').sum()),NombrePassee=('Nom',lambda x: (x == 'Passée').sum())
# ).reset_index()
#     agg1["Temps Moyen de Passage(MIN)"]=agg1['Temps_Moyen_Attente']+agg1['Temps_Moyen_Operation']
#     df2=df_queue.copy()
#     df2['Période'] = df2['Date_Reservation'].dt.date
#     agg2=df2.groupby(['Période','NomAgence',"Region", 'Capacites','Longitude','Latitude']).agg(NombreTickets=('Date_Reservation', np.count_nonzero),AttenteActuel=("NomAgence",lambda x: current_attente(df2,agence=x.iloc[0],HeureFermeture=df2[df2['NomAgence']==x.iloc[0]]['HeureFermeture'].values[0])),TotalMobile=('IsMobile',lambda x: int(sum(x)))).reset_index()
    
#     detail=pd.merge(agg2,agg1,on=['Période','NomAgence',"Region", 'Capacites'],how='outer')
    
#     ##### Global ############
#     globale=detail.groupby(['NomAgence',"Region", 'Capacites','Longitude','Latitude']).agg(
#     Temps_Moyen_Operation=('Temps_Moyen_Operation', lambda x: np.round(np.mean(x)).astype(int)),
#     Temps_Moyen_Attente=('Temps_Moyen_Attente', lambda x: np.round(np.mean(x)).astype(int)),NombreTraites=('NombreTraites',lambda x: x.sum()),NombreRejetee=('NombreRejetee',lambda x: x.sum()),NombrePassee=('NombrePassee',lambda x: x.sum()),
#     TMP=("Temps Moyen de Passage(MIN)", lambda x: np.round(np.mean(x)).astype(int)),
# NombreTickets=('NombreTickets', lambda x: np.sum(x)),AttenteActuel=("AttenteActuel",lambda x: x.sum()),TotalMobile=('TotalMobile',lambda x: int(sum(x)))).reset_index()
#     globale["Période"]=f"{df_queue['Date_Reservation'].min().strftime('%Y-%m-%d')} - {df_queue['Date_Reservation'].max().strftime('%Y-%m-%d')}"
#     globale["Temps Moyen de Passage(MIN)"]=globale['Temps_Moyen_Attente']+globale['Temps_Moyen_Operation']
#     ###########
    
#     new_name={'NomAgence':"Nom d'Agence",'Capacites':'Capacité','Temps_Moyen_Operation':"Temps Moyen d'Operation (MIN)",'Temps_Moyen_Attente':"Temps Moyen d'Attente (MIN)",'NombreTraites':'Total Traités','NombreRejetee':'Total Rejetées','NombrePassee':'Total Passées','NombreTickets':'Total Tickets','AttenteActuel':'Nbs de Clients en Attente'}


#     detail=detail.rename(columns=new_name)
#     globale=globale.rename(columns=new_name)
    

#     # order=['Période',"Nom d'Agence", "Temps Moyen d'Operation (MIN)", "Temps Moyen d'Attente (MIN)","Temps Moyen de Passage(MIN)",'Capacité','Total Tickets','Total Traités','Total Rejetées','Total Passées','TotalMobile','Nbs de Clients en Attente','Longitude','Latitude']
#     # detail=detail[order]
#     # globale=globale[order]
  
#     # globale=globale.replace(-9223372036854775808, 0)
#     # detail=detail.replace(-9223372036854775808, 0)
    
   
#     return detail,globale
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

# Dans shared_code.py

def date_range_selection():
    # Ces widgets vont lire et écrire dans st.session_state grâce à l'argument 'key'
    st.sidebar.date_input(
        "Date Début", 
        key="start_date"  # La valeur sera st.session_state.start_date
    )
    st.sidebar.date_input(
        "Date Fin", 
        key="end_date"    # La valeur sera st.session_state.end_date
    )

    if st.session_state.start_date > st.session_state.end_date:
        st.sidebar.error("La date de début ne peut pas être après la date de fin.")
        st.stop()


def filtering(df, UserName, NomService):
              
    return df.query('UserName in @UserName & NomService in @NomService')



def filter1(df_all):
    
    # Appliquer un style CSS pour restreindre la hauteur
    
    with st.sidebar:
        with st.popover("Nom des Services",use_container_width=True):

            show_multiselect = True
            if show_multiselect:
                
                NomService = st.multiselect(
        'Services',
        options=df_all['NomService'].unique(),
        default=df_all['NomService'].unique()
    )
    
        st.write(f"✅ {len(NomService)} disponible(s)")
    
    # Filter df_all based on the selected NomService
    df = df_all[df_all['NomService'].isin(NomService)]

    # UserName selection

    with st.sidebar:
        with st.popover("Nom des Agents",use_container_width=True):

            show_multiselect = True
            if show_multiselect:
                
                UserName = st.multiselect(
        'Agents',
        options=df['UserName'].unique(),
        default=df['UserName'].unique()
    )
       
        st.write(f"✅ {len(UserName)} Agent(s) en ligne")
    

    
    
    df_selection = filtering(df, UserName, NomService)
    return df_selection

def create_sidebar_filters():
    
    


    # Rendu des date_input avec valeur actuelle
    start_date = st.sidebar.date_input("Date Début", value=st.session_state.start_date, key="start_date_input")
    end_date = st.sidebar.date_input("Date Fin", value=st.session_state.end_date, key="end_date_input")

    # Mise à jour manuelle du session_state
    st.session_state.start_date = start_date
    st.session_state.end_date = end_date



    if st.session_state.start_date > st.session_state.end_date:
        st.sidebar.error("La date de début ne peut pas être après la date de fin.")
        st.stop()

    # Initialiser dans st.session_state si la clé n'existe pas
    if "selected_agencies" not in st.session_state:
        conn = get_connection()
        df_agences = run_query(conn, SQLQueries().AllAgences)
        available_agencies = df_agences['NomAgence'].unique()
        st.session_state.all_agencies = available_agencies
        st.session_state.selected_agencies = available_agencies  # valeur par défaut
    

#     st.sidebar.markdown("""
#     <style>
#     .stMultiSelect > div {
#         max-height: 120px;
#         overflow-y: auto;
#     }
#     </style>
# """, unsafe_allow_html=True)
    st.sidebar.write(' ')
    
    with st.sidebar:
        with st.popover("Agences",use_container_width=True):

            show_multiselect = True
            if show_multiselect:
                
                selected_agencies =st.multiselect('Agences', options=st.session_state.all_agencies,default=st.session_state.selected_agencies ,key="selected_agencies_input")
        st.write(f"✅ {len(selected_agencies)} agences sélectionnées")
    
    
    
    # Empêcher la désélection totale
    if len(selected_agencies) == 0:
        st.sidebar.warning("Vous devez sélectionner au moins une agence.")
        st.session_state.selected_agencies = selected_agencies
        st.stop() # st.rerun() est la version moderne de st.experimental_rerun()
    else:
        # Mise à jour de la sélection
        st.session_state.selected_agencies = selected_agencies
    
    
    
    

    #st.sidebar.markdown("<div style='position: fixed; bottom: 0; left: 0; width: 17rem; padding: 10px; text-align: center;'>Copyright Obertys 2025</div>", unsafe_allow_html=True)
# --- Fonctions de Visualisation Partagées ---


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
    
    max_gauge=100
    min_gauge=0
    
    
   
    
    # --- Determine Pointer Color based on Gauge Progress ---
    current_percentage = value / max_value
    
    pointer_color = '#FF0000' if value >= max_value else ('black' if current_percentage ==0 else
        green_color if current_percentage < 0.5 else blue_clair_color if current_percentage < 0.8 else blue_color
    )
    
    status={"black":'Vide',green_color:"Modérement occupée",blue_clair_color:"Fortement occupée",blue_color:"Très fortement occupée ",'#FF0000':'Congestionnée'}
    
    
    
    seuil_pourcentage = max_value / 100
    # Crée une petite zone rouge autour du seuil (ex: de 29% à 31% si le seuil est 30)
    debut_rouge = max(0, seuil_pourcentage - 0.01)
    fin_rouge = min(1, seuil_pourcentage + 0.01)
    

    options = {"backgroundColor":BackgroundGraphicColor,
               "title": {"text": status[pointer_color],"left": 'center',"top":'2%',
        "textStyle": {
                "color": pointer_color
            }},
    "series": [
        {   
            "type": "gauge",
            "startAngle": 200,
            "endAngle": -20,
            "min": 0,
            "max": 100,
            "splitNumber": max_gauge,
            # --- La barre de progression qui montre la valeur actuelle ---
            "progress": {
                "show": True,
                "width": 20,
                "itemStyle": {
                    "color": "transparent"
                } 
            },
            "axisLine": {
                "lineStyle": {
                    "width": 20,
                    "color": [[value/100,"#013447"],[debut_rouge, "lightblue"],[fin_rouge, "red"],[1,"lightblue"]] if (value/100)<debut_rouge else
                        
                        [[value/100, "#013447"],[fin_rouge, "red"],[1,"lightblue"]] if (value/100)<fin_rouge and (value/100)>=debut_rouge else 

                        [[debut_rouge, "#013447"],[fin_rouge, "red"],[1,"lightblue"]] if (value/100)==fin_rouge else 

                        [[debut_rouge, "#013447"],[fin_rouge, "red"],[value/100,"#013447"],[1,"lightblue"]]
                        
                }
            },
            "pointer": {
                "show": True,
                "length": "65%",
                "width": 6,
                "itemStyle": {
                    "color": "#013447"
                }
            },
        
            # --- MODIFICATION 1 : Masquer les petits traits ---
            "axisTick": {
                "show": False# On cache les petits traits de graduation internes
            },
            "splitLine": {
                "show": False
            },
            # --- MODIFICATION 2 : N'afficher que le label "30" ---
            "axisLabel": {
                "show": True, # L'axe des labels doit rester visible
                "distance": 5, # Distance du label par rapport à la jauge
                "color": blue_color, #"#333",
                "fontSize": 16,
                "interval": 0,
                # Astuce JS pour n'afficher que le label "0,100 ou max_value"
                "formatter": JsCode(f"function(value){{if(value==={min_gauge}||value==={max_gauge}||value==={max_value}){{return value;}}return '';}}").js_code
            },
            "detail": {
                "valueAnimation": True,
                "formatter": f"{value}",
                "fontSize": 60,
                "fontWeight": "bold",
                "color": pointer_color,
                "offsetCenter": [0, "100%"]
            },
            "title": {
                "show": True,
                "offsetCenter": [0, "60%"],
                "fontSize": 22,
                "color": "#333"
            },
            "data": [
                {
                    "value": value,
                    "name": "Clients en Attente"
                }
            ],
          
            
        }
    ]
}
    # Ensure st_echarts is imported
    # from streamlit_echarts import st_echarts
    st_echarts(options=options, height="280px", key='4')

################ Nouveau ###########
def stacked_chart2(data,type:str,concern:str,titre):
    """
    Default values of type:
    'TempsAttenteReel' and 'TempOperation'
    """
    df=data.copy()
    df = df.dropna(subset=[type])

    if df.empty:
        return {"title": {"text": f"(Pas de données)", "left": 'center'}}



    top_categories=['0-5min','5-10min','>10min']
    # color_scale = alt.Scale(
    #     domain=top_categories,  # The top categories you want to color specifically
    #     range=[blue_color,blue_clair_color,green_color]   # Replace with the colors you want to assign to each category
    # ) 
      
  
    if  concern=='NomAgence':
        
        df['Categorie'] = df[type].apply(lambda x: 
        '0-5min' if 0 <= np.round(x/60).astype(int) <= 5 else 
        '5-10min' if 5 < np.round(x/60).astype(int) <= 10 else 
        '>10min'
    )
        df=df.groupby([f'{concern}', 'Categorie']).size().reset_index(name='Count')
        
        df_pivoted = df.pivot_table(
        index=concern,
        columns="Categorie",
        values="Count",
        fill_value=0
    )
        options = {
            "backgroundColor":BackgroundGraphicColor,
            "title": {"text": titre,"left": 'center',
        "textStyle": {
                "color": GraphicTitleColor
            }},
            "color":Simple_pallette
            ,
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        # Get legend data from the pivoted DataFrame's columns
        "legend": {"data": df_pivoted.columns.tolist(),"left":'right'},
        "grid": {
            "left": "3%",
            "right": "6%",
            "bottom": "15%", # Increase bottom margin for rotated labels
            "containLabel": True
        },
        # X-axis uses categories from the pivoted DataFrame's index
        "xAxis": {
            "type": "category",
            "data": df_pivoted.index.tolist(),
            "axisLabel": {
                "rotate": 30,  # Rotate labels to prevent overlap
                "interval": 0  # Ensure all labels are shown
            },
            "name":"Agences"
        },
        # Y-axis is the value axis
        "yAxis": {"type": "value","name":"Valeur totale"},
        # Create a series for each column in the pivoted DataFrame
        "series": [
            {
                "name": category,
                "type": "bar",
                "stack": "total", # This key is what creates the stacking
                "label": {"show": True, "position": "inside"},
                "emphasis": {"focus": "series"},
                "data": df_pivoted[category].tolist(),
            }
            for category in df_pivoted.columns
        ],
    }
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

        top_operations = df.groupby([concern, 'Categorie', 'Type_Operation', type]).size().reset_index(name='OperationCount')
        top_operations = top_operations.sort_values(['UserName', 'Categorie', type], ascending=[True, True, False])
        top_operations = top_operations.groupby([f'{concern}', 'Categorie']).head(5)
        
        
        
        
        # Combine the TypeOperation, TempOperation, and OperationCount into a single string for tooltips
        top_operations['TopOperations'] = top_operations.apply(
    lambda row: f"{row['Type_Operation']} ({row[type]} min, {row['OperationCount']} fois)", axis=1
)
        top_operations = top_operations.groupby([f'{concern}', 'Categorie'])['TopOperations'].apply(lambda x: ', '.join(x)).reset_index()
        
        df = pd.merge(df_count, top_operations, on=[f'{concern}', 'Categorie'], how='left')
        # 2. Construct the ECharts options dictionary from the DataFrame
        
        

        # Use pivot_table to structure data for ECharts series
        df_pivot_count = df.pivot_table(index='UserName', columns='Categorie', values='Count', aggfunc='sum').fillna(0)
        df_pivot_ops = df.pivot_table(index='UserName', columns='Categorie', values='TopOperations', aggfunc='first').fillna('')

        # Define the explicit order for categories and get users
        categories_order = ['0-5min', '5-10min', '>10min']
        users = df_pivot_count.index.tolist()

        # Reorder the columns in the pivot tables to match our desired stacking order
        df_pivot_count = df_pivot_count.reindex(columns=categories_order, fill_value=0)
        df_pivot_ops = df_pivot_ops.reindex(columns=categories_order, fill_value='')


        # --- STEP 2: BUILD THE ENTIRE TOOLTIP HTML IN THE LIST COMPREHENSION ---
        # All formatting logic is now in Python, which is safer and easier to debug.
        
        
        
        tooltip_formatter_js = JsCode("function (params) {return `<b>Agent(s):</b> ${params.name}<br/><b>Queue:</b> ${params.seriesName}<br/><b>Nombre:</b> ${params.value}<br/><b>5 premières opérations:</b><br/>${params.data.operations}`;}").js_code


        series_list = [
    {
        "name": category,
        "type": "bar",
        "stack": "total",
        "emphasis": {"focus": "series"},
        "data": [
            {
                "value": int(df_pivot_count.loc[user, category]),
                # This custom property will be accessible in the tooltip formatter via @{operations}
                "operations": (df_pivot_ops.loc[user, category].replace(', ', '<br/>') or 'N/A')
            }
            for user in users
        ]
    }
    for category in categories_order
]



        # Define the full ECharts options dictionary
        options = {
            "title": {
                "text": titre,
                "left": "center"
            },
            "tooltip": {
        "trigger": "item",
        "formatter": tooltip_formatter_js, # Use the template string
        "axisPointer": {"type": "shadow"},
    },
            "legend": {
                "data": categories_order,
                "top": "bottom"
            },
            "grid": {
                "left": "3%",
                "right": "6%",
                "bottom": "10%",
                "containLabel": True,
            },
            "xAxis": [
                {
                    "type": "category",
                    "data": users,
                    "axisLabel": {
                        "rotate": 45,
                        "interval": 0
                    },
                    "name":"Agents"
                }
            ],
            "yAxis": [{"type": "value", "name": "Valeur totale"}],
            "series": series_list,
        }


        
    
    return options


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
        range=[blue_color,blue_clair_color,green_color]   # Replace with the colors you want to assign to each category
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
        st.write(top_operations)
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
        st.write(df_final)
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
        range=[blue_color,blue_clair_color,green_color]  # Replace with the colors you want to assign to each category
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

################## NEW ######################




def area_graph2(data,concern='UserName',time='TempOperation',date_to_bin='Date_Fin',seuil=5,title='Courbe'):
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
    
#     seuil = st.number_input(
#     "Définir la valeur du seuil",
#     min_value=0,
#     max_value=100,
#     value=seuil, # Valeur par défaut
#     step=1
# )
    
        
    if grouped_data.empty:
        return {"title": {"text": f"(Pas de données)", "left": 'center'}}

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
    
    
    if unit=='Heure':
        all_combinations['Time_Bin'] = pd.Categorical(
            all_combinations['Time_Bin'],
            categories=time_bin_labels,
            ordered=True
        )

    df_pivoted = all_combinations.pivot_table(
        index='Time_Bin',    # This will become the x-axis
        columns=concern,     # These will become the different series (lines)
        values=time          # These are the y-axis values
    ).reset_index() # .reset_index() makes 'Time_Bin' a column again

        # --- 3. BUILD ECHARTS OPTIONS ---
    # Let's also add some colors, similar to your `couleur` variable
    colors = ['#5470C6', '#91CC75', '#EE6666', '#73C0DE', '#3BA272']

    options = {"backgroundColor": GraphicPlotColor,
    "title": {"text": title,"left": 'center',
    "textStyle": {
            "color": GraphicTitleColor
        }},
    "tooltip": {"trigger": "axis"},
    "legend": {"data": top_agences,'orient':'vertical',"left": 'right'}, # Use the list of agencies for the legend
    "grid": {"left": '10%', "right": '10%', "bottom": '5%',"top":"5%", "containLabel": True},
    "toolbox": {"left": "5%", "feature": {"saveAsImage": {},"magicType": {
                "show": True,
                "type": ['line', 'bar', 'stack'], # Types de graphiques interchangeables
                "title": {
                    "line": "Passer en lignes",
                    "bar": "Passer en barres",
                    "stack": "Empiler"
                }
            }}},
    "xAxis": {
        "type": "category",
        "boundaryGap": False,
        "data": df_pivoted['Time_Bin'].tolist(), # X-axis from the pivoted table
    },
    "yAxis": {"type": "value"},
    
    "series": [
        {
            "name": agence,
            "type": "line",
            "areaStyle": {},  # This is equivalent to Plotly's fill='tozeroy'
            "emphasis": {"focus": "series"},
            "data": df_pivoted[agence].tolist(), # Get data for each agency from its column
            "lineStyle": {"color": colors[i % len(colors)]}, # Assign a color
            "itemStyle": {"color": colors[i % len(colors)]}, # Color for markers
            "markLine":{
            "silent": True,               # La ligne n'est pas cliquable/interactive
            "symbol": "none",             # Cache les flèches aux extrémités de la ligne
            "lineStyle": {
                "type": "dashed",         # 'dashed' pour des tirets, 'dotted' pour des points
                "color": "#333",          # Couleur de la ligne (gris foncé)
                "width": 2                # Épaisseur de la ligne
            },
            "data": [
                {
                    "yAxis": seuil, # Positionne la ligne sur l'axe Y à la valeur du seuil
                    "name": "Seuil",      # Nom utilisé pour l'étiquette
                    "label": {
                        "show": True,
                        "position": "end",  # Affiche l'étiquette à la fin de la ligne
                        "formatter": "{b}: {c}", # Format: 'Nom: Valeur' (ex: "Seuil: 25")
                        "color": "#333",
                        "fontSize": 14
                    }
                }
            ]
        }
        }
        for i, agence in enumerate(top_agences) # Loop through agencies to build the series list
    ],
}
    return options
    









#################################################

def top_agence_freq(df_all,df_queue,title,color=[green_color,blue_clair_color]): 
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

def GraphsGlob2(df_all,titre="",color=blue_color):
    

    df=df_all.copy()
    df['TempOperation']=df['TempOperation'].fillna(0)
    df = df.groupby(by=['NomService']).agg(
    TempOperation=('TempOperation', lambda x: np.round(np.mean(x)/60).astype(int))).reset_index()

 
    df = df.rename(columns={'TempOperation': "value", 'NomService': "name"})
   
    chart_data = df.to_dict(orient='records')
    

    # --- CORRECTED ECHARTS OPTIONS ---
    options = {
        "backgroundColor": GraphicPlotColor,
        "title": {
            "text": f"{titre}", # Made title more descriptive
            "left": 'center',
            "textStyle": {
                "color": GraphicTitleColor
            }
        },
        "color":color,
        "tooltip": {
            "trigger": 'axis',  # 'axis' trigger is better for bar charts
            "axisPointer": {
                "type": 'shadow' 
            },
            # CORRECTED: Removed '{d}%' which is for pie charts
            "formatter": '{b}: {c} min' 
        },
        "toolbox": {
            "show": True,
            "orient": "vertical",
            "left": "right",
            "top": "center",
            "feature": {
                "mark": {"show": True},
                "dataView": {"show": True, "readOnly": False},
                "restore": {"show": True},
                "saveAsImage": {"show": True}
            }
        },
        # ADDED: Bar charts require an xAxis and yAxis
        "xAxis": {
            "type": 'value', # The axis with numbers
            "boundaryGap": [0, 0.01],
            "axisLabel": {
                "color": GraphicTitleColor,
                "formatter": '{value} min' # Add units to the axis
            }
        },
        "yAxis": {
            "type": 'category', # The axis with names/labels
            # Data for the category axis is automatically taken 
            # from the 'name' field in the series data
            "data": [item['name'] for item in chart_data],
            "axisLabel": {
                "color": GraphicTitleColor
            }
        },
        "series": [
            {
                "name": 'Temps moyen', # A more descriptive series name
                "type": 'bar',
                # REMOVED: 'radius' is not a bar chart property
                "data": chart_data,
                "emphasis": {
                    "focus": 'series',
                    "itemStyle": {
                        "shadowBlur": 10,
                        "shadowOffsetX": 0,
                        "shadowColor": 'rgba(0, 0, 0, 0.5)'
                    }
                }
            }
        ],
        # Optional: Add a grid to control padding
        "grid": {
            "left": '0%',
            "right": '0%',
            "bottom": '3%',
            "containLabel": True
        }
    } 
    return options

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
    
    
    color_scale = alt.Scale(
        domain=top_categories,  # The top categories you want to color specifically
        range=palette_colors   # Replace with the colors you want to assign to each category
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

def stacked_agent2(data,type:str,concern:str,titre="Nombre de type d'opération par Agent"):
    """
    Default values of type:
    'TempsAttenteReel' and 'TempOperation'
    """
    df=data.copy()
    df[type] = df[type].apply(lambda x: 'Inconnu' if pd.isnull(x) else x)
    
    df=df.groupby([f'{concern}',f'{type}']).size().reset_index(name='Count')
    
    top_categories=df[type].unique()
    
    # Apply this filter to the dataframe. This is the key step that was missing.
    df_filtered = df[df[type].isin(top_categories)]
    
    
    # If filtering removed all data, handle it gracefully
    if df_filtered.empty:
        return {"title": {"text": f"(Pas de données)", "left": 'center'}}

        
    # Pivot the *filtered* data for charting
    df_pivoted = df_filtered.pivot_table(
        index=concern,
        columns=type,
        values="Count",
        fill_value=0
    )
    tooltip_formatter_js = JsCode("function(params){var agentName=params[0].name;var html=`<b>${agentName}</b><br/>`;let nonZeroSeries=params.filter(p=>p.value>0);nonZeroSeries.sort((a,b)=>b.value-a.value);let top10Series=nonZeroSeries.slice(0,10);if(top10Series.length===0){html+='Aucune valeur non-nulle';return html;}top10Series.forEach(p=>{html+=`${p.marker} ${p.seriesName}: <b>${p.value}</b><br/>`;});if(nonZeroSeries.length>10){html+=`... et ${nonZeroSeries.length-10} autre(s)`;}return html;}").js_code
    
    
    options = {
        "backgroundColor":BackgroundGraphicColor,
        "title": {"text": titre,"left": 'center',
    "textStyle": {
            "color": GraphicTitleColor
        }},
        "color":data_visualization_colors,
    "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}, "formatter": tooltip_formatter_js },
    # Get legend data from the pivoted DataFrame's columns
    #"legend": {"data": df_pivoted.columns.tolist(),"left":'right'},
    "grid": {
        "left": "3%",
        "right": "4%",
        "bottom": "6%", # Increase bottom margin for rotated labels
        "containLabel": True
    },
    # X-axis uses categories from the pivoted DataFrame's index
    "xAxis": {
        "type": "category",
        "data": df_pivoted.index.tolist(),
        "axisLabel": {
            "rotate": 30,  # Rotate labels to prevent overlap
            "interval": 0  # Ensure all labels are shown
        },
    },
    # Y-axis is the value axis
    "yAxis": {"type": "value"},
    # Create a series for each column in the pivoted DataFrame
    "series": [
        {
            "name": category,
            "type": "bar",
            "stack": "total", # This key is what creates the stacking
            #"label": {"show": True, "position": "inside"},
            "emphasis": {"focus": "series"},
            "data": df_pivoted[category].tolist(),
        }
        for category in df_pivoted.columns
    ],
}


    return options

def Top10_Type(df_queue,title=""):
    df=df_queue.copy()
    if df.empty:
        return {"title": {"text": f"(Pas de données)", "left": 'center'}}
    df['Type_Operation'] = df['Type_Operation'].apply(lambda x: 'Inconnu' if pd.isnull(x) else x)

    
    top_counts = df['Type_Operation'].value_counts().reset_index()
    top_counts=top_counts.sort_values(by='Type_Operation', ascending=False)
    top_counts=top_counts.head(10)
    top_counts = top_counts.iloc[::-1]

    # Renaming is also correct for ECharts
    top_counts= top_counts.rename(columns={'Type_Operation': "value", 'index': "name"})
    
    chart_data = top_counts.to_dict(orient='records')

    # --- CORRECTED ECHARTS OPTIONS ---
    options = {
        "backgroundColor": GraphicPlotColor,
        "title": {
            "text": title, # Made title more descriptive
            "left": 'center',
            "textStyle": {
                "color": GraphicTitleColor
            }
        },
        "color":green_color,
        "tooltip": {
            "trigger": 'axis',  # 'axis' trigger is better for bar charts
            "axisPointer": {
                "type": 'shadow' 
            },
            # CORRECTED: Removed '{d}%' which is for pie charts
            "formatter": '{b}: {c} ' 
        },
        "toolbox": {
            "show": True,
            "orient": "vertical",
            "left": "right",
            "top": "center",
            "feature": {
                "mark": {"show": True},
                "dataView": {"show": True, "readOnly": False},
                "restore": {"show": True},
                "saveAsImage": {"show": True}
            }
        },
        # ADDED: Bar charts require an xAxis and yAxis
        "xAxis": {
            "type": 'value', # The axis with numbers
            "boundaryGap": [0, 0.01],
            "axisLabel": {
                "color": GraphicTitleColor,
                "formatter": '{value}' # Add units to the axis
            }
        },
        "yAxis": {
            "type": 'category', # The axis with names/labels
            # Data for the category axis is automatically taken 
            # from the 'name' field in the series data
            "data": [item['name'] for item in chart_data],
            "axisLabel": {
                "color": GraphicTitleColor
            }
        },
        "series": [
            {
                "name": "Type d'Opération", # A more descriptive series name
                "type": 'bar',
                "label": {"show": True, "position": "inside"},
                # REMOVED: 'radius' is not a bar chart property
                "data": chart_data,
                "emphasis": {
                    "focus": 'series',
                    "itemStyle": {
                        "shadowBlur": 10,
                        "shadowOffsetX": 0,
                        "shadowColor": 'rgba(0, 0, 0, 0.5)'
                    }
                }
            }
        ],
        # Optional: Add a grid to control padding
        "grid": {
            "left": '0%',
            "right": '0%',
            "bottom": '3%',
            "containLabel": True
        }
    } 
    return options


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
            marker=dict(size=10,color=blue_color),
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
            marker=dict(size=10,color=blue_color),
            showlegend=False

        ))
        

        fig.update_layout(
            xaxis_title='Date de Pick de Client par Agent',
            yaxis_title='Nombre d\'Opérations',
            xaxis_tickangle=-45,plot_bgcolor=GraphicPlotColor,paper_bgcolor=BackgroundGraphicColor,
           
            height=500

        )
    return fig 


 
 ###################   NOUVEAU ###################

def create_bar_chart2(df, status,color=blue_color):
    df_filtered = df[df['Nom'] == status]
    
    if df_filtered.empty:
        return {"title": {"text": f"(Pas de données)", "left": 'center'}}

    # Your data processing is correct
    top = df_filtered.groupby(by=['UserName']).agg(
        TempOperation=('TempOperation', lambda x: np.round(np.mean(x) / 60))
    ).reset_index()
    top = top.sort_values(by='TempOperation', ascending=True)

    # Renaming is also correct for ECharts
    top = top.rename(columns={'TempOperation': "value", 'UserName': "name"})
   
    chart_data = top.to_dict(orient='records')
    

    # --- CORRECTED ECHARTS OPTIONS ---
    options = {
        "backgroundColor": GraphicPlotColor,
        "title": {
            "text": f"Temps moyen d'opération {status}", # Made title more descriptive
            "left": 'center',
            "textStyle": {
                "color": GraphicTitleColor
            }
        },
        "color":color,
        "tooltip": {
            "trigger": 'axis',  # 'axis' trigger is better for bar charts
            "axisPointer": {
                "type": 'shadow' 
            },
            # CORRECTED: Removed '{d}%' which is for pie charts
            "formatter": '{b}: {c} min' 
        },
        "toolbox": {
            "show": True,
            "orient": "vertical",
            "left": "right",
            "top": "center",
            "feature": {
                "mark": {"show": True},
                "dataView": {"show": True, "readOnly": False},
                "restore": {"show": True},
                "saveAsImage": {"show": True}
            }
        },
        # ADDED: Bar charts require an xAxis and yAxis
        "xAxis": {
            "type": 'value', # The axis with numbers
            "boundaryGap": [0, 0.01],
            "axisLabel": {
                "color": GraphicTitleColor,
                "formatter": '{value} min' # Add units to the axis
            }
        },
        "yAxis": {
            "type": 'category', # The axis with names/labels
            # Data for the category axis is automatically taken 
            # from the 'name' field in the series data
            "data": [item['name'] for item in chart_data],
            "axisLabel": {
                "color": GraphicTitleColor
            }
        },
        "series": [
            {
                "name": 'Temps moyen', # A more descriptive series name
                "type": 'bar',
                # REMOVED: 'radius' is not a bar chart property
                "data": chart_data,
                "emphasis": {
                    "focus": 'series',
                    "itemStyle": {
                        "shadowBlur": 10,
                        "shadowOffsetX": 0,
                        "shadowColor": 'rgba(0, 0, 0, 0.5)'
                    }
                }
            }
        ],
        # Optional: Add a grid to control padding
        "grid": {
            "left": '0%',
            "right": '0%',
            "bottom": '3%',
            "containLabel": True
        }
    } 
    return options
    

def create_pie_chart2(df, title='Traitée'):
   
    df=df[df['Nom']==title]
    if df.empty:
        return {"title": {"text": f"(Pas de données)", "left": 'center'}}
    top = df.groupby(by=['UserName'])['Nom'].count().reset_index()
    top=top.rename(columns={'Nom':"value",'UserName':"name"})
    
    chart_data = top.to_dict(orient='records')
    options = {
    "backgroundColor": GraphicPlotColor,
    
    "title": {
        "text": title,
        "left": 'center',
        "textStyle": {
                "color": GraphicTitleColor
            }
    },
    

  "toolbox": {
            "show": True,
            "feature": {
                "mark": {"show": True},
                "dataView": {"show": True, "readOnly": False},
                "restore": {"show": True},
                "saveAsImage": {"show": True}
            }
        },
  
  
  "tooltip": {"left": "10%", 
   " trigger": 'item',
   "formatter": '{a} <br/>{b}: {c} ({d}%)', # Example of a nice formatter
   
  },
  
  "series": [
    {
      "name": 'Nom et Score',
      "type": 'pie',
      "radius": '50%',
      "data": chart_data,
      "emphasis": {
        "itemStyle": {
          "shadowBlur": 10,
          "shadowOffsetX": 0,
          "shadowColor": 'rgba(0, 0, 0, 0.5)'
        }
      }
    }
  ]
} 
    return options
    



def circle(input_text,input_response,list_2color):
    source = pd.DataFrame({
      "Topic": ['', input_text],
      "% value": [100-input_response, input_response]
  })
    source_bg = pd.DataFrame({
        "Topic": ['', input_text],
        "% value": [100, 0]
    })
        
    plot = alt.Chart(source).mark_arc(innerRadius=45, cornerRadius=25).encode(
        theta="% value",
        color= alt.Color("Topic:N",
                        scale=alt.Scale(
                            #domain=['A', 'B'],
                            domain=[input_text, ''],
                            # range=['#29b5e8', '#155F7A']),  # 31333F
                            range=list_2color),
                        legend=None)
    ).properties(width=130, height=130)
        
        
    text = plot.mark_text(align='center', color="#29b5e8", font="Lato", fontSize=32, fontWeight=700, fontStyle="italic").encode(text=alt.value(f'{input_response}'))
    plot_bg = alt.Chart(source_bg).mark_arc(innerRadius=45, cornerRadius=20).encode(
        theta="% value",
        color= alt.Color("Topic:N",
                        scale=alt.Scale(
                            # domain=['A', 'B'],
                            domain=[input_text, ''],
                            range=list_2color),  # 31333F
                        legend=None),
    ).properties(width=130, height=130)

    return plot_bg + plot + text 



def ServiceTable(df,status="Traitée"):
    df1=df.copy()
    df1=df1[df1["Nom"]==status]
    agg = df1.groupby(['UserName']).agg(
    TMO=('TempOperation', lambda x: np.round(np.mean(x)/60).astype(int)),NombreTickets=('Nom','size'),
TotalMobile=('IsMobile',lambda x: (x==1).sum())).reset_index()
    
    
    return agg

def plot_metrics(df,status,var):
    agg = ServiceTable(df,status)
    if agg.empty:
        
        Delta = ''
        st.metric(label=status, value=None, delta=None)
    else:

        Value = agg[var]
        Delta = ''
        st.metric(label=status, value=Value, delta=Delta)





def service_congestion(df_queue,color=[green_color, '#12783D'],title=False):
  
   
  agence=df_queue["NomAgence"].iloc[0]
  if not title:
    title=df_queue["NomService"].iloc[0]
  
  HeureFermeture=df_queue['HeureFermeture'].iloc[0]
  queue_length=current_attente(df_queue,agence,HeureFermeture)
  #max_length=df_queue['Capacites'].iloc[0]
  
#   percentage = (queue_length / max_length) * 100

#   chart_color  = ['#FF0000', '#781F16'] if queue_length >= max_length else (['#FFFFFF', '#D5D5D5']  if percentage ==0 else  
#         [green_color, '#12783D'] if percentage < 50 else [blue_clair_color, '#BF6B3D'] if percentage < 80 else [blue_color, '#B03A30']   
#     )
  #title='Vide' if chart_color==['#FFFFFF', '#D5D5D5']  else "Modérement occupée" if chart_color==[green_color, '#12783D'] else "Fortement occupée" if chart_color==[blue_clair_color, '#BF6B3D'] else "Très fortement occupée " if chart_color==[blue_color, '#B03A30'] else 'Congestionnée'
  
  input_text="Congestion"
  input_response=queue_length
  fig=circle(input_text,input_response,list_2color=color)

  st.markdown(
    f"""
    <div style="text-align: center;">
        <p style="font-size: 20px; font-weight: bold;text-decoration: underline;">{title}</p>
    </div>
    """,
    unsafe_allow_html=True
)

 
  
  
  return fig


# Dans shared_code.py

# ==============================================================================
# --- COMPOSANT "CARTE DE STATUT D'AGENCE" ---
# ==============================================================================


# --- 1. Refined get_status function to return emoji, CSS class, text, and plot color ---
def get_status_info(clients, capacite):
    
    if capacite == 0: # Handle division by zero if capacity can be zero
        return "status-led-black"
    
    ratio = clients / capacite
    
    if ratio == 0: 
        return  "status-led-white" 
    elif ratio < 0.5: 
        return  "status-led-green"
    elif ratio < 0.8: 
        return "status-led-orange"
    elif ratio < 1: 
        return  "status-led-red"
    else:   
        return  "status-led-blue"



# ==============================================================================
# --- FIN DU COMPOSANT ---
# ==============================================================================





def option_agent(df_all_service,df_queue_service):
        df=df_all_service.copy()
        # nom=df["LastName"].iloc[0]
        # prenom=df['FirstName'].iloc[0]
        # nom_service=df["NomService"].iloc[0]
        
        # st.sidebar.markdown(f'SERVICE : :orange[ {nom_service}]')
        # #st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
        # st.sidebar.markdown(f'UTILISATEUR : :blue[  {prenom} {nom}]')
        # #st.sidebar.markdown(f"## Utilisateur :  {prenom} {nom}")
        st.sidebar.markdown("<br><br>", unsafe_allow_html=True) 
        # CSS styling
        st.markdown("""
<style>



[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}

[data-testid="stMetric"] {
    background-color: #393939;
    text-align: center;
    padding: 15px 0;
}

[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
}

[data-testid="stMetricDeltaIcon-Up"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

</style>
""", unsafe_allow_html=True)

        col = st.columns((1.25, 5.25, 1), gap='medium')
        with col[0]:
            
            st.markdown(
    f"""
    <div style="text-align: center;">
        <p style="font-size: 20px; font-weight: bold;text-decoration: underline;">Totaux Opération</p>
    </div>
    """,
    unsafe_allow_html=True
)

            

            plot_metrics(df,'Traitée',"NombreTickets")
            plot_metrics(df,"Passée","NombreTickets")
            plot_metrics(df,"Rejetée","NombreTickets")

            
           

        with col[1]:
            c= st.columns((1.5, 1.5), gap='medium')
            with c[0]:
                fig=stacked_chart(df_all_service,'TempOperation','UserName',"Catégorisation du Temps d'opération")
                st.altair_chart(fig, use_container_width=True)  
            with c[1]:
                fig1=stacked_agent(df_all_service,type='UserName',titre="Nombre de type d'opération",concern='Type_Operation')
                st.altair_chart(fig1, use_container_width=True)
            
        with col[2]:
            st.markdown(
    f"""
    <div style="text-align: center;">
        <p style="font-size: 20px; font-weight: bold;text-decoration: underline;">File d'Attente</p>
    </div>
    """,
    unsafe_allow_html=True
)

            
           
            fig=service_congestion(df_queue_service,color=['#12783D',green_color])
            st.altair_chart(fig,use_container_width=True)
            
            
        col = st.columns((1.25, 5.25, 1), gap='medium')
        
        with col[0]:
            st.markdown(
    f"""
    <div style="text-align: center;">
        <p style="font-size: 20px; font-weight: bold;text-decoration: underline;">Temps Moy Opération (MINUTES)</p>
    </div>
    """,
    unsafe_allow_html=True
)

            
            
            agg=ServiceTable(df,"Rejetée")
            
            plot_metrics(df,'Traitée',"TMO")
            plot_metrics(df,"Passée","TMO")
            plot_metrics(df,"Rejetée","TMO")
        with col[1]:
            
            fig,_,_,_=area_graph(df_all_service,concern='UserName',time='TempOperation',date_to_bin='Date_Fin',seuil=5,title="Evolution du temps moyen de traitement",couleur='#17becf')
            
            st.plotly_chart(fig, use_container_width=True)
        

        with col[2]:

            fig1=service_congestion(df_queue_filtered,color=['#B03A30',blue_color],title='Agence')
            st.altair_chart(fig1,use_container_width=True)

        st.stop()