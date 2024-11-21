import streamlit as st
import pandas as pd
import plotly.express as px

# Crear columnas principales para izquierda y derecha
col1, col2 = st.columns([1, 2])

# Panel izquierdo (Tendencias del Mercado)
with col1:
    st.header("📈 Tendencias del Mercado")
    # Gráfico de líneas
    tendencia_data = pd.DataFrame({
        'Mes': ['Enero', 'Febrero', 'Marzo'],
        'Tendencia': [120, 140, 160]
    })
    fig = px.line(tendencia_data, x='Mes', y='Tendencia', title='Crecimiento Mensual')
    fig.update_traces(line=dict(color="blue", width=3))
    fig.update_layout(title_x=0.5, plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)
    
    # Indicadores clave
    st.markdown("### Indicadores Clave:")
    st.markdown("- **UF Actual:** 36.000 CLP")
    st.markdown("- **Proyectos MOP Activos:** 120")

# Panel derecho (Demanda Pública vs Privada)
with col2:
    st.header("📊 Demanda Pública vs Privada")
    demanda_data = pd.DataFrame({
        'Sector': ['Pública', 'Privada'],
        'Cantidad': [30, 70]
    })
    fig2 = px.bar(demanda_data, x='Sector', y='Cantidad', title='Demanda por Sector', color='Sector')
    fig2.update_layout(title_x=0.5, plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig2, use_container_width=True)
