import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

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
        incluir_proyeccion = st.checkbox('Incluir proyección para el próximo mes')

        if not ver_total:
            material = st.selectbox('Seleccione el material', data['MATERIAL'].unique())

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

        # Mostrar la tabla de datos agrupados
        st.write("Datos agrupados:")
        st.write(grouped_data)

        # Definir función de proyección simple para el próximo mes
        def calcular_proyeccion(datos):
            return datos.mean() * 1.05  # Proyección con un 5% de crecimiento

        # Graficar la cantidad de material por mes y sector
        fig, ax = plt.subplots()

        # Obtener datos por sector
        privado = grouped_data[grouped_data['SECTOR'] == 'PRIVADO']
        publico = grouped_data[grouped_data['SECTOR'] == 'PÚBLICO']

        # Gráficas separadas si hay datos para cada sector
        ancho = 0.3
        indice = range(len(grouped_data['mes_nombre'].unique()))  # Índice para las barras

        if not privado.empty:
            ax.bar(indice, privado['CANTIDAD'], width=ancho, label='PRIVADO', color='blue')

        if not publico.empty:
            ax.bar([i + ancho for i in indice], publico['CANTIDAD'], width=ancho, label='PÚBLICO', color='orange')

        ax.set_xlabel('Mes')
        ax.set_ylabel('Cantidad de Material')
        ax.set_title(f'Proyección de demanda {"total" if ver_total else "para " + material} ({periodo})')
        ax.legend(title='Sector')

        # Incluir la proyección para el próximo mes
        if incluir_proyeccion:
            proyeccion_privado = calcular_proyeccion(privado['CANTIDAD']) if not privado.empty else 0
            proyeccion_publico = calcular_proyeccion(publico['CANTIDAD']) if not publico.empty else 0

            if ver_total:
                proyeccion_total = proyeccion_privado + proyeccion_publico
                nuevo_dato = pd.DataFrame({
                    'mes_nombre': ['Proyección'],
                    'CANTIDAD': [proyeccion_total],
                    'SECTOR': ['Proyección']
                })
                ax.bar([i + ancho * 2 for i in indice], nuevo_dato['CANTIDAD'], width=ancho, label='Proyección', color='green')
            else:
                if not privado.empty:
                    ax.bar([indice[-1] + ancho * 2], proyeccion_privado, width=ancho, label='Proyección PRIVADO', color='green')

                if not publico.empty:
                    ax.bar([indice[-1] + ancho * 2], proyeccion_publico, width=ancho, label='Proyección PÚBLICO', color='green')

        # Mostrar el gráfico
        st.pyplot(fig)
