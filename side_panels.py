import streamlit as st
import pandas as pd
import plotly.express as px

def show_left_panel():
    # Datos para el gráfico de líneas (Tendencias del Mercado)
    tendencia_data = pd.DataFrame({
        'Mes': ['Octubre', 'Noviembre'],
        'Tendencia': [145, 160]
    })
    
    # Crear un gráfico de líneas con Plotly
    fig = px.line(
        tendencia_data, 
        x='Mes', 
        y='Tendencia', 
        title='Tendencias del Mercado (Octubre - Noviembre 2024)',
        text='Tendencia'
    )
    fig.update_traces(
        line=dict(color="dodgerblue", width=4), 
        mode='lines+markers', 
        textposition="top center"
    )
    fig.update_layout(
        title_font_size=18,
        xaxis_title="Mes",
        yaxis_title="Demanda (Miles de Toneladas)",
        title_x=0.5,
        plot_bgcolor="rgba(0,0,0,0)"
    )

    # Mostrar el gráfico
    st.sidebar.header("📈 Tendencias del Mercado")
    st.sidebar.plotly_chart(fig, use_container_width=True)
    
    # Fuente de los datos
    st.sidebar.markdown("**Fuente:** Cámara Chilena de la Construcción (CChC).")

    # Indicadores clave
    st.sidebar.markdown("### Indicadores Clave:")
    st.sidebar.markdown("- **UF Actual:** 36.000 CLP")
    st.sidebar.markdown("- **Proyectos MOP Activos:** 120")


def show_public_vs_private_demand():
    # Datos para el gráfico de barras (ejemplo de nivel nacional)
    demanda_data = pd.DataFrame({
        'Sector': ['Pública', 'Privada'],
        'Cantidad': [35, 65]
    })

    # Crear un gráfico de barras con Plotly
    fig2 = px.bar(
        demanda_data, 
        x='Sector', 
        y='Cantidad', 
        title='Comparativa de Demanda (Nacional)',
        color='Sector', 
        text='Cantidad'
    )
    fig2.update_layout(
        title_font_size=18,
        xaxis_title="Sector",
        yaxis_title="Demanda (Miles de Toneladas)",
        legend_title="Sectores",
        title_x=0.5,
        plot_bgcolor="rgba(0,0,0,0)"
    )
    fig2.update_traces(marker=dict(line=dict(width=1.5, color='black')), textposition='outside')

    # Mostrar el gráfico debajo del panel izquierdo
    st.header("📊 Demanda Pública vs Privada")
    st.plotly_chart(fig2, use_container_width=True)

