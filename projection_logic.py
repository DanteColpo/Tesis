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

    if data_privado.empty or len(data_privado) < 12:
        st.warning("No hay suficientes datos para el sector PRIVADO después del resampleo.")
        return
    else:
        # Resamplear a datos mensuales y seleccionar solo la columna CANTIDAD
        data_privado = data_privado[['CANTIDAD']].resample('M').sum()

        # Suavización exponencial
        best_alpha = 0.9
        data_privado['CANTIDAD_SUAVIZADA'] = SimpleExpSmoothing(data_privado['CANTIDAD']).fit(smoothing_level=best_alpha, optimized=False).fittedvalues

        # División en conjunto de entrenamiento y prueba
        train = data_privado['CANTIDAD_SUAVIZADA'].iloc[:-3]
        test = data_privado['CANTIDAD_SUAVIZADA'].iloc[-3:]

        # Búsqueda del mejor modelo ARIMA
        best_mape = float('inf')
        best_rmse = float('inf')
        best_order = None

        for p in range(1, 5):
            for d in range(1, 2):  # Fijamos d en 1 para diferenciar solo una vez
                for q in range(1, 5):
                    try:
                        model = ARIMA(train, order=(p, d, q)).fit()
                        forecast = model.forecast(steps=3)
                        mape = mean_absolute_percentage_error(test, forecast)
                        rmse = np.sqrt(mean_squared_error(test, forecast))

                        if mape < best_mape:
                            best_mape = mape
                            best_rmse = rmse
                            best_order = (p, d, q)

                    except Exception as e:
                        st.write(f"Error en ARIMA({p},{d},{q}): {e}")

        # Mostrar el mejor modelo encontrado
        st.write(f"Mejor modelo ARIMA encontrado: {best_order} con Precisión del Pronóstico: {100 - best_mape:.2f}% (MAPE: {best_mape:.2%})")

        # Pronóstico final usando el mejor modelo
        model = ARIMA(train, order=best_order).fit()
        forecast_steps = 3  # Proyecta los siguientes 3 meses
        forecast = model.forecast(steps=forecast_steps)
        forecast_dates = pd.date_range(train.index[-1] + pd.DateOffset(months=1), periods=forecast_steps, freq='M')

        # Visualización del resultado
        fig, ax = plt.subplots()
        ax.plot(train.index, train, label='Datos de Entrenamiento Suavizados')
        ax.plot(test.index, test, label='Datos Reales Suavizados')
        ax.plot(forecast_dates, forecast, label=f'Pronóstico ARIMA{best_order}', linestyle='--', color='orange')
        ax.set_xlabel('Fecha')
        ax.set_ylabel('Cantidad de Material')
        ax.legend()

        st.pyplot(fig)

        # Mostrar resultados en tabla
        forecast_table = pd.DataFrame({
            'Fecha': forecast_dates.strftime("%B %Y"),
            'Proyección ARIMA': forecast.values
        })
        st.write("### Valores de Proyección para los Próximos Meses")
        st.write(forecast_table)

        # Explicación sobre la precisión del pronóstico
        st.write("### Precisión del Pronóstico:")
        st.write(f"Este modelo tiene un nivel de precisión del {100 - best_mape:.2f}%, lo que indica que los valores pronosticados están cercanos a los valores reales históricos.")
        st.write("**Interpretación del gráfico:** Las líneas muestran la proyección de demanda esperada en comparación con los datos reales anteriores. La línea sólida representa los datos suavizados históricos, y la línea discontinua muestra la proyección del modelo ARIMA.")

# Cargar y procesar el archivo
data = upload_and_process_file()
if data is not None:
    show_projection(data)
