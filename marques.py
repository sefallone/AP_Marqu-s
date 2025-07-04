import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import datetime

# Configuración de la página
st.set_page_config(layout="wide", page_title="Dashboard Financiero", page_icon="📊")

# Estilos CSS personalizados
st.markdown("""
<style>
    .main {background-color: #f5f5f5;}
    .st-bq {border-radius: 10px;}
    .metric-card {
        padding: 15px;
        border-radius: 10px;
        background-color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 15px;
    }
    .compare-card {
        padding: 15px;
        border-radius: 10px;
        background-color: #e6f7ff;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Función para cargar datos
@st.cache_data
def load_data(file):
    try:
        sheets = {
            'Nómina': pd.read_excel(file, sheet_name='Nómina'),
            'Ventas': pd.read_excel(file, sheet_name='Ventas'),
            'Impuestos': pd.read_excel(file, sheet_name='Impuestos'),
            'Cuentas x Pagar': pd.read_excel(file, sheet_name='Cuentas x Pagar'),
            'Bancos': pd.read_excel(file, sheet_name='Bancos')
        }
        return sheets
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")
        return None

# Función para procesar datos de nómina
def process_nomina(df):
    if df is None or df.empty:
        return None
    
    # Limpieza de datos
    df = df.dropna(how='all')
    df['Fecha'] = pd.to_datetime(df['Fecha']).dt.date
    
    # Calcular totales por empleado
    empleados = df.groupby('Nombre Empleado').agg({
        '$_Nómina_Quincenal': 'sum',
        '$_Horas Extras': 'sum',
        '$_Dia extra': 'sum',
        '$_Bono_Alimentacion': 'sum'
    }).reset_index()
    
    return df, empleados

# Función para procesar datos de ventas
def process_ventas(df):
    if df is None or df.empty:
        return None
    
    # Limpieza de datos
    df['Fecha'] = pd.to_datetime(df['Fecha']).dt.date
    df['Dia_Semana'] = pd.to_datetime(df['Fecha']).dt.day_name()
    
    # Calcular totales por día
    ventas_diarias = df.groupby('Fecha').agg({
        'Totales': 'sum',
        'Plataforma': 'sum',
        'Efectivo_$': 'sum',
        'Zelle': 'sum'
    }).reset_index()
    
    return df, ventas_diarias

# Función para procesar datos de impuestos
def process_impuestos(df):
    if df is None or df.empty:
        return None
    
    # Limpieza de datos
    df['Fecha'] = pd.to_datetime(df['Fecha']).dt.date
    df = df.dropna(subset=['Monto_$'])
    
    # Calcular totales por tipo de impuesto
    impuestos = df.groupby('Descripcion').agg({
        'Monto_$': 'sum'
    }).reset_index()
    
    return df, impuestos

# Función para procesar datos de bancos
def process_bancos(df):
    if df is None or df.empty:
        return None
    
    # Limpieza de datos
    df['Fecha'] = pd.to_datetime(df['Fecha']).dt.date
    df['Debitos'] = df['Com_Débitos'].fillna(0)
    df['Creditos'] = df['Créditos'].fillna(0)
    
    # Calcular flujo diario
    flujo = df.groupby('Fecha').agg({
        'Debitos': 'sum',
        'Creditos': 'sum',
        'Saldo': 'last'
    }).reset_index()
    
    return df, flujo

# Interfaz de usuario
st.title("📊 Dashboard Financiero")
st.write("Carga y compara archivos Excel financieros")

# Carga de archivos
col1, col2 = st.columns(2)
with col1:
    file1 = st.file_uploader("Cargar archivo principal", type=['xlsx'])
with col2:
    file2 = st.file_uploader("Cargar archivo para comparar", type=['xlsx'])

# Procesamiento de datos
data1, data2 = None, None
if file1:
    data1 = load_data(file1)
if file2:
    data2 = load_data(file2)

if not data1 and not data2:
    st.warning("Por favor carga al menos un archivo Excel")
    st.stop()

# Tabs para cada sección
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Nómina", "Ventas", "Impuestos", "Cuentas x Pagar", "Bancos"])

with tab1:
    st.header("Análisis de Nómina")
    
    if data1:
        nomina1, empleados1 = process_nomina(data1['Nómina'])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("Total Nómina", f"${empleados1['$_Nómina_Quincenal'].sum():,.2f}")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("Total Horas Extras", f"${empleados1['$_Horas Extras'].sum():,.2f}")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col3:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("Empleados", len(empleados1))
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Gráficos
        fig1 = px.bar(empleados1, x='Nombre Empleado', y='$_Nómina_Quincenal', 
                     title="Nómina por Empleado", color='Nombre Empleado')
        st.plotly_chart(fig1, use_container_width=True)
        
        fig2 = px.pie(empleados1, names='Nombre Empleado', values='$_Nómina_Quincenal',
                     title="Distribución de Nómina")
        st.plotly_chart(fig2, use_container_width=True)
        
    if data2:
        nomina2, empleados2 = process_nomina(data2['Nómina'])
        
        st.markdown("<div class='compare-card'>", unsafe_allow_html=True)
        st.subheader("Comparación entre archivos")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Nómina Archivo 1", f"${empleados1['$_Nómina_Quincenal'].sum():,.2f}")
        with col2:
            st.metric("Total Nómina Archivo 2", f"${empleados2['$_Nómina_Quincenal'].sum():,.2f}", 
                     delta=f"{(empleados2['$_Nómina_Quincenal'].sum() - empleados1['$_Nómina_Quincenal'].sum()):,.2f}")
        
        # Gráfico comparativo
        compare_df = pd.DataFrame({
            'Archivo': ['Archivo 1', 'Archivo 2'],
            'Total Nómina': [empleados1['$_Nómina_Quincenal'].sum(), empleados2['$_Nómina_Quincenal'].sum()]
        })
        fig_compare = px.bar(compare_df, x='Archivo', y='Total Nómina', 
                            title="Comparación de Nómina Total", color='Archivo')
        st.plotly_chart(fig_compare, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.header("Análisis de Ventas")
    
    if data1:
        ventas1, ventas_diarias1 = process_ventas(data1['Ventas'])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("Ventas Totales", f"${ventas_diarias1['Totales'].sum():,.2f}")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("Ventas Promedio Diario", f"${ventas_diarias1['Totales'].mean():,.2f}")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col3:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("Días Analizados", len(ventas_diarias1))
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Gráficos
        fig1 = px.line(ventas_diarias1, x='Fecha', y='Totales', 
                      title="Ventas Diarias", markers=True)
        st.plotly_chart(fig1, use_container_width=True)
        
        fig2 = px.bar(ventas_diarias1, x='Dia_Semana', y='Totales', 
                     title="Ventas por Día de la Semana", color='Dia_Semana')
        st.plotly_chart(fig2, use_container_width=True)
        
        fig3 = px.pie(ventas1, names='Tipo_Cambio', values='Totales',
                     title="Distribución por Tipo de Cambio")
        st.plotly_chart(fig3, use_container_width=True)
        
    if data2:
        ventas2, ventas_diarias2 = process_ventas(data2['Ventas'])
        
        st.markdown("<div class='compare-card'>", unsafe_allow_html=True)
        st.subheader("Comparación entre archivos")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Ventas Totales Archivo 1", f"${ventas_diarias1['Totales'].sum():,.2f}")
        with col2:
            st.metric("Ventas Totales Archivo 2", f"${ventas_diarias2['Totales'].sum():,.2f}", 
                     delta=f"{(ventas_diarias2['Totales'].sum() - ventas_diarias1['Totales'].sum()):,.2f}")
        
        # Gráfico comparativo
        compare_df = pd.DataFrame({
            'Fecha': pd.concat([ventas_diarias1['Fecha'], ventas_diarias2['Fecha']]),
            'Totales': pd.concat([ventas_diarias1['Totales'], ventas_diarias2['Totales']]),
            'Archivo': ['Archivo 1']*len(ventas_diarias1) + ['Archivo 2']*len(ventas_diarias2)
        })
        fig_compare = px.line(compare_df, x='Fecha', y='Totales', color='Archivo',
                             title="Comparación de Ventas Diarias", markers=True)
        st.plotly_chart(fig_compare, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

with tab3:
    st.header("Análisis de Impuestos")
    
    if data1:
        impuestos1, resumen_impuestos1 = process_impuestos(data1['Impuestos'])
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("Total Impuestos", f"${resumen_impuestos1['Monto_$'].sum():,.2f}")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("Tipos de Impuestos", len(resumen_impuestos1))
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Gráficos
        fig1 = px.bar(resumen_impuestos1, x='Descripcion', y='Monto_$', 
                     title="Impuestos por Tipo", color='Descripcion')
        st.plotly_chart(fig1, use_container_width=True)
        
        fig2 = px.pie(resumen_impuestos1, names='Descripcion', values='Monto_$',
                     title="Distribución de Impuestos")
        st.plotly_chart(fig2, use_container_width=True)
        
    if data2:
        impuestos2, resumen_impuestos2 = process_impuestos(data2['Impuestos'])
        
        st.markdown("<div class='compare-card'>", unsafe_allow_html=True)
        st.subheader("Comparación entre archivos")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Impuestos Archivo 1", f"${resumen_impuestos1['Monto_$'].sum():,.2f}")
        with col2:
            st.metric("Total Impuestos Archivo 2", f"${resumen_impuestos2['Monto_$'].sum():,.2f}", 
                     delta=f"{(resumen_impuestos2['Monto_$'].sum() - resumen_impuestos1['Monto_$'].sum()):,.2f}")
        
        # Gráfico comparativo
        compare_df = pd.DataFrame({
            'Tipo': pd.concat([resumen_impuestos1['Descripcion'], resumen_impuestos2['Descripcion']]),
            'Monto': pd.concat([resumen_impuestos1['Monto_$'], resumen_impuestos2['Monto_$']]),
            'Archivo': ['Archivo 1']*len(resumen_impuestos1) + ['Archivo 2']*len(resumen_impuestos2)
        })
        fig_compare = px.bar(compare_df, x='Tipo', y='Monto', color='Archivo',
                            title="Comparación de Impuestos por Tipo", barmode='group')
        st.plotly_chart(fig_compare, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

with tab4:
    st.header("Análisis de Cuentas por Pagar")
    
    if data1 and 'Cuentas x Pagar' in data1: 
        ctas_pagar1 = data1['Cuentas x Pagar']
        
        # Limpieza básica
        ctas_pagar1 = ctas_pagar1.dropna(how='all')
        if 'Fecha' in ctas_pagar1.columns:
            ctas_pagar1['Fecha'] = pd.to_datetime(ctas_pagar1['Fecha']).dt.date
        
        # KPIs
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("Total a Pagar", f"${ctas_pagar1['Total_$'].sum():,.2f}" if 'Total_$' in ctas_pagar1.columns else "N/D")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("Proveedores", len(ctas_pagar1['Proveedor'].unique()) if 'Proveedor' in ctas_pagar1.columns else "N/D")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col3:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("Total IVA", f"${ctas_pagar1['Iva 16%'].sum():,.2f}" if 'Iva 16%' in ctas_pagar1.columns else "N/D")
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Gráficos (si hay datos suficientes)
        if 'Proveedor' in ctas_pagar1.columns and 'Total_$' in ctas_pagar1.columns:
            top_proveedores = ctas_pagar1.groupby('Proveedor')['Total_$'].sum().nlargest(5).reset_index()
            fig1 = px.bar(top_proveedores, x='Proveedor', y='Total_$', 
                         title="Top 5 Proveedores por Monto", color='Proveedor')
            st.plotly_chart(fig1, use_container_width=True)
        
        if 'Tipo de gasto' in ctas_pagar1.columns and 'Total_$' in ctas_pagar1.columns:
            gastos = ctas_pagar1.groupby('Tipo de gasto')['Total_$'].sum().reset_index()
            fig2 = px.pie(gastos, names='Tipo de gasto', values='Total_$',
                         title="Distribución por Tipo de Gasto")
            st.plotly_chart(fig2, use_container_width=True)
    
    if data2 and 'Cuentas x Pagar' in data2:
        ctas_pagar2 = data2['Cuentas x Pagar']
        
        st.markdown("<div class='compare-card'>", unsafe_allow_html=True)
        st.subheader("Comparación entre archivos")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total a Pagar Archivo 1", f"${ctas_pagar1['Total_$'].sum():,.2f}" if 'Total_$' in ctas_pagar1.columns else "N/D")
        with col2:
            total2 = ctas_pagar2['Total_$'].sum() if 'Total_$' in ctas_pagar2.columns else 0
            total1 = ctas_pagar1['Total_$'].sum() if 'Total_$' in ctas_pagar1.columns else 0
            st.metric("Total a Pagar Archivo 2", f"${total2:,.2f}" if 'Total_$' in ctas_pagar2.columns else "N/D", 
                     delta=f"{(total2 - total1):,.2f}" if 'Total_$' in ctas_pagar1.columns and 'Total_$' in ctas_pagar2.columns else None)
        
        st.markdown("</div>", unsafe_allow_html=True)

with tab5:
    st.header("Análisis de Bancos")
    
    if data1:
        bancos1, flujo1 = process_bancos(data1['Bancos'])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("Saldo Final", f"${flujo1['Saldo'].iloc[-1]:,.2f}")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("Total Débitos", f"${flujo1['Debitos'].sum():,.2f}")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col3:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("Total Créditos", f"${flujo1['Creditos'].sum():,.2f}")
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Gráficos
        fig1 = px.line(flujo1, x='Fecha', y='Saldo', 
                      title="Evolución del Saldo Bancario", markers=True)
        st.plotly_chart(fig1, use_container_width=True)
        
        fig2 = px.bar(flujo1, x='Fecha', y=['Debitos', 'Creditos'],
                     title="Flujo Bancario Diario", barmode='group')
        st.plotly_chart(fig2, use_container_width=True)
        
        if 'Banco' in bancos1.columns:
            bancos_count = bancos1['Banco'].value_counts().reset_index()
            fig3 = px.pie(bancos_count, names='Banco', values='count',
                         title="Transacciones por Banco")
            st.plotly_chart(fig3, use_container_width=True)
        
    if data2:
        bancos2, flujo2 = process_bancos(data2['Bancos'])
        
        st.markdown("<div class='compare-card'>", unsafe_allow_html=True)
        st.subheader("Comparación entre archivos")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Saldo Final Archivo 1", f"${flujo1['Saldo'].iloc[-1]:,.2f}")
        with col2:
            st.metric("Saldo Final Archivo 2", f"${flujo2['Saldo'].iloc[-1]:,.2f}", 
                     delta=f"{(flujo2['Saldo'].iloc[-1] - flujo1['Saldo'].iloc[-1]):,.2f}")
        
        # Gráfico comparativo
        compare_df = pd.DataFrame({
            'Fecha': pd.concat([flujo1['Fecha'], flujo2['Fecha']]),
            'Saldo': pd.concat([flujo1['Saldo'], flujo2['Saldo']]),
            'Archivo': ['Archivo 1']*len(flujo1) + ['Archivo 2']*len(flujo2)
        })
        fig_compare = px.line(compare_df, x='Fecha', y='Saldo', color='Archivo',
                             title="Comparación de Saldos Bancarios", markers=True)
        st.plotly_chart(fig_compare, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# Notas finales
st.sidebar.markdown("""
### Instrucciones:
1. Carga tu archivo Excel financiero
2. Explora las diferentes pestañas para ver los análisis
3. Carga un segundo archivo para comparar métricas
4. Los gráficos son interactivos - usa el cursor para explorar
""")
