import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_percentage_error
import itertools

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

def sarima_forecast(data, horizon):
    """
    Realiza proyecciones SARIMA en base a los datos proporcionados.
    Devuelve la proyección, las fechas proyectadas y el MAPE asociado.
    """
    # Suavización exponencial
    data['CANTIDAD_SUAVIZADA'] = SimpleExpSmoothing(data['CANTIDAD']).fit(smoothing_level=alpha, optimized=False).fittedvalues

    # División en conjunto de entrenamiento y prueba
    train = data['CANTIDAD_SUAVIZADA'].iloc[:-horizon]
    test = data['CANTIDAD_SUAVIZADA'].iloc[-horizon:]

    # Rango de parámetros SARIMA
    p_values = range(1, 3)
    d_values = [0, 1]
    q_values = range(0, 2)
    P_values = range(0, 2)
    D_values = [0, 1]
    Q_values = range(0, 2)
    m = 12  # Periodo estacional de 12 meses (anual)

    # Variables para almacenar el mejor modelo y resultados
    best_mape = float('inf')
    best_order = None
    best_seasonal_order = None
    best_model = None

    # Bucle para optimizar parámetros SARIMA
    for p in p_values:
        for d in d_values:
            for q in q_values:
                for P in P_values:
                    for D in D_values:
                        for Q in Q_values:
                            try:
                                # Definir y ajustar el modelo SARIMA
                                model = SARIMAX(
                                    train,
                                    order=(p, d, q),
                                    seasonal_order=(P, D, Q, m),
                                    enforce_stationarity=False,
                                    enforce_invertibility=False
                                )
                                result = model.fit(disp=False)
                                forecast = result.forecast(steps=horizon)

                                # Calcular MAPE
                                mape = mean_absolute_percentage_error(test, forecast)

                                # Actualizar el mejor modelo si el MAPE es menor
                                if mape < best_mape:
                                    best_mape = mape
                                    best_order = (p, d, q)
                                    best_seasonal_order = (P, D, Q, m)
                                    best_model = result
                            except Exception as e:
                                continue

    # Generar la proyección con el mejor modelo
    forecast = best_model.forecast(steps=horizon)
    forecast = np.maximum(forecast, 0)  # Establecer valores negativos en 0
    forecast_dates = pd.date_range(start=data.index[-1] + pd.DateOffset(months=1), periods=horizon, freq='M')

    return forecast, forecast_dates, best_order, best_seasonal_order, best_mape

def run_sarima_projection(data, horizon=3):
    """
    Función principal para ejecutar SARIMA sobre un conjunto de datos.
    Devuelve las proyecciones y las métricas asociadas.
    """
    data_processed = preprocess_data(data)
    forecast, forecast_dates, best_order, best_seasonal_order, mape = sarima_forecast(data_processed, horizon)
    return {
        "forecast": forecast,
        "forecast_dates": forecast_dates,
        "order": best_order,
        "seasonal_order": best_seasonal_order,
        "mape": mape
    }
