import streamlit as st
import pandas as pd
import plotly.express as px

def show_left_panel():
    # Crear un encabezado en el panel izquierdo
    st.sidebar.header("📈 Tendencias del Mercado")
    
    # Datos para el gráfico de líneas
    tendencia_data = pd.DataFrame({
        'Mes': ['Enero', 'Febrero', 'Marzo'],
        'Tendencia': [120, 140, 160]
    })
    
    # Crear un gráfico de líneas con Plotly
    fig = px.line(tendencia_data, x='Mes', y='Tendencia', 
                  title='Crecimiento Mensual de la Tendencia')
    fig.update_traces(line=dict(color="dodgerblue", width=4), mode='lines+markers')
    fig.update_layout(
        title_font_size=18,
        xaxis_title="Mes",
        yaxis_title="Valor",
        title_x=0.5,  # Centrar el título
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    # Mostrar el gráfico
    st.sidebar.plotly_chart(fig, use_container_width=True)
    
    # Indicadores clave
    st.sidebar.markdown("### Indicadores Clave:")
    st.sidebar.markdown("- **UF Actual:** 36.000 CLP")
    st.sidebar.markdown("- **Proyectos MOP Activos:** 120")


def show_right_panel():
    # Crear un encabezado para el panel derecho
    st.header("📊 Demanda Pública vs Privada")
    
    # Datos para el gráfico de barras
    demanda_data = pd.DataFrame({
        'Sector': ['Pública', 'Privada'],
        'Cantidad': [30, 70]
    })
    
    # Crear un gráfico de barras con Plotly
    fig2 = px.bar(demanda_data, x='Sector', y='Cantidad', 
                  title='Demanda Pública vs Privada', color='Sector')
    fig2.update_layout(
        title_font_size=18,
        xaxis_title="Sector",
        yaxis_title="Cantidad",
        legend_title="Sectores",
        title_x=0.5,  # Centrar el título
        plot_bgcolor="rgba(0,0,0,0)"
    )
    fig2.update_traces(marker=dict(line=dict(width=1.5, color='black')))
    
    # Mostrar el gráfico
    st.plotly_chart(fig2, use_container_width=True)
