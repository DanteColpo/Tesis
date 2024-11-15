import streamlit as st

# Configuración de la página
st.set_page_config(page_title="ProyeKTA+", page_icon="📊", layout="centered")

# Importar funciones del archivo design y projection_logic
from design import show_logo_and_title, show_instructions, show_faq, show_contact_info
from projection_logic import upload_and_process_file, show_projection

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

