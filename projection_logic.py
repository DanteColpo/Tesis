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

# Función para realizar proyecciones ARIMA
def arima_forecast(data, horizon):
    # Suavización exponencial
    data['CANTIDAD_SUAVIZADA'] = SimpleExpSmoothing(data['CANTIDAD']).fit(smoothing_level=alpha, optimized=False).fittedvalues

    # División en conjunto de entrenamiento y prueba
    train = data['CANTIDAD_SUAVIZADA'].iloc[:-horizon]
    test = data['CANTIDAD_SUAVIZADA'].iloc[-horizon:]

    # Optimización de parámetros ARIMA
    best_mape = float("inf")
    best_order = None
    best_model = None

    # Búsqueda de los mejores valores de p, d, q
    p = range(1, 6)
    d = [1]
    q = range(0, 4)
    for combination in itertools.product(p, d, q):
        try:
            model = ARIMA(train, order=combination).fit()
            forecast = model.forecast(steps=horizon)
            mape = mean_absolute_percentage_error(test, forecast)

            if mape < best_mape:
                best_mape = mape
                best_order = combination
                best_model = model
        except:
            continue

    # Generar proyección para los próximos meses
    forecast = best_model.forecast(steps=horizon)
    forecast = forecast.apply(lambda x: max(0, x))  # Establecer valores negativos en 0
    forecast_dates = pd.date_range(start=data.index[-1] + pd.DateOffset(months=1), periods=horizon, freq='M')

    return forecast, forecast_dates, best_order, best_mape

# Función para mostrar la proyección ARIMA general y desglosada
def show_projection(data):
    st.write("Proyección ARIMA para el Sector Privado")

    # Convertir la columna FECHA a tipo datetime y establecerla como índice
    data['FECHA'] = pd.to_datetime(data['FECHA'], errors='coerce')
    data = data.dropna(subset=['FECHA'])
    data = data.set_index('FECHA')

    # Filtrar solo los datos del sector privado
    data_privado = data[data['SECTOR'] == 'PRIVADO']

    if data_privado.empty or len(data_privado) < 12:
        st.warning("No hay suficientes datos para el sector PRIVADO después del resampleo.")
        return

    # Desglosar por tipo de material
    st.write("### Proyección Desglosada por Tipo de Material")
    forecast_results = {}
    if 'MATERIAL' in data_privado.columns:
        for product_type in data_privado['MATERIAL'].unique():
            data_producto = data_privado[data_privado['MATERIAL'] == product_type][['CANTIDAD']].resample('M').sum()

            if len(data_producto) < 6:
                st.warning(f"El material '{product_type}' tiene datos insuficientes para una proyección fiable y se omitirá.")
                continue

            forecast, forecast_dates, _, _ = arima_forecast(data_producto, horizon=3)
            forecast_results[product_type] = {
                "Fecha": forecast_dates.strftime('%B %Y'),
                "Proyección (m³)": forecast.round().astype(int)
            }

        for product_type, results in forecast_results.items():
            st.write(f"#### {product_type}")
            forecast_table = pd.DataFrame({
                "Fecha": results["Fecha"],
                "Proyección ARIMA (m³)": results["Proyección (m³)"]
            })
            st.write(forecast_table)

    # Proyección total
    st.write("### Proyección Total de Demanda (Todos los Tipos de Material)")
    data_privado_total = data_privado[['CANTIDAD']].resample('M').sum()

    horizon = st.selectbox("Selecciona el horizonte de proyección (meses):", [3, 6, 12])
    forecast, forecast_dates, best_order, best_mape = arima_forecast(data_privado_total, horizon=horizon)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data_privado_total.index, y=data_privado_total['CANTIDAD'], mode='lines', name='Datos Suavizados'))
    fig.add_trace(go.Scatter(x=forecast_dates, y=forecast, mode='lines+markers', name=f'Pronóstico ARIMA{best_order} ({horizon} meses)', line=dict(dash='dash', color='green')))
    fig.update_layout(
        title=f'Proyección ARIMA{best_order} ({horizon} meses)',
        xaxis_title='Fecha',
        yaxis_title='Cantidad de Material (m³)',
        hovermode="x"
    )
    st.plotly_chart(fig)

    st.write(f"### Error Promedio del Pronóstico ({horizon} meses)")
    st.write(f"Error Promedio Asociado (MAPE): {best_mape:.2%}")

# Streamlit app
def main():
    st.title("Proyección de Demanda ARIMA")
    data = upload_and_process_file()
    if data is not None:
        show_projection(data)

if __name__ == "__main__":
    main()
