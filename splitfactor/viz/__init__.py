"""
Módulo de visualización de splitfactor.
"""

from .graficas import (
    configurar_estilo,
    graficar_recuperacion_ley,
    graficar_splits,
    graficar_con_test_dilucion,
    graficar_top_n,
    crear_figura_resumen,
    guardar_figura,
    COLORES_DEFAULT,
    MARCADORES_DEFAULT,
    COLORES_TOP10
)

__all__ = [
    'configurar_estilo',
    'graficar_recuperacion_ley',
    'graficar_splits',
    'graficar_con_test_dilucion',
    'graficar_top_n',
    'crear_figura_resumen',
    'guardar_figura',
    'COLORES_DEFAULT',
    'MARCADORES_DEFAULT',
    'COLORES_TOP10'
]
