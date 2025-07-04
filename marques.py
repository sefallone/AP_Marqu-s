import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# =============================================
# CONFIGURACIÓN INICIAL
# =============================================

# Configuración de la página
st.set_page_config(
    layout="wide", 
    page_title="Dashboard Financiero", 
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main {background-color: #f9f9f9;}
    .header {font-size:24px !important; color: #2a3f5f;}
    .metric-card {
        padding: 15px 20px;
        border-radius: 10px;
        background-color: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 15px;
        border-left: 4px solid #4e79a7;
    }
    .compare-card {
        padding: 15px;
        border-radius: 10px;
        background-color: #f0f8ff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
        border-radius: 4px 4px 0 0;
    }
</style>
""", unsafe_allow_html=True)

# =============================================
# FUNCIONES DE CARGA Y PROCESAMIENTO
# =============================================

@st.cache_data(ttl=3600)
def load_data(file):
    """Carga y valida el archivo Excel con manejo robusto de errores"""
    try:
        xls = pd.ExcelFile(file)
        available_sheets = xls.sheet_names
        
        required_sheets = {
            'Nómina': ['Fecha', 'Nombre Empleado', '$_Nómina_Quincenal'],
            'Ventas': ['Fecha', 'Totales', 'Plataforma'],
            'Impuestos': ['Fecha', 'Descripcion', 'Monto_$'],
            'Cuentas x Pagar': ['Proveedor', 'Total_$', 'Fecha'],
            'Bancos': ['Fecha', 'Saldo', 'Créditos', 'Com_Débitos']
        }
        
        sheets = {}
        validation_errors = []
        
        for sheet_name, required_columns in required_sheets.items():
            if sheet_name not in available_sheets:
                validation_errors.append(f"Hoja faltante: {sheet_name}")
                sheets[sheet_name] = pd.DataFrame(columns=required_columns)
                continue
                
            df = pd.read_excel(file, sheet_name=sheet_name)
            missing_cols = [col for col in required_columns if col not in df.columns]
            
            if missing_cols:
                validation_errors.append(f"Columnas faltantes en {sheet_name}: {', '.join(missing_cols)}")
            
            sheets[sheet_name] = df
        
        if validation_errors:
            st.warning("Problemas encontrados:\n- " + "\n- ".join(validation_errors))
            
        return sheets
    
    except Exception as e:
        st.error(f"Error crítico al cargar archivo: {str(e)}")
        return None

def process_nomina(df):
    """Procesa los datos de nómina con validaciones"""
    if df.empty:
        return pd.DataFrame(), pd.DataFrame()
    
    try:
        # Limpieza y transformación
        df = df.copy()
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce').dt.date
        df = df.dropna(subset=['Fecha', 'Nombre Empleado'])
        
        # Cálculo de totales
        agg_config = {
            '$_Nómina_Quincenal': 'sum',
            '$_Horas Extras': 'sum',
            '$_Dia extra': 'sum',
            '$_Bono_Alimentacion': 'sum'
        }
        
        # Solo incluir columnas que existan
        agg_config = {k: v for k, v in agg_config.items() if k in df.columns}
        
        empleados = df.groupby('Nombre Empleado').agg(agg_config).reset_index()
        
        return df, empleados
    
    except Exception as e:
        st.error(f"Error procesando nómina: {str(e)}")
        return pd.DataFrame(), pd.DataFrame()

def process_ventas(df):
    """Procesa los datos de ventas"""
    if df.empty:
        return pd.DataFrame(), pd.DataFrame()
    
    try:
        df = df.copy()
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce').dt.date
        df = df.dropna(subset=['Fecha'])
        
        # Agregar día de la semana si hay fechas válidas
        if not df.empty:
            df['Dia_Semana'] = pd.to_datetime(df['Fecha']).dt.day_name(locale='es')
        
        # Seleccionar solo columnas numéricas para el resumen
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        if numeric_cols:
            ventas_diarias = df.groupby('Fecha')[numeric_cols].sum().reset_index()
        else:
            ventas_diarias = pd.DataFrame(columns=['Fecha'])
        
        return df, ventas_diarias
    
    except Exception as e:
        st.error(f"Error procesando ventas: {str(e)}")
        return pd.DataFrame(), pd.DataFrame()

def process_impuestos(df):
    """Procesa los datos de impuestos"""
    if df.empty:
        return pd.DataFrame(), pd.DataFrame()
    
    try:
        df = df.copy()
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce').dt.date
        
        if 'Monto_$' in df.columns:
            df = df.dropna(subset=['Monto_$'])
            impuestos = df.groupby('Descripcion')['Monto_$'].sum().reset_index()
        else:
            impuestos = pd.DataFrame(columns=['Descripcion', 'Monto_$'])
        
        return df, impuestos
    
    except Exception as e:
        st.error(f"Error procesando impuestos: {str(e)}")
        return pd.DataFrame(), pd.DataFrame()

def process_bancos(df):
    """Procesa los datos bancarios"""
    if df.empty:
        return pd.DataFrame(), pd.DataFrame()
    
    try:
        df = df.copy()
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce').dt.date
        
        # Manejo de columnas
        df['Debitos'] = df.get('Com_Débitos', 0)
        df['Creditos'] = df.get('Créditos', 0)
        
        # Agrupación por fecha
        flujo = df.groupby('Fecha').agg({
            'Debitos': 'sum',
            'Creditos': 'sum',
            'Saldo': 'last'
        }).reset_index()
        
        return df, flujo
    
    except Exception as e:
        st.error(f"Error procesando datos bancarios: {str(e)}")
        return pd.DataFrame(), pd.DataFrame()

# =============================================
# INTERFAZ DE USUARIO
# =============================================

def main():
    st.title("📊 Dashboard Financiero Integral")
    st.markdown("""
    <style>
        .reportview-container .main .block-container {
            padding-top: 2rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Carga de archivos
    with st.expander("📤 Cargar archivos", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            file1 = st.file_uploader("Archivo principal", type=['xlsx'], key="file1")
        with col2:
            file2 = st.file_uploader("Archivo para comparar (opcional)", type=['xlsx'], key="file2")
    
    # Procesamiento de datos
    data1, data2 = None, None
    
    if file1:
        with st.spinner('Cargando archivo principal...'):
            data1 = load_data(file1)
    
    if file2:
        with st.spinner('Cargando archivo de comparación...'):
            data2 = load_data(file2)
    
    if not data1 and not data2:
        st.warning("Por favor sube al menos un archivo Excel válido")
        st.info("""
        El archivo debe contener las siguientes hojas:
        - Nómina
        - Ventas
        - Impuestos
        - Cuentas x Pagar
        - Bancos
        """)
        return
    
    # Pestañas principales
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🧑‍💼 Nómina", 
        "💰 Ventas", 
        "🏛️ Impuestos", 
        "🧾 Cuentas por Pagar", 
        "🏦 Bancos"
    ])
    
    # ========== PESTAÑA NÓMINA ==========
    with tab1:
        st.header("Análisis de Nómina")
        
        if data1 and 'Nómina' in data1:
            with st.spinner('Procesando datos de nómina...'):
                nomina1, empleados1 = process_nomina(data1['Nómina'])
                
                if not nomina1.empty:
                    # KPIs
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                        st.metric("Total Nómina", f"${empleados1['$_Nómina_Quincenal'].sum():,.2f}" 
                                if '$_Nómina_Quincenal' in empleados1.columns else "N/D")
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                        st.metric("Total Horas Extras", f"${empleados1['$_Horas Extras'].sum():,.2f}" 
                                if '$_Horas Extras' in empleados1.columns else "N/D")
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                        st.metric("Empleados", len(empleados1))
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    with col4:
                        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                        st.metric("Período", 
                                 f"{nomina1['Fecha'].min()} a {nomina1['Fecha'].max()}" 
                                 if not nomina1.empty else "N/D")
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Gráficos
                    col1, col2 = st.columns(2)
                    with col1:
                        if 'Nombre Empleado' in empleados1.columns and '$_Nómina_Quincenal' in empleados1.columns:
                            fig = px.bar(empleados1.sort_values('$_Nómina_Quincenal', ascending=False).head(10),
                                       x='Nombre Empleado', y='$_Nómina_Quincenal',
                                       title="Top 10 Empleados por Nómina",
                                       color='Nombre Empleado')
                            st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        if 'Nombre Empleado' in empleados1.columns and '$_Nómina_Quincenal' in empleados1.columns:
                            fig = px.pie(empleados1, names='Nombre Empleado', 
                                        values='$_Nómina_Quincenal',
                                        title="Distribución de Nómina")
                            st.plotly_chart(fig, use_container_width=True)
                    
                    # Datos detallados
                    with st.expander("Ver datos detallados"):
                        st.dataframe(nomina1)
                
                else:
                    st.warning("No hay datos válidos en la hoja de Nómina")
        
        # [Resto de las pestañas siguen el mismo patrón...]
        
        # Sección de comparación si hay segundo archivo
        if data2 and 'Nómina' in data2:
            with st.spinner('Procesando comparación...'):
                nomina2, empleados2 = process_nomina(data2['Nómina'])
                
                if not nomina2.empty and not nomina1.empty:
                    st.markdown("<div class='compare-card'>", unsafe_allow_html=True)
                    st.subheader("🔍 Comparación entre archivos")
                    
                    # Cálculo de diferencias
                    total1 = empleados1['$_Nómina_Quincenal'].sum()
                    total2 = empleados2['$_Nómina_Quincenal'].sum()
                    diferencia = total2 - total1
                    cambio_porcentual = (diferencia / total1 * 100) if total1 != 0 else 0
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Total Archivo 1", f"${total1:,.2f}")
                    with col2:
                        st.metric("Total Archivo 2", f"${total2:,.2f}", 
                                 delta=f"{diferencia:,.2f} ({cambio_porcentual:.1f}%)")
                    
                    # Gráfico comparativo
                    compare_df = pd.DataFrame({
                        'Archivo': ['Archivo 1', 'Archivo 2'],
                        'Total Nómina': [total1, total2],
                        'Empleados': [len(empleados1), len(empleados2)]
                    })
                    
                    fig = px.bar(compare_df, x='Archivo', y='Total Nómina',
                                color='Archivo', barmode='group',
                                title="Comparación de Nómina Total",
                                text='Total Nómina')
                    fig.update_traces(texttemplate='$%{text:,.2f}')
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
    
    # [Las otras pestañas (Ventas, Impuestos, etc.) seguirían la misma estructura...]
    
    # Sidebar con información útil
    st.sidebar.title("ℹ️ Instrucciones")
    st.sidebar.markdown("""
    1. Sube tu archivo Excel financiero
    2. Explora los datos a través de las pestañas
    3. Usa el segundo archivo para comparar
    4. Los gráficos son interactivos
    """)
    
    st.sidebar.download_button(
        label="📥 Descargar plantilla",
        data=open("plantilla_financiera.xlsx", "rb").read(),
        file_name="plantilla_financiera.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

if __name__ == "__main__":
    main()
