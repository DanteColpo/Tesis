import streamlit as st
from design import set_page_config, show_logo_and_title, show_instructions, show_faq, show_contact_info
from projection_logic import upload_and_process_file, show_projection
from side_panels import show_left_panel, show_public_vs_private_demand

# Configuración de la página
st.set_page_config(page_title="ProyeKTA+", page_icon="📊", layout="wide")

# Configuración inicial del diseño de la aplicación
show_logo_and_title()
show_instructions()

# Cargar el archivo y procesar datos para la proyección
data = upload_and_process_file()

# Si hay datos cargados, mostrar proyección
if data is not None:
    show_projection(data)

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


