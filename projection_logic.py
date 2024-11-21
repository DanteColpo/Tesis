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
        data = pd.read_excel(uploaded_file)
        if data.empty:
            st.warning("El archivo está vacío o no tiene datos válidos.")
            return None
        else:
            st.success("Archivo cargado exitosamente.")
            return data
    return None

# Función para optimizar ARIMA
def optimize_arima(data, steps, p_range=(1, 6), d_range=[1], q_range=(0, 4)):
    best_mape = float("inf")
    best_order = None
    best_model = None
    for combination in itertools.product(range(*p_range), d_range, range(*q_range)):
        try:
            model = ARIMA(data, order=combination).fit()
            forecast = model.forecast(steps=steps)
            test_values = data.iloc[-steps:]
            mape = mean_absolute_percentage_error(test_values, forecast)

            if mape < best_mape:
                best_mape = mape
                best_order = combination
                best_model = model
        except Exception:
            continue
    return best_model, best_order, best_mape

# Función general para generar proyecciones
def generar_proyeccion(data, horizonte):
    data['FECHA'] = pd.to_datetime(data['FECHA'], errors='coerce')
    data = data.dropna(subset=['FECHA'])
    data = data.set_index('FECHA')
    data_privado = data[data['SECTOR'] == 'PRIVADO']
    data_privado = data_privado[['CANTIDAD']].resample('M').sum()

    if data_privado.empty or len(data_privado) < horizonte:
        st.warning("No hay suficientes datos para realizar la proyección.")
        return None, None, None, None

    # Suavización exponencial
    data_privado['CANTIDAD_SUAVIZADA'] = SimpleExpSmoothing(data_privado['CANTIDAD']).fit(smoothing_level=alpha, optimized=False).fittedvalues

    # Optimizar ARIMA
    train = data_privado['CANTIDAD_SUAVIZADA']
    best_model, best_order, best_mape = optimize_arima(train, steps=horizonte)

    # Generar proyección
    forecast = best_model.forecast(steps=horizonte).apply(lambda x: max(0, x))
    dates = pd.date_range(start=data_privado.index[-1] + pd.DateOffset(months=1), periods=horizonte, freq='M')

    return data_privado, forecast, dates, (best_order, best_mape)

# Función para mostrar las proyecciones en función del horizonte
def show_projection(data):
    st.write("### Proyección ARIMA para el Sector Privado")

    horizonte = st.selectbox("Selecciona el horizonte de proyección:", [3, 6, 12])
    data_privado, forecast, dates, arima_info = generar_proyeccion(data, horizonte)

    if data_privado is not None:
        # Visualización de resultados
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data_privado.index, y=data_privado['CANTIDAD'],
                                 mode='lines', name='Datos Originales', line=dict(color='red')))
        fig.add_trace(go.Scatter(x=data_privado.index, y=data_privado['CANTIDAD_SUAVIZADA'],
                                 mode='lines', name='Datos Suavizados', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=dates, y=forecast, mode='lines+markers',
                                 name=f'Pronóstico {horizonte} Meses (ARIMA{arima_info[0]})', line=dict(dash='dash', color='green')))
        fig.update_layout(
            title=f"Proyección Total de Demanda ({horizonte} meses)",
            xaxis_title="Fecha",
            yaxis_title="Cantidad de Material (m³)"
        )
        st.plotly_chart(fig)

        # Mostrar tabla
        st.write(f"### Tabla de Proyección ({horizonte} meses)")
        forecast_table = pd.DataFrame({"Fecha": dates, "Proyección ARIMA (m³)": forecast.astype(int)})
        st.write(forecast_table)

        # Mostrar MAPE
        st.write(f"**Mejor modelo ARIMA para {horizonte} meses: {arima_info[0]}, con MAPE: {arima_info[1]:.2%}**")

# Código principal
st.title("ProyeKTA+")
st.subheader("Proyecta tu éxito")
st.markdown("Sube un archivo Excel (.xlsx) con los datos históricos de demanda para obtener proyecciones.")

data = upload_and_process_file()
if data is not None:
    show_projection(data)


