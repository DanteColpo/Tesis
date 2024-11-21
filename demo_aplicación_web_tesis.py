import streamlit as st
from design import set_page_config, show_logo_and_title, show_instructions, show_faq, show_contact_info
from projection_logic import upload_and_process_file, show_projection
from side_panels import show_left_panel, show_public_vs_private_demand

# Configuración de la página (MOVERLO AQUÍ COMO PRIMERA INSTRUCCIÓN)
st.set_page_config(page_title="ProyeKTA+", page_icon="📊", layout="wide")

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
    # Verificar si las columnas necesarias existen
    required_columns = {'FECHA', 'SECTOR', 'MATERIAL', 'CANTIDAD'}
    if not required_columns.issubset(data.columns):
        st.warning(
            "El archivo cargado no contiene las columnas requeridas: 'FECHA', 'SECTOR', 'MATERIAL' y 'CANTIDAD'. "
            "Por favor, verifica el archivo y asegúrate de que cumpla con el formato esperado."
        )
        st.image("Ejemplo Excel.png", caption="Ejemplo del formato correcto para el archivo Excel")
    else:
        show_projection(data)
else:
    st.info("Esperando que se cargue un archivo Excel válido...")

# Mostrar título general antes de los gráficos
st.markdown("## Análisis del Mercado y Demanda 📊")

# Mostrar gráficos en la barra lateral
with st.sidebar:
    # Panel lateral izquierdo: Tendencias del mercado
    show_left_panel()

    # Gráfico de Demanda Pública vs Privada debajo
    show_public_vs_private_demand()

# Mostrar secciones adicionales (Preguntas Frecuentes y Contacto)
show_faq()
show_contact_info()

