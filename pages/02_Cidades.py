#===============================================================
#Imports
#===============================================================
import pandas as pd
import streamlit as st
from PIL import Image
import inflection
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

#===============================================================
#Dados página
#===============================================================
st.set_page_config(page_title="Cidades", page_icon=":cityscape:", layout="wide")

#===============================================================
#Dataset
#===============================================================
df_cru = pd.read_csv ("dataset/zomato.csv")
df = df_cru.copy()


#===============================================================
#Limpeza e renomeação
#===============================================================

#Apaga dados nulos e duplicados
df = df.dropna()
df = df.drop_duplicates()
#--------------------------------------------------------

#Renomeação dos nomes das colunas
def rename_columns(dataframe):
    df = dataframe.copy()
    title = lambda x: inflection.titleize(x)
    snakecase = lambda x: inflection.underscore(x)
    spaces = lambda x: x.replace(" ", "")
    cols_old = list(df.columns)
    cols_old = list(map(title, cols_old))
    cols_old = list(map(spaces, cols_old))
    cols_new = list(map(snakecase, cols_old))
    df.columns = cols_new
    return df
df = rename_columns(df)
#-------------------------------------------------------

#Aplicação do nome do país
def country_name(country_id):
    COUNTRIES = {
    1: "India",
    14: "Australia",
    30: "Brazil",
    37: "Canada",
    94: "Indonesia",
    148: "New Zeland",
    162: "Philippines",
    166: "Qatar",
    184: "Singapure",
    189: "South Africa",
    191: "Sri Lanka",
    208: "Turkey",
    214: "United Arab Emirates",
    215: "England",
    216: "United States of America",
}
    return COUNTRIES[country_id]

df["country_code"] = df["country_code"].apply(country_name)
#-------------------------------------------------------

#Criação dos nomes das cores
def color_name(color_code):
    COLORS = {
   "3F7E00": "darkgreen",
   "5BA829": "green",
   "9ACD32": "lightgreen",
   "CDD614": "orange",
   "FFBA00": "red",
   "CBCBC8": "darkred",
   "FF7800": "darkred",
}
    return COLORS[color_code]

df["rating_color"] = df["rating_color"].apply(color_name)
#-------------------------------------------------------

#Converte para string e limpa mais de um tipo de culinária
df["cuisines"] = df.loc[:, "cuisines"].astype(str).apply(lambda x: x.split(",")[0])

#-------------------------------------------------------

#===============================================================
#Barra Lateral
#===============================================================

#Logo
image = Image.open("logo_fome_zero.png")
st.sidebar.image(image, width=250)
st.sidebar.header("Fome Zero")


st.sidebar.markdown("## Filtros")

#Seleção Países
countries_select = st.sidebar.multiselect("Escolha os Países para visualizar os restaurantes",
                     df.loc[:, "country_code"].unique().tolist(),
                     default=["Brazil", "England", "Qatar", "South Africa", "Canada", "Australia"])


        
#Filtro dos países
linhas_selecionadas = df["country_code"].isin(countries_select)
df_paises = df.loc[linhas_selecionadas, :]


#===============================================================
#Layout
#===============================================================
st.header(" :cityscape: Visão Cidades")

with st.container():
    df_aux = df_paises.loc[:,["city", "restaurant_id", "country_code"]].groupby(["city", "country_code"]).count().sort_values("restaurant_id", ascending=False).reset_index()
    fig = px.bar(df_aux.head(10), x="city", y="restaurant_id", color= "country_code", title = "Top 10 cidades com mais restaurantes cadastrados", labels = {"city":"Cidades", "restaurant_id": "Quantidade de Restaurantes", "country_code": "País"})
    st.plotly_chart(fig, use_continer_width=True)

with st.container():
    
    media_alta, media_baixa = st.columns(2)
        
    with media_alta:
        df_aux = df_paises.loc[df["aggregate_rating"]>=4,["city","restaurant_id", "country_code"]].groupby(["city", "country_code"]).count().sort_values("restaurant_id", ascending=False).reset_index()
        fig = px.bar(df_aux.head(7), x="city", y="restaurant_id", color="country_code", title = "Top 7 cidades com mais restaurantes média de avaliação acima de 4", labels = {"city":"Cidades", "restaurant_id": "Quantidade de Restaurantes", "country_code": "País"})
        st.plotly_chart(fig, use_container_width=True)
    
    with media_baixa:
        df_aux = df_paises.loc[df["aggregate_rating"]<=2.5,["city","restaurant_id", "country_code"]].groupby(["city", "country_code"]).count().sort_values("restaurant_id", ascending=False).reset_index()
        fig = px.bar(df_aux.head(7), x="city", y="restaurant_id", color= "country_code", title = "Top 7 cidades com mais restaurantes média de avaliação abaixo de 2.5", labels = {"city":"Cidades", "restaurant_id": "Quantidade de Restaurantes", "country_code": "País"})
        st.plotly_chart(fig, use_container_width=True)


with st.container():
    df_aux = df_paises.loc[:, ["cuisines", "city", "country_code"]].groupby(["city", "country_code"]).nunique().sort_values("cuisines", ascending=False).reset_index()
    fig = px.bar(df_aux.head(10), x="city", y="cuisines", color= "country_code", title = "Top 10 cidades com mais restaurantes com tipos de culinária distintos", labels = {"city":"Cidades", "cuisines": "Culinária", "country_code": "País"})
    st.plotly_chart(fig, use_container_width=True)