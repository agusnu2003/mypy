import pandas as pd
import streamlit as st
import io

def procesar_datos(archivo_general):
    try:
        # Cargar el archivo de Excel general
        df = pd.read_excel(archivo_general)
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
        return None

    # Asegúrate de que las columnas necesarias existen
    required_columns = ['Id de referencia', 'Fecha planificada', 'Checkout', 'Observaciones', 'Bolsas', 'Kilos', 'Comentarios' , 'Título']
    for col in required_columns:
        if col not in df.columns:
            st.error(f"El archivo no contiene la columna requerida: {col}")
            return None

    # Renombrar y procesar columnas
    df['gran generador'] = df['Id de referencia']
    df['Fecha Recolección'] = pd.to_datetime(df['Checkout']).dt.strftime('%Y-%m-%d')
    df['Hora Recolección'] = pd.to_datetime(df['Checkout']).dt.strftime('%H:%M:%S')

    # Combinar 'Observaciones' y 'Comentarios'
    df['Observaciones'] = df['Observaciones'].fillna('') + ' ' + df['Comentarios'].fillna('')

    df['cantidad'] = df['Bolsas']
    df['peso (kg)'] = df['Kilos'].fillna(0)  # Rellenar valores nulos en 'peso (kg)' con 0

    # Agregar columna 'Título' como columna vacía o con un valor predeterminado
    df['nombre'] = df['Título']  # Puedes ajustar esto si necesitas un valor específico

    # Seleccionar las columnas necesarias
    df_final = df[['nombre','gran generador', 'Fecha Recolección', 'Hora Recolección', 'Observaciones', 'cantidad', 'peso (kg)']]

    return df_final

# Interfaz de usuario con Streamlit
st.title('Procesamiento de Datos de Recolección')

archivo_general = st.file_uploader('Sube el archivo general', type=['xlsx'])

if archivo_general:
    df_resultado = procesar_datos(archivo_general)
    if df_resultado is not None:
        st.write(df_resultado)
        
        # Crear un buffer de bytes en memoria para el archivo Excel
        output = io.BytesIO()
        df_resultado.to_excel(output, index=False)
        output.seek(0)  # Volver al principio del buffer
        
        st.success('Archivo procesado. Puedes descargarlo a continuación:')
        st.download_button(label='Descargar resultado', data=output, file_name='resultado.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
