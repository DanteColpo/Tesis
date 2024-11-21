import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
from statsmodels.tsa.arima.model import ARIMA
from io import BytesIO
import openpyxl

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

# Función para generar proyecciones y permitir descarga
def download_projections(forecast_3, dates_3, forecast_6, dates_6, forecast_12, dates_12):
    # Validar longitudes
    if any(len(lst) == 0 for lst in [forecast_3, dates_3, forecast_6, dates_6, forecast_12, dates_12]):
        st.error("No se pueden descargar las proyecciones debido a datos faltantes.")
        return

    # Crear el DataFrame con las proyecciones
    output = pd.DataFrame({
        "Fecha (3 meses)": dates_3,
        "Proyección (3 meses)": forecast_3,
        "Fecha (6 meses)": dates_6,
        "Proyección (6 meses)": forecast_6,
        "Fecha (12 meses)": dates_12,
        "Proyección (12 meses)": forecast_12,
    })

    # Convertir DataFrame a archivo Excel
    output_buffer = BytesIO()
    with pd.ExcelWriter(output_buffer, engine="openpyxl") as writer:
        output.to_excel(writer, index=False, sheet_name="Proyecciones")

    # Botón de descarga
    st.download_button(
        label="Descargar Proyecciones en Excel",
        data=output_buffer.getvalue(),
        file_name="proyecciones_demanda.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Función para mostrar la proyección ARIMA
def show_projection(data):
    st.write("Proyección ARIMA para el Sector Privado")

    # Procesar datos
    data['FECHA'] = pd.to_datetime(data['FECHA'], errors='coerce')
    data = data.dropna(subset=['FECHA'])
    data = data.set_index('FECHA')
    data_privado = data[data['SECTOR'] == 'PRIVADO']

    if data_privado.empty or len(data_privado) < 12:
        st.warning("No hay suficientes datos para el sector PRIVADO después del resampleo.")
        return

    # Suavización y preparación de datos
    data_privado_total = data_privado[['CANTIDAD']].resample('M').sum()
    data_privado_total['CANTIDAD_SUAVIZADA'] = SimpleExpSmoothing(
        data_privado_total['CANTIDAD']
    ).fit(smoothing_level=0.9, optimized=False).fittedvalues
    train_total = data_privado_total['CANTIDAD_SUAVIZADA'].iloc[:-3]

    # Generar proyecciones con ARIMA
    best_model = ARIMA(train_total, order=(4, 1, 0)).fit()
    forecast_3 = best_model.forecast(steps=3).apply(lambda x: max(0, x))
    forecast_6 = best_model.forecast(steps=6).apply(lambda x: max(0, x))
    forecast_12 = best_model.forecast(steps=12).apply(lambda x: max(0, x))

    # Fechas para proyecciones
    last_date = data_privado_total.index[-1]
    dates_3 = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=3, freq='M')
    dates_6 = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=6, freq='M')
    dates_12 = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=12, freq='M')

    # Visualizar datos históricos y suavizados
    st.write("### Proyección Total de Demanda (3 meses)")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data_privado_total.index, y=data_privado_total['CANTIDAD'], 
                             mode='lines', name='Datos Originales', line=dict(color='red')))
    fig.add_trace(go.Scatter(x=data_privado_total.index, y=data_privado_total['CANTIDAD_SUAVIZADA'], 
                             mode='lines', name='Datos Suavizados', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=dates_3, y=forecast_3, mode='lines+markers', 
                             name='Pronóstico 3 Meses', line=dict(dash='dash', color='green')))
    fig.update_layout(
        title="Proyección Total de Demanda (3 meses)",
        xaxis_title="Fecha",
        yaxis_title="Cantidad de Material (m³)"
    )
    st.plotly_chart(fig)

    # Tablas de proyecciones
    st.write("#### Tabla de Proyección (3 meses)")
    st.table(pd.DataFrame({"Fecha": dates_3, "Proyección ARIMA (m³)": forecast_3}))

    st.write("#### Tabla de Proyección (12 meses)")
    st.table(pd.DataFrame({"Fecha": dates_12, "Proyección ARIMA (m³)": forecast_12}))

    # Opción para descargar datos
    st.write("### Descargar Proyecciones")
    if st.button("Descargar datos en Excel"):
        download_projections(forecast_3, dates_3, forecast_6, dates_6, forecast_12, dates_12)

# Código principal
st.title("ProyeKTA+")
st.subheader("Proyecta tu éxito")
st.markdown("Sube un archivo Excel (.xlsx) con los datos históricos de demanda para obtener proyecciones.")

# Cargar archivo y procesar
data = upload_and_process_file()
if data is not None:
    show_projection(data)

