import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# =========================================
# CONFIGURACIÓN DE LA PÁGINA
# =========================================
st.set_page_config(
    page_title="Calculadora Costo de Oportunidad",
    page_icon="💸",
    layout="wide"
)

# =========================================
# ESTILOS CSS PERSONALIZADOS (El Botón Mágico)
# =========================================
st.markdown("""
<style>
/* Animación de las olas de colores */
@keyframes gradient-animation {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

/* Estilo del botón */
.wave-btn {
    display: block;
    width: 100%;
    padding: 12px 20px;
    margin: 10px 0;
    font-size: 16px;
    font-weight: bold;
    text-align: center;
    color: white !important;
    text-decoration: none !important;
    border-radius: 8px;
    /* Fondo base con gradiente multicolor */
    background: linear-gradient(270deg, #FF512F, #DD2476, #40E0D0, #FF512F);
    background-size: 300% 300%;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    transition: all 0.4s ease;
    border: none;
}

/* Efecto al pasar el mouse (Hover) */
.wave-btn:hover {
    /* Activar la animación de olas */
    animation: gradient-animation 3s ease infinite;
    /* Efecto de iluminación/resplandor */
    box-shadow: 0 0 15px rgba(221, 36, 118, 0.6), 0 0 30px rgba(64, 224, 208, 0.4);
    transform: scale(1.02); /* Crece un poquito */
}
</style>
""", unsafe_allow_html=True)

# =========================================
# BARRA LATERAL (INPUTS, LOGO Y BOTÓN)
# =========================================
with st.sidebar:
    # --- LOGO CENTRADO ---
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("image_ef75e0.png", width=150)
        
    st.header("⚙️ Configura tu Escenario")
    
    moneda = st.selectbox("Moneda", ["$", "€", "S/", "MXN"], index=0)
    
    st.subheader("🚬 Consumo")
    cigarros_diarios = st.slider("Cigarros al día", 1, 40, 10)
    precio_cajetilla = st.number_input(f"Precio por cajetilla ({moneda})", value=75.0, step=5.0)
    cigarros_paquete = 20
    
    st.subheader("📈 Variables Económicas")
    tasa_retorno = st.slider("Tasa de Retorno Anual (Inversión)", 5, 20, 10, help="Ej. Rendimiento de CETES o S&P 500") / 100
    inflacion = st.slider("Inflación Anual del Tabaco", 0, 15, 5) / 100
    anios_proyeccion = st.slider("Años a proyectar", 5, 40, 20)

    # --- LLAMADA A LA ACCIÓN ---
    st.markdown("---")
    st.markdown("### ¿Listo para recuperar tu salud y tu dinero?")
    
    # Botón HTML personalizado
    link_agenda = "https://meetings.hubspot.com/eliuth-misraim?uuid=169366e7-ae2e-4855-8083-cc554bb3db85"
    st.markdown(f"""
        <a href="{link_agenda}" target="_blank" class="wave-btn">
            📅 Agendar Consulta
        </a>
    """, unsafe_allow_html=True)

# =========================================
# LÓGICA FINANCIERA
# =========================================

# 1. Calcular Gasto Base
gasto_diario = (cigarros_diarios / cigarros_paquete) * precio_cajetilla
gasto_anual_inicial = gasto_diario * 365

# 2. Generar Proyección Financiera
def generar_proyeccion(anios, aporte_inicial, inf, tasa):
    registros = []
    saldo_quemado = 0
    saldo_invertido = 0
    aporte_actual = aporte_inicial
    
    for anio in range(1, anios + 1):
        saldo_quemado += aporte_actual
        saldo_invertido = (saldo_invertido * (1 + tasa)) + aporte_actual
        brecha = saldo_invertido - saldo_quemado
        
        registros.append({
            "Año": anio,
            "Gasto Anual": aporte_actual,
            "Dinero Quemado (Pérdida)": saldo_quemado,
            "Patrimonio Invertido (Ganancia)": saldo_invertido,
            "Costo de Oportunidad": brecha
        })
        
        aporte_actual = aporte_actual * (1 + inf)
        
    return pd.DataFrame(registros)

df_resultados = generar_proyeccion(anios_proyeccion, gasto_anual_inicial, inflacion, tasa_retorno)
monto_final_quemado = df_resultados.iloc[-1]['Dinero Quemado (Pérdida)']
monto_final_invertido = df_resultados.iloc[-1]['Patrimonio Invertido (Ganancia)']

# =========================================
# INTERFAZ PRINCIPAL
# =========================================

st.title("💸 Análisis Financiero: El Costo Real de Fumar")
st.markdown("""
Descubre cuánto dinero estás perdiendo a largo plazo. No solo es lo que gastas (dinero quemado), sino lo que **dejas de ganar** al no invertir ese capital aprovechando el interés compuesto.
""")

# --- SECCIÓN 1: MÉTRICAS CLAVE ---
st.divider()
col_m1, col_m2, col_m3 = st.columns(3)

with col_m1:
    st.metric("Gasto Diario Actual", f"{moneda}{gasto_diario:,.2f}")

with col_m2:
    st.metric("Gasto Anual Actual", f"{moneda}{gasto_anual_inicial:,.2f}", 
              delta="Capital disponible para invertir", delta_color="normal")

with col_m3:
    st.metric(f"Patrimonio a {anios_proyeccion} Años", f"{moneda}{monto_final_invertido:,.0f}", 
              delta=f"vs {moneda}{monto_final_quemado:,.0f} quemados", delta_color="inverse")

# --- SECCIÓN 2: GRÁFICO DE PROYECCIÓN INTERACTIVO ---
st.divider()
st.subheader(f"📉 Tu Futuro Financiero a {anios_proyeccion} años")

fig = go.Figure()

# Traza 1: Dinero Quemado
fig.add_trace(go.Scatter(
    x=df_resultados['Año'], 
    y=df_resultados['Dinero Quemado (Pérdida)'],
    mode='lines+markers',
    name='Dinero Quemado (Pérdida Neta)',
    line=dict(color='#e74c3c', width=2, dash='dash'),
    hovertemplate=f'<b>Año %{{x}}</b><br>Pérdida: {moneda}%{{y:,.0f}}<extra></extra>'
))

# Traza 2: Inversión (Interés Compuesto)
fig.add_trace(go.Scatter(
    x=df_resultados['Año'], 
    y=df_resultados['Patrimonio Invertido (Ganancia)'],
    mode='lines+markers',
    name='Patrimonio Potencial (Inversión)',
    line=dict(color='#27ae60', width=4),
    fill='tonexty', 
    fillcolor='rgba(39, 174, 96, 0.15)',
    hovertemplate=f'<b>Año %{{x}}</b><br>Patrimonio: {moneda}%{{y:,.0f}}<extra></extra>'
))

# Callout final
fig.add_annotation(
    x=anios_proyeccion,
    y=monto_final_invertido,
    text=f"<b>{moneda}{monto_final_invertido:,.0f}</b>",
    showarrow=True,
    arrowhead=2,
    ax=-40, ay=-40,
    font=dict(size=14, color="#27ae60")
)

fig.update_layout(
    xaxis_title='Tiempo Transcurrido (Años)',
    yaxis_title=f'Monto Acumulado ({moneda})',
    template='plotly_white',
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    height=450,
    margin=dict(l=0, r=0, t=30, b=0)
)

st.plotly_chart(fig, use_container_width=True)

# --- SECCIÓN 3: SIMULADOR DE ROI / PAYBACK ---
st.divider()
st.subheader("⏱️ Simulador: Recuperación de la Inversión (Payback)")

col_roi1, col_roi2 = st.columns([1, 1.5])

with col_roi1:
    st.markdown("Si inviertes en un programa o tratamiento para dejar de fumar, ¿En cuánto tiempo se paga solo con el dinero que dejas de gastar en cigarros?")
    costo_curso = st.number_input(f"Costo del Tratamiento/Curso ({moneda}):", min_value=0, value=6000, step=500)
    
    ahorro_mensual = gasto_anual_inicial / 12
    
    if ahorro_mensual > 0:
        meses_recuperacion = costo_curso / ahorro_mensual
    else:
        meses_recuperacion = 0
        
    st.success(f"""
    **Tu ahorro mensual estimado es:** {moneda}{ahorro_mensual:,.2f}
    
    ¡Tu inversión se recupera en tan solo **{meses_recuperacion:.1f} meses**!
    """)

with col_roi2:
    # Gráfico de Gauge (Velocímetro)
    fig_gauge = go.Figure(go.Indicator(
        mode = "number+gauge+delta",
        value = meses_recuperacion,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"<b>Meses para recuperar {moneda}{costo_curso:,.0f}</b><br><span style='font-size:0.8em;color:gray'>Ahorrando {moneda}{ahorro_mensual:,.0f}/mes</span>"},
        delta = {'reference': 6, 'increasing': {'color': "#e74c3c"}, 'decreasing': {'color': "#27ae60"}},
        gauge = {
            'axis': {'range': [None, 12], 'tickwidth': 1},
            'bar': {'color': "#2c3e50"},
            'bgcolor': "white",
            'steps': [
                {'range': [0, 3], 'color': "rgba(39, 174, 96, 0.4)"},  # Verde
                {'range': [3, 6], 'color': "rgba(241, 196, 15, 0.4)"}, # Amarillo
                {'range': [6, 12], 'color': "rgba(231, 76, 60, 0.4)"}  # Rojo
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': meses_recuperacion}
        }
    ))
    
    fig_gauge.update_layout(height=350, margin=dict(t=50, b=0, l=0, r=0))
    st.plotly_chart(fig_gauge, use_container_width=True)

# --- SECCIÓN 4: TABLA DETALLADA ---
st.divider()
with st.expander("Ver tabla de datos detallada año por año"):
    st.dataframe(
        df_resultados.style.format({
            "Gasto Anual": f"{moneda}{{:.2f}}",
            "Dinero Quemado (Pérdida)": f"{moneda}{{:.2f}}",
            "Patrimonio Invertido (Ganancia)": f"{moneda}{{:.2f}}",
            "Costo de Oportunidad": f"{moneda}{{:.2f}}"
        }),
        use_container_width=True,
        hide_index=True
    )