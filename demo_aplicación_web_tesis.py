import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Título de la aplicación
st.title('Proyección de Demanda de Áridos')

# Cargar el archivo de Excel
uploaded_file = st.file_uploader("Sube el archivo Excel", type=["xlsx"])

if uploaded_file is not None:
    # Leer el archivo Excel
    data = pd.read_excel(uploaded_file)

    # Verificar si hay datos cargados
    if data.empty:
        st.warning("El archivo está vacío o no tiene datos válidos.")
    else:
        st.write("Datos cargados:")
        st.write(data.head())  # Mostrar los primeros datos del archivo

        # Selección del período y material
        periodo = st.selectbox('Seleccione el período', ['Mensual', 'Trimestral', 'Anual'])
        material = st.selectbox('Seleccione el material', data['MATERIAL'].unique())

        # Filtrar los datos por material seleccionado
        material_data = data[data['MATERIAL'] == material].copy()  # Copiar para evitar advertencias

        # Asegurarse de que la columna FECHA esté en formato de fecha
        material_data['FECHA'] = pd.to_datetime(material_data['FECHA'], errors='coerce')

        # Eliminar filas con valores nulos en la fecha
        material_data = material_data.dropna(subset=['FECHA'])

        # Extraer el mes y año de la fecha
        material_data['mes'] = material_data['FECHA'].dt.month
        material_data['año'] = material_data['FECHA'].dt.year

        # Mapear los meses con sus nombres
        meses = {1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio', 7: 'Julio', 
                 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}
        material_data['mes_nombre'] = material_data['mes'].map(meses)

        # Ordenar por fecha correctamente
        material_data = material_data.sort_values(by=['año', 'mes'])

        # Agrupar los datos por mes y sector
        grouped_data = material_data.groupby(['mes_nombre', 'SECTOR']).agg({'CANTIDAD': 'sum', 'PRECIO': 'sum'}).reset_index()

        # Mostrar la tabla de datos agrupados
        st.write("Datos agrupados:")
        st.write(grouped_data)

        # Gráfica de barras separadas por sector
        fig, ax = plt.subplots()

        # Crear un array con los nombres de los meses
        meses_unicos = grouped_data['mes_nombre'].unique()
        x = np.arange(len(meses_unicos))  # la posición de los meses en el eje X

        # Tamaño de las barras
        width = 0.35

        # Separar datos de los sectores
        privado_data = grouped_data[grouped_data['SECTOR'] == 'PRIVADO']
        publico_data = grouped_data[grouped_data['SECTOR'] == 'PÚBLICO']

        # Ajustar las posiciones de las barras para que no se solapen
        ax.bar(x - width/2, privado_data['CANTIDAD'], width, label='PRIVADO', color='green')
        ax.bar(x + width/2, publico_data['CANTIDAD'], width, label='PÚBLICO', color='blue')

        # Agregar etiquetas y leyenda
        ax.set_xticks(x)
        ax.set_xticklabels(meses_unicos, rotation=45)
        ax.set_xlabel('Mes')
        ax.set_ylabel('Cantidad de Material')
        ax.set_title(f'Proyección de demanda para {material} ({periodo})')
        ax.legend(title="Sector")

        # Mostrar el gráfico
        st.pyplot(fig)
