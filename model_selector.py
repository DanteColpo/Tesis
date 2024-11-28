# model_selector.py

import pandas as pd
import plotly.graph_objects as go
from arima_model import arima_forecast
from linear_projection import linear_projection
from sarima_model import sarima_forecast

def select_best_model(data, horizon):
    """
    Evalúa múltiples modelos de proyección y selecciona el mejor basado en el MAPE más bajo.

    Args:
        data (pd.DataFrame): Datos de entrada (con columna 'CANTIDAD').
        horizon (int): Horizonte de proyección (número de meses).

    Returns:
        dict: Resultados del modelo seleccionado, incluyendo proyección, MAPE y detalles del modelo.
    """
    # Diccionario para almacenar resultados
    results = {}

    # Proyección con ARIMA
    try:
        forecast_arima, dates_arima, order_arima, mape_arima = arima_forecast(data, horizon)
        results['ARIMA'] = {
            'forecast': forecast_arima,
            'dates': dates_arima,
            'order': order_arima,
            'mape': mape_arima
        }
    except Exception as e:
        print(f"Error ejecutando ARIMA: {e}")

    # Proyección con Proyección Lineal
    try:
        forecast_linear, dates_linear, mape_linear = linear_projection(data, horizon)
        results['Linear Projection'] = {
            'forecast': forecast_linear,
            'dates': dates_linear,
            'mape': mape_linear
        }
    except Exception as e:
        print(f"Error ejecutando Proyección Lineal: {e}")

    # Proyección con SARIMA
    try:
        forecast_sarima, dates_sarima, order_sarima, seasonal_order_sarima, mape_sarima = sarima_forecast(data, horizon)
        results['SARIMA'] = {
            'forecast': forecast_sarima,
            'dates': dates_sarima,
            'order': order_sarima,
            'seasonal_order': seasonal_order_sarima,
            'mape': mape_sarima
        }
    except Exception as e:
        print(f"Error ejecutando SARIMA: {e}")

    # Imprimir MAPEs para verificar la ejecución de los modelos
    print("Los % de errores asociados en los modelos fue:")
    for model_name, details in results.items():
        print(f"MAPE de {model_name}: {details['mape']:.2%}")

    # Encontrar el modelo con menor MAPE
    best_model = min(results, key=lambda x: results[x]['mape']) if results else None

    return {
        'best_model': best_model,
        'details': results[best_model] if best_model else None,
        'all_results': results  # Incluye todos los resultados
    }

def generate_graph(data, forecast, forecast_dates, best_model):
    """
    Genera un gráfico interactivo de los datos históricos y la proyección seleccionada.

    Args:
        data (pd.DataFrame): Datos históricos (con columna 'CANTIDAD').
        forecast (pd.Series): Valores proyectados.
        forecast_dates (pd.DatetimeIndex): Fechas asociadas a la proyección.
        best_model (str): Nombre del modelo seleccionado.

    Returns:
        plotly.graph_objects.Figure: Gráfico generado.
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['CANTIDAD'], mode='lines', name='Datos Históricos'))
    fig.add_trace(go.Scatter(x=forecast_dates, y=forecast, mode='lines+markers',
                             name=f'Proyección {best_model}', line=dict(dash='dash', color='green')))
    fig.update_layout(
        title=f"Proyección de Demanda ({best_model})",
        xaxis_title="Fecha",
        yaxis_title="Cantidad de Material (m³)",
        template='plotly_dark',
        hovermode="x"
    )
    return fig

def main(data, horizon):
    """
    Función principal para ejecutar el selector de modelos y generar proyecciones.

    Args:
        data (pd.DataFrame): Datos históricos.
        horizon (int): Horizonte de proyección (número de meses).
    """
    if data is None or data.empty:
        print("Datos inválidos o vacíos. No se puede proceder con la proyección.")
        return

    # Seleccionar el mejor modelo
    results = select_best_model(data, horizon)
    if not results['best_model']:
        print("No se pudo seleccionar un modelo válido.")
        return

    best_model = results['best_model']
    forecast = results['details']['forecast']
    forecast_dates = results['details']['dates']
    mape = results['details']['mape']

    # Generar gráfico
    fig = generate_graph(data, forecast, forecast_dates, best_model)

    # Mostrar resultados
    print(f"Modelo seleccionado: {best_model}")
    print(f"MAPE asociado: {mape:.2%}")
    fig.show()

# Si quieres probar el script de forma independiente:
if __name__ == "__main__":
    # Cargar datos de ejemplo
    file_path = "Base de Datos Áridos.xlsx"
    data = pd.read_excel(file_path)

    # Preprocesar datos para el sector PRIVADO
    data['FECHA'] = pd.to_datetime(data['FECHA'], errors='coerce')
    data = data.dropna(subset=['FECHA'])
    data.set_index('FECHA', inplace=True)
    data_privado = data[data['SECTOR'] == 'PRIVADO'][['CANTIDAD']].resample('M').sum()

    # Definir horizonte
    horizon = 3

    # Ejecutar el selector de modelos
    main(data_privado, horizon)
