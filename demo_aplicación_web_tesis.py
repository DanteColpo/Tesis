import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Aplicar estilo con CSS para cambiar el fondo
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f5f5f5;
    }
    </style>
    """,
    unsafe_allow_html=True
)

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

        # Separar datos en privado y público
        privado = grouped_data[grouped_data['SECTOR'] == 'PRIVADO']
        publico = grouped_data[grouped_data['SECTOR'] == 'PÚBLICO']

        # Inicializar los arrays de cantidad con ceros
        indice = np.arange(len(grouped_data['mes_nombre'].unique()))  # Asegura que el eje x tenga valores uniformes
        ancho = 0.3  # Ancho de las barras

        privado_cantidad = np.zeros(len(indice))  # Inicializamos el array con ceros
        publico_cantidad = np.zeros(len(indice))  # Inicializamos el array con ceros

        # Comprobamos si hay datos para cada sector y si no hay, lo dejamos como 0
        if not privado.empty:
            for i, mes in enumerate(grouped_data['mes_nombre'].unique()):
                if mes in privado['mes_nombre'].values:
                    privado_cantidad[i] = privado[privado['mes_nombre'] == mes]['CANTIDAD'].values[0]

        if not publico.empty:
            for i, mes in enumerate(grouped_data['mes_nombre'].unique()):
                if mes in publico['mes_nombre'].values:
                    publico_cantidad[i] = publico[publico['mes_nombre'] == mes]['CANTIDAD'].values[0]

        # Graficar los datos
        fig, ax = plt.subplots()

        ax.bar(indice - ancho / 2, privado_cantidad, width=ancho, label='PRIVADO', color='blue')
        ax.bar(indice + ancho / 2, publico_cantidad, width=ancho, label='PÚBLICO', color='orange')

        ax.set_xlabel('Mes')
        ax.set_ylabel('Cantidad de Material')
        ax.set_title(f'Proyección de demanda {"total" if ver_total else "para " + material} ({periodo})')
        ax.legend(title='Sector')

        # Proyección para el próximo mes
        if incluir_proyeccion:
            proxima_cantidad_privado = np.mean(privado_cantidad[-3:])  # Proyección basada en el promedio de los últimos 3 meses
            proxima_cantidad_publico = np.mean(publico_cantidad[-3:])
            ax.bar(len(indice), proxima_cantidad_privado, width=ancho, label='Proyección Privado', color='green')
            ax.bar(len(indice) + ancho, proxima_cantidad_publico, width=ancho, label='Proyección Público', color='red')

        # Mostrar el gráfico
        st.pyplot(fig)

