"""
splitfactor - Simulación de circuitos de flotación por Split Factor.

Módulos:
    core: Clases y simulador
    viz: Visualización
    examples: Ejemplos de uso

Uso básico:
    from splitfactor.core import Simulador, cargar_circuito_excel
    from splitfactor.viz import graficar_recuperacion_ley
    
    equipos, flujos = cargar_circuito_excel('circuito.xlsx')
    sim = Simulador(equipos, flujos)
    sim.establecer_alimentacion(4, masa=23.84, ley=2.5167)
    resultado = sim.simular()
"""

__version__ = '0.1.0'
