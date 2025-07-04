import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="Dashboard Financiero MAYO 2025",
    page_icon="💰",
    layout="wide"
)

# Cargar datos (reemplaza con tu carga real de datos)
@st.cache_data
def load_data():
    ventas = pd.read_excel("Resumen Financiero MAYO 2025.xlsx", sheet_name="Ventas")
    nomina = pd.read_excel("Resumen Financiero MAYO 2025.xlsx", sheet_name="Nómina")
    impuestos = pd.read_excel("Resumen Financiero MAYO 2025.xlsx", sheet_name="Impuestos")
    cuentas_pagar = pd.read_excel("Resumen Financiero MAYO 2025.xlsx", sheet_name="Cuentas x Pagar")
    bancos = pd.read_excel("Resumen Financiero MAYO 2025.xlsx", sheet_name="Bancos")
    return ventas, nomina, impuestos, cuentas_pagar, bancos

ventas, nomina, impuestos, cuentas_pagar, bancos = load_data()
"""
# Procesamiento de datos (ejemplos básicos)
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

# Página de Resumen General
if pagina == "Resumen General":
    st.title("Resumen Financiero - Mayo 2025")
    
    # KPIs principales
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_ventas = ventas['Totales'].sum()
        st.metric("Total Ventas", f"${total_ventas:,.2f}")
    
    with col2:
        total_nomina = nomina['$_Nómina_Quincenal'].sum()
        st.metric("Total Nómina", f"${total_nomina:,.2f}")
    
    with col3:
        total_impuestos = impuestos['Monto_$'].sum()
        st.metric("Total Impuestos", f"${total_impuestos:,.2f}")
    
    with col4:
        total_pagar = cuentas_pagar['Total_$'].sum()
        st.metric("Total por Pagar", f"${total_pagar:,.2f}")
    
    with col5:
        saldo_bancos = bancos['Saldo'].iloc[-1]
        st.metric("Saldo Bancario Final", f"${saldo_bancos:,.2f}")
    
    # Gráficos resumen
    st.subheader("Tendencias Mensuales")
    
    fig1 = px.line(ventas, x='Fecha', y='Totales', title='Ventas Diarias')
    st.plotly_chart(fig1, use_container_width=True)
    
    fig2 = px.bar(nomina, x='Nombre Empleado', y='$_Nómina_Quincenal', 
                 title='Distribución de Nómina por Empleado')
    st.plotly_chart(fig2, use_container_width=True)

# Página de Ventas
elif pagina == "Ventas":
    st.title("Análisis de Ventas")
    
    # KPIs de Ventas
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        avg_daily_sales = ventas['Totales'].mean()
        st.metric("Venta Promedio Diaria", f"${avg_daily_sales:,.2f}")
    
    with col2:
        max_daily_sales = ventas['Totales'].max()
        st.metric("Venta Máxima Diaria", f"${max_daily_sales:,.2f}")
    
    with col3:
        min_daily_sales = ventas['Totales'].min()
        st.metric("Venta Mínima Diaria", f"${min_daily_sales:,.2f}")
    
    with col4:
        sales_growth = ((ventas['Totales'].iloc[-1] - ventas['Totales'].iloc[0]) / ventas['Totales'].iloc[0]) * 100
        st.metric("Crecimiento Mensual", f"{sales_growth:.2f}%")
    
    with col5:
        days_above_avg = (ventas['Totales'] > avg_daily_sales).sum()
        st.metric("Días sobre el promedio", f"{days_above_avg}")
    
    # Gráficos de Ventas
    st.subheader("Distribución de Ventas")
    
    fig1 = px.line(ventas, x='Fecha', y='Totales', title='Evolución Diaria de Ventas')
    st.plotly_chart(fig1, use_container_width=True)
    
    fig2 = px.box(ventas, y='Totales', title='Distribución de Ventas Diarias')
    st.plotly_chart(fig2, use_container_width=True)
    
    payment_methods = ventas[['Provincial $', 'Banesco_$', 'Efectivo_$', 'Zelle', 'PayPal']].sum()
    fig3 = px.pie(values=payment_methods, names=payment_methods.index, 
                 title='Distribución por Método de Pago')
    st.plotly_chart(fig3, use_container_width=True)
    
    fig4 = px.scatter(ventas, x='Tipo_Cambio', y='Totales', 
                     title='Relación entre Tipo de Cambio y Ventas')
    st.plotly_chart(fig4, use_container_width=True)
    
    ventas['Dia_Semana'] = ventas['Fecha'].dt.day_name()
    fig5 = px.bar(ventas.groupby('Dia_Semana')['Totales'].mean().reset_index(), 
                 x='Dia_Semana', y='Totales', 
                 title='Ventas Promedio por Día de la Semana')
    st.plotly_chart(fig5, use_container_width=True)

# Página de Nómina
elif pagina == "Nómina":
    st.title("Análisis de Nómina")
    
    # KPIs de Nómina
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_payroll = nomina['$_Nómina_Quincenal'].sum()
        st.metric("Total Nómina", f"${total_payroll:,.2f}")
    
    with col2:
        avg_salary = nomina['$_Nómina_Quincenal'].mean()
        st.metric("Salario Promedio", f"${avg_salary:,.2f}")
    
    with col3:
        num_employees = nomina['Nombre Empleado'].nunique()
        st.metric("Número de Empleados", num_employees)
    
    with col4:
        bonus_total = nomina['$_Bono'].sum()
        st.metric("Total Bonos", f"${bonus_total:,.2f}")
    
    with col5:
        overtime_total = nomina['$_Horas Extras'].sum()
        st.metric("Total Horas Extras", f"${overtime_total:,.2f}")
    
    # Gráficos de Nómina
    st.subheader("Distribución de Nómina")
    
    fig1 = px.bar(nomina, x='Nombre Empleado', y='$_Nómina_Quincenal', 
                 title='Nómina por Empleado')
    st.plotly_chart(fig1, use_container_width=True)
    
    fig2 = px.pie(nomina, values='$_Nómina_Quincenal', names='Nombre Empleado', 
                 title='Distribución de Nómina')
    st.plotly_chart(fig2, use_container_width=True)
    
    fig3 = px.box(nomina, y='$_Nómina_Quincenal', title='Distribución de Salarios')
    st.plotly_chart(fig3, use_container_width=True)
    
    fig4 = px.scatter(nomina, x='Tasa_B$', y='$_Nómina_Quincenal', color='Nombre Empleado',
                     title='Relación Tasa Cambio vs Nómina')
    st.plotly_chart(fig4, use_container_width=True)
    
    nomina_by_date = nomina.groupby('Fecha')['$_Nómina_Quincenal'].sum().reset_index()
    fig5 = px.line(nomina_by_date, x='Fecha', y='$_Nómina_Quincenal', 
                  title='Evolución de Pagos de Nómina')
    st.plotly_chart(fig5, use_container_width=True)

# Página de Impuestos
elif pagina == "Impuestos":
    st.title("Análisis de Impuestos")
    
    # KPIs de Impuestos
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_taxes = impuestos['Monto_$'].sum()
        st.metric("Total Impuestos", f"${total_taxes:,.2f}")
    
    with col2:
        avg_tax_rate = impuestos['Tasa_Cambio'].mean()
        st.metric("Tasa Cambio Promedio", f"{avg_tax_rate:.2f}")
    
    with col3:
        num_payments = len(impuestos)
        st.metric("Número de Pagos", num_payments)
    
    with col4:
        max_tax_payment = impuestos['Monto_$'].max()
        st.metric("Pago Más Alto", f"${max_tax_payment:,.2f}")
    
    with col5:
        tax_orgs = impuestos['N_Organismo'].nunique()
        st.metric("Organismos Diferentes", tax_orgs)
    
    # Gráficos de Impuestos
    st.subheader("Distribución de Impuestos")
    
    fig1 = px.bar(impuestos, x='N_Organismo', y='Monto_$', 
                 title='Impuestos por Organismo')
    st.plotly_chart(fig1, use_container_width=True)
    
    fig2 = px.pie(impuestos, values='Monto_$', names='N_Organismo', 
                 title='Distribución de Impuestos')
    st.plotly_chart(fig2, use_container_width=True)
    
    fig3 = px.line(impuestos, x='Fecha', y='Monto_$', 
                  title='Evolución de Pagos de Impuestos')
    st.plotly_chart(fig3, use_container_width=True)
    
    fig4 = px.scatter(impuestos, x='Tasa_Cambio', y='Monto_$',
                     title='Relación Tasa Cambio vs Monto Impuesto')
    st.plotly_chart(fig4, use_container_width=True)
    
    fig5 = px.box(impuestos, y='Monto_$', title='Distribución de Montos de Impuestos')
    st.plotly_chart(fig5, use_container_width=True)

# Página de Cuentas por Pagar
elif pagina == "Cuentas por Pagar":
    st.title("Análisis de Cuentas por Pagar")
    
    # KPIs de Cuentas por Pagar
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_payable = cuentas_pagar['Total_$'].sum()
        st.metric("Total por Pagar", f"${total_payable:,.2f}")
    
    with col2:
        avg_payment = cuentas_pagar['Total_$'].mean()
        st.metric("Pago Promedio", f"${avg_payment:,.2f}")
    
    with col3:
        num_invoices = len(cuentas_pagar)
        st.metric("Número de Facturas", num_invoices)
    
    with col4:
        max_invoice = cuentas_pagar['Total_$'].max()
        st.metric("Factura Más Alta", f"${max_invoice:,.2f}")
    
    with col5:
        num_vendors = cuentas_pagar['Proveedor'].nunique()
        st.metric("Proveedores Diferentes", num_vendors)
    
    # Gráficos de Cuentas por Pagar
    st.subheader("Distribución de Cuentas por Pagar")
    
    fig1 = px.bar(cuentas_pagar, x='Proveedor', y='Total_$', 
                 title='Facturas por Proveedor')
    st.plotly_chart(fig1, use_container_width=True)
    
    fig2 = px.pie(cuentas_pagar, values='Total_$', names='Tipo de gasto', 
                 title='Distribución por Tipo de Gasto')
    st.plotly_chart(fig2, use_container_width=True)
    
    fig3 = px.histogram(cuentas_pagar, x='Total_$', 
                       title='Distribución de Montos de Facturas')
    st.plotly_chart(fig3, use_container_width=True)
    
    fig4 = px.scatter(cuentas_pagar, x='Tasa_B$', y='Total_$',
                     title='Relación Tasa Cambio vs Monto Factura')
    st.plotly_chart(fig4, use_container_width=True)
    
    fig5 = px.box(cuentas_pagar, y='Total_$', 
                 title='Distribución de Montos de Facturas')
    st.plotly_chart(fig5, use_container_width=True)

# Página de Bancos
elif pagina == "Bancos":
    st.title("Análisis de Transacciones Bancarias")
    
    # KPIs de Bancos
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        final_balance = bancos['Saldo'].iloc[-1]
        st.metric("Saldo Final", f"${final_balance:,.2f}")
    
    with col2:
        avg_balance = bancos['Saldo'].mean()
        st.metric("Saldo Promedio", f"${avg_balance:,.2f}")
    
    with col3:
        total_deposits = bancos[bancos['Créditos'] > 0]['Créditos'].sum()
        st.metric("Total Depósitos", f"${total_deposits:,.2f}")
    
    with col4:
        total_withdrawals = bancos[bancos['Débitos'] > 0]['Débitos'].sum()
        st.metric("Total Retiros", f"${total_withdrawals:,.2f}")
    
    with col5:
        num_transactions = len(bancos)
        st.metric("Número de Transacciones", num_transactions)
    
    # Gráficos de Bancos
    st.subheader("Análisis de Transacciones Bancarias")
    
    fig1 = px.line(bancos, x='Fecha', y='Saldo', title='Evolución del Saldo Bancario')
    st.plotly_chart(fig1, use_container_width=True)
    
    deposits = bancos[bancos['Créditos'] > 0]
    fig2 = px.bar(deposits, x='Fecha', y='Créditos', 
                 title='Depósitos por Día')
    st.plotly_chart(fig2, use_container_width=True)
    
    withdrawals = bancos[bancos['Débitos'] > 0]
    fig3 = px.bar(withdrawals, x='Fecha', y='Débitos', 
                 title='Retiros por Día')
    st.plotly_chart(fig3, use_container_width=True)
    
    fig4 = px.scatter(bancos, x='Tasa_B$', y='Saldo',
                     title='Relación Tasa Cambio vs Saldo Bancario')
    st.plotly_chart(fig4, use_container_width=True)
    
    bank_summary = bancos.groupby('Banco')['Saldo'].last().reset_index()
    fig5 = px.pie(bank_summary, values='Saldo', names='Banco', 
                 title='Distribución de Saldo por Banco')
    st.plotly_chart(fig5, use_container_width=True)

# Notas finales
st.sidebar.markdown("---")
st.sidebar.info("""
**Notas:**
- Datos correspondientes a Mayo 2025
- Actualización diaria automática
- Contacto: admin@empresa.com
""")
"""
