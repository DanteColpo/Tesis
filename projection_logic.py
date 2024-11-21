import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_percentage_error
import itertools

# Definir alpha globalmente para la suavización exponencial
alpha = 0.9

# Función para cargar y procesar el archivo
def upload_and_process_file():
    uploaded_file = st.file_uploader("Subir archivo", type=["xlsx"])
    if uploaded_file is not None:
        try:
            data = pd.read_excel(uploaded_file)
            required_columns = {'FECHA', 'SECTOR', 'MATERIAL', 'CANTIDAD'}
            if not required_columns.issubset(data.columns):
                st.error("El archivo no contiene las columnas requeridas.")
                st.image("Ejemplo Excel.png", caption="Ejemplo del formato correcto")
                return None
            st.success("Archivo cargado exitosamente.")
            return data
        except Exception as e:
            st.error(f"Error al leer el archivo: {str(e)}")
            return None
    return None

# Función para realizar la proyección y descargar los resultados
def show_projection(data):
    st.write("Proyección ARIMA para el Sector Privado")

    # Preprocesamiento de los datos
    data['FECHA'] = pd.to_datetime(data['FECHA'], errors='coerce')
    data = data.dropna(subset=['FECHA'])
    data = data.set_index('FECHA')

    # Filtrar datos del sector privado
    data_privado = data[data['SECTOR'] == 'PRIVADO']

    if data_privado.empty or len(data_privado) < 12:
        st.warning("No hay suficientes datos para el sector PRIVADO.")
        return

    # Proyección total (Todos los tipos de material)
    st.write("### Proyección Total de Demanda (Todos los Tipos de Material)")
    data_privado_total = data_privado[['CANTIDAD']].resample('M').sum()
    data_privado_total['CANTIDAD_SUAVIZADA'] = SimpleExpSmoothing(data_privado_total['CANTIDAD']).fit(smoothing_level=alpha, optimized=False).fittedvalues

    # Entrenamiento y optimización del modelo ARIMA
    train_total = data_privado_total['CANTIDAD_SUAVIZADA'].iloc[:-3]
    test_total = data_privado_total['CANTIDAD_SUAVIZADA'].iloc[-3:]
    best_model, best_order, best_mape = optimize_arima(train_total, test_total)

    # Generar proyección extendida
    forecast_3, dates_3 = generate_forecast(best_model, data_privado_total, 3)
    forecast_6, dates_6 = generate_forecast(best_model, data_privado_total, 6)
    forecast_12, dates_12 = generate_forecast(best_model, data_privado_total, 12)

    # Mostrar resultados
    show_forecast_chart(train_total, test_total, forecast_3, dates_3, best_order)

    # Descarga de proyecciones en Excel
    download_projections(forecast_3, dates_3, forecast_6, dates_6, forecast_12, dates_12)

# Optimización del modelo ARIMA
def optimize_arima(train, test):
    best_mape = float("inf")
    best_order = None
    best_model = None
    p = range(3, 6)
    d = [1]
    q = range(0, 4)
    for combination in itertools.product(p, d, q):
        try:
            model = ARIMA(train, order=combination).fit()
            forecast = model.forecast(steps=len(test))
            mape = mean_absolute_percentage_error(test, forecast)
            if mape < best_mape:
                best_mape = mape
                best_order = combination
                best_model = model
        except Exception:
            continue
    return best_model, best_order, best_mape

# Generar proyección y fechas
def generate_forecast(model, data, steps):
    forecast = model.forecast(steps=steps).apply(lambda x: max(0, x))
    forecast_dates = pd.date_range(start=data.index[-1] + pd.DateOffset(months=1), periods=steps, freq='M')
    return forecast, forecast_dates

# Mostrar gráfico de proyección
def show_forecast_chart(train, test, forecast, forecast_dates, best_order):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=train.index, y=train, mode='lines', name='Datos de Entrenamiento Suavizados'))
    fig.add_trace(go.Scatter(x=test.index, y=test, mode='lines', name='Datos Reales Suavizados', line=dict(color='orange')))
    fig.add_trace(go.Scatter(x=forecast_dates, y=forecast, mode='lines+markers', name=f'Pronóstico ARIMA{best_order}', line=dict(dash='dash', color='green')))
    fig.update_layout(
        title=f'Proyección ARIMA{best_order} sobre Datos Suavizados (Total)',
        xaxis_title='Fecha',
        yaxis_title='Cantidad de Material (m³)',
        hovermode="x"
    )
    st.plotly_chart(fig)

# Descargar proyecciones en Excel
def download_projections(forecast_3, dates_3, forecast_6, dates_6, forecast_12, dates_12):
    output = pd.DataFrame({
        'Fecha (3 meses)': dates_3.strftime('%Y-%m'),
        'Proyección (3 meses)': forecast_3.round().astype(int),
        'Fecha (6 meses)': dates_6.strftime('%Y-%m'),
        'Proyección (6 meses)': forecast_6.round().astype(int),
        'Fecha (12 meses)': dates_12.strftime('%Y-%m'),
        'Proyección (12 meses)': forecast_12.round().astype(int),
    })
    st.download_button(
        label="📥 Descargar Proyecciones (Excel)",
        data=output.to_excel(index=False, engine='openpyxl'),
        file_name="proyecciones_demanda.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


