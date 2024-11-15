import streamlit as st
from design import set_page_config, show_logo_and_title, show_instructions, show_faq, show_contact_info
from projection_logic import upload_and_process_file, show_projection

# Configuración de la página y diseño
set_page_config()
show_logo_and_title()
show_instructions()

# Cargar el archivo y procesar datos para la proyección
data = upload_and_process_file()
if data is not None:
    show_projection(data)

# Mostrar secciones adicionales
show_faq()
show_contact_info()
