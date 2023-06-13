#libraries

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
import folium
import numpy as np

from haversine import haversine
from datetime import datetime
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Empresa', layout='wide')

#========================================================
#funções
#========================================================
def clean_code(df1):
    """limpeza do data frame
    
    1. remoção de dados 'NaN'
    2. mudança do type das colunas
    3. remoção de espaços
    4. formatação coluna datas
    5. limpeza coluna do tempo (remoção do texto 'min')
    """
    
    linhas_selecionadas = df1['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :]
    
    linhas_selecionadas = df1['Road_traffic_density'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :]
    
    linhas_selecionadas = df1['City'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :]
    
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
  
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format = '%d-%m-%Y')

    linhas_selecionadas = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, :]
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)
    
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()

    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)
    
    return df1

def avg_dist(df1):
    cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
    df1['distance'] = df1.loc[:, cols].apply(lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
            
    avg_distance = np.round(df1['distance'].mean(), 2)
                
    return avg_distance
                                             
def delivery_festival_yes(df1):                                 
    dfaux = (df1.loc[:, ['Time_taken(min)', 'Festival']]
                         .groupby('Festival')
                         .agg({'Time_taken(min)': ['mean', 'std']}))

    dfaux.columns = ['avg_time', 'std_time']
    dfaux = dfaux.reset_index()
    dfaux = np.round(dfaux.loc[dfaux['Festival'] == 'Yes', 'avg_time'], 2)
                                             
    return dfaux
                                             
def std_festival_yes(df1):
    dfaux = (df1.loc[:, ['Time_taken(min)', 'Festival']]
                     .groupby('Festival')
                     .agg({'Time_taken(min)': ['mean', 'std']}))
            
    dfaux.columns = ['avg_time', 'std_time']
    dfaux = dfaux.reset_index()
    dfaux = np.round(dfaux.loc[dfaux['Festival'] == 'Yes', 'std_time'], 2)
                                             
    return dfaux
                                             
def delivery_festival_no(df1):
    dfaux = (df1.loc[:, ['Time_taken(min)', 'Festival']]
                     .groupby('Festival')
                     .agg({'Time_taken(min)': ['mean', 'std']}))
            
    dfaux.columns = ['avg_time', 'std_time']
    dfaux = dfaux.reset_index()
    dfaux = np.round(dfaux.loc[dfaux['Festival'] == 'No', 'avg_time'], 2)
                
    return dfaux 
                                             
def std_festival_no(df1):                                
    dfaux = (df1.loc[:, ['Time_taken(min)', 'Festival']]
                     .groupby('Festival')
                     .agg({'Time_taken(min)': ['mean', 'std']}))
            
    dfaux.columns = ['avg_time', 'std_time']
    dfaux = dfaux.reset_index()
    dfaux = np.round(dfaux.loc[dfaux['Festival'] == 'No', 'std_time'], 2)                                             
    
    return dfaux
                                             
def graffic(df1):                                 
    dfaux = (df1.loc[:, ['City', 'Time_taken(min)']]
                     .groupby('City')
                     .agg({'Time_taken(min)' : ['mean', 'std']}))
    dfaux.columns = ['avg_time', 'std_time']
    dfaux = dfaux.reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(name = 'Control', x=dfaux['City'], y=dfaux['avg_time'], error_y = dict(type = 'data', array = dfaux['std_time'])))
    fig.update_layout(barmode='group')
    
    return fig
                                             
def graffic2(df1):
    dfaux = (df1.loc[:, ['City', 'Time_taken(min)', 'Type_of_order']]
                     .groupby(['City', 'Type_of_order'])
                     .agg({'Time_taken(min)' : ['mean', 'std']}))
    dfaux.columns = ['avg_time', 'std_time']
    dfaux = dfaux.reset_index()
            
    return dfaux
                                             
def location(df1):
    cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
    df1['distance'] = df1.loc[:, cols].apply(lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
    avg_distance = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
    fig = go.Figure(data = [go.Pie(labels = avg_distance['City'], values = avg_distance['distance'], pull = [0, 0.1, 0])])
    
    return fig

def location2(df1):
    dfaux = (df1.loc[:, ['City', 'Time_taken(min)', 'Road_traffic_density']]
                     .groupby(['City', 'Road_traffic_density'])
                     .agg({'Time_taken(min)' : ['mean', 'std']}))
    dfaux.columns = ['avg_time', 'std_time']
    dfaux = dfaux.reset_index()
                     
    fig = px.sunburst(dfaux, path=['City', 'Road_traffic_density'], values='avg_time', color='std_time', color_continuous_scale='RdBu', color_continuous_midpoint=np.average(dfaux['std_time']))
            
    return fig                                            

#========================================================
#importar dataset
#========================================================
df = pd.read_csv('dataset/train.csv')

#========================================================
#limpando dados
#========================================================
df1 = clean_code(df)
#========================================================
#barra Lateral
#========================================================

st.header('Marketplace - Visão Restaurantes')

#image_path = 'C:/Users/rapha/repos/logo.png'
image = Image.open('logo.png')
st.sidebar.image(image, width = 120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')

date_slider = st.sidebar.slider(
    'Até qual data?',
    value = datetime(2022, 4, 19),
    min_value = datetime(2022, 2, 11),
    max_value = datetime(2022, 4, 6),
    format = 'DD-MM-YYYY')

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default = ['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown("""---""")

weather_options = st.sidebar.multiselect(
    'Quais as condições climáticas?',
    ['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy', 'conditions Sunny', 'conditions Windy'],
    default = ['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy', 'conditions Sunny', 'conditions Windy'])

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered BY Comunidade DS')

#filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

#filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

#filtro de clima
linhas_selecionadas = df1['Weatherconditions'].isin(weather_options)
df1 = df1.loc[linhas_selecionadas, :]

#========================================================
#layout streamlit
#========================================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title('Overal Metrics')
        
        col1, col2, col3, col4, col5, col6 = st.columns (6)
        
        with col1:
            delivery_unique = len(df1.loc[:, 'Delivery_person_ID'].unique())
            col1.metric('Entregadores', delivery_unique)
                    
        with col2:
            avg_distance = avg_dist(df1)
            col2.metric('A distancia media das entregas', avg_distance)
            
        with col3:
            dfaux = delivery_festival_yes(df1)                                 
            col3.metric('Tempo Médio de Entrega c/ Festival', dfaux)
                                             
        with col4:
            dfaux = std_festival_yes(df1)
            col4.metric('STD Médio de Entrega c/ Festival', dfaux)
            
        with col5:
            dfaux = delivery_festival_no(df1)
            col5.metric('Tempo Médio de Entrega s/ Festival', dfaux)
            
        with col6:
            dfaux = std_festival_no(df1)
            col6.metric('STD Médio de Entrega s/ Festival', dfaux)                                 
            
    with st.container():
        st.markdown("""___""")
        col1, col2 = st.columns(2)
        
        with col1:
            fig = graffic(df1)
            st.plotly_chart(fig)                                 
            
        with col2:
            dfaux = graffic2(df1)                                
            st.dataframe(dfaux)
        
    with st.container():
        st.markdown("""___""")
        st.title('Time Distribution')
        
        col1, col2, = st.columns(2)
        
        with col1:
            fig = location(df1)                                 
            st.plotly_chart(fig)                                 
            
        with col2:
            fig = location2(df1)
            st.plotly_chart(fig)                                 
            