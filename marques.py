import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración básica
st.set_page_config(layout="wide", page_title="Dashboard Financiero")

# Función de carga de datos mejorada
@st.cache_data
def load_data(file):
    try:
        # Leer todas las hojas disponibles
        xls = pd.ExcelFile(file)
        sheets = {}
        
        # Cargar solo las hojas existentes
        for sheet_name in xls.sheet_names:
            sheets[sheet_name] = pd.read_excel(file, sheet_name=sheet_name)
        
        return sheets
    except Exception as e:
        st.error(f"Error al cargar el archivo: {str(e)}")
        return None

# Interfaz de usuario
st.title("📊 Dashboard Financiero Básico")
uploaded_file = st.file_uploader("Sube tu archivo Excel", type=["xlsx", "xls"])

if uploaded_file:
    data = load_data(uploaded_file)
    
    if data:
        st.success(f"¡Archivo cargado correctamente! Hojas disponibles: {', '.join(data.keys())}")
        
        # Mostrar vista previa de la primera hoja
        first_sheet = list(data.keys())[0]
        st.subheader(f"Vista previa - Hoja: '{first_sheet}'")
        st.dataframe(data[first_sheet].head())
        
        # Análisis simple (ejemplo con Plotly)
        st.subheader("Análisis Rápido")
        selected_sheet = st.selectbox("Selecciona una hoja para analizar", options=list(data.keys()))
        
        df = data[selected_sheet]
        
        # Auto-detección de columnas numéricas/fechas
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        date_cols = df.select_dtypes(include=['datetime', 'datetimetz']).columns.tolist()
        
        if numeric_cols:
            col1, col2 = st.columns(2)
            with col1:
                selected_column = st.selectbox("Selecciona columna numérica", options=numeric_cols)
                fig = px.histogram(df, x=selected_column, title=f"Distribución de {selected_column}")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if date_cols:
                    time_column = st.selectbox("Selecciona columna de fecha", options=date_cols)
                    fig2 = px.line(df, x=time_column, y=selected_column, title="Tendencia temporal")
                    st.plotly_chart(fig2, use_container_width=True)
    else:
        st.error("No se pudo cargar el archivo. Verifica el formato.")
else:
    st.warning("Por favor, sube un archivo Excel para comenzar.")
