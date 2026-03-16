# --- ANÁLISIS DE TIEMPOS (GRÁFICO AGRANDADO) ---
st.markdown("### ⏱️ Análisis Detallado de Tiempos de Atención")

# Calculamos cuántos nombres únicos hay para ajustar la altura
nombres_unicos = df_filtrado['Destino'].nunique()
# Altura base de 400px + 30px por cada nombre extra (mínimo 500px)
altura_dinamica = max(500, nombres_unicos * 30)

# Creamos el gráfico horizontal para mayor legibilidad
fig_atencion = px.box(
    df_filtrado, 
    y='Destino',           # Ahora los nombres van aquí
    x='Tiempo Atención',    # Los minutos van en la base
    color='Destino', 
    points="all", 
    orientation='h',       # ¡Esto lo hace horizontal!
    title="Distribución de Tiempos por Destino (Ordenado)",
    labels={'Tiempo Atención': 'Minutos en Operación', 'Destino': 'Punto de Destino'}
)

# Ajustes estéticos para que se vea "pro"
fig_atencion.update_layout(
    height=altura_dinamica, # Aplicamos la altura calculada
    showlegend=False,       # Quitamos la leyenda porque los nombres ya están en el eje Y
    margin=dict(l=20, r=20, t=50, b=50),
    xaxis_title="Minutos",
    yaxis={'categoryorder':'total ascending'} # Ordena automáticamente los más rápidos arriba
)

# Lo mostramos usando todo el ancho de la página
st.plotly_chart(fig_atencion, use_container_width=True)

# --- GRÁFICO SECUNDARIO: PRODUCTIVIDAD ---
st.markdown("---")
st.markdown("### 📊 Volumen por Transporte")
fig_trans = px.bar(
    df_filtrado.groupby('Transporte')['Qty Entrega'].sum().reset_index(), 
    x='Transporte', 
    y='Qty Entrega', 
    text_auto='.2s',
    color_discrete_sequence=['#1E88E5']
)
st.plotly_chart(fig_trans, use_container_width=True)
