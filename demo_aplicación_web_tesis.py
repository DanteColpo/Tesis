import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_percentage_error
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Proyección de Demanda de Áridos", layout="centered")

# Título de la aplicación
st.title('Proyección de Demanda de Áridos')

# Instrucciones para el usuario
st.write("Sube un archivo Excel (.xlsx) con los datos de demanda histórica para obtener una proyección de los próximos meses.")

# Cargar el archivo de Excel
uploaded_file = st.file_uploader("Sube el archivo Excel", type=["xlsx"])

# Diccionarios de meses en español y orden para visualización
meses_ordenados = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
meses_dict = {1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}

# Procesamiento si el archivo está cargado
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

        # Selección de opciones para el análisis
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

        # Configurar el gráfico según el período seleccionado
        if periodo == 'Anual':
            grouped_data = grouped_data.groupby(['AÑO', 'SECTOR']).agg({'CANTIDAD': 'sum'}).reset_index()
            x = grouped_data['AÑO']
            xlabel = 'Año'
        else:
            x = grouped_data['MES']
            xlabel = 'Mes'

        # Graficar los datos agrupados por sector
        fig, ax = plt.subplots()
        for sector in grouped_data['SECTOR'].unique():
            sector_data = grouped_data[grouped_data['SECTOR'] == sector]
            ax.plot(x, sector_data['CANTIDAD'], label=sector)

        # Configuración de etiquetas y título del gráfico
        ax.set_xlabel(xlabel)
        ax.set_ylabel('Cantidad de Material (M3)')
        ax.set_title(f'Proyección de demanda {"total" if ver_total else "para " + material} ({periodo})')
        ax.legend(title='Sector')

        # Incluir proyección ARIMA y MAPE
        if incluir_proyeccion and periodo == 'Mensual':
            try:
                # Entrenar el modelo ARIMA para proyección
                arima_model = ARIMA(grouped_data['CANTIDAD'], order=(4, 1, 1)).fit()
                forecast = arima_model.forecast(steps=1)
                mape = mean_absolute_percentage_error(grouped_data['CANTIDAD'], arima_model.predict())
                conf_interval = arima_model.get_forecast(steps=1).conf_int()

                st.write(f"**Proyección del próximo mes:** {forecast.values[0]:.2f} ± ({conf_interval.iloc[0, 0]:.2f}, {conf_interval.iloc[0, 1]:.2f})")
                st.write(f"**MAPE del modelo:** {mape:.2%}")

                # Añadir la proyección al gráfico
                future_date = grouped_data['MES'].max() + 1 if periodo == 'Mensual' else grouped_data['AÑO'].max() + 1
                ax.plot([future_date], forecast.values, 'ro--', label="Proyección ARIMA")
                ax.fill_between([future_date], conf_interval.iloc[:, 0], conf_interval.iloc[:, 1], color='red', alpha=0.3)
                ax.legend()

            except Exception as e:
                st.error(f"Error al generar la proyección ARIMA: {e}")

        # Mostrar el gráfico en Streamlit
        st.pyplot(fig)

# Pie de página con instrucciones adicionales
st.markdown("___")
st.markdown("**Nota:** Esta herramienta proporciona una proyección de demanda basada en datos históricos y modelos estadísticos. Los resultados son aproximados y deben interpretarse con precaución.")
st.markdown("¿Necesitas ayuda? Consulta nuestras [Preguntas Frecuentes](#) o [Contáctanos](#).")


