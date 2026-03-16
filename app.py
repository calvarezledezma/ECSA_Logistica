import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
from datetime import time, timedelta
import os

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="ECSA - KPI Despacho", layout="wide", page_icon="🥤")

# --- FUNCIONES DE UTILIDAD ---
def convertir_a_minutos(valor):
    if pd.isna(valor): return 0
    if isinstance(valor, time):
        return valor.hour * 60 + valor.minute + valor.second / 60
    elif isinstance(valor, pd.Timedelta):
        return valor.total_seconds() / 60
    elif isinstance(valor, (int, float)):
        return valor
    return 0

def format_time(minutes):
    if pd.isna(minutes) or minutes <= 0: return "00:00:00"
    td = timedelta(seconds=int(round(minutes * 60)))
    return str(td).zfill(8)

def crear_html_hexagono(nombre, total, mejor, peor, promedio, cumplimiento):
    return f"""
    <div style="display: flex; justify-content: center; align-items: center; font-family: Arial; height: 320px; margin-bottom: 20px;">
        <div style="position: relative; width: 500px; height: 280px;">
            <div style="position: absolute; top: 0; left: 40%; font-size: 22px; font-weight: bold;"><span style="color:blue">🔄</span> [{total}] 🚛</div>
            <div style="position: absolute; top: 50%; left: 70px; width: 80px; height: 3px; background: #4A90E2;"></div>
            <div style="position: absolute; top: 50%; right: 70px; width: 80px; height: 3px; background: #4A90E2;"></div>
            <div style="position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%); 
                        width: 200px; height: 170px; background: #E30613; 
                        clip-path: polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%);
                        display: flex; justify-content: center; align-items: center; 
                        color: white; font-weight: bold; font-size: 16px; text-align: center; padding: 10px;">{nombre}</div>
            <div style="position: absolute; top: 20%; left: 0; text-align: right; font-weight: bold; font-size: 16px;">🟢⬆️ ⌛<br>{mejor} —</div>
            <div style="position: absolute; bottom: 10%; left: 0; text-align: right; font-weight: bold; font-size: 16px;">{peor} —<br>🔴⬇️ ⌛</div>
            <div style="position: absolute; top: 20%; right: 0; font-weight: bold; font-size: 16px;">— ⌛ x&#772;<br>&nbsp;&nbsp;{promedio}</div>
            <div style="position: absolute; bottom: 10%; right: 0; font-weight: bold; font-size: 18px;">— {cumplimiento}%<br>&nbsp;&nbsp;🎯✅</div>
        </div>
    </div>
    """

# --- CABECERA CON LOGOS ---
col_ecsa, col_titulo, col_sbi = st.columns([1, 2, 1])
with col_ecsa:
    if os.path.exists("ecsa.png"): st.image("ecsa.png", width=180)
with col_titulo:
    st.markdown("<h1 style='text-align: center; margin-top: 20px;'>Dashboard Operaciones Despacho</h1>", unsafe_allow_html=True)
with col_sbi:
    if os.path.exists("SBI.jpg"):
        st.markdown("<div style='display: flex; justify-content: flex-end;'>", unsafe_allow_html=True)
        st.image("SBI.jpg", width=180)
        st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# --- LÓGICA DE CARGA DE DATOS INTELIGENTE ---
uploaded_file = st.file_uploader("Cargar Archivo Excel manualmente (Opcional)", type=["xlsx"])

df = None
nombre_pestana = "Reporte"

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    nombre_pestana = xls.sheet_names[0]
    df = pd.read_excel(xls, sheet_name=nombre_pestana)
else:
    # Buscar el archivo en el directorio actual (GitHub)
    archivos_excel = [f for f in os.listdir(".") if f.endswith(".xlsx")]
    archivo_objetivo = "Trazabilidad Logística.xlsx"
    
    # Intentar encontrar por nombre exacto o cargar el primero que sea Excel
    archivo_a_cargar = archivo_objetivo if archivo_objetivo in archivos_excel else (archivos_excel[0] if archivos_excel else None)

    if archivo_a_cargar:
        try:
            xls = pd.ExcelFile(archivo_a_cargar)
            nombre_pestana = xls.sheet_names[0]
            df = pd.read_excel(xls, sheet_name=nombre_pestana)
            st.info(f"📊 Reporte automático cargado: {archivo_a_cargar} ({nombre_pestana})")
        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")
            st.stop()
    else:
        st.warning("👋 Por favor, sube el archivo Excel o asegúrate de que esté en GitHub.")
        st.stop()

# --- PROCESAMIENTO ---
if df is not None:
    df.columns = df.columns.str.strip()
    COL_L, COL_Q, COL_FECHA = 'Tiempo Atención', 'Supervisor Despacho', 'Fecha'

    if COL_L in df.columns and COL_Q in df.columns:
        df['minutos_L'] = df[COL_L].apply(convertir_a_minutos)
        if COL_FECHA in df.columns:
            df[COL_FECHA] = pd.to_datetime(df[COL_FECHA], errors='coerce')

        df['Estado'] = df['minutos_L'].apply(lambda t: 'Alerta' if t > 60 else ('Excelente' if t < 40 else 'Aceptable'))

        # --- 📊 CUADRO RESUMEN ---
        res = df.groupby([COL_Q, 'Estado']).size().unstack(fill_value=0)
        for c in ['Alerta', 'Aceptable', 'Excelente']:
            if c not in res.columns: res[c] = 0
        res = res[['Alerta', 'Aceptable', 'Excelente']]
        res['Total'] = res.sum(axis=1)
        res['% viajes demorados'] = (res['Alerta'] / res['Total'] * 100).apply(lambda x: int(round(x)))
        
        # Ordenar tabla por Total de camiones (Mayor a Menor)
        res = res.sort_values(by='Total', ascending=False)

        t_total = res['Total'].sum()
        pct_gral = int(round((res['Alerta'].sum() / t_total * 100))) if t_total > 0 else 0

        filas_html = ""
        for name, row in res.iterrows():
            filas_html += f"""
            <tr style="border: 1px solid black; font-weight: bold; font-size: 15px;">
                <td style="text-align: left; padding: 10px; border: 1px solid black; background-color: white;">{name}</td>
                <td style="background-color: #FFC0CB; border: 1px solid black;">{row['Alerta']}</td>
                <td style="background-color: #FFF3CD; border: 1px solid black;">{row['Aceptable']}</td>
                <td style="background-color: #D4EDDA; border: 1px solid black;">{row['Excelente']}</td>
                <td style="background-color: #4472C4; color: white; border: 1px solid black;">{row['Total']}</td>
                <td style="background-color: white; color: red; border: 1px solid black;">{row['% viajes demorados']}%</td>
            </tr>"""

        tabla_html = f"""
        <div style="font-family: Arial; text-align: center;">
            <h2 style="margin-bottom: 10px;">Cuadro Tiempo de Atención Despachadores</h2>
            <table style="width: 100%; border-collapse: collapse; text-align: center; border: 2px solid black;">
                <thead>
                    <tr style="background-color: white;">
                        <th style="border: 1px solid black; padding: 10px; width: 30%;">Supervisor Despacho</th>
                        <th style="background-color: #FFC0CB; border: 1px solid black;">Alerta (>1h)</th>
                        <th style="background-color: #FFF3CD; border: 1px solid black;">Aceptable (40-60m)</th>
                        <th style="background-color: #D4EDDA; border: 1px solid black;">Excelente (<40m)</th>
                        <th style="background-color: #4472C4; color: white; border: 1px solid black;">Total</th>
                        <th style="background-color: red; color: white; border: 1px solid black; padding: 10px;">% viajes demorados</th>
                    </tr>
                </thead>
                <tbody>{filas_html}</tbody>
                <tfoot style="background-color: #FFFF00; font-weight: bold; font-size: 18px;">
                    <tr><td style="text-align: right; padding: 10px; border: 1px solid black;">Total Semana</td>
                    <td colspan="3" style="border: 1px solid black;"></td>
                    <td style="border: 1px solid black;">{t_total}</td>
                    <td style="border: 1px solid black;">{pct_gral}%</td></tr>
                </tfoot>
            </table>
        </div>"""
        components.html(tabla_html, height=350)

        st.divider()

        # --- ⬢ HEXÁGONOS (ORDENADOS POR VOLUMEN) ---
        st.subheader("Performance Individual por Despachador")
        supervisores_ordenados = res.index.tolist()
        cols = st.columns(2)
        for i, supervisor in enumerate(supervisores_ordenados):
            d_s = df[df[COL_Q] == supervisor]
            mejor = format_time(d_s['minutos_L'].min())
            peor = format_time(d_s['minutos_L'].max())
            promedio = format_time(d_s['minutos_L'].mean())
            cumplimiento = int(100 - (res.loc[supervisor, '% viajes demorados']))
            html_hex = crear_html_hexagono(supervisor, int(res.loc[supervisor, 'Total']), mejor, peor, promedio, cumplimiento)
            with cols[i % 2]:
                components.html(html_hex, height=330)

        st.divider()

        # --- 📈 GRÁFICO FINAL (TÍTULO AJUSTADO) ---
        if COL_FECHA in df.columns:
            df_diario = df.groupby(COL_FECHA).size().reset_index(name='Total').sort_values(COL_FECHA)
            df_diario[COL_FECHA] = df_diario[COL_FECHA].dt.strftime('%d-%m-%Y')
            
            fig = px.line(df_diario, x=COL_FECHA, y='Total', title=f"Despachos diarios {nombre_pestana}", markers=True, text='Total')
            
            fig.update_traces(line=dict(color='#4472C4', width=4), 
                              marker=dict(size=28, color='#4472C4', line=dict(width=2, color='white')),
                              textposition="middle center", textfont=dict(color='white', size=12, family="Arial Black"))
            
            fig.update_layout(plot_bgcolor='rgba(240,240,240,0.5)', paper_bgcolor='white', 
                              title_x=0.33, 
                              title_font=dict(size=26, color="black", family="Arial Black"),
                              xaxis=dict(showgrid=True, gridcolor='lightgray', title="Fecha"),
                              yaxis=dict(showgrid=True, gridcolor='lightgray', title="", showticklabels=False), margin=dict(t=80))
            st.plotly_chart(fig, use_container_width=True)

# --- 🏢 FOOTER SBI LATAM ---
st.markdown("""
    <style>
    .footer { position: relative; left: 0; bottom: 0; width: 100%; color: #555555; text-align: center; padding: 30px 0px; 
              font-family: Arial; border-top: 1px solid #e6e6e6; margin-top: 50px; }
    .footer b { color: #E30613; }
    </style>
    <div class="footer"><p>Herramienta desarrollada por <b>SBI Latam</b> © 2025</p></div>
""", unsafe_allow_html=True)