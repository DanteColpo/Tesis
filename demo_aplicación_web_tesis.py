import streamlit as st
import pandas as pd
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
            # Seleccionar horizonte
            horizon = st.selectbox("Selecciona el horizonte de proyección (meses):", [3, 6, 12])

            # Ejecutar selección del mejor modelo
            with st.spinner("Calculando la mejor proyección..."):
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
                        model_options = ["ARIMA", "Proyección Lineal", "SARIMA"]
                        selected_models = st.multiselect(
                            "Selecciona los modelos a comparar:",
                            options=model_options,
                            default=["SARIMA"]  # Preseleccionar el mejor modelo
                        )

                        # Generar gráficos de comparación
                        if selected_models:
                            st.markdown("### Comparativa de Proyecciones")
                            fig = go.Figure()
                            fig.add_trace(go.Scatter(
                                x=data.index, y=data['CANTIDAD'], mode='lines',
                                name='Datos Históricos'
                            ))
                            for model in selected_models:
                                model_results = results['all_results'][model]
                                fig.add_trace(go.Scatter(
                                    x=model_results['forecast_dates'],
                                    y=model_results['forecast'],
                                    mode='lines+markers',
                                    name=f"Proyección {model}"
                                ))
                            fig.update_layout(
                                title="Comparación de Modelos de Proyección",
                                xaxis_title="Fecha",
                                yaxis_title="Cantidad de Material (m³)",
                                template="plotly_dark",
                                hovermode="x"
                            )
                            st.plotly_chart(fig)

                        # Mostrar tabla de resultados del modelo seleccionado
                        st.markdown("### Tabla de Resultados del Modelo Seleccionado")
                        if 'results_table' in details:
                            st.dataframe(details['results_table'])
                        else:
                            st.warning("No se generó una tabla de resultados.")

                        # Añadir tabla comparativa de MAPEs
                        st.markdown("### Comparativa de Modelos (MAPE)")
                        mape_comparison = pd.DataFrame([
                            {"Modelo": "ARIMA", "MAPE (%)": results['all_results']['ARIMA']['mape'] * 100},
                            {"Modelo": "Proyección Lineal", "MAPE (%)": results['all_results']['Linear Projection']['mape'] * 100},
                            {"Modelo": "SARIMA", "MAPE (%)": results['all_results']['SARIMA']['mape'] * 100},
                        ])
                        mape_comparison = mape_comparison.sort_values(by="MAPE (%)")
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
