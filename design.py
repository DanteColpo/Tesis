import streamlit as st

# Configuración inicial de la página
def set_page_config():
    st.set_page_config(page_title="ProyeKTA+", page_icon="📊", layout="centered")

# Función para mostrar el logo y título de la aplicación
def show_logo_and_title():
    st.image("Logo_ProyeKTA+.png", width=300)
    st.markdown("<h1 style='text-align: center; font-weight: bold; font-size: 3em; color: #4E74F4;'>ProyeKTA+</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; font-style: italic; font-size: 1.5em; color: #333333; margin-top: -10px;'>Proyecta tu éxito</h2>", unsafe_allow_html=True)

# Función para mostrar las instrucciones de uso
def show_instructions():
    st.markdown(
        "<p style='text-align: center; color: #4E74F4; font-size: 1.2em;'>"
        "Sube un archivo Excel (.xlsx) con los datos de demanda histórica para obtener una proyección de los próximos 3 meses."
        "</p>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='text-align: center; color: #999999; font-size: 0.9em;'>"
        "Asegúrate de que el archivo contenga columnas como 'Fecha', 'Sector', 'Material' y 'Cantidad'.</p>",
        unsafe_allow_html=True
    )

# Función para mostrar la sección de preguntas frecuentes
def show_faq():
    st.markdown("<h3 style='text-align: center; color: #4E74F4; font-size: 1.4em; font-weight: bold;'>Preguntas Frecuentes</h3>", unsafe_allow_html=True)
    faq_content = {
        "¿Qué método utiliza esta aplicación para la proyección de demanda?": 
        "Esta aplicación emplea el modelo ARIMA para realizar proyecciones basadas en datos históricos de demanda. ARIMA permite identificar patrones y prever fluctuaciones de manera precisa.",
        
        "¿Por qué se usa ARIMA para la proyección de demanda?": 
        "ARIMA es eficaz en el análisis de series temporales con patrones y estacionalidad, ayudando a las PYMEs a planificar sus recursos y mejorar la gestión de inventario.",
        
        "¿A quién va enfocada esta aplicación?": 
        "Esta aplicación está orientada a PYMEs en sectores con alta variabilidad de demanda, como el sector de áridos. Su objetivo es mejorar la planificación y reducir costos operativos.",
        
        "¿Cómo puedo aprovechar al máximo esta herramienta?": 
        "Para obtener el mejor resultado, carga datos históricos completos, idealmente de al menos 3 a 5 años, para asegurar un buen entrenamiento del modelo. Esto ayudará a optimizar la gestión de inventario y reducir costos.",
        
        "¿Qué datos son necesarios en el archivo de Excel?": 
        "El archivo debe incluir una columna con fechas, cantidad en m³, sector (PRIVADO/PÚBLICO) y tipo de producto. A continuación se muestra un ejemplo visual de la estructura:"
    }
    for question, answer in faq_content.items():
        with st.expander(question):
            st.markdown(f"<p style='text-align: justify; color: #333333;'>{answer}</p>", unsafe_allow_html=True)
            if question == "¿Qué datos son necesarios en el archivo de Excel?":
                st.image("Ejemplo Excel.png", caption="Ejemplo de estructura de archivo Excel para la proyección")

# Función para mostrar la información de contacto
def show_contact_info():
    st.markdown("<h3 style='text-align: center; color: #4E74F4; font-size: 1.2em;'>¿Tienes dudas? ¡Contáctanos en nuestras redes o por correo!</h3>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style='text-align: center; font-size: 1.1em; color: #333333;'>
            <p>📷 Instagram: <a href='https://instagram.com/DanteColpo' target='_blank' style='color: #4E74F4;'>@DanteColpo</a></p>
            <p>📧 Correo Electrónico: <a href='mailto:dante.colpo@gmail.com' style='color: #4E74F4;'>dante.colpo@gmail.com</a></p>
        </div>
        """, 
        unsafe_allow_html=True
    )

# Ejecución de las funciones de la aplicación
set_page_config()
show_logo_and_title()
show_instructions()
show_faq()
show_contact_info()


