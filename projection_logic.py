import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_percentage_error
import itertools

# Definir alpha globalmente para la suavización exponencial
alpha = 0.9

# Función para cargar y procesar el archivo
def upload_and_process_file():
    uploaded_file = st.file_uploader("Subir archivo", type=["xlsx"])
    if uploaded_file is not None:
        data = pd.read_excel(uploaded_file)
        if data.empty:
            st.warning("El archivo está vacío o no tiene datos válidos.")
            return None
        else:
            st.success("Archivo cargado exitosamente.")
            return data
    return None

# Función para mostrar la proyección ARIMA general y desagregada
def show_projection(data):
    st.write("Proyección ARIMA para el Sector Privado")

    # Convertir la columna FECHA a tipo datetime y establecerla como índice
    data['FECHA'] = pd.to_datetime(data['FECHA'], errors='coerce')
    data = data.dropna(subset=['FECHA'])
    data = data.set_index('FECHA')

    # Filtrar solo los datos del sector privado, manteniendo 'MATERIAL'
    data_privado = data[data['SECTOR'] == 'PRIVADO']

    # Verificación de que hay suficientes datos
    if data_privado.empty or len(data_privado) < 12:
        st.warning("No hay suficientes datos para el sector PRIVADO después del resampleo.")
        return

    # Crear un diccionario para almacenar las proyecciones de cada tipo de material
    forecast_results = {}

    # Proyección para cada tipo de material
    if 'MATERIAL' in data_privado.columns:
        for product_type in data_privado['MATERIAL'].unique():
            # Filtrar los datos por tipo de material
            data_producto = data_privado[data_privado['MATERIAL'] == product_type]
            data_producto = data_producto[['CANTIDAD']].resample('M').sum()

            # Verificar que no haya valores NaN y que `data_producto['CANTIDAD']` sea unidimensional
            if data_producto['CANTIDAD'].isnull().all() or data_producto['CANTIDAD'].ndim != 1:
                st.warning(f"Los datos para {product_type} no son adecuados para la proyección y se omitirán.")
                continue

            # Rellenar valores NaN con ceros para asegurar la unidimensionalidad
            data_producto['CANTIDAD'] = data_producto['CANTIDAD'].fillna(0)

            # Suavización exponencial
            data_producto['CANTIDAD_SUAVIZADA'] = SimpleExpSmoothing(data_producto['CANTIDAD']).fit(smoothing_level=alpha, optimized=False).fittedvalues

            # División en conjunto de entrenamiento y prueba
            train = data_producto['CANTIDAD_SUAVIZADA'].iloc[:-3]
            test = data_producto['CANTIDAD_SUAVIZADA'].iloc[-3:]

            # Optimización de parámetros ARIMA en un rango limitado
            best_mape = float("inf")
            best_order = None
            best_model = None

            # Búsqueda de los mejores valores de p, d, q
            p = range(3, 6)
            d = [1]
            q = range(0, 4)

            for combination in itertools.product(p, d, q):
                try:
                    model = ARIMA(train, order=combination).fit()
                    forecast = model.forecast(steps=3)
                    mape = mean_absolute_percentage_error(test, forecast)

                    if mape < best_mape:
                        best_mape = mape
                        best_order = combination
                        best_model = model
                except Exception as e:
                    continue

            # Generar proyección para los próximos 3 meses
            forecast = best_model.forecast(steps=3)
            forecast_dates = pd.date_range(data_producto.index[-1] + pd.DateOffset(months=1), periods=3, freq='M')

            # Guardar los resultados en el diccionario
            forecast_results[product_type] = {
                "Fecha": forecast_dates.strftime('%B %Y'),
                "Proyección (m³)": forecast.round().astype(int),
                "MAPE": best_mape
            }

        # Mostrar tabla desglosada por tipo de material
        st.write("### Proyección Desglosada por Tipo de Material")
        for product_type, results in forecast_results.items():
            st.write(f"#### {product_type}")
            forecast_table = pd.DataFrame({
                "Fecha": results["Fecha"],
                "Proyección ARIMA (m³)": results["Proyección (m³)"],
                "Error Promedio Asociado (MAPE)": f"{results['MAPE']:.2%}"
            })
            st.write(forecast_table)
    else:
        st.warning("No se encontró la columna 'MATERIAL' en los datos. Solo se mostrará la proyección total.")

    # Gráfico y proyección para el total
    st.write("### Proyección Total de Demanda (Todos los Tipos de Material)")
    data_privado_total = data_privado[['CANTIDAD']].resample('M').sum()
    data_privado_total['CANTIDAD_SUAVIZADA'] = SimpleExpSmoothing(data_privado_total['CANTIDAD'].fillna(0)).fit(smoothing_level=alpha, optimized=False).fittedvalues
    train_total = data_privado_total['CANTIDAD_SUAVIZADA'].iloc[:-3]
    test_total = data_privado_total['CANTIDAD_SUAVIZADA'].iloc[-3:]

    # Optimización automática para el total
    best_mape = float("inf")
    best_order = None
    best_model = None
    p = range(3, 6)
    d = [1]
    q = range(0, 4)
    for combination in itertools.product(p, d, q):
        try:
            model = ARIMA(train_total, order=combination).fit()
            forecast = model.forecast(steps=3)
            mape = mean_absolute_percentage_error(test_total, forecast)

            if mape < best_mape:
                best_mape = mape
                best_order = combination
                best_model = model
        except Exception as e:
            continue

    # Proyección con el mejor modelo para el total
    forecast = best_model.forecast(steps=3)
    forecast_dates = pd.date_range(data_privado_total.index[-1] + pd.DateOffset(months=1), periods=3, freq='M')

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=train_total.index, y=train_total, mode='lines', name='Datos de Entrenamiento Suavizados'))
    fig.add_trace(go.Scatter(x=test_total.index, y=test_total, mode='lines', name='Datos Reales Suavizados', line=dict(color='orange')))
    fig.add_trace(go.Scatter(x=forecast_dates, y=forecast, mode='lines+markers', name=f'Pronóstico ARIMA{best_order}', line=dict(dash='dash', color='green')))
    fig.update_layout(
        title=f'Proyección ARIMA{best_order} sobre Datos Suavizados (Total)',
        xaxis_title='Fecha',
        yaxis_title='Cantidad de Material (m³)',
        xaxis=dict(tickformat="%b %Y"),
        hovermode="x"
    )
    st.plotly_chart(fig)

    # Mostrar MAPE del total
    st.write("### Error Promedio del Pronóstico")
    st.write(f"Error Promedio Asociado (MAPE): {best_mape:.2%}")

