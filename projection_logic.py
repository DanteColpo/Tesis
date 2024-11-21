import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_percentage_error


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


def generate_projections(model, steps, last_date):
    try:
        forecast = model.forecast(steps=steps).apply(lambda x: max(0, x))  # Evitar negativos
        forecast_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=steps, freq='M')
        return forecast, forecast_dates
    except Exception as e:
        st.error(f"Error al generar proyecciones: {e}")
        return None, None


def download_projections(forecast_3, dates_3, forecast_6, dates_6, forecast_12, dates_12):
    # Validar que todas las listas sean de igual longitud
    if len(forecast_3) == len(dates_3) and len(forecast_6) == len(dates_6) and len(forecast_12) == len(dates_12):
        output = pd.DataFrame({
            "Fecha (3 meses)": dates_3,
            "Proyección (3 meses)": forecast_3,
            "Fecha (6 meses)": dates_6,
            "Proyección (6 meses)": forecast_6,
            "Fecha (12 meses)": dates_12,
            "Proyección (12 meses)": forecast_12,
        })

        st.download_button(
            label="Descargar Proyecciones en Excel",
            data=output.to_csv(index=False).encode('utf-8'),
            file_name="proyecciones_demanda.csv",
            mime="text/csv"
        )
    else:
        st.error("Las longitudes de las proyecciones y las fechas no coinciden. Por favor, revise los datos.")


def show_projection(data):
    st.write("Proyección ARIMA para el Sector Privado")

    # Preprocesamiento de datos
    data['FECHA'] = pd.to_datetime(data['FECHA'], errors='coerce')
    data = data.dropna(subset=['FECHA'])
    data = data.set_index('FECHA')

    # Filtrar datos del sector privado
    data_privado = data[data['SECTOR'] == 'PRIVADO']

    if data_privado.empty or len(data_privado) < 12:
        st.warning("No hay suficientes datos para el sector PRIVADO.")
        return

    # Preparar datos para la proyección
    data_privado_total = data_privado[['CANTIDAD']].resample('M').sum()
    data_privado_total['CANTIDAD_SUAVIZADA'] = SimpleExpSmoothing(data_privado_total['CANTIDAD']).fit(
        smoothing_level=0.9, optimized=False).fittedvalues
    train_total = data_privado_total['CANTIDAD_SUAVIZADA'].iloc[:-3]
    last_date = data_privado_total.index[-1]

    # Crear modelo ARIMA
    try:
        best_model = ARIMA(train_total, order=(4, 1, 0)).fit()
    except Exception as e:
        st.error(f"Error al ajustar el modelo ARIMA: {e}")
        return

    # Generar proyecciones
    forecast_3, dates_3 = generate_projections(best_model, 3, last_date)
    forecast_6, dates_6 = generate_projections(best_model, 6, last_date)
    forecast_12, dates_12 = generate_projections(best_model, 12, last_date)

    if None in (forecast_3, dates_3, forecast_6, dates_6, forecast_12, dates_12):
        st.error("No se pudieron generar todas las proyecciones.")
        return

    # Descargar las proyecciones
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
