import streamlit as st
import pandas as pd

# Función para mostrar contenido en el lado izquierdo
def show_left_panel():
    with st.sidebar:
        st.header("Tendencias del Mercado")
        # Ejemplo de gráfico de tendencias
        st.line_chart(data={"Enero": [100, 120], "Febrero": [90, 110], "Marzo": [80, 95]})
        # Indicadores clave
        st.write("UF Actual: **36.000 CLP**")
        st.write("Proyectos MOP Activos: **120**")

# Función para mostrar contenido en el lado derecho
def show_right_panel():
    st.header("Demanda Pública vs Privada")
    st.bar_chart(data={"Pública": [30], "Privada": [70]})
