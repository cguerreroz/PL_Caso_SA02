"""
DASHBOARD INTERACTIVO DE OPTIMIZACIÓN DE PRODUCCIÓN
Autor: Especialista en Optimización y Ciencia de Datos
Tecnología: Streamlit + Scipy (no requiere licencia)
Versión: 2.1 - Corrección de sintaxis
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from utils import optimizar_produccion, calcular_metricas_clave

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
    .stButton > button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
        padding: 0.5rem;
        border-radius: 10px;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #2ca02c;
        transform: scale(1.02);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# TÍTULO Y DESCRIPCIÓN
# ============================================

st.markdown('<p class="main-header">🧸 Dashboard de Optimización de Producción</p>', 
            unsafe_allow_html=True)

st.markdown("""
<div style="background-color: #e8f4f8; padding: 1rem; border-radius: 10px; margin-bottom: 1.5rem;">
    <p style="font-size: 1.1rem; margin: 0;">
        📊 Este dashboard interactivo permite optimizar la producción de juguetes 
        <strong>A</strong> y <strong>B</strong> para maximizar beneficios. 
        Ajusta los parámetros en el panel izquierdo y observa los resultados en tiempo real.
    </p>
</div>
""", unsafe_allow_html=True)

# ============================================
# BARRA LATERAL - PARÁMETROS
# ============================================

with st.sidebar:
    st.header("⚙️ Parámetros de Optimización")
    st.markdown("---")
    
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
    
    st.markdown("---")
    st.subheader("🏭 Recursos Disponibles")
    
    col1, col2 = st.columns(2)
    with col1:
        horas_ensamblaje = st.number_input(
            "Ensamblaje (h)",
            min_value=50,
            max_value=200,
            value=100,
            step=5,
            help="Horas disponibles en ensamblaje"
        )
    with col2:
        horas_empaque = st.number_input(
            "Empaque (h)",
            min_value=40,
            max_value=160,
            value=80,
            step=5,
            help="Horas disponibles en empaque"
        )
    
    st.markdown("---")
    st.subheader("📦 Restricciones de Producción")
    
    usar_capacidad = st.checkbox(
        "Activar límite de capacidad",
        value=True,
        help="Limitar la producción total máxima"
    )
    
    if usar_capacidad:
        capacidad_maxima = st.slider(
            "Capacidad máxima (unidades)",
            min_value=10,
            max_value=100,
            value=50,
            step=5,
            help="Número máximo de unidades totales a producir"
        )
    else:
        capacidad_maxima = None
        st.caption("✅ Sin límite de capacidad")
    
    st.markdown("---")
    st.subheader("📋 Demanda Mínima")
    
    col1, col2 = st.columns(2)
    with col1:
        demanda_min_a = st.number_input(
            "Mínimo A",
            min_value=0,
            max_value=50,
            value=0,
            step=1,
            help="Producción mínima requerida de A"
        )
    with col2:
        demanda_min_b = st.number_input(
            "Mínimo B",
            min_value=0,
            max_value=50,
            value=0,
            step=1,
            help="Producción mínima requerida de B"
        )
    
    st.markdown("---")
    st.subheader("🔢 Tipo de Variable")
    entero = st.checkbox(
        "Producción en unidades enteras",
        value=False,
        help="Activar si solo se pueden producir unidades completas (sin fracciones)"
    )
    
    st.markdown("---")
    
    # Botón de optimización
    optimizar_btn = st.button(
        "🚀 Optimizar Producción",
        type="primary",
        use_container_width=True
    )
    
    st.markdown("---")
    st.caption("💡 Desarrollado con Streamlit + Scipy")

# ============================================
# OPTIMIZACIÓN Y RESULTADOS
# ============================================

# Estado inicial
if 'resultados' not in st.session_state:
    st.session_state.resultados = None

# Ejecutar optimización al presionar el botón
if optimizar_btn:
    with st.spinner('🔍 Optimizando producción...'):
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
    
    # Verificar si la solución es óptima
    if resultados['status'] != 'Óptimo':
        st.error(f"❌ {resultados['status']}")
        st.info("💡 **Sugerencia:** Ajusta los parámetros (aumenta recursos o reduce demandas mínimas)")
        st.stop()
    
    # ============================================
    # MÉTRICAS PRINCIPALES (Fila Superior)
    # ============================================
    
    st.markdown("---")
    st.header("📊 Resultados de la Optimización")
    
    # Crear 4 columnas para métricas clave
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">${resultados['beneficio']:,.2f}</div>
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
        <div class="metric-card" style="border-left-color: #2ca02c;">
            <div class="metric-value" style="color: #2ca02c;">{resultados['x']:.0f}</div>
            <div class="metric-label">🧸 Juguete A</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #ff7f0e;">
            <div class="metric-value" style="color: #ff7f0e;">{resultados['y']:.0f}</div>
            <div class="metric-label">🧸 Juguete B</div>
        </div>
        """, unsafe_allow_html=True)
    
    # ============================================
    # GRÁFICOS (Fila Media)
    # ============================================
    
    st.markdown("---")
    
    # Crear subplots con dos gráficos
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('📊 Mix de Producción', '📈 Uso de Recursos'),
        specs=[[{'type': 'pie'}, {'type': 'bar'}]]
    )
    
    # Gráfico 1: Pie chart del mix de producción
    valores = [max(0, resultados['x']), max(0, resultados['y'])]
    labels = ['Juguete A', 'Juguete B']
    colores = ['#2ca02c', '#ff7f0e']
    
    if sum(valores) > 0:
        fig.add_trace(
            go.Pie(
                labels=labels,
                values=valores,
                marker=dict(colors=colores),
                textinfo='label+percent',
                hoverinfo='label+value+percent',
                pull=[0.05, 0] if valores[0] > valores[1] else [0, 0.05]
            ),
            row=1, col=1
        )
    else:
        fig.add_trace(
            go.Pie(
                labels=['Sin producción'],
                values=[1],
                marker=dict(colors=['lightgray']),
                textinfo='label'
            ),
            row=1, col=1
        )
    
    # Gráfico 2: Barras de uso de recursos
    recursos = ['Ensamblaje', 'Empaque']
    disponible = [
        resultados['uso_ensamblaje'] + resultados['holgura_ensamblaje'],
        resultados['uso_empaque'] + resultados['holgura_empaque']
    ]
    usado = [resultados['uso_ensamblaje'], resultados['uso_empaque']]
    
    fig.add_trace(
        go.Bar(
            x=recursos,
            y=usado,
            name='Usado',
            marker_color='#1f77b4',
            text=[f'{u:.1f}h' for u in usado],
            textposition='inside',
            textfont=dict(color='white', size=12)
        ),
        row=1, col=2
    )
    
    fig.add_trace(
        go.Bar(
            x=recursos,
            y=[max(0, d - u) for d, u in zip(disponible, usado)],
            name='Disponible',
            marker_color='lightgray',
            text=[f'{d - u:.1f}h' for d, u in zip(disponible, usado)],
            textposition='inside',
            textfont=dict(color='#666', size=12)
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        height=400,
        showlegend=True,
        barmode='stack',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Ajustar títulos de los ejes
    fig.update_yaxes(title_text="Horas", row=1, col=2)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # ============================================
    # ANÁLISIS DE SENSIBILIDAD Y MÉTRICAS (Fila Inferior)
    # ============================================
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📈 Análisis de Sensibilidad")
        
        # Crear gráfico de sensibilidad para beneficio vs capacidad
        if capacidad_maxima is not None and capacidad_maxima > 0:
            # Generar datos para diferentes capacidades
            capacidades = np.arange(
                max(10, capacidad_maxima - 30),
                min(100, capacidad_maxima + 30) + 5,
                5
            )
            
            beneficios = []
            for cap in capacidades:
                res = optimizar_produccion(
                    beneficio_a=beneficio_a,
                    beneficio_b=beneficio_b,
                    horas_ensamblaje=horas_ensamblaje,
                    horas_empaque=horas_empaque,
                    capacidad_maxima=cap,
                    demanda_minima_a=demanda_min_a,
                    demanda_minima_b=demanda_min_b,
                    entero=entero
                )
                if res['status'] == 'Óptimo':
                    beneficios.append(res['beneficio'])
                else:
                    beneficios.append(None)
            
            # Crear figura de sensibilidad
            fig_sens = go.Figure()
            
            # Línea de beneficio
            fig_sens.add_trace(go.Scatter(
                x=capacidades,
                y=beneficios,
                mode='lines+markers',
                name='Beneficio',
                line=dict(color='#2ca02c', width=3),
                marker=dict(size=10, color='#2ca02c', symbol='circle'),
                hovertemplate='Capacidad: %{x:.0f} unidades<br>Beneficio: $%{y:,.2f}<extra></extra>'
            ))
            
            # Marcar punto actual
            if capacidad_maxima in capacidades:
                idx = list(capacidades).index(capacidad_maxima)
                if idx < len(beneficios) and beneficios[idx] is not None:
                    fig_sens.add_trace(go.Scatter(
                        x=[capacidad_maxima],
                        y=[beneficios[idx]],
                        mode='markers',
                        name='Punto actual',
                        marker=dict(size=15, color='red', symbol='star'),
                        hovertemplate='<b>Capacidad actual: %{x:.0f} unidades</b><br>Beneficio: $%{y:,.2f}<extra></extra>'
                    ))
            
            fig_sens.update_layout(
                title='Impacto de la Capacidad en el Beneficio',
                xaxis_title='Capacidad Máxima (unidades)',
                yaxis_title='Beneficio ($)',
                height=350,
                hovermode='x unified',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig_sens, use_container_width=True)
        else:
            st.info("💡 Activa la restricción de capacidad para ver el análisis de sensibilidad")
    
    with col2:
        st.subheader("💡 Insights Clave")
        
        # Verificar restricciones activas
        restricciones_activas = []
        if resultados['holgura_ensamblaje'] < 0.1:
            restricciones_activas.append("Ensamblaje")
        if resultados['holgura_empaque'] < 0.1:
            restricciones_activas.append("Empaque")
        if 'holgura_capacidad' in resultados and resultados['holgura_capacidad'] < 0.1:
            restricciones_activas.append("Capacidad")
        
        # Mostrar restricciones activas
        if restricciones_activas:
            st.markdown(f"""
            <div class="insight-box">
                <strong>🔍 Restricciones Activas:</strong><br>
                {' • '.join(restricciones_activas)}
                <br><span style="font-size: 0.85rem; color: #666;">
                    Estos recursos están al 100% de su capacidad
                </span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="insight-box">
                <strong>✅ Recursos Sobrantes:</strong><br>
                Ninguna restricción está activa
                <br><span style="font-size: 0.85rem; color: #666;">
                    Hay capacidad disponible en todos los recursos
                </span>
            </div>
            """, unsafe_allow_html=True)
        
        # Precios sombra
        precio_sombra_ens = resultados.get('precio_sombra_Ensamblaje', 0)
        precio_sombra_emp = resultados.get('precio_sombra_Empaque', 0)
        
        if precio_sombra_ens > 0.01:
            st.markdown(f"""
            <div class="success-box">
                <strong>💰 Valor del Ensamblaje:</strong><br>
                <span style="font-size: 1.2rem; font-weight: bold; color: #2ca02c;">
                    ${precio_sombra_ens:.2f}
                </span>
                <br><span style="font-size: 0.85rem; color: #666;">
                    por hora adicional
                </span>
            </div>
            """, unsafe_allow_html=True)
        
        if precio_sombra_emp > 0.01:
            st.markdown(f"""
            <div class="success-box">
                <strong>💰 Valor del Empaque:</strong><br>
                <span style="font-size: 1.2rem; font-weight: bold; color: #2ca02c;">
                    ${precio_sombra_emp:.2f}
                </span>
                <br><span style="font-size: 0.85rem; color: #666;">
                    por hora adicional
                </span>
            </div>
            """, unsafe_allow_html=True)
        
        if 'precio_sombra_Capacidad' in resultados:
            precio_sombra_cap = resultados['precio_sombra_Capacidad']
            if precio_sombra_cap > 0.01:
                st.markdown(f"""
                <div class="success-box">
                    <strong>💰 Valor de Capacidad:</strong><br>
                    <span style="font-size: 1.2rem; font-weight: bold; color: #2ca02c;">
                        ${precio_sombra_cap:.2f}
                    </span>
                    <br><span style="font-size: 0.85rem; color: #666;">
                        por unidad adicional
                    </span>
                </div>
                """, unsafe_allow_html=True)
        
        # Recomendación estratégica
        if len(restricciones_activas) >= 2:
            st.markdown("""
            <div class="warning-box">
                <strong>⚠️ Cuello de Botella Detectado:</strong><br>
                Múltiples recursos están al límite.
                <br><span style="font-size: 0.85rem; color: #666;">
                    Considera aumentar la capacidad de los recursos con mayor precio sombra
                </span>
            </div>
            """, unsafe_allow_html=True)
        
        # Mostrar eficiencia
        eficiencia = (resultados['beneficio'] / resultados['produccion_total']) if resultados['produccion_total'] > 0 else 0
        st.markdown(f"""
        <div style="background-color: #f9f9f9; padding: 0.8rem; border-radius: 10px; margin-top: 0.5rem;">
            <strong>📊 Eficiencia Promedio:</strong><br>
            <span style="font-size: 1.3rem; font-weight: bold; color: #1f77b4;">
                ${eficiencia:.2f}
            </span>
            <br><span style="font-size: 0.85rem; color: #666;">
                por unidad producida
            </span>
        </div>
        """, unsafe_allow_html=True)
    
    # ============================================
    # TABLA DE DETALLES (Expandible)
    # ============================================
    
    with st.expander("📋 Ver detalles completos de la solución", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**📦 Variables de Decisión**")
            df_vars = pd.DataFrame({
                'Variable': ['Juguete A', 'Juguete B', 'Total'],
                'Cantidad': [f"{resultados['x']:.0f}", f"{resultados['y']:.0f}", f"{resultados['produccion_total']:.0f}"],
                'Beneficio Unitario': [f"${beneficio_a:.2f}", f"${beneficio_b:.2f}", "-"],
                'Beneficio Total': [
                    f"${resultados['x'] * beneficio_a:,.2f}",
                    f"${resultados['y'] * beneficio_b:,.2f}",
                    f"${resultados['beneficio']:,.2f}"
                ]
            })
            st.dataframe(df_vars, hide_index=True, use_container_width=True)
        
        with col2:
            st.write("**🏭 Uso de Recursos**")
            recursos_data = {
                'Recurso': ['Ensamblaje', 'Empaque'],
                'Disponible': [
                    f"{resultados['uso_ensamblaje'] + resultados['holgura_ensamblaje']:.1f}h",
                    f"{resultados['uso_empaque'] + resultados['holgura_empaque']:.1f}h"
                ],
                'Usado': [
                    f"{resultados['uso_ensamblaje']:.1f}h",
                    f"{resultados['uso_empaque']:.1f}h"
                ],
                'Holgura': [
                    f"{resultados['holgura_ensamblaje']:.1f}h",
                    f"{resultados['holgura_empaque']:.1f}h"
                ],
                'Precio Sombra': [
                    f"${resultados.get('precio_sombra_Ensamblaje', 0):.2f}",
                    f"${resultados.get('precio_sombra_Empaque', 0):.2f}"
                ]
            }
            
            if 'holgura_capacidad' in resultados:
                recursos_data['Recurso'].append('Capacidad')
                recursos_data['Disponible'].append(f"{capacidad_maxima:.0f}u")
                recursos_data['Usado'].append(f"{resultados['produccion_total']:.0f}u")
                recursos_data['Holgura'].append(f"{resultados['holgura_capacidad']:.0f}u")
                recursos_data['Precio Sombra'].append(f"${resultados.get('precio_sombra_Capacidad', 0):.2f}")
            
            df_recursos = pd.DataFrame(recursos_data)
            st.dataframe(df_recursos, hide_index=True, use_container_width=True)

# ============================================
# ESTADO INICIAL (Sin optimización)
# ============================================

else:
    # Mostrar mensaje de bienvenida y guía
    st.markdown("""
    <div style="background-color: #e8f4f8; padding: 2rem; border-radius: 15px; text-align: center; margin: 2rem 0;">
        <h2 style="color: #1f77b4;">🎯 ¡Bienvenido al Dashboard de Optimización!</h2>
        <p style="font-size: 1.1rem; margin: 1rem 0;">
            Ajusta los parámetros en el panel izquierdo y presiona el botón para comenzar.
        </p>
        <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap; margin-top: 1.5rem;">
            <div style="background: white; padding: 1rem; border-radius: 10px; flex: 1; min-width: 150px;">
                <span style="font-size: 2rem;">💰</span>
                <p style="font-weight: bold;">Beneficios</p>
                <p style="font-size: 0.9rem; color: #666;">Ajusta precios unitarios</p>
            </div>
            <div style="background: white; padding: 1rem; border-radius: 10px; flex: 1; min-width: 150px;">
                <span style="font-size: 2rem;">🏭</span>
                <p style="font-weight: bold;">Recursos</p>
                <p style="font-size: 0.9rem; color: #666;">Modifica horas disponibles</p>
            </div>
            <div style="background: white; padding: 1rem; border-radius: 10px; flex: 1; min-width: 150px;">
                <span style="font-size: 2rem;">📦</span>
                <p style="font-weight: bold;">Capacidad</p>
                <p style="font-size: 0.9rem; color: #666;">Define límites de producción</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Mostrar información del problema
    with st.expander("ℹ️ Información del Problema de Optimización", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 📊 Datos del Problema
            
            **Variables:**
            - **x** = Unidades de Juguete A
            - **y** = Unidades de Juguete B
            
            **Función Objetivo:**
