import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_percentage_error
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="ProyeKTA+", page_icon="📊", layout="centered")

# Estilo CSS personalizado para justificación y colores profesionales
st.markdown("""
    <style>
        /* Justificación de texto y colores */
        .justificado {
            text-align: justify;
        }
        .titulo {
            font-size: 2em;
            font-weight: bold;
            color: #2C3E50; /* Azul oscuro */
            text-align: center;
        }
        .subtitulo {
            font-size: 1.5em;
            color: #7F8C8D; /* Gris */
            text-align: center;
        }
        .preguntas-frecuentes, .contacto-titulo {
            color: #2C3E50; /* Azul oscuro */
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# Insertar el logo y título de la aplicación
st.image("Logo_ProyeKTA+.png", width=300)  # Asegúrate de que el archivo del logo esté en el mismo directorio
st.markdown("<div class='titulo'>ProyeKTA+</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitulo'>Proyecta tu éxito</div>", unsafe_allow_html=True)

# Instrucciones rápidas para el usuario
st.markdown("<p class='justificado' style='color: #34495E;'>Sube un archivo Excel (.xlsx) con los datos de demanda histórica para obtener una proyección de los próximos meses.</p>", unsafe_allow_html=True)

# Cargar el archivo de Excel
uploaded_file = st.file_uploader("Subir archivo", type=["xlsx"])

# Diccionarios de meses en español y orden para visualización
meses_ordenados = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
meses_dict = {1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}

if uploaded_file is not None:
    # Leer el archivo Excel
    data = pd.read_excel(uploaded_file)

    # Verificar si el archivo contiene datos
    if data.empty:
        st.warning("El archivo está vacío o no tiene datos válidos.")
    else:
        st.success("Archivo cargado exitosamente.")
        st.write("Datos cargados:")
        st.write(data.head())

        # Selección del período y material
        periodo = st.selectbox('Seleccione el período', ['Mensual', 'Anual'])
        ver_total = st.checkbox('Mostrar demanda total')
        incluir_proyeccion = st.checkbox('Incluir proyección para el próximo mes')

        if not ver_total:
            material = st.selectbox('Seleccione el material', data['MATERIAL'].unique())

        # Asegurarse de que la columna FECHA esté en formato de fecha
        data['FECHA'] = pd.to_datetime(data['FECHA'], errors='coerce')
        data = data.dropna(subset=['FECHA'])
        data['AÑO'] = data['FECHA'].dt.year
        data['MES'] = data['FECHA'].dt.month.map(meses_dict)

        # Agrupación de datos por período y material
        if ver_total:
            grouped_data = data.groupby(['AÑO', 'MES', 'SECTOR']).agg({'CANTIDAD': 'sum'}).reset_index()
        else:
            material_data = data[data['MATERIAL'] == material].copy()
            grouped_data = material_data.groupby(['AÑO', 'MES', 'SECTOR']).agg({'CANTIDAD': 'sum'}).reset_index()

        # Ajustar el gráfico según el período seleccionado
        if periodo == 'Anual':
            grouped_data = grouped_data.groupby(['AÑO', 'SECTOR']).agg({'CANTIDAD': 'sum'}).reset_index()
            x = grouped_data['AÑO']
            xlabel = 'Año'
        else:
            x = grouped_data['MES']
            xlabel = 'Mes'

        # Separar datos en sectores y graficar
        fig, ax = plt.subplots()
        for sector in grouped_data['SECTOR'].unique():
            sector_data = grouped_data[grouped_data['SECTOR'] == sector]
            ax.plot(x, sector_data['CANTIDAD'], label=sector)

        # Ajustar etiquetas y título
        ax.set_xlabel(xlabel)
        ax.set_ylabel('Cantidad de Material M3')
        ax.set_title(f'Proyección de demanda {"total" if ver_total else "para " + material} ({periodo})')
        ax.legend(title='Sector')

        # Incluir proyección con ARIMA y MAPE
        if incluir_proyeccion and periodo == 'Mensual':
            try:
                # ARIMA para proyección
                arima_model = ARIMA(grouped_data['CANTIDAD'], order=(4, 1, 1)).fit()
                forecast = arima_model.forecast(steps=1)
                mape = mean_absolute_percentage_error(grouped_data['CANTIDAD'], arima_model.predict())
                conf_interval = arima_model.get_forecast(steps=1).conf_int()

                st.write(f"**Proyección del próximo mes:** {forecast.values[0]:.2f} ± ({conf_interval.iloc[0, 0]:.2f}, {conf_interval.iloc[0, 1]:.2f})")
                st.write(f"**MAPE del modelo:** {mape:.2%}")

                # Mostrar la proyección en el gráfico
                future_dates = [x.max() + 1]  # Suponiendo meses en orden
                ax.plot(future_dates, forecast.values, label="Proyección ARIMA", linestyle='--', color='red')
                ax.fill_between(future_dates, conf_interval.iloc[:, 0], conf_interval.iloc[:, 1], color='red', alpha=0.3)

            except Exception as e:
                st.error(f"Error al generar la proyección ARIMA: {e}")

        st.pyplot(fig)

# Preguntas Frecuentes
st.markdown("<hr><h2 class='preguntas-frecuentes'>Preguntas Frecuentes</h2>", unsafe_allow_html=True)
faq_items = [
    "¿Qué método utiliza esta aplicación para la proyección de demanda?",
    "¿Por qué se usa ARIMA para la proyección de demanda?",
    "¿A quién va enfocada esta aplicación?",
    "¿Cómo puedo aprovechar al máximo esta herramienta?",
    "¿Qué datos son necesarios en el archivo de Excel?"
]
for question in faq_items:
    with st.expander(question):
        st.write("Respuesta pendiente")  # Placeholder para respuestas

# Sección de contacto estilizada
st.markdown("<hr><h2 class='contacto-titulo'>¿Tienes dudas? ¡Contáctanos en nuestras redes o por correo!</h2>", unsafe_allow_html=True)
st.markdown("""
    <div style='text-align: center;'>
        <p>📸 Instagram: <a href="https://instagram.com/Dante.Colpo" target="_blank">@Dante.Colpo</a></p>
        <p>✉️ Correo Electrónico: <a href="mailto:dante.colpo@gmail.com">dante.colpo@gmail.com</a></p>
    </div>
""", unsafe_allow_html=True)

# Ocultar pie de página de Streamlit
st.markdown("<style> footer {visibility: hidden;} </style>", unsafe_allow_html=True)
