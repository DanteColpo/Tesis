import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_percentage_error
import matplotlib.pyplot as plt
from itertools import product

def preprocess_data(data):
    """
    Preprocesar los datos cargados, filtrando por sector privado
    y resampleando mensualmente.
    """
    data['FECHA'] = pd.to_datetime(data['FECHA'], errors='coerce')
    data = data.dropna(subset=['FECHA'])
    data = data.set_index('FECHA')
    data_privado = data[data['SECTOR'] == 'PRIVADO']
    
    # Resamplear datos mensuales
    data_resampled = data_privado[['CANTIDAD']].resample('MS').sum()
    
    # Manejo de valores negativos o nulos
    data_resampled['CANTIDAD'] = data_resampled['CANTIDAD'].clip(lower=0).fillna(0)
    
    return data_resampled

def find_best_alpha(data):
    """
    Encuentra el mejor valor de alpha para la suavización exponencial
    basado en el MAPE más bajo.
    """
    alphas = np.linspace(0.01, 1.0, 20)  # Mayor granularidad
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

def sarima_forecast(data, horizon, seasonal_period=3):
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

    # Variables para almacenar el mejor modelo y resultados
    best_mape = float('inf')
    best_order = None
    best_seasonal_order = None
    best_model = None
    best_forecast = None

    # Bucle para optimizar parámetros SARIMA
    for (p, d, q), (P, D, Q) in product(product(p_values, d_values, q_values), product(P_values, D_values, Q_values)):
        try:
            # Definir y ajustar el modelo SARIMA
            model = SARIMAX(
                train,
                order=(p, d, q),
                seasonal_order=(P, D, Q, seasonal_period),
                enforce_stationarity=False,
                enforce_invertibility=False
            )
            result = model.fit(disp=False)

            # Generar predicciones
            forecast = result.predict(start=len(train), end=len(train) + len(test) - 1)

            # Calcular el MAPE
            mape = mean_absolute_percentage_error(test, forecast)

            # Actualizar el mejor modelo si el MAPE es menor
            if mape < best_mape:
                best_mape = mape
                best_order = (p, d, q)
                best_seasonal_order = (P, D, Q, seasonal_period)
                best_model = result
                best_forecast = forecast
        except Exception as e:
            continue

    # Generar la proyección con el mejor modelo
    future_forecast = best_model.predict(start=len(train), end=len(train) + horizon - 1)
    future_forecast = np.maximum(future_forecast, 0)  # Establecer valores negativos en 0
    forecast_dates = pd.date_range(start=data.index[-1] + pd.DateOffset(months=1), periods=horizon, freq='M')

    return future_forecast, forecast_dates, best_order, best_seasonal_order, best_mape

def run_sarima_projection(data, horizon=3, seasonal_period=3):
    """
    Función principal para ejecutar SARIMA sobre un conjunto de datos.
    Devuelve las proyecciones, las métricas asociadas y los datos en tabla.
    """
    data_processed = preprocess_data(data)
    
    # Validar que haya suficientes datos para realizar la proyección
    if len(data_processed) < horizon + 1:
        raise ValueError("Datos insuficientes para realizar la proyección SARIMA.")
    
    forecast, forecast_dates, best_order, best_seasonal_order, mape = sarima_forecast(data_processed, horizon, seasonal_period)
    
    # Crear tabla con los resultados
    results_table = pd.DataFrame({
        'Fecha': forecast_dates,
        'Proyección (m³)': forecast
    })
    
    # Mostrar resultados
    print("\nResultados de Proyección:")
    print(results_table)

    # Visualización de los resultados finales
    plt.figure(figsize=(10, 6))
    plt.plot(data_processed.index, data_processed['CANTIDAD_SUAVIZADA'], label='Datos Suavizados')
    plt.plot(forecast_dates, forecast, label='Pronóstico SARIMA', linestyle='--')
    plt.xlabel('Fecha')
    plt.ylabel('Cantidad de Material')
    plt.title(f'Proyección de Demanda (SARIMA) - Periodo Estacional = {seasonal_period}')
    plt.legend()
    plt.show()
    
    return {
        "forecast": forecast,
        "forecast_dates": forecast_dates,
        "order": best_order,
        "seasonal_order": best_seasonal_order,
        "mape": mape,
        "results_table": results_table
    }
