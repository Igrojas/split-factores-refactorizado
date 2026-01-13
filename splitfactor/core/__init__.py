"""
Módulo core de splitfactor.

Contiene las clases y funciones principales para simulación.
"""

from .equipos import Flujo, Equipo, Celda, Suma, copiar_estado
from .io import (
    cargar_circuito_excel,
    cargar_multiples_simulaciones,
    identificar_flujos_globales,
    crear_circuito_desde_dict
)
from .simulador import Simulador, ConfiguracionMC, simular_escenarios

__all__ = [
    'Flujo', 'Equipo', 'Celda', 'Suma', 'copiar_estado',
    'cargar_circuito_excel', 'cargar_multiples_simulaciones',
    'identificar_flujos_globales', 'crear_circuito_desde_dict',
    'Simulador', 'ConfiguracionMC', 'simular_escenarios'
]
