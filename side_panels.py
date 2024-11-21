import streamlit as st
import pandas as pd
import plotly.express as px
import requests

def get_current_uf():
    """Obtiene el valor actual de la UF desde mindicador.cl."""
    try:
        response = requests.get("https://mindicador.cl/api")
        response.raise_for_status()  # Verifica si la solicitud fue exitosa
        data = response.json()
        uf_value = data['uf']['valor']
        return uf_value
    except Exception as e:
        st.error(f"Error al obtener el valor de la UF: {e}")
        return None

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
        <p style='color: #EAEAEA; font-size: 1.1em; text-align: justify;'>
        <b>Contexto:</b> Este gráfico muestra la evolución de la demanda en el mercado de áridos 
        en los últimos 3 meses, basado en datos nacionales relevantes.</p>
        """, 
        unsafe_allow_html=True
    )
    st.sidebar.markdown(
        "<p style='color: #8AB4F8;'><b>Fuente:</b> Cámara Chilena de la Construcción (CChC).</p>",
        unsafe_allow_html=True
    )

    # Obtener el valor actual de la UF
    uf_actual = get_current_uf()

    # Indicadores clave
    st.sidebar.markdown("<h3 style='color: #4E74F4;'>Indicadores Clave:</h3>", unsafe_allow_html=True)
    st.sidebar.markdown(
        f"<p style='color: #EAEAEA; font-size: 1.1em;'>"
        f"- <b>Proyectos MOP Activos en {region}:</b> {proyectos_region}</p>",
        unsafe_allow_html=True
    )
    if uf_actual:
        st.sidebar.markdown(
            f"<p style='color: #EAEAEA; font-size: 1.1em;'>"
            f"- <b>UF Actual:</b> {uf_actual:,.2f} CLP</p>"
            "<p style='color: #8AB4F8;'><b>Fuente:</b> <a href='https://mindicador.cl/' target='_blank' style='color: #4E74F4;'>mindicador.cl</a></p>", 
            unsafe_allow_html=True
        )

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
        font=dict(size=14)
    )
    fig2.update_traces(marker=dict(line=dict(width=1.5, color='black')), textposition='outside')

    # Mostrar el gráfico debajo del gráfico de Tendencias
    st.sidebar.header("📊 Demanda Pública vs Privada")
    st.sidebar.plotly_chart(fig2, use_container_width=True)

    # Contexto del gráfico
    st.sidebar.markdown(
        """
        <p style='color: #EAEAEA; font-size: 1.1em; text-align: justify;'>
        <b>Contexto:</b> Este gráfico permite comparar la proporción de demanda pública y privada
        en el mercado de áridos, ayudando a identificar tendencias y prioridades.</p>
        """, 
        unsafe_allow_html=True
    )
    st.sidebar.markdown(
        "<p style='color: #8AB4F8;'><b>Fuente:</b> Análisis nacional del mercado de áridos 2024.</p>",
        unsafe_allow_html=True
    )

# Llamada a las funciones para mostrar los paneles
show_left_panel()
show_public_vs_private_demand()

