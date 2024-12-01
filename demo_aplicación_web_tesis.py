import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from design import show_logo_and_title, show_instructions, show_faq, show_contact_info
from model_selector import select_best_model, generate_graph
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
            # Convertir la columna FECHA a Datetime y configurar como índice
            data['FECHA'] = pd.to_datetime(data['FECHA'], errors='coerce')
            data = data.dropna(subset=['FECHA']).set_index('FECHA')

            # Seleccionar horizonte
            horizon = st.selectbox("Selecciona el horizonte de proyección (meses):", [3, 6, 12])

            # Ejecutar selección del mejor modelo
            with st.spinner("Calculando las proyecciones..."):
                try:
                    results = select_best_model(data, horizon)
                    if results:
                        # Mostrar detalles del modelo seleccionado
                        best_model = results['best_model']
                        details = results['details']

                        st.success(f"Modelo seleccionado: {best_model}")
                        st.write(f"Error Promedio Asociado (MAPE): {details['mape']:.2%}")

                        # Selección de modelos a comparar
                        st.markdown("### Comparar Modelos de Proyección")
                        model_options = list(results['all_results'].keys())
                        selected_models = st.multiselect(
                            "Selecciona los modelos a comparar:",
                            options=model_options,
                            default=[best_model]  # Preseleccionar el mejor modelo
                        )

                        # Generar gráficos de comparación
                        if selected_models:
                            st.markdown("### Comparativa de Proyecciones")
                            fig = generate_graph(data, selected_models, results['all_results'])
                            st.plotly_chart(fig)
                        else:
                            st.warning("Por favor selecciona al menos un modelo para comparar.")

                        # Mostrar tabla de resultados del modelo seleccionado
                        st.markdown("### Tabla de Resultados del Modelo Seleccionado")
                        if 'results_table' in details:
                            st.dataframe(details['results_table'])
                        else:
                            st.warning("No se generó una tabla de resultados.")

                        # Añadir tabla comparativa de MAPEs
                        st.markdown("### Comparativa de Modelos (MAPE)")
                        mape_comparison = pd.DataFrame([
                            {"Modelo": model, "MAPE (%)": results['all_results'][model]['mape'] * 100}
                            for model in model_options
                        ])
                        mape_comparison = mape_comparison.sort_values(by="MAPE (%)").reset_index(drop=True)
                        st.table(mape_comparison)
                    else:
                        st.error("No se pudo seleccionar un modelo. Verifica los datos.")
                except Exception as e:
                    st.error(f"Error durante la proyección: {e}")
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
