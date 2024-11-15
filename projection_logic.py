import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error
import matplotlib.pyplot as plt
import streamlit as st

def show_projection(data):
    # Convertir la columna FECHA a tipo datetime y establecerla como índice
    data['FECHA'] = pd.to_datetime(data['FECHA'], errors='coerce')
    data = data.dropna(subset=['FECHA'])
    data = data.set_index('FECHA')

    # Filtrar solo los datos del sector privado
    data_privado = data[data['SECTOR'] == 'PRIVADO']

    if data_privado.empty or len(data_privado) < 12:
        st.warning("No hay suficientes datos para el sector PRIVADO después del resampleo.")
    else:
        # Resamplear a datos mensuales y seleccionar solo la columna CANTIDAD
        data_privado = data_privado[['CANTIDAD']].resample('M').sum()

        # Suavización exponencial con el mejor alpha determinado previamente
        best_alpha = 0.9
        data_privado['CANTIDAD_SUAVIZADA'] = SimpleExpSmoothing(data_privado['CANTIDAD']).fit(smoothing_level=best_alpha, optimized=False).fittedvalues

        # División en conjunto de entrenamiento y prueba
        train = data_privado['CANTIDAD_SUAVIZADA'].iloc[:-3]
        test = data_privado['CANTIDAD_SUAVIZADA'].iloc[-3:]

        # Ajuste del mejor modelo ARIMA encontrado: (4, 1, 1)
        best_order = (4, 1, 1)
        model = ARIMA(train, order=best_order).fit()
        forecast = model.forecast(steps=3)

        # Cálculo de métricas
        mape = mean_absolute_percentage_error(test, forecast)
        rmse = np.sqrt(mean_squared_error(test, forecast))

        # Visualización de resultados en Streamlit
        st.write("### Proyección ARIMA para el Sector Privado")
        st.write(f"**MAPE:** {mape:.2%}, **RMSE:** {rmse:.2f}")

        # Mostrar gráfico
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(train.index, train, label='Datos de Entrenamiento Suavizados')
        ax.plot(test.index, test, label='Datos Reales Suavizados')
        ax.plot(test.index, forecast, label=f'Pronóstico ARIMA({best_order[0]},{best_order[1]},{best_order[2]})', linestyle='--', color='red')
        ax.set_xlabel('Fecha')
        ax.set_ylabel('Cantidad de Material')
        ax.legend()
        ax.set_title(f'Proyección ARIMA({best_order[0]},{best_order[1]},{best_order[2]}) sobre Datos Suavizados')
        st.pyplot(fig)

        # Mostrar tabla con los valores de la proyección
        projection_data = pd.DataFrame({
            'Fecha': test.index,
            'Demanda Real': test.values,
            'Proyección ARIMA': forecast.values
        })
        st.write("### Valores de Proyección para los Próximos 3 Meses")
        st.table(projection_data)
