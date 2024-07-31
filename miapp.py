import pandas as pd
import streamlit as st

# Función para procesar los datos
def procesar_datos(archivo_principal, archivo_generadores):
    # Cargar los archivos de Excel
    df = pd.read_excel(archivo_principal)
    df_generadores = pd.read_excel(archivo_generadores)
    
    # Renombrar columnas para el merge
    df_generadores.rename(columns={'Account Name': 'Título', 'Account ID': 'Id Generador'}, inplace=True)
    
    # Unir los dataframes para completar los IDs faltantes
    df = df.merge(df_generadores[['Título', 'Id Generador']], on='Título', how='left')
    
    # Rellenar los IDs faltantes en 'Id de referencia' con 'Id Generador' del archivo de generadores
    df['Id de referencia'] = df['Id de referencia'].combine_first(df['Id Generador'])
    
    # Seleccionar y renombrar las columnas necesarias
    df['gran generador'] = df['Id de referencia']
    df['Fecha Recolección'] = pd.to_datetime(df['Fecha planificada']).dt.strftime('%Y-%m-%d')
    df['Hora Recolección'] = pd.to_datetime(df['Checkout']).dt.strftime('%H:%M:%S')
    df['Observaciones'] = df['Observaciones']
    df['cantidad'] = df['Bolsas']
    df['peso (kg)'] = df['Kilos']
    
    # Llenar los valores nulos en 'peso (kg)' con 0
    df['peso (kg)'] = df['peso (kg)'].fillna(0)
    
    # Crear el DataFrame final
    df_final = df[['gran generador', 'Fecha Recolección', 'Hora Recolección', 'Observaciones', 'cantidad', 'peso (kg)']]
    
    return df_final

# Interfaz de usuario con Streamlit
st.title('Procesamiento de Datos de Recolección')

archivo_principal = st.file_uploader('Sube el archivo principal', type=['xlsx'])
archivo_generadores = st.file_uploader('Sube el archivo con los IDs de los generadores', type=['xlsx'])

if archivo_principal and archivo_generadores:
    df_resultado = procesar_datos(archivo_principal, archivo_generadores)
    st.write(df_resultado)
    
    # Guardar el DataFrame final en un nuevo archivo Excel
    df_resultado.to_excel('resultado.xlsx', index=False)
    st.success('Archivo procesado y guardado como resultado.xlsx')
    st.download_button(label='Descargar resultado', data=df_resultado.to_excel(index=False), file_name='resultado.xlsx')

