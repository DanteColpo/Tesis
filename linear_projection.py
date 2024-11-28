import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_percentage_error
from statsmodels.tsa.holtwinters import SimpleExpSmoothing

# Definir alpha globalmente para la suavización exponencial
alpha = 0.9

def preprocess_data(data):
    """
    Preprocesar los datos cargados, filtrando por sector privado
    y resampleando mensualmente.
    """
    data['FECHA'] = pd.to_datetime(data['FECHA'], errors='coerce')
    data = data.dropna(subset=['FECHA'])
    data = data.set_index('FECHA')
    data_privado = data[data['SECTOR'] == 'PRIVADO']
    return data_privado[['CANTIDAD']].resample('MS').sum()  # Resampleo mensual con suma

def linear_forecast(data, horizon):
    """
    Realiza proyecciones lineales en base a los datos proporcionados.
    Devuelve la proyección, las fechas proyectadas y el MAPE asociado.
    """
    # Suavización exponencial
    data['CANTIDAD_SUAVIZADA'] = SimpleExpSmoothing(data['CANTIDAD']).fit(smoothing_level=alpha, optimized=False).fittedvalues

    # División en conjunto de entrenamiento y prueba
    train = data['CANTIDAD_SUAVIZADA'].iloc[:-horizon]
    test = data['CANTIDAD_SUAVIZADA'].iloc[-horizon:]

    # Crear las variables independientes para regresión lineal
    train_index = np.arange(len(train)).reshape(-1, 1)
    test_index = np.arange(len(train), len(train) + horizon).reshape(-1, 1)

    # Ajustar el modelo de regresión lineal
    linear_model = LinearRegression()
    linear_model.fit(train_index, train)

    # Generar las proyecciones
    forecast = linear_model.predict(test_index)
    forecast = np.maximum(forecast, 0)  # Establecer valores negativos en 0
    forecast_dates = pd.date_range(start=data.index[-1] + pd.DateOffset(months=1), periods=horizon, freq='M')

    # Calcular el MAPE
    mape = mean_absolute_percentage_error(test, forecast)

    return forecast, forecast_dates, mape

def run_linear_projection(data, horizon=3):
    """
    Función principal para ejecutar Proyección Lineal sobre un conjunto de datos.
    Devuelve las proyecciones y las métricas asociadas.
    """
    data_processed = preprocess_data(data)
    forecast, forecast_dates, mape = linear_forecast(data_processed, horizon)
    return {
        "forecast": forecast,
        "forecast_dates": forecast_dates,
        "mape": mape
    }
