import streamlit as st

def set_page_config():
    st.set_page_config(page_title="ProyeKTA+", page_icon="📊", layout="centered")

def show_logo_and_title():
    st.image("Logo_ProyeKTA+.png", width=300)
    st.markdown("<h1 style='text-align: center;'>ProyeKTA+</h1>", unsafe_allow_html=True)
    st.subheader("Proyecta tu éxito")

def show_instructions():
    st.markdown(
        "<h2 style='text-align: center;'>Sube un archivo Excel (.xlsx) con los datos de demanda histórica para obtener una proyección de los próximos meses.</h2>",
        unsafe_allow_html=True
    )

def show_faq():
    st.markdown("<h3 style='text-align: center;'>Preguntas Frecuentes</h3>", unsafe_allow_html=True)
    faq_items = [
        "¿Qué método utiliza esta aplicación para la proyección de demanda?",
        "¿Por qué se usa ARIMA para la proyección de demanda?",
        "¿A quién va enfocada esta aplicación?",
        "¿Cómo puedo aprovechar al máximo esta herramienta?",
        "¿Qué datos son necesarios en el archivo de Excel?"
    ]
    for question in faq_items:
        with st.expander(question):
            st.write("Respuesta pendiente")

def show_contact_info():
    st.markdown("<h3 style='text-align: center;'>¿Tienes dudas? ¡Contáctanos en nuestras redes o por correo!</h3>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style='text-align: center;'>
            <p>📷 Instagram: <a href='https://instagram.com/Dante.Colpo' target='_blank'>@Dante.Colpo</a></p>
            <p>📧 Correo Electrónico: <a href='mailto:dante.colpo@gmail.com'>dante.colpo@gmail.com</a></p>
        </div>
        """, 
        unsafe_allow_html=True
    )
