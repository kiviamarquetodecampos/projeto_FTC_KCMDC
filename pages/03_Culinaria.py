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
st.set_page_config(page_title="Culinárias", page_icon=":knife_fork_plate:", layout="wide")

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


        
#Quantidade restaurantes
qtde_rest = st.sidebar.slider(
        "Selecione a quantidade de Restaurantes que deseja visualizar", 1, 20, 10
    )


#Seleção Culinárias
cuisines_select = st.sidebar.multiselect("Escolha os Tipos de Culinária",
                     df.loc[:, "cuisines"].unique().tolist(),
                     default=["Home-made", "BBQ", "Japanese", "Brazilian", "Arabian", "American", "Italian"])


#Filtro dos países e culinarias
linhas_selecionadas = (df["country_code"].isin(countries_select)) & (df["cuisines"].isin(cuisines_select))
df_paises = df.loc[linhas_selecionadas, :]


#===============================================================
#Layout
#===============================================================
st.title(" :knife_fork_plate: Visão Tipos de Culinárias")

st.header("Melhores Restaurantes dos Principais tipos Culinários")

italiana, americana, arabe, japonesa, caseira = st.columns(5)

with italiana:
    df_aux = df.loc[df["cuisines"] == "Italian", [ "restaurant_id", "restaurant_name", "aggregate_rating"]].sort_values(["aggregate_rating", "restaurant_id"], ascending=[False,True]).head(1)
    restaurante = df_aux.iloc[0,1]
    nota = df_aux.iloc[0,2]
    italiana.metric(label=f'Italiana: {restaurante}', value=f'{nota}/5.0')

with americana:
    df_aux = df.loc[df["cuisines"] == "American", [ "restaurant_id", "restaurant_name", "aggregate_rating"]].sort_values(["aggregate_rating", "restaurant_id"], ascending=[False,True]).head(1)
    restaurante = df_aux.iloc[0,1]
    nota = df_aux.iloc[0,2]
    americana.metric(label=f'Americana: {restaurante}', value=f'{nota}/5.0')

with arabe:
    df_aux = df.loc[df["cuisines"] == "Arabian", [ "restaurant_id", "restaurant_name", "aggregate_rating"]].sort_values(["aggregate_rating", "restaurant_id"], ascending=[False,True]).head(1)
    restaurante = df_aux.iloc[0,1]
    nota = df_aux.iloc[0,2]
    arabe.metric(label=f'Árabe: {restaurante}', value=f'{nota}/5.0')

with japonesa:
    df_aux = df.loc[df["cuisines"] == "Japanese", [ "restaurant_id", "restaurant_name", "aggregate_rating"]].sort_values(["aggregate_rating", "restaurant_id"], ascending=[False,True]).head(1)
    restaurante = df_aux.iloc[0,1]
    nota = df_aux.iloc[0,2]
    japonesa.metric(label=f'Japonesa: {restaurante}', value=f'{nota}/5.0')

with caseira:
    df_aux = df.loc[df["cuisines"] == "Home-made", [ "restaurant_id", "restaurant_name", "aggregate_rating"]].sort_values(["aggregate_rating", "restaurant_id"], ascending=[False,True]).head(1)
    restaurante = df_aux.iloc[0,1]
    nota = df_aux.iloc[0,2]
    caseira.metric(label=f'Caseira: {restaurante}', value=f'{nota}/5.0')

with st.container():
    st.markdown(f'## Top {qtde_rest} Restaurantes')
    df_aux = df_paises.loc[:, ["restaurant_id", "restaurant_name", "country_code", "city", "cuisines", "aggregate_rating", "average_cost_for_two", "votes"]].sort_values(["aggregate_rating", "restaurant_id"], ascending=[False,True]).head(qtde_rest)
    st.dataframe(df_aux)

with st.container():
    melhor, pior = st.columns(2)
    with melhor:
        df_aux = df_paises.loc[:, ["cuisines", "aggregate_rating", "restaurant_id"]].groupby("cuisines").mean().sort_values(["aggregate_rating", "restaurant_id"], ascending=[False,True]).reset_index().head(qtde_rest)
        fig = px.bar(df_aux, x="cuisines", y="aggregate_rating", title=f"Os {qtde_rest} melhores tipos de Culinária por País", labels = {"cuisines": "Tipos de Culinária", "aggregate_rating": "Média de Avaliação"})
        st.plotly_chart(fig, use_container_width=True)
    
    with pior:
        df_aux = df_paises.loc[:, ["cuisines", "aggregate_rating", "restaurant_id"]].groupby("cuisines").mean().sort_values(["aggregate_rating", "restaurant_id"], ascending=[True,True]).reset_index().head(qtde_rest)
        fig = px.bar(df_aux, x="cuisines", y="aggregate_rating", title=f"Os {qtde_rest} piores tipos de Culinária por País", labels = {"cuisines": "Tipos de Culinária", "aggregate_rating": "Média de Avaliação"})
        st.plotly_chart(fig, use_container_width=True)