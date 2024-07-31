import pandas as pd
import streamlit as st
import io

def procesar_datos(archivo_principal, archivo_generadores):
    try:
        # Cargar los archivos de Excel
        df_principal = pd.read_excel(archivo_principal)
        df_generadores = pd.read_excel(archivo_generadores)
    except Exception as e:
        st.error(f"Error al leer los archivos: {e}")
        return None

    # Asegúrate de que las columnas necesarias existen en ambos archivos
    required_columns_principal = ['Título', 'Id de referencia', 'Fecha planificada', 'Checkout', 'Observaciones', 'Bolsas', 'Kilos', 'Comentarios']
    for col in required_columns_principal:
        if col not in df_principal.columns:
            st.error(f"El archivo principal no contiene la columna requerida: {col}")
            return None
    
    required_columns_generadores = ['Account ID', 'Account Name']
    for col in required_columns_generadores:
        if col not in df_generadores.columns:
            st.error(f"El archivo de generadores no contiene la columna requerida: {col}")
            return None

    # Renombrar y procesar columnas en el archivo principal
    df_principal['gran generador'] = df_principal['Id de referencia']
    df_principal['Fecha Recolección'] = pd.to_datetime(df_principal['Checkout']).dt.strftime('%Y-%m-%d')
    df_principal['Hora Recolección'] = pd.to_datetime(df_principal['Checkout']).dt.strftime('%H:%M:%S')

    # Combinar 'Observaciones' y 'Comentarios'
    df_principal['Observaciones'] = df_principal['Observaciones'].fillna('') + ' ' + df_principal['Comentarios'].fillna('')

    df_principal['cantidad'] = df_principal['Bolsas']
    df_principal['peso (kg)'] = df_principal['Kilos'].fillna(0)  # Rellenar valores nulos en 'peso (kg)' con 0

    # Crear un diccionario de mapeo para los IDs de generadores
    generadores_dict = dict(zip(df_generadores['Account Name'], df_generadores['Account ID']))

    # Buscar IDs faltantes y mapear con el diccionario
    df_principal['gran generador'] = df_principal['gran generador'].map(generadores_dict).fillna(df_principal['gran generador'])

    # Eliminar duplicados basados en columnas específicas
    df_principal = df_principal.drop_duplicates(subset=['gran generador', 'Fecha Recolección', 'Hora Recolección', 'cantidad', 'peso (kg)'])

    # Agregar columna 'Título' como columna vacía o con un valor predeterminado
    df_principal['nombre'] = df_principal['Título']

    # Seleccionar las columnas necesarias
    df_final = df_principal[['nombre', 'gran generador', 'Fecha Recolección', 'Hora Recolección', 'Observaciones', 'cantidad', 'peso (kg)']]
    
    return df_final

# Interfaz de usuario con Streamlit
st.title('Procesamiento de Datos de Recolección')

archivo_principal = st.file_uploader('Sube el archivo principal', type=['xlsx'])
archivo_generadores = st.file_uploader('Sube el archivo de generadores', type=['xlsx'])

if archivo_principal and archivo_generadores:
    df_resultado = procesar_datos(archivo_principal, archivo_generadores)
    if df_resultado is not None:
        st.write(df_resultado)
        
        # Crear un buffer de bytes en memoria para el archivo Excel
        output = io.BytesIO()
        df_resultado.to_excel(output, index=False)
        output.seek(0)  # Volver al principio del buffer
        
        st.success('Archivo procesado. Puedes descargarlo a continuación:')
        st.download_button(label='Descargar resultado', data=output, file_name='resultado.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
