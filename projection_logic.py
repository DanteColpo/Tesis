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

# Función para optimizar el modelo ARIMA
def optimize_arima(data, steps):
    p = range(1, 6)
    d = [1]
    q = range(0, 4)
    best_mape = float("inf")
    best_order = None
    best_model = None

    for order in itertools.product(p, d, q):
        try:
            model = ARIMA(data, order=order).fit()
            forecast = model.forecast(steps=steps)
            mape = mean_absolute_percentage_error(data.iloc[-steps:], forecast)
            if mape < best_mape:
                best_mape = mape
                best_order = order
                best_model = model
        except:
            continue
    return best_model, best_order, best_mape

# Función para generar las proyecciones por horizonte
def generate_projection(data, steps):
    forecast_results = {}
    if 'MATERIAL' in data.columns:
        for material in data['MATERIAL'].unique():
            material_data = data[data['MATERIAL'] == material]
            material_data = material_data[['CANTIDAD']].resample('M').sum()
            
            if material_data['CANTIDAD'].count() < 6:
                st.warning(f"El material '{material}' tiene datos insuficientes para una proyección fiable y se omitirá.")
                continue

            material_data['CANTIDAD_SUAVIZADA'] = SimpleExpSmoothing(
                material_data['CANTIDAD']
            ).fit(smoothing_level=alpha, optimized=False).fittedvalues
            
            best_model, best_order, best_mape = optimize_arima(material_data['CANTIDAD_SUAVIZADA'], steps)

            forecast = best_model.forecast(steps=steps).apply(lambda x: max(0, x))
            forecast_dates = pd.date_range(start=material_data.index[-1] + pd.DateOffset(months=1), periods=steps, freq='M')

            forecast_results[material] = {
                "Fecha": forecast_dates.strftime('%B %Y'),
                "Proyección (m³)": forecast.round().astype(int),
                "MAPE": best_mape
            }

    return forecast_results

# Función principal para mostrar proyecciones
def show_projection(data):
    st.write("Proyección ARIMA para el Sector Privado")

    data['FECHA'] = pd.to_datetime(data['FECHA'], errors='coerce')
    data = data.dropna(subset=['FECHA'])
    data = data.set_index('FECHA')

    data_privado = data[data['SECTOR'] == 'PRIVADO']

    if data_privado.empty or len(data_privado) < 12:
        st.warning("No hay suficientes datos para el sector PRIVADO después del resampleo.")
        return

    # Selección de horizonte de predicción
    horizonte = st.selectbox("Selecciona el horizonte de proyección:", [3, 6, 12], index=0)

    # Proyección por material
    forecast_results = generate_projection(data_privado, horizonte)

    if forecast_results:
        st.write(f"### Proyección Desglosada por Tipo de Material ({horizonte} meses)")
        for material, result in forecast_results.items():
            st.write(f"#### {material}")
            forecast_table = pd.DataFrame({
                "Fecha": result["Fecha"],
                "Proyección ARIMA (m³)": result["Proyección (m³)"
                ]
            })
            st.write(forecast_table)

    # Proyección total
    st.write("### Proyección Total de Demanda (Todos los Tipos de Material)")

    data_total = data_privado[['CANTIDAD']].resample('M').sum()
    data_total['CANTIDAD_SUAVIZADA'] = SimpleExpSmoothing(
        data_total['CANTIDAD']
    ).fit(smoothing_level=alpha, optimized=False).fittedvalues

    best_model, best_order, best_mape = optimize_arima(data_total['CANTIDAD_SUAVIZADA'], horizonte)

    forecast = best_model.forecast(steps=horizonte).apply(lambda x: max(0, x))
    forecast_dates = pd.date_range(start=data_total.index[-1] + pd.DateOffset(months=1), periods=horizonte, freq='M')

    if horizonte == 3:  # Gráfico solo para 3 meses
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data_total.index, y=data_total['CANTIDAD_SUAVIZADA'], mode='lines', name='Datos Suavizados'))
        fig.add_trace(go.Scatter(x=forecast_dates, y=forecast, mode='lines+markers', name=f'Pronóstico ARIMA{best_order}', line=dict(dash='dash', color='green')))
        fig.update_layout(
            title=f"Proyección ARIMA{best_order} ({horizonte} meses)",
            xaxis_title='Fecha',
            yaxis_title='Cantidad de Material (m³)'
        )
        st.plotly_chart(fig)

    st.write(f"### Error Promedio del Pronóstico ({horizonte} meses)")
    st.write(f"Error Promedio Asociado (MAPE): {best_mape:.2%}")

# Main
st.title("Proyección de Demanda con ARIMA")
data = upload_and_process_file()
if data is not None:
    show_projection(data)


