from data_preprocessor import preprocess_data  # Usar la función centralizada de preprocesamiento
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_percentage_error
from statsmodels.tsa.holtwinters import SimpleExpSmoothing

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

def linear_forecast(data, horizon):
    """
    Realiza proyecciones lineales en base a los datos proporcionados.
    Devuelve la proyección, las fechas proyectadas y el MAPE asociado.
    """
    # Encontrar el mejor alpha para suavización exponencial
    best_alpha = find_best_alpha(data)
    data['CANTIDAD_SUAVIZADA'] = SimpleExpSmoothing(data['CANTIDAD']).fit(smoothing_level=best_alpha, optimized=False).fittedvalues

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
    data_processed = preprocess_data(data)  # Usar la nueva función de preprocesamiento
    
    # Validar que haya suficientes datos para realizar la proyección
    if len(data_processed) < horizon + 1:
        raise ValueError("Datos insuficientes para realizar la proyección lineal.")
    
    forecast, forecast_dates, mape = linear_forecast(data_processed, horizon)
    
    # Crear tabla de resultados para integración
    results_table = pd.DataFrame({
        'Fecha': forecast_dates,
        'Proyección (m³)': forecast
    })

    return {
        "forecast": forecast,
        "forecast_dates": forecast_dates,
        "mape": mape,
        "results_table": results_table
    }
