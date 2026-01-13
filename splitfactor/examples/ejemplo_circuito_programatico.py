"""
Ejemplo 3: Definir circuito programáticamente.

Este ejemplo muestra cómo crear circuitos sin usar Excel,
útil para:
- Probar rápidamente diferentes topologías
- Automatizar generación de circuitos
- Integrar con otros sistemas
"""

import sys
sys.path.insert(0, '..')

from splitfactor.core import (
    Flujo, Celda, Suma, Simulador,
    crear_circuito_desde_dict
)


def ejemplo_circuito_manual():
    """
    Crea un circuito manualmente usando las clases.
    
    Circuito: Jameson -> (conc) + (relave -> Scavenger)
    """
    
    print("Creando circuito manualmente...")
    
    # === Crear flujos ===
    flujos = {
        1: Flujo(id=1, nombre='Alimentación'),
        2: Flujo(id=2, nombre='Conc Jameson'),
        3: Flujo(id=3, nombre='Rel Jameson'),
        4: Flujo(id=4, nombre='Conc Scavenger'),
        5: Flujo(id=5, nombre='Rel Scavenger'),
    }
    
    # === Crear equipos ===
    jameson = Celda(nombre='Jameson 1')
    jameson.flujos_entrada = [1]
    jameson.flujos_salida = [2, 3]  # [concentrado, relave]
    jameson.split_factor = [0.10, 0.75]  # 10% masa, 75% Cu al conc
    
    scavenger = Celda(nombre='Scavenger')
    scavenger.flujos_entrada = [3]  # relave de Jameson
    scavenger.flujos_salida = [4, 5]
    scavenger.split_factor = [0.30, 0.90]
    
    equipos = {
        'Jameson 1': jameson,
        'Scavenger': scavenger
    }
    
    # === Configurar simulador ===
    sim = Simulador(
        equipos, flujos,
        flujos_relave={5}  # Flujo 5 es relave final
    )
    
    # Alimentación
    sim.establecer_alimentacion(1, masa=100, ley=1.5)
    
    # === Ejecutar ===
    print("Ejecutando simulación...")
    resultado = sim.simular()
    
    # === Resultados ===
    print("\n" + "="*50)
    print("RESULTADOS")
    print("="*50)
    print(f"Recuperación: {resultado['recuperacion']:.2f}%")
    print(f"Mass Pull: {resultado['mass_pull']:.2f}%")
    print(f"Ley Concentrado: {resultado['ley_concentrado']:.2f}%")
    
    print("\nFlujos:")
    for id_f, f in flujos.items():
        print(f"  {id_f} ({f.nombre}): {f.masa:.2f} t, {f.ley:.2f}%")
    
    return resultado


def ejemplo_circuito_dict():
    """
    Crea circuito desde diccionario de configuración.
    
    Más limpio para circuitos complejos.
    """
    
    print("\nCreando circuito desde diccionario...")
    
    # === Definición del circuito ===
    config = {
        'equipos': [
            {
                'nombre': 'Jameson 1',
                'tipo': 'celda',
                'entrada': [1],
                'salida': [2, 3],
                'split_factor': [0.08, 0.70]
            },
            {
                'nombre': 'Mezclador',
                'tipo': 'suma',
                'entrada': [3, 6],  # Relave Jameson + Rec Scavenger
                'salida': [4],
                'split_factor': [0, 0]
            },
            {
                'nombre': 'Scavenger',
                'tipo': 'celda',
                'entrada': [4],
                'salida': [5, 6],  # Conc (sale) + Rel (recircula)
                'split_factor': [0.25, 0.92]
            }
        ]
    }
    
    # === Crear circuito ===
    equipos, flujos = crear_circuito_desde_dict(config)
    
    print(f"Equipos: {list(equipos.keys())}")
    print(f"Flujos: {list(flujos.keys())}")
    
    # === Simular ===
    sim = Simulador(equipos, flujos, flujos_relave={6})
    sim.establecer_alimentacion(1, masa=50, ley=2.0)
    
    resultado = sim.simular()
    
    print(f"\nRecuperación: {resultado['recuperacion']:.2f}%")
    print(f"Ley Conc: {resultado['ley_concentrado']:.2f}%")
    
    return resultado


def ejemplo_variacion_topologia():
    """
    Compara diferentes configuraciones de circuito.
    """
    
    print("\nComparando topologías...")
    
    resultados = []
    
    # Config 1: Sin recirculación
    config1 = {
        'equipos': [
            {'nombre': 'Celda 1', 'tipo': 'celda', 'entrada': [1], 'salida': [2, 3],
             'split_factor': [0.15, 0.80]}
        ]
    }
    
    # Config 2: Con scavenger
    config2 = {
        'equipos': [
            {'nombre': 'Celda 1', 'tipo': 'celda', 'entrada': [1], 'salida': [2, 3],
             'split_factor': [0.15, 0.80]},
            {'nombre': 'Scavenger', 'tipo': 'celda', 'entrada': [3], 'salida': [4, 5],
             'split_factor': [0.30, 0.90]}
        ]
    }
    
    # Config 3: Con recirculación
    config3 = {
        'equipos': [
            {'nombre': 'Celda 1', 'tipo': 'celda', 'entrada': [1], 'salida': [2, 3],
             'split_factor': [0.15, 0.80]},
            {'nombre': 'Mezclador', 'tipo': 'suma', 'entrada': [3, 6], 'salida': [4],
             'split_factor': [0, 0]},
            {'nombre': 'Scavenger', 'tipo': 'celda', 'entrada': [4], 'salida': [5, 6],
             'split_factor': [0.30, 0.90]}
        ]
    }
    
    configs = [
        ('Sin Scavenger', config1, {3}),
        ('Con Scavenger', config2, {5}),
        ('Con Recirculación', config3, {6})
    ]
    
    for nombre, config, relaves in configs:
        equipos, flujos = crear_circuito_desde_dict(config)
        sim = Simulador(equipos, flujos, flujos_relave=relaves)
        sim.establecer_alimentacion(1, masa=100, ley=1.5)
        
        res = sim.simular()
        resultados.append({
            'config': nombre,
            'recuperacion': res['recuperacion'],
            'ley_conc': res['ley_concentrado'],
            'mass_pull': res['mass_pull']
        })
    
    print("\n" + "="*60)
    print("COMPARACIÓN DE TOPOLOGÍAS")
    print("="*60)
    print(f"{'Configuración':<25} {'Rec %':<10} {'Ley %':<10} {'MP %':<10}")
    print("-"*55)
    for r in resultados:
        print(f"{r['config']:<25} {r['recuperacion']:<10.2f} {r['ley_conc']:<10.2f} {r['mass_pull']:<10.2f}")
    
    return resultados


if __name__ == '__main__':
    print("="*60)
    print("EJEMPLO: Circuito Manual")
    print("="*60)
    ejemplo_circuito_manual()
    
    print("\n" + "="*60)
    print("EJEMPLO: Circuito desde Dict")
    print("="*60)
    ejemplo_circuito_dict()
    
    print("\n" + "="*60)
    print("EJEMPLO: Comparación de Topologías")
    print("="*60)
    ejemplo_variacion_topologia()
