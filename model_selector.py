# Esqueleto inicial de model_selector.py

# Importar los modelos
from arima_model import arima_forecast
from linear_projection import linear_projection
from sarima_model import sarima_forecast

# Función para seleccionar el mejor modelo basado en MAPE
def select_best_model(data, horizon):
    """
    Evalúa múltiples modelos de proyección y selecciona el mejor basado en el MAPE más bajo.

    Args:
        data (pd.DataFrame): Datos de entrada.
        horizon (int): Horizonte de proyección (número de meses).

    Returns:
        dict: Resultados del modelo seleccionado, incluyendo proyección, MAPE, y detalles del modelo.
    """
    # Diccionario para almacenar resultados
    results = {}

    # Proyección con ARIMA
    forecast_arima, dates_arima, order_arima, mape_arima = arima_forecast(data, horizon)
    results['ARIMA'] = {
        'forecast': forecast_arima,
        'dates': dates_arima,
        'order': order_arima,
        'mape': mape_arima
    }

    # Proyección con Proyección Lineal
    forecast_linear, dates_linear, mape_linear = linear_projection(data, horizon)
    results['Linear Projection'] = {
        'forecast': forecast_linear,
        'dates': dates_linear,
        'mape': mape_linear
    }

    # Proyección con SARIMA
    forecast_sarima, dates_sarima, order_sarima, seasonal_order_sarima, mape_sarima = sarima_forecast(data, horizon)
    results['SARIMA'] = {
        'forecast': forecast_sarima,
        'dates': dates_sarima,
        'order': order_sarima,
        'seasonal_order': seasonal_order_sarima,
        'mape': mape_sarima
    }

    # Encontrar el modelo con menor MAPE
    best_model = min(results, key=lambda x: results[x]['mape'])

    # Retornar los resultados del mejor modelo
    return {
        'best_model': best_model,
        'details': results[best_model],
        'all_results': results  # Opcional: incluir detalles de todos los modelos
    }

