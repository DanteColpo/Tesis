import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

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

        # Agrupar los datos por mes, trimestre o año según la selección
        if periodo == 'Mensual':
            material_data['mes'] = material_data['FECHA'].dt.month
            grouped_data = material_data.groupby('mes').agg({'CANTIDAD': 'sum', 'PRECIO': 'sum'})
        elif periodo == 'Trimestral':
            material_data['trimestre'] = material_data['FECHA'].dt.to_period('Q')
            grouped_data = material_data.groupby('trimestre').agg({'CANTIDAD': 'sum', 'PRECIO': 'sum'})
        else:
            material_data['año'] = material_data['FECHA'].dt.year
            grouped_data = material_data.groupby('año').agg({'CANTIDAD': 'sum', 'PRECIO': 'sum'})

        # Mostrar la tabla de datos agrupados
        st.write("Datos agrupados:")
        st.write(grouped_data)

        # Graficar la cantidad de material por el período seleccionado
        fig, ax = plt.subplots()
        ax.bar(grouped_data.index.astype(str), grouped_data['CANTIDAD'])
        ax.set_xlabel(periodo)
        ax.set_ylabel('Cantidad de Material')
        ax.set_title(f'Proyección de demanda para {material} ({periodo})')

        # Mostrar el gráfico
        st.pyplot(fig)
