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

# Función para encontrar el mejor modelo ARIMA según el menor MAPE
def optimize_arima(data, steps):
    p = range(1, 6)
    d = [1, 2]
    q = range(1, 5)
    best_mape = float("inf")
    best_order = None
    best_model = None

    for order in product(p, d, q):
        try:
            model = ARIMA(data, order=order).fit()
            forecast = model.forecast(steps=steps)
            test_values = data.iloc[-steps:]
            # Verifica que los valores estén en la misma escala y ajusta si es necesario
            mape = mean_absolute_percentage_error(test_values, forecast) * 100  # Asegura que esté en porcentaje
            if mape < best_mape:
                best_mape = mape
                best_order = order
                best_model = model
        except Exception:
            continue

    return best_model, best_order, best_mape


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

        # Proyección de 3 meses fija para el gráfico principal
        train_total = data_privado_total['CANTIDAD_SUAVIZADA']
        best_model_3, best_order_3, best_mape_3 = optimize_arima(train_total, steps=3)
        forecast_3 = best_model_3.forecast(steps=3).apply(lambda x: max(0, x)).astype(int)
        dates_3 = pd.date_range(start=data_privado_total.index[-1] + pd.DateOffset(months=1), periods=3, freq='M')

        # Visualizar datos históricos y suavizados
        st.write("### Proyección Total de Demanda (3 meses)")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data_privado_total.index, y=data_privado_total['CANTIDAD'], 
                                 mode='lines', name='Datos Originales', line=dict(color='red')))
        fig.add_trace(go.Scatter(x=data_privado_total.index, y=data_privado_total['CANTIDAD_SUAVIZADA'], 
                                 mode='lines', name='Datos Suavizados', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=dates_3, y=forecast_3, mode='lines+markers', 
                                 name=f'Pronóstico 3 Meses (ARIMA{best_order_3})', line=dict(dash='dash', color='green')))
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
            st.write(f"Mejor modelo ARIMA para 3 meses: {best_order_3}, con MAPE: {best_mape_3:.2f}%")

        elif projection_choice == "6 meses":
            best_model, best_order, best_mape = optimize_arima(data_privado_total['CANTIDAD_SUAVIZADA'], steps=6)
            forecast_6 = best_model.forecast(steps=6).apply(lambda x: max(0, x)).astype(int)
            dates_6 = pd.date_range(start=data_privado_total.index[-1] + pd.DateOffset(months=1), periods=6, freq='M')
            st.write("#### Tabla de Proyección (6 meses)")
            st.table(pd.DataFrame({"Fecha": dates_6, "Proyección ARIMA (m³)": forecast_6}))
            st.write(f"Mejor modelo ARIMA para 6 meses: {best_order}, con MAPE: {best_mape:.2f}%")

        elif projection_choice == "12 meses":
            best_model, best_order, best_mape = optimize_arima(data_privado_total['CANTIDAD_SUAVIZADA'], steps=12)
            forecast_12 = best_model.forecast(steps=12).apply(lambda x: max(0, x)).astype(int)
            dates_12 = pd.date_range(start=data_privado_total.index[-1] + pd.DateOffset(months=1), periods=12, freq='M')
            st.write("#### Tabla de Proyección (12 meses)")
            st.table(pd.DataFrame({"Fecha": dates_12, "Proyección ARIMA (m³)": forecast_12}))
            st.write(f"Mejor modelo ARIMA para 12 meses: {best_order}, con MAPE: {best_mape:.2f}%")

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


