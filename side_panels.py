import streamlit as st
import pandas as pd
import plotly.express as px

def show_left_panel():
    # Datos simulados del MOP por región
    mop_data = pd.DataFrame({
        'Región': ['Metropolitana', 'Valparaíso', 'Biobío', 'Los Lagos', 'Los Ríos'],
        'Proyectos Activos': [120, 85, 90, 65, 50]
    })
    
    # Selector de región
    region = st.sidebar.selectbox("Selecciona una región para ver proyectos activos:", mop_data['Región'])
    
    # Filtrar los datos por región seleccionada
    proyectos_region = mop_data[mop_data['Región'] == region]['Proyectos Activos'].values[0]
    
    # Mostrar el gráfico de tendencias
    tendencia_data = pd.DataFrame({
        'Mes': ['Septiembre', 'Octubre', 'Noviembre'],
        'Demanda': [135, 145, 160]
    })
    fig = px.line(
        tendencia_data,
        x='Mes',
        y='Demanda',
        title='Tendencias del Mercado (Últimos 3 meses)',
        text='Demanda'
    )
    fig.update_traces(
        line=dict(color="dodgerblue", width=4),
        mode='lines+markers',
        textposition="top center"
    )
    fig.update_layout(
        title_font_size=20,
        xaxis_title="Mes",
        yaxis_title="Demanda (Miles de Toneladas)",
        title_x=0.5,
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(size=14)
    )
    st.sidebar.header("📈 Tendencias del Mercado")
    st.sidebar.plotly_chart(fig, use_container_width=True)

    # Contexto y fuente del gráfico
    st.sidebar.markdown(
        """
        **Contexto:** Este gráfico muestra la evolución de la demanda en el mercado de áridos 
        en los últimos 3 meses, basado en datos nacionales relevantes.
        """
    )
    st.sidebar.markdown("**Fuente:** Cámara Chilena de la Construcción (CChC).")

    # Indicadores clave
    st.sidebar.markdown("### Indicadores Clave:")
    st.sidebar.markdown(f"- **Proyectos MOP Activos en {region}:** {proyectos_region}")
    st.sidebar.markdown("- **UF Actual:** 36.000 CLP")

def show_public_vs_private_demand():
    # Datos para el gráfico de barras
    demanda_data = pd.DataFrame({
        'Sector': ['Pública', 'Privada'],
        'Demanda': [35, 65]
    })

    # Crear un gráfico de barras con Plotly
    fig2 = px.bar(
        demanda_data, 
        x='Sector', 
        y='Demanda', 
        title='Comparativa de Demanda (Nacional)',
        color='Sector', 
        text='Demanda'
    )
    fig2.update_layout(
        title_font_size=20,
        xaxis_title="Sector",
        yaxis_title="Demanda (Miles de Toneladas)",
        legend_title="Sectores",
        title_x=0.5,
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(size=14)  # Tamaño de fuente más grande
    )
    fig2.update_traces(marker=dict(line=dict(width=1.5, color='black')), textposition='outside')

    # Mostrar el gráfico debajo del gráfico de Tendencias
    st.sidebar.header("📊 Demanda Pública vs Privada")
    st.sidebar.plotly_chart(fig2, use_container_width=True)

    # Contexto del gráfico
    st.sidebar.markdown(
        """
        **Contexto:** Este gráfico permite comparar la proporción de demanda pública y privada
        en el mercado de áridos, ayudando a identificar tendencias y prioridades.
        """
    )
    # Fuente del gráfico
    st.sidebar.markdown("**Fuente:** Análisis nacional del mercado de áridos 2024.")

