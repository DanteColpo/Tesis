import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error
import matplotlib.pyplot as plt
import streamlit as st

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

        # Suavización exponencial
        best_alpha = 0.9
        data_privado['CANTIDAD_SUAVIZADA'] = SimpleExpSmoothing(data_privado['CANTIDAD']).fit(smoothing_level=best_alpha, optimized=False).fittedvalues

        # División en conjunto de entrenamiento
        train = data_privado['CANTIDAD_SUAVIZADA']

        # Ajuste del modelo ARIMA
        best_order = (4, 1, 1)
        model = ARIMA(train, order=best_order).fit()

        # Pronóstico para los próximos meses
        forecast_steps = 3  # Proyecta los siguientes 3 meses
        forecast = model.forecast(steps=forecast_steps)
        forecast_dates = pd.date_range(train.index[-1] + pd.DateOffset(months=1), periods=forecast_steps, freq='M')

        # Visualización de resultados
        fig, ax = plt.subplots()
        ax.plot(train.index, train, label='Datos de Entrenamiento Suavizados')
        ax.plot(forecast_dates, forecast, label=f'Pronóstico ARIMA({best_order[0]},{best_order[1]},{best_order[2]})', linestyle='--', color='orange')
        ax.set_xlabel('Fecha')
        ax.set_ylabel('Cantidad de Material')
        ax.legend()

        # Formato de las fechas en el eje X
        ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m'))  # Solo muestra año y mes
        plt.xticks(rotation=45)  # Rota las etiquetas de fechas para mayor claridad

        st.pyplot(fig)

        # Mostrar resultados en tabla con formato de mes y año
        forecast_table = pd.DataFrame({
            'Fecha': forecast_dates.strftime('%B %Y'),  # Formato de mes y año
            'Proyección ARIMA': forecast
        })
        st.write("### Valores de Proyección para los Próximos Meses")
        st.write(forecast_table)
