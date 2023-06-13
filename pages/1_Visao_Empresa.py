#libraries

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
import folium

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

def country_maps(df1):
    dfaux = (df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']]
             .groupby(['City', 'Road_traffic_density'])
             .median()
             .reset_index())
    map = folium.Map()
    for index, location_info in dfaux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'],
                           location_info['Delivery_location_longitude']],
                          popup = location_info[['City', 'Road_traffic_density']]).add_to(map)
    folium_static(map, width = 1024, height = 600)

def order_share_by_week(df1): 
    dfaux01 = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    dfaux02= df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()
    dfaux = pd.merge(dfaux01, dfaux02, how = 'inner', on = 'week_of_year')
    dfaux['order_by_delivery'] = dfaux['ID'] / dfaux['Delivery_person_ID']
    fig = px.line(dfaux, x='week_of_year', y='order_by_delivery')
    
    return fig

def order_by_week(df1):
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    dfaux = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    fig = px.line(dfaux, x = 'week_of_year', y = 'ID')
        
    return fig

def traffic_order_city(df1):
    dfaux = (df1.loc[:, ['ID', 'City', 'Road_traffic_density']]
             .groupby(['City', 'Road_traffic_density'])
             .count()
             .reset_index())
    fig = px.scatter(dfaux, x='City', y='Road_traffic_density', size='ID', color='City')
    
    return fig

def traffic_order_share(df1):
    dfaux = df1.loc[:, ['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
    dfaux['entregas_perc'] = dfaux['ID'] / dfaux['ID'].sum()
    fig = px.pie(dfaux, values = 'entregas_perc', names = 'Road_traffic_density')
    
    return fig

def order_metric(df1):
    dfaux = df1.loc[:, ['ID', 'Order_Date']].groupby('Order_Date').count().reset_index()
    dfaux.columns = ['Order_Date', 'quant_entregas']
    fig = px.bar(dfaux, x = 'Order_Date', y = 'quant_entregas')
    
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
#barra lateral
#========================================================

st.header('Marketplace - Visão Empresa')

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
st.sidebar.markdown('### Powered BY Comunidade DS')

#filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

#filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

#========================================================
#layout streamlit
#========================================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        fig = order_metric(df1)        
        st.markdown('# Orders BY Day')
        st.plotly_chart(fig, use_container_width = True)
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            fig = traffic_order_share(df1)
            st.header('Traffic Order Share')
            st.plotly_chart(fig, use_container_width = True)
               
        with col2:
            fig = traffic_order_city(df1)
            st.header('Traffic Order City')
            st.plotly_chart(fig, use_container_width = True)
                            
with tab2:
    with st.container():
        st.header('Order BY Week')
        fig = order_by_week(df1)
        st.plotly_chart(fig, use_container_width = True)
        
    with st.container():
        st.header('Order Share BY Week')
        fig = order_share_by_week(df1)
        st.plotly_chart(fig, use_container_width = True)
        
with tab3:
    st.header('Country Maps')
    country_maps(df1)
    
    
    
    

