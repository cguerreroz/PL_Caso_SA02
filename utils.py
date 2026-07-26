"""
Módulo de optimización para el dashboard de juguetes
Usa scipy.optimize.linprog (no requiere licencia)
"""

import numpy as np
from scipy.optimize import linprog
import pandas as pd

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
    Función principal de optimización con scipy.optimize.linprog
    """
    
    # Coeficientes de la función objetivo (negativos para maximizar)
    c = [-beneficio_a, -beneficio_b]
    
    # Matriz de restricciones de desigualdad (<=)
    A_ub = [
        [2, 1],  # Ensamblaje
        [1, 1.5] # Empaque
    ]
    b_ub = [horas_ensamblaje, horas_empaque]
    
    # Añadir restricción de capacidad si existe
    if capacidad_maxima is not None and capacidad_maxima > 0:
        A_ub.append([1, 1])
        b_ub.append(capacidad_maxima)
    
    # Límites de las variables
    bounds = [
        (demanda_minima_a, demanda_maxima_a if demanda_maxima_a != float('inf') else None),
        (demanda_minima_b, demanda_maxima_b if demanda_maxima_b != float('inf') else None)
    ]
    
    try:
        result = linprog(
            c,
            A_ub=A_ub,
            b_ub=b_ub,
            bounds=bounds,
            method='highs'
        )
        
        if result.success:
            x = result.x[0]
            y = result.x[1]
            
            # Si se requiere variables enteras
            if entero:
                x = round(x)
                y = round(y)
                # Verificar factibilidad
                if 2*x + y <= horas_ensamblaje and x + 1.5*y <= horas_empaque:
                    if capacidad_maxima is None or x + y <= capacidad_maxima:
                        pass
                    else:
                        while x + y > capacidad_maxima:
                            if beneficio_a >= beneficio_b:
                                x -= 1
                            else:
                                y -= 1
            
            # Calcular precios sombra (aproximados)
            precio_sombra_ens = 0
            precio_sombra_emp = 0
            precio_sombra_cap = 0
            
            # Solo calcular si la restricción está activa
            if abs(2*x + y - horas_ensamblaje) < 0.1:
                test_result = linprog(
                    c,
                    A_ub=A_ub,
                    b_ub=[horas_ensamblaje+1, horas_empaque] + ([capacidad_maxima] if capacidad_maxima else []),
                    bounds=bounds,
                    method='highs'
                )
                if test_result.success:
                    precio_sombra_ens = -test_result.fun + result.fun
            
            if abs(x + 1.5*y - horas_empaque) < 0.1:
                test_result = linprog(
                    c,
                    A_ub=A_ub,
                    b_ub=[horas_ensamblaje, horas_empaque+1] + ([capacidad_maxima] if capacidad_maxima else []),
                    bounds=bounds,
                    method='highs'
                )
                if test_result.success:
                    precio_sombra_emp = -test_result.fun + result.fun
            
            if capacidad_maxima and abs(x + y - capacidad_maxima) < 0.1:
                test_result = linprog(
                    c,
                    A_ub=A_ub,
                    b_ub=[horas_ensamblaje, horas_empaque, capacidad_maxima+1],
                    bounds=bounds,
                    method='highs'
                )
                if test_result.success:
                    precio_sombra_cap = -test_result.fun + result.fun
            
            resultados = {
                'status': 'Óptimo',
                'x': float(x),
                'y': float(y),
                'beneficio': -result.fun,
                'produccion_total': float(x + y),
                'uso_ensamblaje': 2*x + y,
                'uso_empaque': x + 1.5*y,
                'holgura_ensamblaje': horas_ensamblaje - (2*x + y),
                'holgura_empaque': horas_empaque - (x + 1.5*y),
                'precio_sombra_Ensamblaje': precio_sombra_ens,
                'precio_sombra_Empaque': precio_sombra_emp,
            }
            
            if capacidad_maxima is not None:
                resultados['precio_sombra_Capacidad'] = precio_sombra_cap
                resultados['holgura_capacidad'] = capacidad_maxima - (x + y)
            
            return resultados
        else:
            return {'status': f'No factible: {result.message}'}
    
    except Exception as e:
        return {'status': f'Error: {str(e)}'}

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
    }
    
    horas_ensamblaje = resultados['uso_ensamblaje'] + resultados['holgura_ensamblaje']
    horas_empaque = resultados['uso_empaque'] + resultados['holgura_empaque']
    
    if horas_ensamblaje > 0:
        metricas['Uso de ensamblaje'] = f"{(resultados['uso_ensamblaje']/horas_ensamblaje*100):.1f}%"
    else:
        metricas['Uso de ensamblaje'] = "0%"
    
    if horas_empaque > 0:
        metricas['Uso de empaque'] = f"{(resultados['uso_empaque']/horas_empaque*100):.1f}%"
    else:
        metricas['Uso de empaque'] = "0%"
    
    metricas['Precio sombra ensamblaje'] = f"${resultados.get('precio_sombra_Ensamblaje', 0):.2f}"
    metricas['Precio sombra empaque'] = f"${resultados.get('precio_sombra_Empaque', 0):.2f}"
    
    if 'precio_sombra_Capacidad' in resultados:
        metricas['Precio sombra capacidad'] = f"${resultados['precio_sombra_Capacidad']:.2f}"
    
    return metricas
