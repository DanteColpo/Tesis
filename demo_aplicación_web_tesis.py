import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Título de la aplicación
st.title('Proyección de Demanda de Áridos')

# Cargar el archivo de Excel
uploaded_file = st.file_uploader("Sube el archivo Excel", type=["xlsx"])

# Definir el orden de los meses
meses_ordenados = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

if uploaded_file is not None:
    # Leer el archivo Excel
    data = pd.read_excel(uploaded_file)

    # Verificar si hay datos cargados
    if data.empty:
        st.warning("El archivo está vacío o no tiene datos válidos.")
    else:
        st.write("Datos cargados:")
        st.write(data.head())  # Mostrar los primeros datos del archivo

        # Selección del período, material y si se quiere ver demanda total
        periodo = st.selectbox('Seleccione el período', ['Mensual', 'Trimestral', 'Anual'])
        ver_total = st.checkbox('Mostrar demanda total')
        if not ver_total:
            material = st.selectbox('Seleccione el material', data['MATERIAL'].unique())

        # Asegurarse de que la columna FECHA esté en formato de fecha
        data['FECHA'] = pd.to_datetime(data['FECHA'], errors='coerce')

        # Eliminar filas con valores nulos en la fecha
        data = data.dropna(subset=['FECHA'])

        # Extraer nombre del mes en español
        data['mes_nombre'] = data['FECHA'].dt.month_name(locale='es_ES')
        data['mes_numero'] = data['FECHA'].dt.month

        if ver_total:
            # Agrupar por mes y sector para ver demanda total
            grouped_data = data.groupby(['mes_numero', 'mes_nombre', 'SECTOR']).agg({'CANTIDAD': 'sum', 'PRECIO': 'sum'}).reset_index()
        else:
            # Filtrar los datos por material seleccionado
            material_data = data[data['MATERIAL'] == material].copy()  # Copiar para evitar advertencias

            # Agrupar por mes y sector para ver demanda del material
            grouped_data = material_data.groupby(['mes_numero', 'mes_nombre', 'SECTOR']).agg({'CANTIDAD': 'sum', 'PRECIO': 'sum'}).reset_index()

        # Ordenar por mes_numero
        grouped_data['mes_nombre'] = pd.Categorical(grouped_data['mes_nombre'], categories=meses_ordenados, ordered=True)
        grouped_data = grouped_data.sort_values('mes_numero')

        # Mostrar la tabla de datos agrupados
        st.write("Datos agrupados:")
        st.write(grouped_data)

        # Graficar la cantidad de material por mes y sector
        fig, ax = plt.subplots()
        for sector in grouped_data['SECTOR'].unique():
            sector_data = grouped_data[grouped_data['SECTOR'] == sector]
            ax.bar(sector_data['mes_nombre'], sector_data['CANTIDAD'], label=sector)

        ax.set_xlabel('Mes')
        ax.set_ylabel('Cantidad de Material')
        ax.set_title(f'Proyección de demanda {"total" if ver_total else "para " + material} ({periodo})')
        ax.legend(title='Sector')

        # Mostrar el gráfico
        st.pyplot(fig)
