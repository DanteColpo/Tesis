import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_percentage_error
from datetime import datetime

# Configuración de la página con icono y título
st.set_page_config(page_title="Proyekta+", layout="centered", page_icon="📈")

# Insertar el logo y título de la aplicación
st.image("Logo_ProyeKTA+.png", width=200)  # Asegúrate de que el nombre del archivo del logo coincida
st.title('Proyekta+')
st.subheader('Proyecta tu éxito')

# Descripción breve de la aplicación
st.write("Sube un archivo Excel (.xlsx) con los datos de demanda histórica para obtener una proyección de los próximos meses.")

# Cargar el archivo de Excel
uploaded_file = st.file_uploader("Subir archivo", type=["xlsx"])

# Diccionario de meses y orden en español
meses_ordenados = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
meses_dict = {1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}

if uploaded_file is not None:
    # Leer el archivo Excel
    data = pd.read_excel(uploaded_file)
    
    if data.empty:
        st.warning("El archivo está vacío o no tiene datos válidos.")
    else:
        st.success("Archivo cargado exitosamente.")
        st.write("Datos cargados:")
        st.write(data.head())

        # Opciones de configuración para visualización y proyección
        periodo = st.selectbox('Seleccione el período', ['Mensual', 'Anual'])
        ver_total = st.checkbox('Mostrar demanda total')
        incluir_proyeccion = st.checkbox('Incluir proyección para el próximo mes')
        
        if not ver_total:
            material = st.selectbox('Seleccione el material', data['MATERIAL'].unique())

        # Conversión de fechas y agrupación de datos
        data['FECHA'] = pd.to_datetime(data['FECHA'], errors='coerce')
        data = data.dropna(subset=['FECHA'])
        data['AÑO'] = data['FECHA'].dt.year
        data['MES'] = data['FECHA'].dt.month.map(meses_dict)

        # Agrupación de datos
        if ver_total:
            grouped_data = data.groupby(['AÑO', 'MES', 'SECTOR']).agg({'CANTIDAD': 'sum'}).reset_index()
        else:
            material_data = data[data['MATERIAL'] == material].copy()
            grouped_data = material_data.groupby(['AÑO', 'MES', 'SECTOR']).agg({'CANTIDAD': 'sum'}).reset_index()

        # Gráfica según el periodo seleccionado
        if periodo == 'Anual':
            grouped_data = grouped_data.groupby(['AÑO', 'SECTOR']).agg({'CANTIDAD': 'sum'}).reset_index()
            x = grouped_data['AÑO']
            xlabel = 'Año'
        else:
            x = grouped_data['MES']
            xlabel = 'Mes'

        # Creación del gráfico con colores temáticos
        fig, ax = plt.subplots()
        colors = ['#FF6F61', '#6B5B95', '#88B04B']  # Colores temáticos
        for i, sector in enumerate(grouped_data['SECTOR'].unique()):
            sector_data = grouped_data[grouped_data['SECTOR'] == sector]
            ax.plot(x, sector_data['CANTIDAD'], label=sector, color=colors[i % len(colors)], linewidth=2)

        ax.set_xlabel(xlabel)
        ax.set_ylabel('Cantidad de Material (M3)')
        ax.set_title(f'Proyección de demanda {"total" if ver_total else "para " + material} ({periodo})')
        ax.legend(title='Sector')

        # Incluir proyección con ARIMA
        if incluir_proyeccion and periodo == 'Mensual':
            try:
                arima_model = ARIMA(grouped_data['CANTIDAD'], order=(4, 1, 1)).fit()
                forecast = arima_model.forecast(steps=1)
                mape = mean_absolute_percentage_error(grouped_data['CANTIDAD'], arima_model.predict())
                conf_interval = arima_model.get_forecast(steps=1).conf_int()

                st.write(f"**Proyección del próximo mes:** {forecast.values[0]:.2f} ± ({conf_interval.iloc[0, 0]:.2f}, {conf_interval.iloc[0, 1]:.2f})")
                st.write(f"**MAPE del modelo:** {mape:.2%}")
                
                # Mostrar la proyección en el gráfico
                future_dates = [x.max() + 1]  # Ajustar para meses
                ax.plot(future_dates, forecast.values, label="Proyección ARIMA", linestyle='--', color='red')
                ax.fill_between(future_dates, conf_interval.iloc[:, 0], conf_interval.iloc[:, 1], color='red', alpha=0.3)

            except Exception as e:
                st.error(f"Error al generar la proyección ARIMA: {e}")

        st.pyplot(fig)

# Sección de Preguntas Frecuentes y Contacto
st.markdown("---")
st.markdown("### Preguntas Frecuentes")
with st.expander("¿Qué método utiliza esta aplicación para la proyección de demanda?"):
    st.write("Utilizamos el modelo ARIMA, adecuado para series temporales y datos históricos.")
with st.expander("¿Por qué se usa ARIMA para la proyección de demanda?"):
    st.write("ARIMA permite capturar tendencias en datos históricos y generar proyecciones confiables.")
with st.expander("¿A quién va enfocada esta aplicación?"):
    st.write("Está diseñada para PYMEs en el sector de áridos que necesitan mejorar la precisión de su planificación de demanda.")
with st.expander("¿Cómo puedo aprovechar al máximo esta herramienta?"):
    st.write("Sigue subiendo tus datos históricos actualizados para mejorar la precisión de las proyecciones.")
with st.expander("¿Qué datos son necesarios en el archivo de Excel?"):
    st.write("El archivo debe contener columnas de fecha, sector, material, y cantidad para un análisis óptimo.")

st.markdown("### Contáctanos")
st.write("Si tienes preguntas adicionales, puedes contactarnos a través de:")
st.write("- **Instagram**: [Dante.Colpo](https://instagram.com/Dante.Colpo)")
st.write("- **Correo Electrónico**: [dante.colpo@gmail.com](mailto:dante.colpo@gmail.com)")




