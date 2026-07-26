"""
Módulo de optimización para el dashboard de juguetes
Contiene todas las funciones de cálculo y análisis
"""

import gurobipy as gp
from gurobipy import GRB
import pandas as pd
import numpy as np

def optimizar_produccion(
    beneficio_a=40,
    beneficio_b=30,
    horas_ensamblaje=100,
    horas_empaque=80,
    capacidad_maxima=None,
    demanda_minima_a=0,
    demanda_minima_b=0,
    demanda_maxima_a=float('inf'),
    demanda_maxima_b=float('inf'),
    entero=False
):
    """
    Función principal de optimización con Gurobi
    
    Parámetros:
    - beneficio_a, beneficio_b: Beneficios unitarios
    - horas_ensamblaje, horas_empaque: Recursos disponibles
    - capacidad_maxima: Límite de producción total (None = sin límite)
    - demanda_minima_a/b: Producción mínima requerida
    - demanda_maxima_a/b: Producción máxima permitida
    - entero: True para variables enteras, False para continuas
    
    Retorna:
    - Diccionario con resultados completos
    """
    
    # Crear modelo
    modelo = gp.Model("Juguetes_Dashboard")
    modelo.setParam('OutputFlag', 0)  # Silencioso
    
    # Variables
    vtype = GRB.INTEGER if entero else GRB.CONTINUOUS
    x = modelo.addVar(lb=demanda_minima_a, ub=demanda_maxima_a, 
                      name="Juguete_A", vtype=vtype)
    y = modelo.addVar(lb=demanda_minima_b, ub=demanda_maxima_b, 
                      name="Juguete_B", vtype=vtype)
    
    # Función objetivo
    modelo.setObjective(beneficio_a*x + beneficio_b*y, GRB.MAXIMIZE)
    
    # Restricciones de recursos
    modelo.addConstr(2*x + y <= horas_ensamblaje, name="Ensamblaje")
    modelo.addConstr(x + 1.5*y <= horas_empaque, name="Empaque")
    
    # Restricción de capacidad (opcional)
    if capacidad_maxima is not None:
        modelo.addConstr(x + y <= capacidad_maxima, name="Capacidad")
    
    # Optimizar
    modelo.optimize()
    
    # Extraer resultados
    if modelo.Status == GRB.OPTIMAL:
        resultados = {
            'status': 'Óptimo',
            'x': x.X,
            'y': y.X,
            'beneficio': modelo.ObjVal,
            'produccion_total': x.X + y.X,
            'uso_ensamblaje': 2*x.X + y.X,
            'uso_empaque': x.X + 1.5*y.X,
            'holgura_ensamblaje': horas_ensamblaje - (2*x.X + y.X),
            'holgura_empaque': horas_empaque - (x.X + 1.5*y.X),
        }
        
        # Precios sombra
        for c in modelo.getConstrs():
            resultados[f'precio_sombra_{c.ConstrName}'] = c.Pi
        
        # Rangos de optimalidad
        for v in modelo.getVars():
            resultados[f'rango_{v.VarName}_low'] = v.SAObjLow if hasattr(v, 'SAObjLow') else None
            resultados[f'rango_{v.VarName}_up'] = v.SAObjUp if hasattr(v, 'SAObjUp') else None
        
        # Rangos de factibilidad
        for c in modelo.getConstrs():
            if hasattr(c, 'SARHSLow'):
                resultados[f'factibilidad_{c.ConstrName}_low'] = c.SARHSLow
                resultados[f'factibilidad_{c.ConstrName}_up'] = c.SARHSUp
        
        return resultados
    else:
        return {'status': 'No factible o infactible'}

def generar_datos_analisis_sensibilidad(param_base, param_rango, paso=1):
    """
    Genera datos para análisis de sensibilidad variando un parámetro
    """
    resultados = []
    for valor in np.arange(param_rango[0], param_rango[1] + paso, paso):
        # Esta función se personaliza según el parámetro a variar
        pass
    return pd.DataFrame(resultados)

def calcular_metricas_clave(resultados):
    """
    Calcula métricas clave para el dashboard
    """
    if resultados['status'] != 'Óptimo':
        return {}
    
    metricas = {
        'Beneficio total': f"${resultados['beneficio']:,.2f}",
        'Producción total': f"{resultados['produccion_total']:.0f} unidades",
        'Juguete A': f"{resultados['x']:.0f} unidades",
        'Juguete B': f"{resultados['y']:.0f} unidades",
        'Uso de ensamblaje': f"{resultados['uso_ensamblaje']:.1f}%",
        'Uso de empaque': f"{resultados['uso_empaque']:.1f}%",
        'Precio sombra ensamblaje': f"${resultados.get('precio_sombra_Ensamblaje', 0):.2f}",
        'Precio sombra empaque': f"${resultados.get('precio_sombra_Empaque', 0):.2f}",
    }
    
    if 'precio_sombra_Capacidad' in resultados:
        metricas['Precio sombra capacidad'] = f"${resultados['precio_sombra_Capacidad']:.2f}"
    
    return metricas