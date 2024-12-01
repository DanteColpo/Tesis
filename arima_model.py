from data_preprocessor import preprocess_data  # Importar la nueva función de preprocesamiento
import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_percentage_error
import itertools

# Definir alpha globalmente para la suavización exponencial
alpha = 0.9

def arima_forecast(data, horizon):
    """
    Realiza proyecciones ARIMA en base a los datos proporcionados.
    Devuelve la proyección, las fechas proyectadas, el mejor orden
    y el MAPE asociado.
    """
    # Suavización exponencial
    data['CANTIDAD_SUAVIZADA'] = SimpleExpSmoothing(data['CANTIDAD']).fit(smoothing_level=alpha, optimized=False).fittedvalues

    # División en conjunto de entrenamiento y prueba
    train = data['CANTIDAD_SUAVIZADA'].iloc[:-horizon]
    test = data['CANTIDAD_SUAVIZADA'].iloc[-horizon:]

    # Optimización de parámetros ARIMA
    best_mape = float("inf")
    best_order = None
    best_model = None

    # Búsqueda de los mejores valores de p, d, q
    p = range(1, 6)
    d = [1]
    q = range(0, 4)
    for combination in itertools.product(p, d, q):
        try:
            model = ARIMA(train, order=combination).fit()
            forecast = model.forecast(steps=horizon)
            mape = mean_absolute_percentage_error(test, forecast)

            if mape < best_mape:
                best_mape = mape
                best_order = combination
                best_model = model
        except Exception as e:
            continue

    # Generar proyección para los próximos meses
    forecast = best_model.forecast(steps=horizon)
    forecast = forecast.apply(lambda x: max(0, x))  # Establecer valores negativos en 0
    forecast_dates = pd.date_range(start=data.index[-1] + pd.DateOffset(months=1), periods=horizon, freq='M')

    return forecast, forecast_dates, best_order, best_mape

def run_arima(data, horizon=3):
    """
    Función principal para ejecutar ARIMA sobre un conjunto de datos.
    Devuelve las proyecciones y las métricas asociadas.
    """
    data_processed = preprocess_data(data)  # Usar la nueva función de preprocesamiento
    forecast, forecast_dates, best_order, best_mape = arima_forecast(data_processed, horizon)
    return {
        "forecast": forecast,
        "forecast_dates": forecast_dates,
        "best_order": best_order,
        "mape": best_mape
    }
