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

# Función para mostrar la proyección ARIMA
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
        # Resamplear a datos mensuales y seleccionar solo la columna CANTIDAD
        data_privado = data_privado[['CANTIDAD']].resample('M').sum()

        # Suavización exponencial con el mejor alpha
        alpha = 0.9
        data_privado['CANTIDAD_SUAVIZADA'] = SimpleExpSmoothing(data_privado['CANTIDAD']).fit(smoothing_level=alpha, optimized=False).fittedvalues

        # División en conjunto de entrenamiento y prueba
        train = data_privado['CANTIDAD_SUAVIZADA'].iloc[:-3]
        test = data_privado['CANTIDAD_SUAVIZADA'].iloc[-3:]

        # Optimización de parámetros ARIMA en un rango limitado, minimizando el MAPE
        best_mape = float("inf")
        best_order = None
        best_model = None

        # Rango limitado de p, d, q
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

        # Generación de la proyección con el mejor modelo
        forecast = best_model.forecast(steps=3)
        forecast_dates = pd.date_range(test.index[-1], periods=4, freq='M')[1:]

        # Gráfico interactivo con plotly
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=train.index, y=train, mode='lines', name='Datos de Entrenamiento Suavizados'))
        fig.add_trace(go.Scatter(x=test.index, y=test, mode='lines', name='Datos Reales Suavizados', line=dict(color='orange')))
        fig.add_trace(go.Scatter(x=forecast_dates, y=forecast, mode='lines+markers', name=f'Pronóstico ARIMA{best_order}', line=dict(dash='dash', color='green')))
        fig.update_layout(
            title=f'Proyección ARIMA{best_order} sobre Datos Suavizados',
            xaxis_title='Fecha',
            yaxis_title='Cantidad de Material (m³)',
            xaxis=dict(tickformat="%b %Y"),
            hovermode="x"
        )
        st.plotly_chart(fig)

        # Mostrar resultados en tabla sin decimales
        forecast_table = pd.DataFrame({
            'Fecha': forecast_dates.strftime('%B %Y'),
            'Proyección ARIMA (m³)': forecast.round().astype(int)  # Mostramos solo enteros y añadimos m³
        })
        st.write("### Valores de Proyección para los Próximos Meses")
        st.write(forecast_table)

        # Mostrar el Error Promedio (MAPE) sin decimales
        st.write("### Error Promedio del Pronóstico")
        st.write(f"Error Promedio (MAPE): {best_mape:.2%}")

        # Explicación del gráfico
        st.write("Este modelo tiene un nivel de error promedio que indica qué tan cerca están los valores pronosticados de los valores reales históricos.")
        st.write("**Interpretación del gráfico:** Las líneas muestran la proyección de demanda esperada en comparación con los datos reales anteriores. La línea sólida representa los datos suavizados históricos, y la línea discontinua muestra la proyección del modelo ARIMA.")

