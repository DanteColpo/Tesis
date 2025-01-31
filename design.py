import streamlit as st

def set_page_config():
    st.set_page_config(page_title="ProyeKTA+", page_icon="📊", layout="wide")

# Función para mostrar el logo y título de la aplicación
def show_logo_and_title():
    st.image("Logo_ProyeKTA+.png", width=300)
    st.markdown(
        "<h1 style='text-align: center; font-weight: bold; font-size: 3em; color: #4E74F4;'>ProyeKTA+</h1>", 
        unsafe_allow_html=True
    )
    st.markdown(
        "<h2 style='text-align: center; font-style: italic; font-size: 1.5em; color: #2ECC71; margin-top: -10px;'>Proyecta tu éxito</h2>", 
        unsafe_allow_html=True
    )

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
    st.markdown(
        "<h3 style='text-align: center; color: #4E74F4; font-size: 1.4em; font-weight: bold;'>Preguntas Frecuentes</h3>", 
        unsafe_allow_html=True
    )
    
    faq_content = {
        "1.- ¿Qué métodos utiliza esta aplicación para la proyección de demanda?": 
        "Esta aplicación emplea los modelos ARIMA, SARIMA y proyección lineal para realizar proyecciones basadas en datos históricos de demanda. Estos métodos permiten identificar patrones y prever fluctuaciones de manera precisa.",
        
        "2.- ¿Por qué se usan estos métodos para la proyección de demanda?": 
        "Estos métodos son eficaces en el análisis de series temporales con patrones y estacionalidad, ayudando a las PYMEs a planificar sus recursos y mejorar la gestión de inventario.",
        
        "3.- ¿A quién va enfocada esta aplicación?": 
        "Esta aplicación está orientada a PYMEs en sectores con alta variabilidad de demanda, como el sector de áridos. Su objetivo es mejorar la planificación y reducir costos operativos.",
        
        "4.- ¿Cómo puedo aprovechar al máximo esta herramienta?": 
        "Para obtener el mejor resultado, carga datos históricos completos, idealmente de al menos 3 a 5 años, para asegurar un buen entrenamiento del modelo. Esto ayudará a optimizar la gestión de inventario y reducir costos.",
        
        "5.- ¿Qué datos son necesarios en el archivo de Excel?": 
        "El archivo debe incluir una columna con fechas, cantidad en m³, sector (PRIVADO/PÚBLICO) y tipo de producto. A continuación se muestra un ejemplo visual de la estructura:"
    }

    for question, answer in faq_content.items():
        with st.expander(question):
            # Agregar texto de respuesta con color ajustado para mayor contraste
            st.markdown(
                f"<p style='text-align: justify; color: #EAEAEA; font-size: 1.1em;'>{answer}</p>", 
                unsafe_allow_html=True
            )
            # Insertar imagen para la pregunta 5 con tamaño reducido
            if question == "5.- ¿Qué datos son necesarios en el archivo de Excel?":
                st.image(
                    "Ejemplo Excel.png", 
                    caption="Ejemplo de estructura de archivo Excel para la proyección", 
                    use_column_width=False, 
                    width=400
                )

# Función para mostrar un mensaje claro en caso de error con el archivo subido
def show_error_instructions():
    st.error(
        "El archivo cargado no cumple con los requisitos. Asegúrate de que el archivo contenga las siguientes columnas: "
        "Fecha, Sector, Material, y Cantidad. A continuación, se muestra un ejemplo del formato esperado:"
    )
    st.image(
        "Ejemplo Excel.png", 
        caption="Ejemplo de estructura de archivo Excel para la proyección", 
        use_column_width=False, 
        width=400
    )

# Función para mostrar la información de contacto
def show_contact_info():
    st.markdown(
        "<h3 style='text-align: center; color: #4E74F4; font-size: 1.2em;'>¿Tienes dudas? ¡Contáctanos en nuestras redes o por correo!</h3>", 
        unsafe_allow_html=True
    )
    st.markdown(
        """
        <div style='text-align: center; font-size: 1.1em;'>
            <p style='color: #2ECC71;'>📷 Instagram: <a href='https://instagram.com/DanteColpo' target='_blank' style='color: #4E74F4;'>@DanteColpo</a></p>
            <p style='color: #2ECC71;'>📧 Correo Electrónico: <a href='mailto:dante.colpo@gmail.com' style='color: #4E74F4;'>dante.colpo@gmail.com</a></p>
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
