import pandas as pd
import plotly.graph_objects as go
from arima_model import run_arima_projection  # Corrección del nombre de la función importada
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

    # Proyección con ARIMA
    try:
        arima_results = run_arima_projection(data, horizon)
        results['ARIMA'] = arima_results
    except Exception as e:
        print(f"Error ejecutando ARIMA: {e}")
        arima_results = None  # Asegurarse de que la variable exista

    # Proyección con Proyección Lineal
    try:
        linear_results = run_linear_projection(data, horizon)
        results['Linear Projection'] = linear_results
    except Exception as e:
        print(f"Error ejecutando Proyección Lineal: {e}")
        linear_results = None  # Asegurarse de que la variable exista

    # Proyección con SARIMA
    try:
        sarima_results = run_sarima_projection(data, horizon)
        results['SARIMA'] = sarima_results
    except Exception as e:
        print(f"Error ejecutando SARIMA: {e}")
        sarima_results = None  # Asegurarse de que la variable exista

    # Verificar si al menos un modelo se ejecutó correctamente
    if not results:
        print("No se pudo ejecutar ningún modelo. Por favor, verifica los datos y los parámetros.")
        return None

    # Imprimir MAPEs para verificar la ejecución de los modelos
    print("\nLos % de errores asociados en los modelos fue:")
    for model_name, details in results.items():
        print(f"- MAPE de {model_name}: {details['mape']:.2%}")

    # MAPE individual para depuración
    print("MAPE de ARIMA:", arima_results.get('mape') if arima_results else "No se ejecutó")
    print("MAPE de Proyección Lineal:", linear_results.get('mape') if linear_results else "No se ejecutó")
    print("MAPE de SARIMA:", sarima_results.get('mape') if sarima_results else "No se ejecutó")

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
