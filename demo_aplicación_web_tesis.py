import streamlit as st
import pandas as pd
from design import show_logo_and_title, show_instructions, show_faq, show_contact_info
from model_selector import select_best_model, generate_graph
from data_preprocessor import preprocess_data
from side_panels import show_left_panel, show_public_vs_private_demand

# Configuración de la página
st.set_page_config(page_title="ProyeKTA+", page_icon="📊", layout="wide")

# Mostrar título e instrucciones
show_logo_and_title()
show_instructions()

# Subir y procesar el archivo
uploaded_file = st.file_uploader("Subir archivo Excel", type=["xlsx"])
if uploaded_file:
    try:
        # Leer el archivo Excel
        data = pd.read_excel(uploaded_file)
        st.success("Archivo cargado exitosamente.")

        # Validar columnas requeridas
        required_columns = {'FECHA', 'SECTOR', 'MATERIAL', 'CANTIDAD'}
        if not required_columns.issubset(data.columns):
            st.error("El archivo no contiene las columnas requeridas. Por favor verifica el formato.")
        else:
            # Procesar datos con función centralizada
            try:
                data_processed = preprocess_data(data)
                if data_processed.empty:
                    st.warning("Los datos procesados están vacíos después del filtrado. Verifica tu archivo.")
                else:
                    # Seleccionar horizonte
                    horizon = st.selectbox("Selecciona el horizonte de proyección (meses):", [3, 6, 12])

                    # Ejecutar selección del mejor modelo
                    with st.spinner("Calculando la mejor proyección..."):
                        results = select_best_model(data_processed, horizon)

                    if results:
                        # Mostrar detalles del modelo seleccionado
                        best_model = results['best_model']
                        details = results['details']

                        st.success(f"Modelo seleccionado: {best_model}")
                        st.write(f"Error Promedio Asociado (MAPE): {details['mape']:.2%}")

                        # Mostrar gráfico del mejor modelo
                        fig = generate_graph(data_processed, details['forecast'], details['forecast_dates'], best_model)
                        st.plotly_chart(fig)

                        # Mostrar tabla de resultados si está disponible
                        if 'results_table' in details:
                            st.markdown("### Tabla de Resultados")
                            st.dataframe(details['results_table'])
                        else:
                            st.warning("No se generó una tabla de resultados.")
                    else:
                        st.error("No se pudo seleccionar un modelo. Verifica los datos.")
            except Exception as e:
                st.error(f"Error al procesar los datos: {e}")
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
else:
    st.info("Sube un archivo Excel para comenzar.")

# Mostrar secciones adicionales
show_faq()
show_contact_info()

with st.sidebar:
    show_left_panel()
    show_public_vs_private_demand()
