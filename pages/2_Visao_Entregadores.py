#libraries

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
import folium

from datetime import datetime
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Entregadores', layout='wide')

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


def slow_delivery(df1):
    df2 = (df1.loc[:, ['Delivery_person_ID', 'Time_taken(min)', 'City']]
                       .groupby(['City', 'Delivery_person_ID'])
                       .max()
                       .sort_values(['City', 'Time_taken(min)'], ascending = False)
                       .reset_index())

    df2_01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    df2_02 = df2.loc[df2['City'] == 'Urban', :].head(10)
    df2_03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)

    df3 = pd.concat([df2_01, df2_02, df2_03]).reset_index(drop=True)
                
    return df3

def fast_delivery(df1):
    df2 = (df1.loc[:, ['Delivery_person_ID', 'Time_taken(min)', 'City']]
                       .groupby(['City', 'Delivery_person_ID'])
                       .min()
                       .sort_values(['City', 'Time_taken(min)'], ascending = True)
                       .reset_index())

    df2_01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    df2_02 = df2.loc[df2['City'] == 'Urban', :].head(10)
    df2_03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)

    df3 = pd.concat([df2_01, df2_02, df2_03]).reset_index(drop=True)
                
    return df3
    
def avg_traffic(df1):
    avg_traffic = (df1.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']]
                               .groupby('Road_traffic_density')
                               .agg({'Delivery_person_Ratings':['mean', 'std']}))

    avg_traffic.columns = ['Delivery_mean', 'Delivery_std']
    avg_traffic.reset_index()
                
    return avg_traffic
                
def avg_weathercondition(df1):
    avg_weathercondition = (df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']]
                                    .groupby('Weatherconditions')
                                    .agg({'Delivery_person_Ratings': ['mean', 'std']}))
            
    avg_weathercondition.columns = ['Delivery_mean', 'Delivey_std']
    avg_weathercondition.reset_index()
            
    return avg_weathercondition
                
#========================================================
#importar dataset
#========================================================
df = pd.read_csv('dataset/train.csv')

#========================================================
#limpando dados
#========================================================
df1 = clean_code(df)

#========================================================
#barra lateral
#========================================================

st.header('Marketplace - Visão Entregadores')

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
        st.title('Overall Metrics')
        
        col1, col2, col3, col4 = st.columns(4, gap='large')
        
        with col1:
            # maior idade dos entregadores
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric('Maior idade', maior_idade)
        
        with col2:
            # menor idade dos entregadores
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric('Menor idade', menor_idade)
            
        with col3:
            # melhor condição de veiculo
            melhor_condicao = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric('Melhor condição', melhor_condicao)
            
        with col4:
            # pior condição de veiculo
            pior_condicao = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric('Pior condição', pior_condicao)
        
    with st.container():
        st.markdown("""---""")
        st.title('Avalições')
        
        col1, col2 = st.columns(2, gap='large')
        
        with col1:
            st.markdown('##### Avaliação média por Entregadores')
            avg_per_delivery = (df1.loc[:, ['Delivery_person_Ratings', 'Delivery_person_ID']]
                                .groupby('Delivery_person_ID')
                                .mean()
                                .reset_index())
            
            st.dataframe(avg_per_delivery)
        
        with col2:
            st.markdown('##### Avaliação média por Transito')
            df3 = avg_traffic(df1)
            st.dataframe(df3)
            
            
        
            st.markdown('##### Avaliação média por Condição Climática')
            df3 = avg_weathercondition(df1)
            st.dataframe(df3)
            
    
    with st.container():
        st.markdown("""---""")
        st.title('Velocidade de Entrega')
        
        col1, col2 = st.columns(2, gap='large')
        
        with col1:
            st.markdown('##### Top entregadores mais rápidos')
            df3 = fast_delivery(df1)
            st.dataframe(df3)
            
        with col2:
            st.markdown('##### Top entregadores mais lentos')
            df3 = slow_delivery(df1)
            st.dataframe(df3)
            
            
            