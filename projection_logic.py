import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_percentage_error
import itertools

# Función para cargar y procesar el archivo
def upload_and_process_file():
    uploaded_file = st.file_uploader("Subir archivo", type=["xlsx"])
    if uploaded_file is not None:
        data = pd.read_excel(uploaded_file)
        if data.empty:
            st.warning("El archivo está vacío o no tiene datos válidos.")
            return None
        else:
            st.success("Archivo cargado exitosamente.")
            return data
    return None

# Función para generar proyecciones y descargar los resultados
def download_projections(forecast_3, dates_3, forecast_6, dates_6, forecast_12, dates_12):
    # Validar las longitudes de los datos antes de construir el DataFrame
    if len(forecast_3) != len(dates_3):
        st.error("Error: Las proyecciones para 3 meses y las fechas no coinciden en longitud.")
        return
    if len(forecast_6) != len(dates_6):
        st.error("Error: Las proyecciones para 6 meses y las fechas no coinciden en longitud.")
        return
    if len(forecast_12) != len(dates_12):
        st.error("Error: Las proyecciones para 12 meses y las fechas no coinciden en longitud.")
        return

    # Crear DataFrame con las proyecciones
    output = pd.DataFrame({
        "Fecha (3 meses)": dates_3,
        "Proyección (3 meses)": forecast_3,
        "Fecha (6 meses)": dates_6,
        "Proyección (6 meses)": forecast_6,
        "Fecha (12 meses)": dates_12,
        "Proyección (12 meses)": forecast_12,
    })

    # Descargar como archivo Excel
    st.download_button(
        label="Descargar Proyecciones en Excel",
        data=output.to_csv(index=False).encode('utf-8'),
        file_name="proyecciones_demanda.xlsx",
        mime="text/csv"
    )

# Función para mostrar la proyección ARIMA general y desagregada
def show_projection(data):
    st.write("Proyección ARIMA para el Sector Privado")

    # Convertir la columna FECHA a tipo datetime y establecerla como índice
    data['FECHA'] = pd.to_datetime(data['FECHA'], errors='coerce')
    data = data.dropna(subset=['FECHA'])
    data = data.set_index('FECHA')

    # Filtrar solo los datos del sector privado
    data_privado = data[data['SECTOR'] == 'PRIVADO']

    # Verificación de que hay suficientes datos
    if data_privado.empty or len(data_privado) < 12:
        st.warning("No hay suficientes datos para el sector PRIVADO después del resampleo.")
        return

    # Proyección total
    data_privado_total = data_privado[['CANTIDAD']].resample('M').sum()
    data_privado_total['CANTIDAD_SUAVIZADA'] = SimpleExpSmoothing(data_privado_total['CANTIDAD']).fit(smoothing_level=0.9, optimized=False).fittedvalues
    train_total = data_privado_total['CANTIDAD_SUAVIZADA'].iloc[:-3]

    # Generar proyección para los próximos 3, 6 y 12 meses
    best_model = ARIMA(train_total, order=(4, 1, 0)).fit()
    forecast_3 = best_model.forecast(steps=3).apply(lambda x: max(0, x))
    forecast_6 = best_model.forecast(steps=6).apply(lambda x: max(0, x))
    forecast_12 = best_model.forecast(steps=12).apply(lambda x: max(0, x))

    # Crear fechas para las proyecciones
    last_date = data_privado_total.index[-1]
    dates_3 = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=3, freq='M')
    dates_6 = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=6, freq='M')
    dates_12 = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=12, freq='M')

    # Validación de longitudes y descarga
    st.write("Validando proyecciones para la descarga...")
    st.write(f"Longitud de Forecast (3 meses): {len(forecast_3)}, Longitud de Dates (3 meses): {len(dates_3)}")
    st.write(f"Longitud de Forecast (6 meses): {len(forecast_6)}, Longitud de Dates (6 meses): {len(dates_6)}")
    st.write(f"Longitud de Forecast (12 meses): {len(forecast_12)}, Longitud de Dates (12 meses): {len(dates_12)}")

    download_projections(forecast_3, dates_3, forecast_6, dates_6, forecast_12, dates_12)

    # Mostrar gráfico
    st.write("### Proyección Total de Demanda")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=train_total.index, y=train_total, mode='lines', name='Datos de Entrenamiento Suavizados'))
    fig.add_trace(go.Scatter(x=dates_3, y=forecast_3, mode='lines+markers', name='Pronóstico 3 Meses', line=dict(dash='dash', color='green')))
    fig.add_trace(go.Scatter(x=dates_6, y=forecast_6[:6], mode='lines+markers', name='Pronóstico 6 Meses', line=dict(dash='dot', color='orange')))
    fig.add_trace(go.Scatter(x=dates_12, y=forecast_12[:12], mode='lines+markers', name='Pronóstico 12 Meses', line=dict(dash='longdash', color='blue')))
    fig.update_layout(
        title="Proyección Total de Demanda",
        xaxis_title="Fecha",
        yaxis_title="Cantidad de Material (m³)"
    )
    st.plotly_chart(fig)
