"""
Ejemplo 2: Simulación Monte Carlo.

Este ejemplo muestra cómo:
1. Configurar una simulación Monte Carlo
2. Definir rangos de split factors
3. Ejecutar la simulación
4. Analizar y visualizar resultados
"""

import sys
sys.path.insert(0, '..')

import pandas as pd
from splitfactor.core import (
    cargar_circuito_excel,
    Simulador,
    ConfiguracionMC
)
from splitfactor.viz import (
    configurar_estilo,
    graficar_recuperacion_ley,
    graficar_splits,
    graficar_top_n,
    crear_figura_resumen
)
import matplotlib.pyplot as plt


def ejemplo_montecarlo():
    """Ejecuta simulación Monte Carlo básica."""
    
    # === Configuración ===
    archivo = '../data/Simulacion_caso_base.xlsx'
    hoja = 'Sim MC Dia'
    
    alimentacion = {
        4: {'masa': 23.84, 'ley': 2.5167}
    }
    flujos_relave = {9}
    
    # === Cargar circuito base ===
    print("Cargando circuito...")
    equipos, flujos = cargar_circuito_excel(archivo, hoja, id_simulacion=1)
    
    # === Configurar Monte Carlo ===
    config_mc = ConfiguracionMC(
        equipos_objetivo=['Jameson 1'],
        rangos={
            'Jameson 1': {
                'masa': (0.02, 0.70),  # Rango para split de masa
                'cuf': (0.02, 0.90)    # Rango para split de Cu fino
            }
        },
        n_iteraciones=10_000,  # Reducido para ejemplo rápido
        ley_min=10,            # Filtrar ley < 10%
        ley_max=30             # Filtrar ley > 30%
    )
    
    print(f"\nConfiguración MC:")
    print(f"  Equipos a variar: {config_mc.equipos_objetivo}")
    print(f"  Iteraciones: {config_mc.n_iteraciones:,}")
    print(f"  Filtro ley: [{config_mc.ley_min}, {config_mc.ley_max}]")
    
    # === Crear simulador ===
    sim = Simulador(equipos, flujos, flujos_relave)
    
    # === Ejecutar Monte Carlo ===
    print("\nEjecutando Monte Carlo...")
    df_mc = sim.simular_montecarlo(config_mc, alimentacion)
    
    print(f"\nIteraciones válidas: {len(df_mc):,}")
    
    # === Estadísticas ===
    print("\n" + "="*50)
    print("ESTADÍSTICAS")
    print("="*50)
    
    for col in ['recuperacion', 'ley_concentrado', 'razon_enriquecimiento']:
        print(f"\n{col}:")
        print(f"  Media: {df_mc[col].mean():.2f}")
        print(f"  Std:   {df_mc[col].std():.2f}")
        print(f"  Min:   {df_mc[col].min():.2f}")
        print(f"  Max:   {df_mc[col].max():.2f}")
    
    # === Visualización ===
    configurar_estilo()
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # 1. Recuperación vs Ley
    graficar_recuperacion_ley(df_mc, ax=axes[0])
    
    # 2. Split factors
    graficar_splits(
        df_mc, 'Jameson 1',
        color_por='razon_enriquecimiento',
        ax=axes[1]
    )
    
    # 3. Top 10 por razón de enriquecimiento
    graficar_top_n(
        df_mc, n=10,
        criterio='razon_enriquecimiento',
        ax=axes[2]
    )
    
    plt.tight_layout()
    plt.savefig('../results/montecarlo_ejemplo.png', dpi=150)
    print("\nGráfica guardada en: ../results/montecarlo_ejemplo.png")
    plt.show()
    
    return df_mc


def ejemplo_mc_multiples_equipos():
    """Monte Carlo variando múltiples equipos."""
    
    archivo = '../data/Simulacion_caso_base.xlsx'
    hoja = 'Sim MC Dia'
    alimentacion = {4: {'masa': 23.84, 'ley': 2.5167}}
    flujos_relave = {9}
    
    equipos, flujos = cargar_circuito_excel(archivo, hoja, id_simulacion=1)
    
    # Configuración con múltiples equipos
    config_mc = ConfiguracionMC(
        equipos_objetivo=['Jameson 1', 'Scavenger'],
        rangos={
            'Jameson 1': {'masa': (0.05, 0.50), 'cuf': (0.50, 0.90)},
            'Scavenger': {'masa': (0.20, 0.40), 'cuf': (0.80, 0.98)}
        },
        n_iteraciones=5_000,
        ley_min=12,
        ley_max=28
    )
    
    sim = Simulador(equipos, flujos, flujos_relave)
    
    print("Ejecutando MC con múltiples equipos...")
    df_mc = sim.simular_montecarlo(config_mc, alimentacion)
    
    print(f"Iteraciones válidas: {len(df_mc):,}")
    print("\nColumnas de split factors:")
    cols_split = [c for c in df_mc.columns if '_sp_' in c]
    print(cols_split)
    
    return df_mc


def guardar_resultados(df: pd.DataFrame, nombre: str = 'resultados_mc.xlsx'):
    """Guarda resultados en Excel."""
    import os
    os.makedirs('../results', exist_ok=True)
    ruta = f'../results/{nombre}'
    df.to_excel(ruta, index=False)
    print(f"Resultados guardados en: {ruta}")


if __name__ == '__main__':
    print("="*60)
    print("EJEMPLO: Monte Carlo Básico")
    print("="*60)
    df = ejemplo_montecarlo()
    
    guardar_resultados(df)

