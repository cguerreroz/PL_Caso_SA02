"""
DASHBOARD INTERACTIVO DE OPTIMIZACIÓN DE PRODUCCIÓN
Autor: Especialista en Optimización y Ciencia de Datos
Tecnología: Streamlit + Gurobi
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from utils import optimizar_produccion, calcular_metricas_clave
import matplotlib.pyplot as plt

# ============================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================

st.set_page_config(
    page_title="Dashboard de Optimización - Juguetes",
    page_icon="🧸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin-bottom: 0.5rem;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #666;
    }
    .insight-box {
        background-color: #e6f3ff;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #ff7f0e;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3e6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #d62728;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #e6ffe6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #2ca02c;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# TÍTULO Y DESCRIPCIÓN
# ============================================

st.markdown('<p class="main-header">🧸 Dashboard de Optimización de Producción</p>', 
            unsafe_allow_html=True)

st.markdown("""
Este dashboard interactivo permite optimizar la producción de juguetes 
**A** y **B** para maximizar beneficios. Ajusta los parámetros en el panel 
izquierdo y observa los resultados en tiempo real.
""")

# ============================================
# BARRA LATERAL - PARÁMETROS
# ============================================

with st.sidebar:
    st.header("⚙️ Parámetros de Optimización")
    
    st.subheader("💰 Beneficios Unitarios")
    beneficio_a = st.number_input(
        "Juguete A ($)",
        min_value=10,
        max_value=100,
        value=40,
        step=5,
        help="Beneficio por unidad del Juguete A"
    )
    beneficio_b = st.number_input(
        "Juguete B ($)",
        min_value=10,
        max_value=100,
        value=30,
        step=5,
        help="Beneficio por unidad del Juguete B"
    )
    
    st.subheader("🏭 Recursos Disponibles")
    horas_ensamblaje = st.slider(
        "Horas de Ensamblaje",
        min_value=50,
        max_value=200,
        value=100,
        step=5,
        help="Horas disponibles en el área de ensamblaje"
    )
    horas_empaque = st.slider(
        "Horas de Empaque",
        min_value=40,
        max_value=160,
        value=80,
        step=5,
        help="Horas disponibles en el área de empaque"
    )
    
    st.subheader("📦 Restricciones de Producción")
    
    col1, col2 = st.columns(2)
    with col1:
        capacidad_maxima = st.number_input(
            "Capacidad máxima",
            min_value=0,
            max_value=100,
            value=50,
            step=5,
            help="0 = sin límite"
        )
        if capacidad_maxima == 0:
            capacidad_maxima = None
            st.caption("✅ Sin límite de capacidad")
        else:
            st.caption(f"🔒 Límite: {capacidad_maxima} unidades")
    
    with col2:
        st.caption(" ")
        st.caption(" ")
        usar_capacidad = st.checkbox("Activar límite de capacidad", value=True)
        if not usar_capacidad:
            capacidad_maxima = None
            st.caption("✅ Capacidad desactivada")
    
    st.subheader("📋 Demanda Mínima")
    demanda_min_a = st.number_input(
        "Mínimo Juguete A",
        min_value=0,
        max_value=50,
        value=0,
        step=1
    )
    demanda_min_b = st.number_input(
        "Mínimo Juguete B",
        min_value=0,
        max_value=50,
        value=0,
        step=1
    )
    
    st.subheader("🔢 Tipo de Variable")
    entero = st.checkbox(
        "Producción en unidades enteras",
        value=False,
        help="Activar si solo se pueden producir unidades completas"
    )
    
    # Botón de optimización
    st.markdown("---")
    optimizar_btn = st.button(
        "🚀 Optimizar Producción",
        type="primary",
        use_container_width=True
    )

# ============================================
# OPTIMIZACIÓN Y RESULTADOS
# ============================================

# Estado inicial
if 'resultados' not in st.session_state:
    st.session_state.resultados = None

# Ejecutar optimización
if optimizar_btn:
    with st.spinner('Optimizando producción...'):
        resultados = optimizar_produccion(
            beneficio_a=beneficio_a,
            beneficio_b=beneficio_b,
            horas_ensamblaje=horas_ensamblaje,
            horas_empaque=horas_empaque,
            capacidad_maxima=capacidad_maxima,
            demanda_minima_a=demanda_min_a,
            demanda_minima_b=demanda_min_b,
            entero=entero
        )
        st.session_state.resultados = resultados

# Mostrar resultados si existen
if st.session_state.resultados is not None:
    resultados = st.session_state.resultados
    
    if resultados['status'] != 'Óptimo':
        st.error("❌ No se encontró una solución óptima con los parámetros actuales. Por favor, ajusta las restricciones.")
        st.stop()
    
    # ============================================
    # MÉTRICAS PRINCIPALES (Fila Superior)
    # ============================================
    
    st.markdown("---")
    st.header("📊 Resultados de la Optimización")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">${resultados['beneficio']:,.0f}</div>
            <div class="metric-label">💵 Beneficio Total</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{resultados['produccion_total']:.0f}</div>
            <div class="metric-label">📦 Producción Total</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{resultados['x']:.0f}</div>
            <div class="metric-label">🧸 Juguete A</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{resultados['y']:.0f}</div>
            <div class="metric-label">🧸 Juguete B</div>
        </div>
        """, unsafe_allow_html=True)
    
    # ============================================
    # GRÁFICOS (Fila Media)
    # ============================================
    
    st.markdown("---")
    
    # Crear subplots
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Mix de Producción', 'Uso de Recursos'),
        specs=[[{'type': 'pie'}, {'type': 'bar'}]]
    )
    
    # Gráfico 1: Pie chart del mix de producción
    fig.add_trace(
        go.Pie(
            labels=['Juguete A', 'Juguete B'],
            values=[resultados['x'], resultados['y']],
            marker=dict(colors=['#1f77b4', '#ff7f0e']),
            textinfo='label+percent',
            hoverinfo='label+value+percent'
        ),
        row=1, col=1
    )
    
    # Gráfico 2: Barras de uso de recursos
    recursos = ['Ensamblaje', 'Empaque']
    usado = [resultados['uso_ensamblaje'], resultados['uso_empaque']]
    disponible = [horas_ensamblaje, horas_empaque]
    
    fig.add_trace(
        go.Bar(
            x=recursos,
            y=usado,
            name='Usado',
            marker_color='#1f77b4',
            text=[f'{u:.1f}h' for u in usado],
            textposition='inside'
        ),
        row=1, col=2
    )
    
    fig.add_trace(
        go.Bar(
            x=recursos,
            y=[max(0, d - u) for d, u in zip(disponible, usado)],
            name='Disponible',
            marker_color='lightgray',
            text=[f'{d:.1f}h' for d in disponible],
            textposition='inside'
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        height=400,
        showlegend=True,
        barmode='stack'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # ============================================
    # ANÁLISIS DE SENSIBILIDAD Y MÉTRICAS (Fila Inferior)
    # ============================================
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📈 Análisis de Sensibilidad")
        
        # Crear gráfico de sensibilidad para beneficio vs capacidad
        capacidades = np.arange(20, 81, 5) if capacidad_maxima else []
        
        if capacidades:
            beneficios = []
            for cap in capacidades:
                res = optimizar_produccion(
                    beneficio_a=beneficio_a,
                    beneficio_b=beneficio_b,
                    horas_ensamblaje=horas_ensamblaje,
                    horas_empaque=horas_empaque,
                    capacidad_maxima=cap,
                    entero=entero
                )
                if res['status'] == 'Óptimo':
                    beneficios.append(res['beneficio'])
                else:
                    beneficios.append(None)
            
            fig_sens = go.Figure()
            fig_sens.add_trace(go.Scatter(
                x=capacidades,
                y=beneficios,
                mode='lines+markers',
                name='Beneficio',
                line=dict(color='#2ca02c', width=3),
                marker=dict(size=8)
            ))
            fig_sens.update_layout(
                title='Impacto de la Capacidad en el Beneficio',
                xaxis_title='Capacidad Máxima (unidades)',
                yaxis_title='Beneficio ($)',
                height=300,
                hovermode='x'
            )
            st.plotly_chart(fig_sens, use_container_width=True)
    
    with col2:
        st.subheader("💡 Insights Clave")
        
        # Calcular métricas adicionales
        if resultados['status'] == 'Óptimo':
            # Verificar restricciones activas
            restricciones_activas = []
            if resultados['holgura_ensamblaje'] < 0.01:
                restricciones_activas.append("Ensamblaje")
            if resultados['holgura_empaque'] < 0.01:
                restricciones_activas.append("Empaque")
            
            precio_sombra_ens = resultados.get('precio_sombra_Ensamblaje', 0)
            precio_sombra_emp = resultados.get('precio_sombra_Empaque', 0)
            
            st.markdown(f"""
            <div class="insight-box">
                <strong>🔍 Restricciones Activas:</strong><br>
                {', '.join(restricciones_activas) if restricciones_activas else 'Ninguna (recursos sobrantes)'}
            </div>
            """, unsafe_allow_html=True)
            
            if precio_sombra_ens > 0:
                st.markdown(f"""
                <div class="success-box">
                    <strong>💰 Valor del Ensamblaje:</strong><br>
                    Cada hora extra de ensamblaje genera <strong>${precio_sombra_ens:.2f}</strong> adicionales
                </div>
                """, unsafe_allow_html=True)
            
            if precio_sombra_emp > 0:
                st.markdown(f"""
                <div class="success-box">
                    <strong>💰 Valor del Empaque:</strong><br>
                    Cada hora extra de empaque genera <strong>${precio_sombra_emp:.2f}</strong> adicionales
                </div>
                """, unsafe_allow_html=True)
            
            if 'precio_sombra_Capacidad' in resultados:
                precio_sombra_cap = resultados['precio_sombra_Capacidad']
                if precio_sombra_cap > 0:
                    st.markdown(f"""
                    <div class="success-box">
                        <strong>💰 Valor de Capacidad:</strong><br>
                        Cada unidad extra de capacidad genera <strong>${precio_sombra_cap:.2f}</strong> adicionales
                    </div>
                    """, unsafe_allow_html=True)
            
            # Recomendación
            if len(restricciones_activas) == 2:
                st.markdown("""
                <div class="warning-box">
                    <strong>⚠️ Cuello de Botella:</strong><br>
                    Ambos recursos están al límite. Considera aumentar capacidad de ensamblaje y empaque.
                </div>
                """, unsafe_allow_html=True)
    
    # ============================================
    # TABLA DE DETALLES
    # ============================================
    
    with st.expander("📋 Ver detalles completos de la solución"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Variables de Decisión**")
            df_vars = pd.DataFrame({
                'Variable': ['Juguete A', 'Juguete B', 'Total'],
                'Cantidad': [resultados['x'], resultados['y'], resultados['produccion_total']],
                'Beneficio Unitario': [beneficio_a, beneficio_b, '-'],
                'Beneficio Total': [
                    resultados['x'] * beneficio_a,
                    resultados['y'] * beneficio_b,
                    resultados['beneficio']
                ]
            })
            st.dataframe(df_vars, hide_index=True, use_container_width=True)
        
        with col2:
            st.write("**Uso de Recursos**")
            df_recursos = pd.DataFrame({
                'Recurso': ['Ensamblaje', 'Empaque'],
                'Disponible': [horas_ensamblaje, horas_empaque],
                'Usado': [resultados['uso_ensamblaje'], resultados['uso_empaque']],
                'Holgura': [resultados['holgura_ensamblaje'], resultados['holgura_empaque']],
                'Precio Sombra': [
                    resultados.get('precio_sombra_Ensamblaje', 0),
                    resultados.get('precio_sombra_Empaque', 0)
                ]
            })
            st.dataframe(df_recursos, hide_index=True, use_container_width=True)

else:
    # Mensaje inicial
    st.info("👈 Ajusta los parámetros en la barra lateral y presiona 'Optimizar Producción' para comenzar")
    
    # Mostrar ejemplo de cómo funciona
    st.markdown("""
    ### 🎯 ¿Qué puedes hacer con este dashboard?
    
    1. **Ajustar beneficios unitarios** - Ver cómo cambiar el precio afecta la producción
    2. **Modificar recursos disponibles** - Analizar el impacto de tener más horas
    3. **Activar/desactivar límites de capacidad** - Evaluar restricciones de producción
    4. **Probar con variables enteras** - Simular producción en unidades completas
    
    ### 📈 Análisis disponible en tiempo real
    - Optimización automática con Gurobi
    - Visualización del mix de producción
    - Uso de recursos y holguras
    - Precios sombra para cada recurso
    - Análisis de sensibilidad de capacidad
    """)

# ============================================
# FOOTER
# ============================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.8rem;">
    Desarrollado con ❤️ usando Streamlit y Gurobi | 
    Optimización de Producción - Juguetes A y B
</div>
""", unsafe_allow_html=True)