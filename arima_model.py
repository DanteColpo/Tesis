import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_percentage_error
from statsmodels.tsa.holtwinters import SimpleExpSmoothing

def preprocess_arima_data(data):
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

def arima_forecast(data, horizon):
    """
    Realiza proyecciones ARIMA en base a los datos proporcionados.
    Devuelve la proyección, las fechas proyectadas y el MAPE asociado.
    """
    # Suavización exponencial
    best_alpha = find_best_alpha(data)
    data['CANTIDAD_SUAVIZADA'] = SimpleExpSmoothing(data['CANTIDAD']).fit(smoothing_level=best_alpha, optimized=False).fittedvalues

    # División en conjunto de entrenamiento y prueba
    train = data['CANTIDAD_SUAVIZADA'].iloc[:-horizon]
    test = data['CANTIDAD_SUAVIZADA'].iloc[-horizon:]

    # Optimización de parámetros ARIMA
    best_mape = float('inf')
    best_order = None
    best_model = None

    # Rango de búsqueda para p, d, q
    p_values = range(0, 3)
    d_values = range(0, 2)
    q_values = range(0, 3)

    for p in p_values:
        for d in d_values:
            for q in q_values:
                try:
                    model = ARIMA(train, order=(p, d, q)).fit()
                    forecast = model.forecast(steps=horizon)
                    mape = mean_absolute_percentage_error(test, forecast)

                    if mape < best_mape:
                        best_mape = mape
                        best_order = (p, d, q)
                        best_model = model
                except:
                    continue

    # Generar la proyección futura
    forecast = best_model.forecast(steps=horizon)
    forecast = np.maximum(forecast, 0)  # Establecer valores negativos en 0
    forecast_dates = pd.date_range(start=data.index[-1] + pd.DateOffset(months=1), periods=horizon, freq='M')

    return forecast, forecast_dates, best_order, best_mape

def run_arima_projection(data, horizon=3):
    """
    Función principal para ejecutar ARIMA sobre un conjunto de datos.
    Devuelve las proyecciones y las métricas asociadas.
    """
    data_processed = preprocess_arima_data(data)  # Usar la nueva función de preprocesamiento

    # Validar que haya suficientes datos para realizar la proyección
    if len(data_processed) < horizon + 1:
        raise ValueError("Datos insuficientes para realizar la proyección ARIMA.")

    forecast, forecast_dates, best_order, mape = arima_forecast(data_processed, horizon)

    # Crear tabla con los resultados
    results_table = pd.DataFrame({
        'Fecha': forecast_dates,
        'Proyección (m³)': forecast
    })

    return {
        "forecast": forecast,
        "forecast_dates": forecast_dates,
        "best_order": best_order,
        "mape": mape,
        "results_table": results_table
    }
