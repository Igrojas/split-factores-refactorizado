#%%
"""
Script de simulación con split factors.
Ejecuta simulación base y análisis Monte Carlo.
"""

# ============================================================================
# IMPORTS
# ============================================================================
import importlib
import sys
import pandas as pd
import matplotlib.pyplot as plt

# ============================================================================
# FUNCIÓN PARA RECARGAR MÓDULOS (ejecutar siempre antes de usar splitfactor)
# ============================================================================
def recargar_splitfactor(verbose: bool = True):
    """
    Recarga todos los módulos de splitfactor para aplicar cambios en desarrollo.
    Debe ejecutarse cada vez que se modifique código en splitfactor.
    
    Args:
        verbose: Si True, imprime mensajes de recarga
    """
    # Importar módulos primero si no están cargados
    try:
        import splitfactor.core.equipos
        import splitfactor.core.io
        import splitfactor.core.simulador
        import splitfactor.viz.graficas
        import splitfactor.core
        import splitfactor.viz
    except ImportError:
        pass  # Si no están instalados, continuar
    
    # Lista de submódulos a recargar (en orden inverso de dependencias)
    # Primero los submódulos, luego los módulos padre
    modulos_a_recargar = [
        'splitfactor.core.equipos',
        'splitfactor.core.io',
        'splitfactor.core.simulador',
        'splitfactor.viz.graficas',
        'splitfactor.core',
        'splitfactor.viz',
        'splitfactor',  # Módulo raíz
    ]
    
    # Recargar cada módulo si existe (en orden inverso para evitar dependencias)
    recargados = []
    for modulo_nombre in modulos_a_recargar:
        if modulo_nombre in sys.modules:
            try:
                importlib.reload(sys.modules[modulo_nombre])
                recargados.append(modulo_nombre)
                if verbose:
                    print(f"✓ Recargado: {modulo_nombre}")
            except Exception as e:
                if verbose:
                    print(f"⚠ Error al recargar {modulo_nombre}: {e}")
    
    if verbose and recargados:
        print(f"✓ Total de módulos recargados: {len(recargados)}")


# Recargar módulos de splitfactor para ver cambios en desarrollo
recargar_splitfactor()

# Importar funciones y clases después del reload
from splitfactor.core import (
    cargar_circuito_excel,
    Simulador,
    ConfiguracionMC
)
from splitfactor.viz import (
    graficar_recuperacion_ley,
    graficar_splits,
    graficar_top_n
)

# ============================================================================
# RECARGAR MÓDULOS - Ejecutar esta celda después de modificar código en splitfactor
# ============================================================================
# Si modificaste código en splitfactor/core o splitfactor/viz, ejecuta esta celda
# para recargar los módulos y aplicar los cambios sin reiniciar el kernel
recargar_splitfactor()

# Reimportar después del reload
from splitfactor.core import (
    cargar_circuito_excel,
    Simulador,
    ConfiguracionMC
)
from splitfactor.viz import (
    graficar_recuperacion_ley,
    graficar_splits,
    graficar_top_n
)

print("✓ Módulos recargados y reimportados correctamente")


# ============================================================================
# CONFIGURACIÓN - MODIFICAR AQUÍ LOS VALORES
# ============================================================================
# Archivos de entrada
CONFIG = {
    'archivo_circuito': "data/caso 3/simulacion_caso_3.xlsx",
    'hoja_circuito': "Sim Promedio",
    'id_simulacion': 1,
    'archivo_split_factors': "data/caso 3/sf_caso_3.xlsx",
    'hoja_split_factors': None,  # None = primera hoja
    
    # Configuración de simulación base
    'flujos_relave': {9},
    'alimentacion': {
        'id_flujo': 4,
        'masa': 22.84,
        'ley': 2.16
    },
    
    # Configuración Monte Carlo
    'montecarlo': {
        'equipos_objetivo': ['Jameson 1'],
        'rangos': {
            'Jameson 1': {
                'masa': (0.01, 0.4),
                'cuf': (0.5, 0.95)
            }

        },
        'n_iteraciones': 10_000,
        'ley_min': 2,
        'ley_max': 35
    },
    
    # Filtrado de resultados
    'filtros': {
        'equipo_analisis': 'Jameson 1',  # Equipo para calcular ER
        'er_min': 2.5,  # Razón de enriquecimiento mínima
        'er_max': 6  # Razón de enriquecimiento máxima
    },
    
    # Visualizaciones
    'graficas': {
        'figsize_doble': (12, 5),
        'figsize_simple': (10, 6),
        'dpi': 150,
        'archivo_resultados': 'resultados.png',
        'archivo_top10': 'top10.png',
        'titulo_recuperacion_ley': 'Recuperación vs Ley de Concentrado',
        'top_n': 15,
        'criterio_top_n': 'razon_enriquecimiento',
        'columnas_top10': [
            'recuperacion',
            'ley_concentrado',
            'razon_enriquecimiento',
            'Jameson 1_sp_masa',
            'Jameson 1_sp_cuf'
        ]
    },
    
    # Opciones de ejecución
    'mostrar_resultados': True,
    'mostrar_graficas': True,
    'guardar_graficas': True
}


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================
def actualizar_split_factors(equipos: dict, archivo_sf: str, hoja: str = None) -> None:
    """
    Actualiza los split factors de los equipos desde un Excel.
    
    Args:
        equipos: Diccionario de equipos del circuito
        archivo_sf: Ruta al Excel con split factors
        hoja: Nombre de la hoja (opcional)
    """
    if hoja:
        df = pd.read_excel(archivo_sf, sheet_name=hoja)
    else:
        df = pd.read_excel(archivo_sf)
    
    actualizados = []
    for _, row in df.iterrows():
        nombre = row['Equipo']
        if nombre in equipos:
            equipos[nombre].split_factor = [row['sp_masa'], row['sp_cuf']]
            actualizados.append(nombre)
    
    if CONFIG['mostrar_resultados']:
        print(f"Split factors actualizados: {actualizados}")


# ============================================================================
# CARGA Y CONFIGURACIÓN INICIAL
# ============================================================================
if CONFIG['mostrar_resultados']:
    print("Módulos importados correctamente")

# Cargar circuito
equipos, flujos = cargar_circuito_excel(
    archivo=CONFIG['archivo_circuito'],
    hoja=CONFIG['hoja_circuito'],
    id_simulacion=CONFIG['id_simulacion']
)

# Actualizar split factors
actualizar_split_factors(
    equipos,
    CONFIG['archivo_split_factors'],
    CONFIG['hoja_split_factors']
)

# Verificar qué se cargó
if CONFIG['mostrar_resultados']:
    print("\nEquipos cargados:")
    for nombre, equipo in equipos.items():
        print(f"  {nombre}: split_factor = {equipo.split_factor}")
    print(f"\nFlujos: {list(flujos.keys())}")


# ============================================================================
# SIMULACIÓN BASE
# ============================================================================
sim = Simulador(
    equipos=equipos,
    flujos=flujos,
    flujos_relave=CONFIG['flujos_relave']
)

sim.establecer_alimentacion(
    id_flujo=CONFIG['alimentacion']['id_flujo'],
    masa=CONFIG['alimentacion']['masa'],
    ley=CONFIG['alimentacion']['ley']
)

resultado = sim.simular()

if CONFIG['mostrar_resultados']:
    print("\n" + "="*50)
    print("Resultado de la simulación:")
    print("="*50)
    print(f"Recuperación: {resultado['recuperacion']:.2f} %")
    print(f"Mass Pull: {resultado['mass_pull']:.2f} %")
    print(f"Ley de Concentrado: {resultado['ley_concentrado']:.2f} %")
    print(f"Razón Enriquecimiento: {resultado['razon_enriquecimiento']:.2f}")
    print(f"Error Masa: {resultado['error_masa']:.6f}")
    print(f"Error CuF: {resultado['error_cuf']:.6f}")


# ============================================================================
# SIMULACIÓN MONTE CARLO
# ============================================================================
config_mc = ConfiguracionMC(
    equipos_objetivo=CONFIG['montecarlo']['equipos_objetivo'],
    rangos=CONFIG['montecarlo']['rangos'],
    n_iteraciones=CONFIG['montecarlo']['n_iteraciones'],
    ley_min=CONFIG['montecarlo']['ley_min'],
    ley_max=CONFIG['montecarlo']['ley_max']
)

# Ejecutar Monte Carlo
df_mc = sim.simular_montecarlo(
    config=config_mc,
    alimentacion={
        CONFIG['alimentacion']['id_flujo']: {
            'masa': CONFIG['alimentacion']['masa'],
            'ley': CONFIG['alimentacion']['ley']
        }
    }
)

if CONFIG['mostrar_resultados']:
    print("\n" + "="*50)
    print("Resultados Monte Carlo:")
    print("="*50)
    print(f"Iteraciones válidas: {len(df_mc)}")
    print(f"Recuperación promedio: {df_mc['recuperacion'].mean():.2f} %")
    print(f"Ley promedio: {df_mc['ley_concentrado'].mean():.2f} %")


# ============================================================================
# ANÁLISIS Y FILTRADO
# ============================================================================
equipo_analisis = CONFIG['filtros']['equipo_analisis']
columna_er = f"er_{equipo_analisis.lower().replace(' ', '_')}"

df_mc[columna_er] = (
    df_mc[f"{equipo_analisis}_sp_cuf"] / 
    df_mc[f"{equipo_analisis}_sp_masa"]
)

df_mc = df_mc[
    (df_mc[columna_er] >= CONFIG['filtros']['er_min']) & 
    (df_mc[columna_er] < CONFIG['filtros']['er_max'])
]
# Filtrar todas las columnas que tengan nombre 'flujos_n_ley' para eliminar filas con valores > 26
import re

cols_ley = [col for col in df_mc.columns if re.fullmatch(r'flujos_\d+_ley', col)]
if cols_ley:
    mask = (df_mc[cols_ley] <= 35).all(axis=1)
    df_mc = df_mc[mask]

if CONFIG['mostrar_resultados']:
    print(f"\nIteraciones después del filtro ER: {len(df_mc)}")



# ============================================================================
# VISUALIZACIONES
# ============================================================================
# Gráfico 1a: Split factors, rango conocido
split_rango_conocido = [0.7, 0.75]
split_rango_optimista = [0.9, 0.95]
split_col = 'Jameson 1_sp_cuf'

if CONFIG['mostrar_graficas']:
    fig, axes = plt.subplots(2, 2, figsize=(2 * CONFIG['graficas']['figsize_simple'][0], 2 * CONFIG['graficas']['figsize_simple'][1]))

    # RANGO CONOCIDO (col 0)
    # Fila 0: Splits - conocido
    graficar_splits(
        df=df_mc,
        equipo=equipo_analisis,
        color_por=columna_er,
        split_rango=split_rango_conocido,
        split_col=split_col,
        ax=axes[0, 0]
    )
    axes[0, 0].set_title("Splits (Rango conocido)")
    # Fila 1: Recuperación vs Ley - conocido
    graficar_recuperacion_ley(
        df=df_mc,
        titulo=CONFIG['graficas']['titulo_recuperacion_ley'] + " (Rango conocido)",
        color_por=columna_er,
        split_rango=split_rango_conocido,
        split_col=split_col,
        ax=axes[1, 0]
    )
    axes[1, 0].set_title("Recuperación vs Ley (Rango conocido)")

    # RANGO OPTIMISTA (col 1)
    # Fila 0: Splits - optimista
    graficar_splits(
        df=df_mc,
        equipo=equipo_analisis,
        color_por=columna_er,
        split_rango=split_rango_optimista,
        split_col=split_col,
        ax=axes[0, 1]
    )
    axes[0, 1].set_title("Splits (Rango optimista)")
    # Fila 1: Recuperación vs Ley - optimista
    graficar_recuperacion_ley(
        df=df_mc,
        titulo=CONFIG['graficas']['titulo_recuperacion_ley'] + " (Rango optimista)",
        color_por=columna_er,
        split_rango=split_rango_optimista,
        split_col=split_col,
        ax=axes[1, 1]
    )
    axes[1, 1].set_title("Recuperación vs Ley (Rango optimista)")

    plt.tight_layout()
    if CONFIG['guardar_graficas']:
        plt.savefig(CONFIG['graficas']['archivo_resultados'].replace('.png', '_split_recuperacion_conocido_vs_optimista.png'),
                    dpi=CONFIG['graficas']['dpi'])
    plt.show()



    # Gráfica 2: Top N

    fig, ax = plt.subplots(figsize=CONFIG['graficas']['figsize_simple'])
    
    ax, df_top10 = graficar_top_n(
        df=df_mc,
        n=CONFIG['graficas']['top_n'],
        criterio=CONFIG['graficas']['criterio_top_n'],
        split_rango=split_rango_conocido,
        split_col=split_col,
        ax=ax
    )
    
    plt.tight_layout()
    if CONFIG['guardar_graficas']:
        plt.savefig(CONFIG['graficas']['archivo_top10'].replace('.png', '_conocido.png'), 
                   dpi=CONFIG['graficas']['dpi'])
    plt.show()

    # Gráfica 3: Top N - optimista
    fig, ax = plt.subplots(figsize=CONFIG['graficas']['figsize_simple'])
    
    ax, df_top10 = graficar_top_n(
        df=df_mc,
        n=CONFIG['graficas']['top_n'],
        criterio=CONFIG['graficas']['criterio_top_n'],
        split_rango=split_rango_optimista,
        split_col=split_col,
        ax=ax
    )
    
    plt.tight_layout()
    if CONFIG['guardar_graficas']:
        plt.savefig(CONFIG['graficas']['archivo_top10'].replace('.png', '_optimista.png'), 
                   dpi=CONFIG['graficas']['dpi'])
    plt.show()
    


#%%
    # Ver los datos del top N
    if CONFIG['mostrar_resultados']:
        print("\n" + "="*50)
        print(f"Top {CONFIG['graficas']['top_n']} simulaciones:")
        print("="*50)
        columnas = CONFIG['graficas']['columnas_top10']
        # Ajustar nombres de columnas según el equipo de análisis
        columnas_ajustadas = [
            col.replace('Jameson 1', equipo_analisis) 
            if 'Jameson 1' in col else col 
            for col in columnas
        ]
        # Guardar dos tablas (top N para rango conocido y optimista) en un solo archivo Excel, en hojas separadas

        df_mc_optimista = df_mc[(df_mc[split_col] >= split_rango_optimista[0]) & (df_mc[split_col] <= split_rango_optimista[1])]
        df_mc_conocido = df_mc[(df_mc[split_col] >= split_rango_conocido[0]) & (df_mc[split_col] <= split_rango_conocido[1])]


#%%
        # Ordena por 'ley_confinal' descendente para ambos top N
        df_top10_optimista = df_mc_optimista.sort_values('ley_concentrado', ascending=False).head(CONFIG['graficas']['top_n']).copy()
        df_top10_conocido = df_mc_conocido.sort_values('ley_concentrado', ascending=False).head(CONFIG['graficas']['top_n']).copy()

        # Guardar ambas en un solo Excel por hojas separadas
        excel_outfile = 'data/caso 3/topN_simulaciones_caso_3.xlsx'
        with pd.ExcelWriter(excel_outfile) as writer:
            df_top10_conocido.to_excel(writer, sheet_name='TopN_Conocido', index=False)
            df_top10_optimista.to_excel(writer, sheet_name='TopN_Optimista', index=False)
            df_mc_conocido.to_excel(writer, sheet_name='MC_Conocido', index=False)
            df_mc_optimista.to_excel(writer, sheet_name='MC_Optimista', index=False)

        print("\nTabla Top N (Split rango CONOCIDO):")
        display(df_top10_conocido)
        print("\nTabla Top N (Split rango OPTIMISTA):")
        display(df_top10_optimista)


# %%
