# data_preprocessor.py
import pandas as pd

def preprocess_data(data, sector='PRIVADO', resample_frequency='MS'):
    """
    Preprocesar los datos cargados, filtrando por sector y resampleando según la frecuencia indicada.
    Args:
        data (pd.DataFrame): Datos crudos cargados desde el archivo.
        sector (str): Sector para filtrar (ejemplo: 'PRIVADO').
        resample_frequency (str): Frecuencia para resamplear los datos (ejemplo: 'MS' para mensual).
    Returns:
        pd.DataFrame: Datos procesados y resampleados.
    """
    # Asegurarse de que la columna 'FECHA' esté en formato datetime
    data['FECHA'] = pd.to_datetime(data['FECHA'], errors='coerce')
    data = data.dropna(subset=['FECHA'])

    # Filtrar por sector
    data = data[data['SECTOR'] == sector]

    # Establecer FECHA como índice y resamplear
    data = data.set_index('FECHA')
    data_resampled = data[['CANTIDAD']].resample(resample_frequency).sum()

    # Manejar valores nulos o negativos
    data_resampled['CANTIDAD'] = data_resampled['CANTIDAD'].clip(lower=0).fillna(0)
    return data_resampled
