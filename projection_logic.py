import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
from statsmodels.tsa.arima.model import ARIMA
from io import BytesIO
import openpyxl

# Función para cargar y procesar el archivo
def upload_and_process_file():
    uploaded_file = st.file_uploader("Subir archivo", type=["xlsx"])
    if uploaded_file is not None:
        try:
            data = pd.read_excel(uploaded_file)
            if data.empty:
                st.warning("El archivo está vacío o no tiene datos válidos.")
                return None
            st.success("Archivo cargado exitosamente.")
            return data
        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")
    return None

# Función para calcular MAPE
def calculate_mape(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100

# Función para ajustar modelo ARIMA óptimo y generar proyección
def generate_optimal_arima(data, steps):
    try:
        model = ARIMA(data, order=(4, 1, 0)).fit()
        forecast = model.forecast(steps=steps).apply(lambda x: max(0, x)).astype(int)
        return forecast
    except Exception as e:
        st.error(f"Error al generar proyección: {e}")
        return None

# Función para mostrar la proyección ARIMA
def show_projection(data):
    try:
        st.write("Proyección ARIMA para el Sector Privado")

        # Procesar datos
        data['FECHA'] = pd.to_datetime(data['FECHA'], errors='coerce')
        data = data.dropna(subset=['FECHA'])
        data = data.set_index('FECHA')
        data_privado = data[data['SECTOR'] == 'PRIVADO']

        if data_privado.empty or len(data_privado) < 12:
            st.warning("No hay suficientes datos para el sector PRIVADO después del resampleo.")
            return

        # Suavización y preparación de datos
        data_privado_total = data_privado[['CANTIDAD']].resample('M').sum()
        data_privado_total['CANTIDAD_SUAVIZADA'] = SimpleExpSmoothing(
            data_privado_total['CANTIDAD']
        ).fit(smoothing_level=0.9, optimized=False).fittedvalues
        train_total = data_privado_total['CANTIDAD_SUAVIZADA'].iloc[:-3]

        # Generar proyección para 3 meses (gráfico principal)
        model_3_months = ARIMA(train_total, order=(4, 1, 0)).fit()
        forecast_3 = model_3_months.forecast(steps=3).apply(lambda x: max(0, x)).astype(int)
        dates_3 = pd.date_range(start=data_privado_total.index[-1] + pd.DateOffset(months=1), periods=3, freq='M')

        # Calcular MAPE para los 3 meses
        actual_values = data_privado_total['CANTIDAD_SUAVIZADA'].iloc[-3:]
        mape = calculate_mape(actual_values, forecast_3[:3])
        confidence = 100 - mape

        # Visualizar datos históricos y suavizados
        st.write("### Proyección Total de Demanda (3 meses)")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data_privado_total.index, y=data_privado_total['CANTIDAD'], 
                                 mode='lines', name='Datos Originales', line=dict(color='red')))
        fig.add_trace(go.Scatter(x=data_privado_total.index, y=data_privado_total['CANTIDAD_SUAVIZADA'], 
                                 mode='lines', name='Datos Suavizados', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=dates_3, y=forecast_3, mode='lines+markers', 
                                 name='Pronóstico 3 Meses', line=dict(dash='dash', color='green')))
        fig.update_layout(
            title="Proyección Total de Demanda (3 meses)",
            xaxis_title="Fecha",
            yaxis_title="Cantidad de Material (m³)"
        )
        st.plotly_chart(fig)

        # Selección de meses para mostrar
        projection_choice = st.selectbox("Selecciona el periodo de proyección:", ["3 meses", "6 meses", "12 meses"])

        if projection_choice == "3 meses":
            st.write("#### Tabla de Proyección (3 meses)")
            st.table(pd.DataFrame({"Fecha": dates_3, "Proyección ARIMA (m³)": forecast_3}))

        elif projection_choice == "6 meses":
            forecast_6 = generate_optimal_arima(train_total, steps=6)
            dates_6 = pd.date_range(start=data_privado_total.index[-1] + pd.DateOffset(months=1), periods=6, freq='M')
            st.write("#### Tabla de Proyección (6 meses)")
            st.table(pd.DataFrame({"Fecha": dates_6, "Proyección ARIMA (m³)": forecast_6}))

        elif projection_choice == "12 meses":
            forecast_12 = generate_optimal_arima(train_total, steps=12)
            dates_12 = pd.date_range(start=data_privado_total.index[-1] + pd.DateOffset(months=1), periods=12, freq='M')
            st.write("#### Tabla de Proyección (12 meses)")
            st.table(pd.DataFrame({"Fecha": dates_12, "Proyección ARIMA (m³)": forecast_12}))

        # Texto informativo sobre MAPE y confiabilidad
        st.markdown(
            f"**La proyección tiene un MAPE de {mape:.2f}%**, lo que equivale a un "
            f"**{confidence:.2f}% de confiabilidad** para la proyección de los 3 meses. "
            f"En el caso de una mayor proyección, la confiabilidad se ve reducida."
        )
    except Exception as e:
        st.error(f"Error al calcular las proyecciones: {e}")

# Código principal
st.title("ProyeKTA+")
st.subheader("Proyecta tu éxito")
st.markdown("Sube un archivo Excel (.xlsx) con los datos históricos de demanda para obtener proyecciones.")

# Cargar archivo y procesar
data = upload_and_process_file()
if data is not None:
    show_projection(data)




