import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
from statsmodels.tsa.arima.model import ARIMA
from itertools import product
from sklearn.metrics import mean_absolute_percentage_error

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

# Función para optimizar ARIMA
def optimize_arima(data, steps):
    p = range(1, 6)
    d = [1, 2]
    q = range(1, 4)
    best_mape = float("inf")
    best_order = None
    best_model = None

    for order in product(p, d, q):
        try:
            model = ARIMA(data, order=order).fit()
            forecast = model.forecast(steps=steps)
            test_values = data.iloc[-steps:]
            mape = mean_absolute_percentage_error(test_values, forecast) * 100  # En porcentaje
            if mape < best_mape:
                best_mape = mape
                best_order = order
                best_model = model
        except Exception:
            continue

    return best_model, best_order, best_mape

# Validar el modelo ARIMA (5, 1, 3)
def validate_fixed_arima(data, steps):
    fixed_order = (5, 1, 3)
    try:
        model = ARIMA(data, order=fixed_order).fit()
        forecast = model.forecast(steps=steps)
        test_values = data.iloc[-steps:]
        mape = mean_absolute_percentage_error(test_values, forecast) * 100
        return model, fixed_order, mape, forecast
    except Exception:
        return None, fixed_order, None, None

# Función para calcular la proyección de 3 meses
def calculate_3_months_projection(data):
    data['FECHA'] = pd.to_datetime(data['FECHA'], errors='coerce')
    data = data.dropna(subset=['FECHA'])
    data = data.set_index('FECHA')
    data_privado = data[data['SECTOR'] == 'PRIVADO']
    data_privado = data_privado[['CANTIDAD']].resample('M').sum()

    if data_privado.empty or len(data_privado) < 12:
        st.warning("No hay suficientes datos para el sector PRIVADO después del resampleo.")
        return None, None, None, None, None

    # Suavización
    data_privado['CANTIDAD_SUAVIZADA'] = SimpleExpSmoothing(
        data_privado['CANTIDAD']
    ).fit(smoothing_level=0.9, optimized=False).fittedvalues

    # Optimizar ARIMA para 3 meses
    train = data_privado['CANTIDAD_SUAVIZADA']
    best_model, best_order, best_mape = optimize_arima(train, steps=3)

    # Validar el modelo fijo (5, 1, 3)
    fixed_model, fixed_order, fixed_mape, fixed_forecast = validate_fixed_arima(train, steps=3)

    # Proyección del mejor modelo
    if fixed_model and fixed_mape < best_mape:
        final_model, final_order, final_mape = fixed_model, fixed_order, fixed_mape
        forecast = fixed_forecast
    else:
        final_model, final_order, final_mape = best_model, best_order, best_mape
        forecast = final_model.forecast(steps=3).apply(lambda x: max(0, x)).astype(int)

    dates = pd.date_range(start=data_privado.index[-1] + pd.DateOffset(months=1), periods=3, freq='M')

    return data_privado, forecast, dates, (final_order, final_mape)

# Función principal para mostrar la proyección
def show_projection(data):
    try:
        # Cálculo de proyección para 3 meses
        data_privado, forecast_3, dates_3, arima_info = calculate_3_months_projection(data)

        if data_privado is not None:
            # Visualización de resultados
            st.write("### Proyección Total de Demanda (3 meses)")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=data_privado.index, y=data_privado['CANTIDAD'],
                                     mode='lines', name='Datos Originales', line=dict(color='red')))
            fig.add_trace(go.Scatter(x=data_privado.index, y=data_privado['CANTIDAD_SUAVIZADA'],
                                     mode='lines', name='Datos Suavizados', line=dict(color='blue')))
            fig.add_trace(go.Scatter(x=dates_3, y=forecast_3, mode='lines+markers',
                                     name=f'Pronóstico 3 Meses (ARIMA{arima_info[0]})', line=dict(dash='dash', color='green')))
            fig.update_layout(
                title="Proyección Total de Demanda (3 meses)",
                xaxis_title="Fecha",
                yaxis_title="Cantidad de Material (m³)"
            )
            st.plotly_chart(fig)

            # Mostrar tabla y métricas
            st.write("#### Tabla de Proyección (3 meses)")
            st.table(pd.DataFrame({"Fecha": dates_3, "Proyección ARIMA (m³)": forecast_3}))
            st.write(f"Mejor modelo ARIMA para 3 meses: {arima_info[0]}, con MAPE: {arima_info[1]:.2f}%")
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

