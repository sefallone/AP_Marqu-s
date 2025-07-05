import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="Dashboard Financiero",
    page_icon="💰",
    layout="wide"
)

# Función para cargar datos desde el archivo subido
def load_data(uploaded_file):
    try:
        # Lista de hojas requeridas
        required_sheets = ["Ventas", "Nómina", "Impuestos", "Cuentas x Pagar", "Bancos"]
        
        # Leer el archivo Excel y verificar hojas
        with pd.ExcelFile(uploaded_file) as xls:
            if not all(sheet in xls.sheet_names for sheet in required_sheets):
                missing = [sheet for sheet in required_sheets if sheet not in xls.sheet_names]
                st.error(f"❌ Faltan hojas requeridas: {', '.join(missing)}")
                return None
            
            ventas = pd.read_excel(xls, sheet_name="Ventas")
            nomina = pd.read_excel(xls, sheet_name="Nómina")
            impuestos = pd.read_excel(xls, sheet_name="Impuestos")
            cuentas_pagar = pd.read_excel(xls, sheet_name="Cuentas x Pagar")
            bancos = pd.read_excel(xls, sheet_name="Bancos")
            
        return ventas, nomina, impuestos, cuentas_pagar, bancos
    
    except Exception as e:
        st.error(f"Error al leer el archivo: {str(e)}")
        return None

# Widget para cargar archivo (sidebar o main)
uploaded_file = st.sidebar.file_uploader(
    "📤 Sube tu archivo Excel financiero",
    type=["xlsx", "xls"],
    help="El archivo debe contener hojas específicas (Ventas, Nómina, etc.)"
)

# Mostrar instrucciones si no hay archivo
if uploaded_file is None:
    st.info("👋 Por favor, sube un archivo Excel para comenzar.")
    st.stop()  # Detener la ejecución si no hay archivo

# Cargar datos
ventas, nomina, impuestos, cuentas_pagar, bancos = load_data(uploaded_file)

# Verificar si los datos se cargaron correctamente
if ventas is None:
    st.error("No se pudieron cargar los datos. Verifica el archivo.")
    st.stop()

ventas['Fecha'] = pd.to_datetime(ventas['Fecha'])
nomina['Fecha'] = pd.to_datetime(nomina['Fecha'])
impuestos['Fecha'] = pd.to_datetime(impuestos['Fecha'])
bancos['Fecha'] = pd.to_datetime(bancos['Fecha'])

# Sidebar para navegación
st.sidebar.title("Navegación")
pagina = st.sidebar.radio(
    "Seleccione una sección:",
    ("Resumen General", "Ventas", "Nómina", "Impuestos", "Cuentas por Pagar", "Bancos")
)

