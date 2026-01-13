"""
Ejemplo 1: Simulación simple desde Excel.

Este ejemplo muestra cómo:
1. Cargar un circuito desde Excel
2. Establecer condiciones de alimentación
3. Ejecutar simulación
4. Visualizar resultados
"""

import sys
sys.path.insert(0, '..')  # Para ejecutar desde /examples

from splitfactor.core import (
    cargar_circuito_excel,
    Simulador,
    simular_escenarios
)


def ejemplo_simulacion_simple():
    """Ejecuta una simulación simple."""
    
    # === Configuración ===
    archivo = '../data/Simulacion_caso_base.xlsx'
    hoja = 'Sim Dia'
    
    # Alimentación al circuito
    alimentacion = {
        4: {'masa': 23.84, 'ley': 2.5167}  # Flujo 4: alimentación 1ra Limpieza
    }
    
    # Flujos de relave final (para cálculo de recuperación)
    flujos_relave = {9}
    
    # === Cargar circuito ===
    print("Cargando circuito...")
    equipos, flujos = cargar_circuito_excel(archivo, hoja, id_simulacion=1)
    
    print(f"\nEquipos cargados: {list(equipos.keys())}")
    print(f"Flujos: {list(flujos.keys())}")
    
    # === Crear simulador ===
    sim = Simulador(equipos, flujos, flujos_relave)
    
    # Establecer alimentación
    for id_flujo, valores in alimentacion.items():
        sim.establecer_alimentacion(id_flujo, valores['masa'], valores['ley'])
    
    # === Ejecutar simulación ===
    print("\nEjecutando simulación...")
    resultado = sim.simular()
    
    # === Mostrar resultados ===
    print("\n" + "="*50)
    print("RESULTADOS")
    print("="*50)
    print(f"Recuperación:           {resultado['recuperacion']:.2f}%")
    print(f"Mass Pull:              {resultado['mass_pull']:.2f}%")
    print(f"Ley de Concentrado:     {resultado['ley_concentrado']:.2f}%")
    print(f"Razón Enriquecimiento:  {resultado['razon_enriquecimiento']:.2f}")
    print(f"Error Masa:             {resultado['error_masa']:.6f}")
    print(f"Error CuF:              {resultado['error_cuf']:.6f}")
    
    print("\nFlujos individuales:")
    for id_f, vals in resultado['flujos'].items():
        print(f"  Flujo {id_f}: masa={vals['masa']:.4f}, ley={vals['ley']:.4f}%")
    
    return resultado


def ejemplo_multiples_escenarios():
    """Simula todos los escenarios de una hoja."""
    
    archivo = '../data/Simulacion_caso_base.xlsx'
    hoja = 'Sim Dia'
    alimentacion = {4: {'masa': 23.84, 'ley': 2.5167}}
    flujos_relave = {9}
    
    print("Simulando múltiples escenarios...")
    df = simular_escenarios(archivo, hoja, alimentacion, flujos_relave)
    
    print("\nResultados por escenario:")
    print(df.to_string(index=False))
    
    return df


if __name__ == '__main__':
    print("="*60)
    print("EJEMPLO 1: Simulación Simple")
    print("="*60)
    ejemplo_simulacion_simple()
    
    print("\n" + "="*60)
    print("EJEMPLO 2: Múltiples Escenarios")
    print("="*60)
    ejemplo_multiples_escenarios()
