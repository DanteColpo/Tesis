import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_percentage_error
from io import BytesIO

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

# Función para generar proyecciones y descargar los resultados
def download_projections(forecast_3, dates_3, forecast_6, dates_6, forecast_12, dates_12):
    # Validar las entradas
    if not all([forecast_3, dates_3, forecast_6, dates_6, forecast_12, dates_12]):
        st.error("Error: Una o más de las listas de proyecciones está vacía o no se generó correctamente.")
        return

    # Validar longitud de cada lista (asegúrate de que coincidan)
    if len(forecast_3) != len(dates_3):
        st.error("Error: Las proyecciones para 3 meses y las fechas no coinciden en longitud.")
        return
    if len(forecast_6) != len(dates_6):
        st.error("Error: Las proyecciones para 6 meses y las fechas no coinciden en longitud.")
        return
    if len(forecast_12) != len(dates_12):
        st.error("Error: Las proyecciones para 12 meses y las fechas no coinciden en longitud.")
        return

    # Crear el DataFrame
    try:
        output = pd.DataFrame({
            "Fecha (3 meses)": dates_3,
            "Proyección (3 meses)": forecast_3,
            "Fecha (6 meses)": dates_6,
            "Proyección (6 meses)": forecast_6,
            "Fecha (12 meses)": dates_12,
            "Proyección (12 meses)": forecast_12,
        })

        # Mostrar botón de descarga solo si el usuario lo selecciona
        st.markdown("### Descargar Proyecciones")
        if st.button("Generar archivo Excel"):
            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                output.to_excel(writer, index=False, sheet_name="Proyecciones")

            # Descargar el archivo Excel
            st.download_button(
                label="Descargar Proyecciones en Excel",
                data=excel_buffer.getvalue(),
                file_name="proyecciones_demanda.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    except Exception as e:
        st.error(f"Error al generar el archivo Excel: {e}")



# Función para mostrar la proyección ARIMA general y desagregada
def show_projection(data):
    st.write("Proyección ARIMA para el Sector Privado")

    # Preprocesamiento de datos
    data['FECHA'] = pd.to_datetime(data['FECHA'], errors='coerce')
    data = data.dropna(subset=['FECHA'])
    data = data.set_index('FECHA')

    # Filtrar datos del sector privado
    data_privado = data[data['SECTOR'] == 'PRIVADO']

    if data_privado.empty or len(data_privado) < 12:
        st.warning("No hay suficientes datos para el sector PRIVADO.")
        return

    # Preparar datos para la proyección
    data_privado_total = data_privado[['CANTIDAD']].resample('M').sum()
    data_privado_total['CANTIDAD_SUAVIZADA'] = SimpleExpSmoothing(data_privado_total['CANTIDAD']).fit(
        smoothing_level=0.9, optimized=False).fittedvalues
    train_total = data_privado_total['CANTIDAD_SUAVIZADA'].iloc[:-3]
    last_date = data_privado_total.index[-1]

    # Crear modelo ARIMA
    best_model = ARIMA(train_total, order=(4, 1, 0)).fit()

    # Generar proyección de 3 meses
    forecast_3 = best_model.forecast(steps=3).apply(lambda x: max(0, x))
    dates_3 = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=3, freq='M')

    # Mostrar gráfico de los 3 meses
    st.write("### Proyección Total de Demanda (3 meses)")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=train_total.index, y=train_total, mode='lines', name='Datos de Entrenamiento Suavizados'))
    fig.add_trace(go.Scatter(x=dates_3, y=forecast_3, mode='lines+markers', name='Pronóstico 3 Meses', line=dict(dash='dash', color='green')))
    fig.update_layout(
        title="Proyección Total de Demanda (3 meses)",
        xaxis_title="Fecha",
        yaxis_title="Cantidad de Material (m³)"
    )
    st.plotly_chart(fig)

    # Mostrar tabla de proyección de 3 meses
    st.write("### Tabla de Proyección (3 meses)")
    table_3 = pd.DataFrame({
        "Fecha": dates_3.strftime('%B %Y'),
        "Proyección ARIMA (m³)": forecast_3.round().astype(int)
    })
    st.write(table_3)

    # Desplegable para elegir 6 o 12 meses adicionales
    st.write("### Proyección Extendida")
    option = st.selectbox(
        "Seleccione el periodo de proyección adicional",
        ("6 meses", "12 meses")
    )

    if option == "6 meses":
        steps = 6
    else:
        steps = 12

    # Generar proyección extendida
    forecast_extended = best_model.forecast(steps=steps).apply(lambda x: max(0, x))
    dates_extended = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=steps, freq='M')

    # Mostrar tabla de proyección extendida
    st.write(f"### Tabla de Proyección ({steps} meses)")
    table_extended = pd.DataFrame({
        "Fecha": dates_extended.strftime('%B %Y'),
        "Proyección ARIMA (m³)": forecast_extended.round().astype(int)
    })
    st.write(table_extended)

    # Descargar todas las proyecciones
    st.write("### Descargar Proyecciones")
    download_projections(
        forecast_3, dates_3,
        forecast_extended[:6] if steps == 12 else forecast_extended, 
        dates_extended[:6] if steps == 12 else dates_extended, 
        forecast_extended if steps == 12 else [], 
        dates_extended if steps == 12 else []
    )
