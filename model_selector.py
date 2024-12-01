import pandas as pd
import plotly.graph_objects as go
from arima_model import run_arima_projection  # Proyección con ARIMA
from linear_projection import run_linear_projection  # Proyección Lineal
from sarima_model import run_sarima_projection  # Proyección con SARIMA
import traceback  # Para manejo detallado de errores

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
        print("Ejecutando ARIMA...")
        arima_results = run_arima_projection(data, horizon)
        print("Resultado ARIMA:", arima_results)
        results['ARIMA'] = arima_results
    except Exception as e:
        print(f"Error ejecutando ARIMA: {e}")
        traceback.print_exc()

    # Proyección con Proyección Lineal
    try:
        print("Ejecutando Proyección Lineal...")
        linear_results = run_linear_projection(data, horizon)
        print("Resultado Proyección Lineal:", linear_results)
        results['Linear Projection'] = linear_results
    except Exception as e:
        print(f"Error ejecutando Proyección Lineal: {e}")
        traceback.print_exc()

    # Proyección con SARIMA
    try:
        print("Ejecutando SARIMA...")
        sarima_results = run_sarima_projection(data, horizon)
        print("Resultado SARIMA:", sarima_results)
        results['SARIMA'] = sarima_results
    except Exception as e:
        print(f"Error ejecutando SARIMA: {e}")
        traceback.print_exc()

    # Verificar si al menos un modelo se ejecutó correctamente
    if not results:
        print("No se pudo ejecutar ningún modelo. Verifica los datos y parámetros.")
        return None

    # Imprimir MAPEs para cada modelo
    print("\nMAPE de cada modelo:")
    for model_name, details in results.items():
        print(f"- MAPE de {model_name}: {details['mape']:.2%}")

    # Seleccionar el modelo con menor MAPE
    best_model = min(results, key=lambda x: results[x]['mape'])

    return {
        'best_model': best_model,
        'details': results[best_model],
        'all_results': results  # Todos los resultados para análisis posterior
    }

def generate_graph(data, selected_models, all_results):
    """
    Genera un gráfico interactivo de los datos históricos y las proyecciones seleccionadas.
    Args:
        data (pd.DataFrame): Datos históricos (con columna 'CANTIDAD').
        selected_models (list): Lista de nombres de los modelos seleccionados (ej. ['ARIMA', 'SARIMA']).
        all_results (dict): Diccionario con los resultados de todos los modelos disponibles.
    Returns:
        plotly.graph_objects.Figure: Gráfico generado.
    """
    # Asegurarse de que el índice sea un DatetimeIndex
    if not isinstance(data.index, pd.DatetimeIndex):
        data['FECHA'] = pd.to_datetime(data['FECHA'], errors='coerce')
        data = data.dropna(subset=['FECHA'])
        data = data.set_index('FECHA')

    # Consolidar datos históricos por mes
    data_monthly = data.resample('MS').sum()

    fig = go.Figure()

    # Agregar datos históricos
    fig.add_trace(go.Scatter(
        x=data_monthly.index,
        y=data_monthly['CANTIDAD'],
        mode='lines',
        name='Datos Históricos',
        line=dict(color='blue')
    ))

    # Agregar las proyecciones de los modelos seleccionados
    for model in selected_models:
        model_results = all_results.get(model)
        if model_results:
            fig.add_trace(go.Scatter(
                x=model_results['forecast_dates'],
                y=model_results['forecast'],
                mode='lines+markers',
                name=f"Proyección {model}",
                line=dict(dash='dash')
            ))

    # Configuración del gráfico
    fig.update_layout(
        title="Comparación de Proyecciones",
        xaxis_title="Fecha",
        yaxis_title="Cantidad de Material (m³)",
        template='plotly_dark',
        hovermode="x"
    )

    return fig
