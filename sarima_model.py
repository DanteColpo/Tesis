import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_percentage_error
import itertools

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

def find_best_alpha(data):
    """
    Encuentra el mejor valor de alpha para la suavización exponencial
    basado en el MAPE más bajo.
    """
    alphas = np.linspace(0.01, 1.0, 10)
    best_alpha = None
    best_mape = float('inf')

    for alpha in alphas:
        model = SimpleExpSmoothing(data['CANTIDAD']).fit(smoothing_level=alpha, optimized=False)
        fitted_values = model.fittedvalues
        mape = mean_absolute_percentage_error(data['CANTIDAD'], fitted_values)
        if mape < best_mape:
            best_mape = mape
            best_alpha = alpha

    return best_alpha

def sarima_forecast(data, horizon):
    """
    Realiza proyecciones SARIMA en base a los datos proporcionados.
    Devuelve la proyección, las fechas proyectadas y el MAPE asociado.
    """
    # Encontrar el mejor alpha para suavización exponencial
    best_alpha = find_best_alpha(data)
    data['CANTIDAD_SUAVIZADA'] = SimpleExpSmoothing(data['CANTIDAD']).fit(smoothing_level=best_alpha, optimized=False).fittedvalues

    # División en conjunto de entrenamiento y prueba
    train = data['CANTIDAD_SUAVIZADA'].iloc[:-horizon]
    test = data['CANTIDAD_SUAVIZADA'].iloc[-horizon:]

    # Rango de parámetros para SARIMA
    p_values = [1, 2, 3, 4]
    d_values = [0, 1]
    q_values = [0, 1, 2]
    P_values = [0, 1, 2]
    D_values = [0, 1]
    Q_values = [0, 1, 2]
    m = 12  # Periodo estacional de 12 meses

    # Variables para almacenar el mejor modelo y resultados
    best_mape = float('inf')
    best_order = None
    best_seasonal_order = None
    best_forecast = None

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
                                forecast = result.predict(start=len(train), end=len(train) + len(test) - 1)

                                # Calcular MAPE
                                mape = mean_absolute_percentage_error(test, forecast)

                                # Actualizar el mejor modelo si el MAPE es menor
                                if mape < best_mape:
                                    best_mape = mape
                                    best_order = (p, d, q)
                                    best_seasonal_order = (P, D, Q, m)
                                    best_forecast = forecast
                            except Exception as e:
                                continue

    # Generar la proyección con el mejor modelo
    forecast_dates = pd.date_range(start=data.index[-1] + pd.DateOffset(months=1), periods=horizon, freq='M')

    return best_forecast, forecast_dates, best_order, best_seasonal_order, best_mape

def run_sarima_projection(data, horizon=3):
    """
    Función principal para ejecutar SARIMA sobre un conjunto de datos.
    Devuelve las proyecciones y las métricas asociadas.
    """
    data_processed = preprocess_data(data)
    
    # Validar que haya suficientes datos para realizar la proyección
    if len(data_processed) < horizon + 1:
        raise ValueError("Datos insuficientes para realizar la proyección SARIMA.")
    
    forecast, forecast_dates, best_order, best_seasonal_order, mape = sarima_forecast(data_processed, horizon)
    
    return {
        "forecast": forecast,
        "forecast_dates": forecast_dates,
        "order": best_order,
        "seasonal_order": best_seasonal_order,
        "mape": mape
    }
