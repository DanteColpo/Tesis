import streamlit as st
import pandas as pd
from design import set_page_config, show_logo_and_title, show_instructions, show_faq, show_contact_info
from model_selector import select_best_model, generate_graph
from side_panels import show_left_panel, show_public_vs_private_demand

# Configuración de la página
st.set_page_config(page_title="ProyeKTA+", page_icon="📊", layout="wide")

# Función para cargar y procesar el archivo
def upload_and_process_file():
    uploaded_file = st.file_uploader("Subir archivo", type=["xlsx"])
    if uploaded_file is not None:
        try:
            # Leer el archivo Excel
            data = pd.read_excel(uploaded_file)
            if data.empty:
                st.warning("El archivo está vacío o no tiene datos válidos.")
                return None
            else:
                st.success("Archivo cargado exitosamente.")
                return data
        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")
            return None
    else:
        return None

# Configuración inicial del diseño de la aplicación
show_logo_and_title()
show_instructions()

# Mostrar mensaje inicial antes de cargar cualquier archivo
st.info(
    "Por favor, sube un archivo Excel con las columnas requeridas: 'FECHA', 'SECTOR', 'MATERIAL' y 'CANTIDAD'. "
    "Consulta el ejemplo visual más abajo si tienes dudas sobre el formato (Pregunta 5)."
)

# Cargar el archivo y procesar datos para la proyección
data = upload_and_process_file()

# Validación y manejo de datos
if data is not None:
    required_columns = {'FECHA', 'SECTOR', 'MATERIAL', 'CANTIDAD'}
    if not required_columns.issubset(data.columns):
        st.warning(
            "El archivo cargado no contiene las columnas requeridas: 'FECHA', 'SECTOR', 'MATERIAL' y 'CANTIDAD'. "
            "Por favor, verifica el archivo y asegúrate de que cumpla con el formato esperado."
        )
        st.image("Ejemplo Excel.png", caption="Ejemplo del formato correcto para el archivo Excel")
    else:
        # Preprocesar los datos para el sector PRIVADO
        data['FECHA'] = pd.to_datetime(data['FECHA'], errors='coerce')
        data = data.dropna(subset=['FECHA'])
        data.set_index('FECHA', inplace=True)
        data_privado = data[data['SECTOR'] == 'PRIVADO'][['CANTIDAD']].resample('M').sum()

        # Probar el horizonte con selección del usuario
        horizon = st.selectbox("Selecciona el horizonte de proyección (meses):", [3, 6, 12])

        # Ejecutar el selector de modelos
        with st.spinner("Calculando la mejor proyección..."):
            results = select_best_model(data_privado, horizon)

        # Mostrar los resultados
        st.success(f"Modelo seleccionado: {results['best_model']}")
        st.write(f"Error Promedio Asociado (MAPE): {results['details']['mape']:.2%}")

        # Generar el gráfico del mejor modelo
        fig = generate_graph(
            data_privado,
            results['details']['forecast'],
            results['details']['dates'],
            results['best_model']
        )
        st.plotly_chart(fig)
else:
    st.info("Esperando que se cargue un archivo Excel válido...")

# Mostrar secciones adicionales
st.markdown("## Análisis del Mercado y Demanda 📊")

with st.sidebar:
    show_left_panel()
    show_public_vs_private_demand()

show_faq()
show_contact_info()
