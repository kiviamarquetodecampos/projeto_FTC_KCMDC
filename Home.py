#===============================================================
#Imports
#===============================================================
import pandas as pd
import streamlit as st
import folium
from folium.plugins import MarkerCluster
from PIL import Image
from streamlit_folium import folium_static
import inflection
import numpy as np

st.set_page_config(page_title="Home", page_icon="📊", layout="wide")

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

st.header("Fome Zero")
st.subheader("O melhor lugar para encontrar seu mais novo restaurante favorito!")
st.markdown("### Temos as seguintes marcas dentro da nossa plataforma:")


#-------------------------------------------------------
#Dados das colunas
restaurante, pais, cidade, avaliacao, culinaria = st.columns(5)
with restaurante:
    restaurantes = df.loc[:, "restaurant_id"].shape[0]
    restaurante.metric("Restaurantes Cadastrados", restaurantes)

with pais:
    paises = df.loc[:, "country_code"].nunique()
    pais.metric("Países Cadastrados", paises)

with cidade:
    cidades = df.loc[:, "city"].nunique()
    cidade.metric("Cidades Cadastradas", cidades)

with avaliacao:
    avaliacoes = df.loc[:, "votes"].sum()
    avaliacao.metric("Avaliações Feitas", avaliacoes)

with culinaria:
    culinarias = df.loc[:, "cuisines"].nunique()
    culinaria.metric("Tipos de Culinária", culinarias)
#-------------------------------------------------------
#Mapa
f = folium.Figure(width=1920, height=1080)

m = folium.Map(max_bounds=True).add_to(f)

marker_cluster = MarkerCluster().add_to(m)

for _, line in df_paises.iterrows():

        name = line["restaurant_name"]
        price_for_two = line["average_cost_for_two"]
        cuisine = line["cuisines"]
        currency = line["currency"]
        rating = line["aggregate_rating"]
        color = f'{line["rating_color"]}'

        html = "<p><strong>{}</strong></p>"
        html += "<p>Price: {},00 ({}) para dois"
        html += "<br />Type: {}"
        html += "<br />Aggragate Rating: {}/5.0"
        html = html.format(name, price_for_two, currency, cuisine, rating)

        popup = folium.Popup(
            folium.Html(html, script=True),
            max_width=500,
        )

        folium.Marker(
            [line["latitude"], line["longitude"]],
            popup=popup,
            icon=folium.Icon(color=color, icon="home", prefix="fa"),
        ).add_to(marker_cluster)

folium_static(m, width=1024, height=768)
