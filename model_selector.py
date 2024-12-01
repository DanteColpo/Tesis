import pandas as pd
import plotly.graph_objects as go
from arima_model import arima_forecast
from linear_projection import run_linear_projection
from sarima_model import run_sarima_projection

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

    # Lista de modelos a evaluar
    models = {
        "ARIMA": arima_forecast,
        "Linear Projection": run_linear_projection,
        "SARIMA": run_sarima_projection
    }

    for model_name, model_function in models.items():
        try:
            model_results = model_function(data, horizon)
            # Validar MAPE y almacenar si es válido
            if model_results["mape"] < 1.0:  # Excluir modelos con MAPE >= 100%
                results[model_name] = model_results
        except Exception as e:
            print(f"Error ejecutando {model_name}: {e}")

    # Verificar si al menos un modelo se ejecutó correctamente
    if not results:
        print("No se pudo ejecutar ningún modelo. Por favor, verifica los datos y los parámetros.")
        return None

    # Imprimir MAPEs para verificar la ejecución de los modelos
    print("\nLos % de errores asociados en los modelos fue:")
    for model_name, details in results.items():
        print(f"- MAPE de {model_name}: {details['mape']:.2%}")

    # Encontrar el modelo con menor MAPE
    best_model = min(results, key=lambda x: results[x]['mape'])

    return {
        'best_model': best_model,
        'details': results[best_model],
        'all_results': results  # Incluye todos los resultados para análisis posterior
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
    if not results or not results['best_model']:
        print("No se pudo seleccionar un modelo válido.")
        return

    best_model = results['best_model']
    forecast = results['details']['forecast']
    forecast_dates = results['details']['forecast_dates']
    mape = results['details']['mape']

    # Generar gráfico
    fig = generate_graph(data, forecast, forecast_dates, best_model)

    # Mostrar resultados
    print(f"\nModelo seleccionado: {best_model}")
    print(f"MAPE asociado: {mape:.2%}")
    fig.show()

    # Mostrar tabla de resultados si está disponible
    if 'results_table' in results['details']:
        print("\nTabla de Predicciones:")
        print(results['details']['results_table'])
