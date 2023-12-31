import streamlit as st
import requests
from io import BytesIO
import pickle
import seaborn as sns
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import json
import random 
import plotly.express as px
import pandas as pd
import numpy as np
import plotly.graph_objects as go


# Configuración de la página Streamlit
st.set_page_config(layout="wide")
st.set_option('deprecation.showPyplotGlobalUse', False)

# Función para cargar datos desde el archivo CSV
def load_data():
    data = pd.read_csv("topic_2022_yucatan.csv")
    return data

# Función principal de la aplicación
def main():
    # Barra lateral con widgets de selección
    st.sidebar.write("Topics demo")
    st.sidebar.title("Selecciona estado y año:")
    state = st.sidebar.selectbox("Estado", ['Yucatán'])
    year = st.sidebar.selectbox("Año", ['2022'])
    run = st.sidebar.button('Mostrar')

    # Verificar si se ha hecho clic en el botón "Mostrar"
    if run:
        if year == '2022':
            archivo_json = 'yucatan2022.json'  
            nombre_archivo = "data2022.json"

            try:
                with open(nombre_archivo, 'r') as archivo:
                    data = json.load(archivo)
                
                wordcloud_data = []
                for topic, word_probs in data.items():
                    for word, prob in word_probs.items():
                        wordcloud_data.append({"Topic": topic, "Word": word, "Probability": prob})

                num_words = len(wordcloud_data)
                random_latitudes = np.random.uniform(20.3, 21.3, num_words)
                random_longitudes = np.random.uniform(-88.3, -89.3, num_words)

                df1 = pd.DataFrame(wordcloud_data)
                max_prob = df1["Probability"].max()
                min_prob = df1["Probability"].min()
                df1["Size"] = np.interp(df1["Probability"], (min_prob, max_prob), (2, 200))

                mapbox_token = "pk.eyJ1IjoiaXZhbmxvc2FyIiwiYSI6ImNrZTJpdWN0NDA5cXUyem1oOGx3NGh1bGsifQ.wuhB2vmk4QGrciFWYygqaA"

                fig_mapa = px.scatter_mapbox(
                    df1,
                    lat=random_latitudes,
                    lon=random_longitudes,
                    hover_name="Word",
                    hover_data={"Probability": True},
                    text="Word",
                    size="Size",
                    color="Topic",
                    color_discrete_sequence=px.colors.qualitative.Plotly,
                    zoom=7.5,
                    mapbox_style="outdoors",
                    title="Nube de Palabras por Tópico en Yucatán",
                    labels={"Probability": "Probabilidad", "Word": "Palabra"},
                )

                fig_mapa.update_traces(
                    textfont_color='black'
                )

                fig_mapa.update_layout(
                    width=1200,
                    height=900
                )

                fig_mapa.update_layout(mapbox=dict(accesstoken=mapbox_token))

                added_topics = {}

                for row in df1.itertuples():
                    topic = row.Topic
                    if topic not in added_topics:
                        added_topics[topic] = True
                        fig_mapa.add_annotation(
                            go.layout.Annotation(
                                text=topic,
                                x=random_latitudes[row.Index],
                                y=random_longitudes[row.Index],
                                showarrow=False,
                                font=dict(size=14),
                            )
                        )

                data = load_data()

                st.title("Tópicos LDA en Yucatán durante 2022")
                st.plotly_chart(fig_mapa)

                st.title("Descripción de Tópicos")
                st.dataframe(data)

            except FileNotFoundError:
                st.error(f"Archivo '{nombre_archivo}' no encontrado.")
            except json.JSONDecodeError as e:
                st.error(f"Error al cargar el archivo JSON: {e}")
        else:
            st.error("Año no válido")

        # Definir la ruta al archivo JSON
        archivo_json = 'yucatan2022.json'


        # Crear una lista para almacenar los objetos JSON
        data2 = []

        # Cargar datos desde el archivo JSON
        try:
            with open(archivo_json, 'r') as json_file:
                for line in json_file:
                    try:
                        record = json.loads(line)
                        data2.append(record)
                    except json.JSONDecodeError as e:
                        st.warning(f"Error al cargar una línea del archivo JSON: {e}")

            # Convertir la lista de objetos JSON en un DataFrame de Pandas
            df_data2 = pd.DataFrame(data2)

            # Mostrar los datos en Streamlit
            st.title("solicitudes de información en yucatán durante el año 2022")
            st.write(df_data2)


            # Verificar si la columna 'DEPENDENCIA' existe en los datos
            if data2 and all('DEPENDENCIA' in record for record in data2):
                # Crear un DataFrame a partir de los datos JSON
                df = pd.DataFrame(data2)

            # Verificar si la columna 'DEPENDENCIA' existe en el DataFrame
            if 'DEPENDENCIA' in df.columns:
                # Obtener los valores y frecuencias de la columna 'DEPENDENCIA'
                dependencia_counts = df['DEPENDENCIA'].value_counts()

                # Generar colores aleatorios para cada barra
                colors = [f'#{random.randint(0, 0xFFFFFF):06x}' for _ in range(len(dependencia_counts[:50]))]

                # Crear un gráfico interactivo de barras utilizando Plotly Express
                fig_dependencia = px.bar(x=dependencia_counts[:50].index, y=dependencia_counts[:50],
                                title='Top 25 Dependencias más Comunes', labels={'y': 'Cantidad', 'x': 'Dependencia'},
                                color=colors)  # Usar los colores generados para colorear las barras
                fig_dependencia.update_layout(
                    xaxis={'categoryorder': 'total descending'},
                    xaxis_title='Dependencia',
                    yaxis_title='Cantidad',
                    width=1200,  # Ajusta el ancho del gráfico según tus preferencias
                    height=900,  # Ajusta la altura del gráfico según tus preferencias
                )
                fig_dependencia.update_xaxes(tickangle=90)

                # Mostrar el gráfico de barras de Dependencia
                st.title("Distribución de Dependencias")
                st.plotly_chart(fig_dependencia)
            else:
                st.error("La columna 'DEPENDENCIA' no se encontró en los datos.")
            # Verificar si la columna 'SECTOR' existe en el DataFrame
            if 'SECTOR' in df.columns:
                # Calcular el conteo de cada sector
                count_data = df['SECTOR'].value_counts().reset_index()
                count_data.columns = ['SECTOR', 'COUNT']

                # Crear el gráfico interactivo de barras utilizando Plotly Express
                fig_sector = px.bar(count_data, x='SECTOR', y='COUNT', title='Distribución de Sectores', color='COUNT',
                                color_continuous_scale='inferno')
                fig_sector.update_layout(
                    xaxis={'categoryorder': 'total descending'},
                    xaxis_title='Sector',
                    yaxis_title='Frecuencia',
                    xaxis_tickangle=45,
                    width=1200,
                    height=600
                )

                # Mostrar el gráfico de barras de Sectores
                st.title("Distribución de Sectores")
                st.plotly_chart(fig_sector)

            else:
                st.error("La columna 'SECTOR' no se encontró en los datos.")

            # Verificar si la columna 'MEDIOENTRADA' existe en el DataFrame
            if 'MEDIOENTRADA' in df.columns:
                # Calcular el conteo de cada medio de entrada
                count_data_medioentrada = df['MEDIOENTRADA'].value_counts().reset_index()
                count_data_medioentrada.columns = ['MEDIOENTRADA', 'COUNT']

                # Crear el gráfico de barras
                fig_medioentrada = px.bar(count_data_medioentrada, x='MEDIOENTRADA', y='COUNT', title='Distribución de Medios de Entrada')
                # Ajustar el tamaño del gráfico
                fig_medioentrada.update_layout(
                    width=1200,
                    height=600  # Ajusta la altura del gráfico según tus preferencias
                )

                # Mostrar el gráfico de barras de Medios de Entrada
                st.title("Distribución de Medios de Entrada")
                st.plotly_chart(fig_medioentrada)
            else:
                st.error("La columna 'MEDIOENTRADA' no se encontró en los datos.")
            # Verificar si la columna 'TIPOSOLICITUD' existe en el DataFrame
            if 'TIPOSOLICITUD' in df.columns:
                # Calcular el conteo de cada tipo de solicitud
                count_data_tiposolicitud = df['TIPOSOLICITUD'].value_counts().reset_index()
                count_data_tiposolicitud.columns = ['TIPOSOLICITUD', 'COUNT']

                # Crear el gráfico de barras
                fig_tipo_solicitud = px.bar(count_data_tiposolicitud, x='TIPOSOLICITUD', y='COUNT', title='Distribución de Tipos de Solicitud')
                fig_tipo_solicitud.update_layout(
                    width=1200,
                    height=600  # Ajusta la altura del gráfico según tus preferencias
                )

                # Mostrar el gráfico de barras de Tipos de Solicitud
                st.title("Distribución de Tipos de Solicitud")
                st.plotly_chart(fig_tipo_solicitud)
            else:
                st.error("La columna 'TIPOSOLICITUD' no se encontró en los datos.")

            # Verificar si la columna 'RESPUESTA' existe en el DataFrame
            if 'RESPUESTA' in df.columns:
                # Calcular el conteo de cada respuesta
                count_data_respuesta = df['RESPUESTA'].value_counts().reset_index()
                count_data_respuesta.columns = ['RESPUESTA', 'COUNT']

                # Crear el gráfico de barras
                fig_respuesta = px.bar(count_data_respuesta, x='RESPUESTA', y='COUNT', title='Distribución de Respuestas')
                fig_respuesta.update_layout(
                    width=1200,
                    height=600  # Ajusta la altura del gráfico según tus preferencias
                )

                # Mostrar el gráfico de barras de Respuestas
                st.title("Distribución de Respuestas")
                st.plotly_chart(fig_respuesta)
            else:
                st.error("La columna 'RESPUESTA' no se encontró en los datos.")


        except FileNotFoundError:
            st.error(f"Archivo '{archivo_json}' no encontrado.")


# Ejecutar la función principal
if __name__ == "__main__":
    main()
