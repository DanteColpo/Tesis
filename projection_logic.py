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

def find_best_alpha(data):
    """Función para encontrar el mejor alpha minimizando el MAPE en la suavización exponencial."""
    best_alpha = None
    best_mape = float('inf')
    
    for alpha in np.arange(0.1, 1.0, 0.1):  # Búsqueda de alpha en pasos de 0.1
        fitted_values = SimpleExpSmoothing(data['CANTIDAD']).fit(smoothing_level=alpha, optimized=False).fittedvalues
        mape = mean_absolute_percentage_error(data['CANTIDAD'], fitted_values)
        
        if mape < best_mape:
            best_mape = mape
            best_alpha = alpha
    
    return best_alpha, best_mape

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

    # Resamplear a datos mensuales y seleccionar solo la columna CANTIDAD
    data_privado = data_privado[['CANTIDAD']].resample('M').sum()

    # Buscar el mejor alpha para la suavización exponencial
    best_alpha, best_mape = find_best_alpha(data_privado)
    data_privado['CANTIDAD_SUAVIZADA'] = SimpleExpSmoothing(data_privado['CANTIDAD']).fit(smoothing_level=best_alpha, optimized=False).fittedvalues

    # División en conjunto de entrenamiento y prueba
    train = data_privado['CANTIDAD_SUAVIZADA'].iloc[:-3]
    test = data_privado['CANTIDAD_SUAVIZADA'].iloc[-3:]

    # Buscar el mejor modelo ARIMA (4,1,1) o ajustar otros valores
    best_order = (4, 1, 1)
    model = ARIMA(train, order=best_order).fit()
    forecast = model.forecast(steps=3)

    # Cálculo de métricas
    mape = mean_absolute_percentage_error(test, forecast)
    rmse = np.sqrt(mean_squared_error(test, forecast))

    # Visualización de resultados
    fig, ax = plt.subplots()
    ax.plot(train.index, train, label='Datos de Entrenamiento Suavizados')
    ax.plot(test.index, test, label='Datos Reales Suavizados')
    ax.plot(pd.date_range(test.index[-1], periods=4, freq='M')[1:], forecast, label=f'Pronóstico ARIMA({best_order[0]},{best_order[1]},{best_order[2]})', linestyle='--', color='orange')
    ax.set_xlabel('Fecha')
    ax.set_ylabel('Cantidad de Material')
    ax.legend()
    st.pyplot(fig)

    # Mostrar resultados en tabla
    forecast_table = pd.DataFrame({
        'Fecha': pd.date_range(test.index[-1] + pd.DateOffset(months=1), periods=3, freq='M'),
        'Proyección ARIMA': forecast
    })
    st.write("### Valores de Proyección para los Próximos Meses")
    st.write(forecast_table)

    # Mostrar precisión y alpha óptimo
    st.write(f"### Mejor alpha encontrado para Suavización Exponencial: {best_alpha:.2f}")
    st.write(f"### Precisión del Pronóstico: {100 - mape:.2f}% (MAPE: {mape:.2f}%)")
