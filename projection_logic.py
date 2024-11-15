import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import matplotlib.dates as mdates
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error

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
        best_alpha = 0.9
        data_privado['CANTIDAD_SUAVIZADA'] = SimpleExpSmoothing(data_privado['CANTIDAD']).fit(smoothing_level=best_alpha, optimized=False).fittedvalues

        # División en conjunto de entrenamiento y prueba
        train = data_privado['CANTIDAD_SUAVIZADA'].iloc[:-3]
        test = data_privado['CANTIDAD_SUAVIZADA'].iloc[-3:]

        # Ajuste del modelo ARIMA
        best_order = (4, 1, 1)
        model = ARIMA(train, order=best_order).fit()

        # Pronóstico para los próximos meses
        forecast_steps = 3  # Proyecta los siguientes 3 meses
        forecast = model.forecast(steps=forecast_steps)
        forecast_dates = pd.date_range(test.index[-1], periods=forecast_steps + 1, freq='M')[1:]

        # Cálculo del MAPE como "Error Promedio"
        mape = mean_absolute_percentage_error(test, forecast)

        # Visualización del gráfico
        fig, ax = plt.subplots()
        ax.plot(train.index, train, label='Datos de Entrenamiento Suavizados')
        ax.plot(test.index, test, label='Datos Reales Suavizados')
        ax.plot(forecast_dates, forecast, label=f'Pronóstico ARIMA({best_order[0]},{best_order[1]},{best_order[2]})', linestyle='--', color='orange')
        ax.set_xlabel('Fecha')
        ax.set_ylabel('Cantidad de Material')
        ax.legend()

        # Formato de fecha en el eje X
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
        plt.xticks(rotation=45)

        # Mostrar el gráfico en Streamlit
        st.pyplot(fig)

        # Mostrar resultados en tabla
        forecast_table = pd.DataFrame({
            'Fecha': forecast_dates.strftime('%B %Y'),
            'Proyección ARIMA': forecast
        })
        st.write("### Valores de Proyección para los Próximos Meses")
        st.write(forecast_table)

        # Mostrar el Error Promedio (MAPE)
        st.write("### Error Promedio del Pronóstico")
        st.write(f"Error Promedio (MAPE): {mape:.2%}")

        # Agregar una breve explicación sobre cómo interpretar el error promedio
        st.write("Este modelo tiene un nivel de error promedio que indica qué tan cerca están los valores pronosticados de los valores reales históricos.")
        st.write("**Interpretación del gráfico:** Las líneas muestran la proyección de demanda esperada en comparación con los datos reales anteriores. La línea sólida representa los datos suavizados históricos, y la línea discontinua muestra la proyección del modelo ARIMA.")

# Configuración de la página y diseño inicial
st.title("ProyeKTA+")
st.subheader("Proyecta tu éxito")
st.markdown("Sube un archivo Excel (.xlsx) con los datos de demanda histórica para obtener una proyección de los próximos meses.")

# Cargar el archivo y procesar datos para la proyección
data = upload_and_process_file()
if data is not None:
    show_projection(data)
