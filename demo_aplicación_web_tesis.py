import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Título de la aplicación
st.title('Proyección de Demanda de Áridos')

# Cargar el archivo de Excel
uploaded_file = st.file_uploader("Sube el archivo Excel", type=["xlsx"])

# Definir el orden de los meses y los nombres en español
meses_ordenados = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
meses_dict = {1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}

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
        
        proyeccion = st.checkbox('Incluir proyección para el próximo mes')

        # Asegurarse de que la columna FECHA esté en formato de fecha
        data['FECHA'] = pd.to_datetime(data['FECHA'], errors='coerce')

        # Eliminar filas con valores nulos en la fecha
        data = data.dropna(subset=['FECHA'])

        # Extraer el número del mes y asignar el nombre del mes usando el diccionario manual
        data['mes_numero'] = data['FECHA'].dt.month
        data['mes_nombre'] = data['mes_numero'].map(meses_dict)

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

        # Proyección de demanda para el próximo mes
        if proyeccion:
            proximo_mes = 'Septiembre'  # Aquí puedes ajustar al mes que corresponda según la fecha
            proyeccion_privado = np.random.randint(50, 200)
            proyeccion_publico = np.random.randint(100, 400)
            nuevo_dato = pd.DataFrame({
                'mes_numero': [9],  # 9 es Septiembre
                'mes_nombre': ['Septiembre'],
                'SECTOR': ['PRIVADO', 'PÚBLICO'],
                'CANTIDAD': [proyeccion_privado, proyeccion_publico],
                'PRECIO': [0, 0]  # Ajustar precio si es necesario
            })
            grouped_data = pd.concat([grouped_data, nuevo_dato], ignore_index=True)

        # Mostrar la tabla de datos agrupados
        st.write("Datos agrupados:")
        st.write(grouped_data)

        # Graficar la cantidad de material por mes y sector
        fig, ax = plt.subplots()

        # Definir colores para barras separadas y proyección
        colores = {'PRIVADO': 'blue', 'PÚBLICO': 'orange', 'PROYECCIÓN': 'green'}
        
        # Graficar cada sector por separado con barras separadas
        width = 0.35  # Ancho de las barras
        meses = grouped_data['mes_nombre'].unique()
        posiciones = np.arange(len(meses))

        for sector in grouped_data['SECTOR'].unique():
            sector_data = grouped_data[grouped_data['SECTOR'] == sector]
            ax.bar(posiciones, sector_data['CANTIDAD'], width=width, label=sector, color=colores[sector])

        # Añadir la proyección con un color diferente
        if proyeccion:
            proyeccion_data = grouped_data[grouped_data['mes_nombre'] == proximo_mes]
            ax.bar(posiciones[-1] + width, proyeccion_data['CANTIDAD'], width=width, label='PROYECCIÓN', color=colores['PROYECCIÓN'])

        # Añadir línea punteada para guiar la curva de demanda
        ax.plot(posiciones, grouped_data.groupby('mes_nombre')['CANTIDAD'].sum(), linestyle='--', color='gray')

        ax.set_xlabel('Mes')
        ax.set_ylabel('Cantidad de Material M3')
        ax.set_title(f'Proyección de demanda {"total" if ver_total else "para " + material} ({periodo})')
        ax.set_xticks(posiciones)
        ax.set_xticklabels(meses, rotation=45)
        ax.legend(title='Sector')

        # Mostrar el gráfico
        st.pyplot(fig)


