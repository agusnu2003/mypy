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

    # Asegúrate de que las columnas necesarias existen
    required_columns_principal = ['Título','Id de referencia', 'Fecha planificada', 'Checkout', 'Observaciones', 'Bolsas', 'Kilos', 'Comentarios']
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
    df_principal['Fecha Recolección'] = pd.to_datetime(df_principal['Fecha planificada']).dt.strftime('%Y-%m-%d')
    df_principal['Hora Recolección'] = pd.to_datetime(df_principal['Checkout']).dt.strftime('%H:%M:%S')

    # Combinar 'Observaciones' y 'Comentarios'
    df_principal['Observaciones'] = df_principal['Observaciones'].fillna('') + ' ' + df_principal['Comentarios'].fillna('')

    df_principal['cantidad'] = df_principal['Bolsas']
    df_principal['peso (kg)'] = df_principal['Kilos'].fillna(0)  # Rellenar valores nulos en 'peso (kg)' con 0

    # Buscar IDs faltantes
    ids_faltantes = df_principal[df_principal['gran generador'].isna()]
    ids_faltantes = ids_faltantes[['Id de referencia']].drop_duplicates()
    ids_faltantes = ids_faltantes.rename(columns={'Id de referencia': 'gran generador'})

    # Mapear IDs desde el archivo de generadores
    generadores_dict = dict(zip(df_generadores['Account Name'], df_generadores['Account ID']))
    ids_faltantes['gran generador'] = ids_faltantes['gran generador'].map(generadores_dict)

    # Unir la información de IDs en el DataFrame principal
    df_principal = df_principal.merge(ids_faltantes[['gran generador']], how='left', left_on='gran generador', right_on='gran generador')
    
    # Mostrar columnas para depuración
    st.write("Columnas después del merge:", df_principal.columns)

    # Actualizar el 'gran generador' con la información del merge
    df_principal['gran generador'] = df_principal['gran generador_y'].fillna(df_principal['gran generador_x'])

    # Eliminar columnas innecesarias
    df_principal = df_principal.drop(columns=['gran generador_x', 'gran generador_y'])

    # Eliminar duplicados basados en 'gran generador'
    df_principal = df_principal.drop_duplicates(subset=['gran generador'])

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
