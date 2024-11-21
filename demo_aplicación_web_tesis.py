import streamlit as st
from design import set_page_config, show_logo_and_title, show_instructions, show_faq, show_contact_info
from projection_logic import upload_and_process_file, show_projection
from side_panels import show_left_panel, show_right_panel

# Configuración de la página debe ir aquí, como primera función
st.set_page_config(page_title="ProyeKTA+", page_icon="📊", layout="centered")

# Configuración de la página y diseño
show_logo_and_title()
show_instructions()

# Cargar el archivo y procesar datos para la proyección
data = upload_and_process_file()
if data is not None:
    show_projection(data)

# Mostrar secciones adicionales
show_faq()
show_contact_info()

# Mostrar paneles laterales
show_left_panel()
show_right_panel()
