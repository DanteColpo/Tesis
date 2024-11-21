import streamlit as st
from design import set_page_config, show_logo_and_title, show_instructions, show_faq, show_contact_info
from projection_logic import upload_and_process_file, show_projection
from side_panels import show_left_panel, show_right_panel

# Configuración de la página
st.set_page_config(page_title="ProyeKTA+", page_icon="📊", layout="centered")

# Configuración inicial del diseño de la aplicación
show_logo_and_title()
show_instructions()

# Cargar el archivo y procesar datos para la proyección
data = upload_and_process_file()

# Si hay datos cargados, mostrar proyección
if data is not None:
    show_projection(data)

# Mostrar título general antes de los paneles laterales
st.markdown("## Análisis del Mercado y Demanda 📊")

# Mostrar paneles laterales en columnas
col1, col2 = st.columns([1, 2])  # La primera columna es más pequeña que la segunda
with col1:
    show_left_panel()
with col2:
    show_right_panel()

# Mostrar secciones adicionales (Preguntas Frecuentes y Contacto)
show_faq()
show_contact_info()
