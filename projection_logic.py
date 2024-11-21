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
def optimize_arima(data, steps):
    best_mape = float("inf")
    best_order = None
    best_model = None
    for combination in itertools.product(range(1, 6), [1], range(0, 4)):
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

# Función para generar proyección desglosada
def generar_proyeccion_desglosada(data, horizonte):
    forecast_results = {}
    if 'MATERIAL' in data.columns:
        for product_type in data['MATERIAL'].unique():
            data_producto = data[data['MATERIAL'] == product_type]
            data_producto = data_producto[['CANTIDAD']].resample('M').sum()

            if data_producto['CANTIDAD'].count() < horizonte:
                st.warning(f"El material '{product_type}' tiene datos insuficientes para una proyección fiable y se omitirá.")
                continue

            data_producto['CANTIDAD_SUAVIZADA'] = SimpleExpSmoothing(data_producto['CANTIDAD']).fit(smoothing_level=alpha, optimized=False).fittedvalues

            best_model, best_order, _ = optimize_arima(data_producto['CANTIDAD_SUAVIZADA'], steps=horizonte)
            forecast = best_model.forecast(steps=horizonte).apply(lambda x: max(0, x)).astype(int)
            forecast_dates = pd.date_range(start=data_producto.index[-1] + pd.DateOffset(months=1), periods=horizonte, freq='M')

            forecast_results[product_type] = {
                "Fecha": forecast_dates.strftime('%B %Y'),
                "Proyección (m³)": forecast
            }
    return forecast_results

# Función principal para mostrar la proyección
def show_projection(data):
    st.write("Proyección ARIMA para el Sector Privado")
    data['FECHA'] = pd.to_datetime(data['FECHA'], errors='coerce')
    data = data.dropna(subset=['FECHA'])
    data = data.set_index('FECHA')
    data_privado = data[data['SECTOR'] == 'PRIVADO']

    if data_privado.empty or len(data_privado) < 12:
        st.warning("No hay suficientes datos para el sector PRIVADO después del resampleo.")
        return

    # Selector para el horizonte de proyección
    horizonte = st.selectbox("Selecciona el horizonte de proyección:", [3, 6, 12], index=0)

    # Mostrar tabla desglosada por tipo de material
    st.write(f"### Proyección Desglosada por Tipo de Material ({horizonte} meses)")
    forecast_results = generar_proyeccion_desglosada(data_privado, horizonte)
    for product_type, results in forecast_results.items():
        st.write(f"#### {product_type}")
        forecast_table = pd.DataFrame({
            "Fecha": results["Fecha"],
            "Proyección ARIMA (m³)": results["Proyección (m³)"]
        })
        st.write(forecast_table)

    # Solo generar el gráfico para 3 meses
    if horizonte == 3:
        st.write("### Proyección Total de Demanda (3 meses)")
        data_privado_total = data_privado[['CANTIDAD']].resample('M').sum()
        data_privado_total['CANTIDAD_SUAVIZADA'] = SimpleExpSmoothing(data_privado_total['CANTIDAD']).fit(smoothing_level=alpha, optimized=False).fittedvalues
        train_total = data_privado_total['CANTIDAD_SUAVIZADA'].iloc[:-3]
        test_total = data_privado_total['CANTIDAD_SUAVIZADA'].iloc[-3:]

        best_model, best_order, best_mape = optimize_arima(train_total, steps=3)
        forecast = best_model.forecast(steps=3).apply(lambda x: max(0, x))
        forecast_dates = pd.date_range(start=data_privado_total.index[-1] + pd.DateOffset(months=1), periods=3, freq='M')

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=train_total.index, y=train_total, mode='lines', name='Datos de Entrenamiento Suavizados'))
        fig.add_trace(go.Scatter(x=test_total.index, y=test_total, mode='lines', name='Datos Reales Suavizados', line=dict(color='orange')))
        fig.add_trace(go.Scatter(x=forecast_dates, y=forecast, mode='lines+markers', name=f'Pronóstico ARIMA{best_order}', line=dict(dash='dash', color='green')))
        fig.update_layout(
            title=f'Proyección ARIMA{best_order} sobre Datos Suavizados (Total)',
            xaxis_title='Fecha',
            yaxis_title='Cantidad de Material (m³)',
            xaxis=dict(tickformat="%b %Y"),
            hovermode="x"
        )
        st.plotly_chart(fig)

        st.write("### Error Promedio del Pronóstico (3 meses)")
        st.write(f"Error Promedio Asociado (MAPE): {best_mape:.2%}")

# Código principal
st.title("ProyeKTA+")
st.subheader("Proyecta tu éxito")
st.markdown("Sube un archivo Excel (.xlsx) con los datos históricos de demanda para obtener proyecciones.")

data = upload_and_process_file()
if data is not None:
    show_projection(data)
