import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_percentage_error
import itertools

# Configuración inicial de la página
st.set_page_config(page_title="ProyeKTA+", page_icon="📊", layout="centered")

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
    else:
        # Crear un diccionario para almacenar las proyecciones de cada tipo de producto
        forecast_results = {}

        # Proyección para cada tipo de material
        for product_type in data_privado['TIPO_PRODUCTO'].unique():
            # Filtrar los datos por tipo de producto
            data_producto = data_privado[data_privado['TIPO_PRODUCTO'] == product_type]
            data_producto = data_producto[['CANTIDAD']].resample('M').sum()

            # Suavización exponencial
            alpha = 0.9
            data_producto['CANTIDAD_SUAVIZADA'] = SimpleExpSmoothing(data_producto['CANTIDAD']).fit(smoothing_level=alpha, optimized=False).fittedvalues

            # División en conjunto de entrenamiento y prueba
            train = data_producto['CANTIDAD_SUAVIZADA'].iloc[:-3]
            test = data_producto['CANTIDAD_SUAVIZADA'].iloc[-3:]

            # Optimización de parámetros ARIMA en un rango limitado
            best_mape = float("inf")
            best_order = None
            best_model = None

            # Búsqueda de los mejores valores de p, d, q
            p = range(3, 6)
            d = [1]
            q = range(0, 4)

            for combination in itertools.product(p, d, q):
                try:
                    model = ARIMA(train, order=combination).fit()
                    forecast = model.forecast(steps=3)
                    mape = mean_absolute_percentage_error(test, forecast)

                    if mape < best_mape:
                        best_mape = mape
                        best_order = combination
                        best_model = model
                except Exception as e:
                    continue

            # Generar proyección para los próximos 3 meses
            forecast = best_model.forecast(steps=3)
            forecast_dates = pd.date_range(test.index[-1], periods=4, freq='M')[1:]

            # Guardar los resultados en el diccionario
            forecast_results[product_type] = {
                "Fecha": forecast_dates.strftime('%B %Y'),
                "Proyección (m³)": forecast.round().astype(int)
            }

        # Gráfico interactivo con plotly para el total
        st.write("### Proyección Total de Demanda (Todos los Tipos de Material)")
        data_privado = data_privado[['CANTIDAD']].resample('M').sum()
        data_privado['CANTIDAD_SUAVIZADA'] = SimpleExpSmoothing(data_privado['CANTIDAD']).fit(smoothing_level=alpha, optimized=False).fittedvalues
        train = data_privado['CANTIDAD_SUAVIZADA'].iloc[:-3]
        test = data_privado['CANTIDAD_SUAVIZADA'].iloc[-3:]

        # Optimización automática para el total
        best_mape = float("inf")
        best_order = None
        best_model = None
        for combination in itertools.product(p, d, q):
            try:
                model = ARIMA(train, order=combination).fit()
                forecast = model.forecast(steps=3)
                mape = mean_absolute_percentage_error(test, forecast)

                if mape < best_mape:
                    best_mape = mape
                    best_order = combination
                    best_model = model
            except Exception as e:
                continue

        # Proyección con el mejor modelo para el total
        forecast = best_model.forecast(steps=3)
        forecast_dates = pd.date_range(test.index[-1], periods=4, freq='M')[1:]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=train.index, y=train, mode='lines', name='Datos de Entrenamiento Suavizados'))
        fig.add_trace(go.Scatter(x=test.index, y=test, mode='lines', name='Datos Reales Suavizados', line=dict(color='orange')))
        fig.add_trace(go.Scatter(x=forecast_dates, y=forecast, mode='lines+markers', name=f'Pronóstico ARIMA{best_order}', line=dict(dash='dash', color='green')))
        fig.update_layout(
            title=f'Proyección ARIMA{best_order} sobre Datos Suavizados (Total)',
            xaxis_title='Fecha',
            yaxis_title='Cantidad de Material (m³)',
            xaxis=dict(tickformat="%b %Y"),
            hovermode="x"
        )
        st.plotly_chart(fig)

        # Tabla desglosada por tipo de material
        st.write("### Proyección Desglosada por Tipo de Material")
        for product_type, results in forecast_results.items():
            st.write(f"#### {product_type}")
            forecast_table = pd.DataFrame({
                "Fecha": results["Fecha"],
                "Proyección ARIMA (m³)": results["Proyección (m³)"]
            })
            st.write(forecast_table)
