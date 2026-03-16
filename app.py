# --- 📊 CUADRO RESUMEN (con tabla scrollable) ---
res = df.groupby([COL_Q, 'Estado']).size().unstack(fill_value=0)
for c in ['Alerta', 'Aceptable', 'Excelente']:
    if c not in res.columns: res[c] = 0
res = res[['Alerta', 'Aceptable', 'Excelente']]
res['Total'] = res.sum(axis=1)
res['% viajes demorados'] = (res['Alerta'] / res['Total'] * 100).apply(lambda x: int(round(x)))

# Ordenar por Total camiones (Mayor a Menor)
res = res.sort_values(by='Total', ascending=False)

t_total = res['Total'].sum()
pct_gral = int(round((res['Alerta'].sum() / t_total * 100))) if t_total > 0 else 0

# --- Tabla HTML con scroll vertical ---
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
<div style="font-family: Arial; text-align: center; margin-top: 20px;">
    <h2 style="margin-bottom: 10px;">Cuadro Tiempo de Atención Despachadores</h2>
    
    <!-- Contenedor scrollable -->
    <div style="max-height: 350px; overflow-y: auto; border: 2px solid black; border-radius: 8px;">
        <table style="width: 100%; border-collapse: collapse; text-align: center; margin-bottom: 0;">
            <thead style="position: sticky; top: 0; background-color: white; z-index: 1;">
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
                <tr>
                    <td style="text-align: right; padding: 10px; border: 1px solid black;">Total Semana</td>
                    <td colspan="3" style="border: 1px solid black;"></td>
                    <td style="border: 1px solid black;">{t_total}</td>
                    <td style="border: 1px solid black;">{pct_gral}%</td>
                </tr>
            </tfoot>
        </table>
    </div>
</div>"""

components.html(tabla_html, height=450)  # altura ajustada para el scroll
