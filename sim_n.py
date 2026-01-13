#%%
"""
Script de simulación con split factors.
Ejecuta simulación base y análisis Monte Carlo.
"""

# ============================================================================
# IMPORTS
# ============================================================================
import importlib
import pandas as pd
import matplotlib.pyplot as plt

# Recargar módulos de splitfactor para ver cambios en desarrollo
import splitfactor.core
import splitfactor.viz
importlib.reload(splitfactor.core)
importlib.reload(splitfactor.viz)

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
# CONFIGURACIÓN - MODIFICAR AQUÍ LOS VALORES
# ============================================================================
# Archivos de entrada
CONFIG = {
    'archivo_circuito': "data/caso 4/Simulacion_caso_base.xlsx",
    'hoja_circuito': "Sim Dia",
    'id_simulacion': 1,
    'archivo_split_factors': "data/caso 4/sf_caso_4.xlsx",
    'hoja_split_factors': None,  # None = primera hoja
    
    # Configuración de simulación base
    'flujos_relave': {9},
    'alimentacion': {
        'id_flujo': 4,
        'masa': 23.84,
        'ley': 2.5167
    },
    
    # Configuración Monte Carlo
    'montecarlo': {
        'equipos_objetivo': ['Jameson 1'],
        'rangos': {
            'Jameson 1': {
                'masa': (0.02, 0.14),
                'cuf': (0.01, 0.9)
            }
        },
        'n_iteraciones': 10_000,
        'ley_min': 10,
        'ley_max': 26
    },
    
    # Filtrado de resultados
    'filtros': {
        'equipo_analisis': 'Jameson 1',  # Equipo para calcular ER
        'er_min': 6,  # Razón de enriquecimiento mínima
        'er_max': 11  # Razón de enriquecimiento máxima
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
    mask = (df_mc[cols_ley] <= 26).all(axis=1)
    df_mc = df_mc[mask]

if CONFIG['mostrar_resultados']:
    print(f"\nIteraciones después del filtro ER: {len(df_mc)}")


# ============================================================================
# VISUALIZACIONES
# ============================================================================
if CONFIG['mostrar_graficas']:
    # Gráfica 1: Recuperación vs Ley y Split factors
    fig, axes = plt.subplots(1, 2, figsize=CONFIG['graficas']['figsize_doble'])
    
    graficar_recuperacion_ley(
        df=df_mc,
        titulo=CONFIG['graficas']['titulo_recuperacion_ley'],
        color_por=columna_er,
        ax=axes[1]
    )
    
    graficar_splits(
        df=df_mc,
        equipo=equipo_analisis,
        color_por=columna_er,
        ax=axes[0]
    )
    
    plt.tight_layout()
    if CONFIG['guardar_graficas']:
        plt.savefig(CONFIG['graficas']['archivo_resultados'], 
                   dpi=CONFIG['graficas']['dpi'])
    plt.show()
    
    # Gráfica 2: Top N
    fig, ax = plt.subplots(figsize=CONFIG['graficas']['figsize_simple'])
    
    ax, df_top10 = graficar_top_n(
        df=df_mc,
        n=CONFIG['graficas']['top_n'],
        criterio=CONFIG['graficas']['criterio_top_n'],
        ax=ax
    )
    
    plt.tight_layout()
    if CONFIG['guardar_graficas']:
        plt.savefig(CONFIG['graficas']['archivo_top10'], 
                   dpi=CONFIG['graficas']['dpi'])
    plt.show()
    
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
        # Filtrar solo las columnas que existen
        columnas_validas = [col for col in columnas_ajustadas if col in df_top10.columns]
        print(df_top10[columnas_validas].to_string())

#%%

df_superior_96 = df_mc[df_mc['recuperacion'] > 96]
# Mostrar en tabla ordenada por 'ley_concentrado' descendente
df_superior_96_ordenado = df_superior_96.sort_values(by='ley_concentrado', ascending=False)
print("\nValores con recuperación superior a 96%, ordenados por ley_concentrado:")
print(df_superior_96_ordenado.to_string(index=False))

# Graficar los puntos
plt.figure(figsize=(8,6))
plt.scatter(df_superior_96['recuperacion'], df_superior_96['ley_concentrado'])
plt.xlabel('Recuperación (%)')
plt.ylabel('Ley Concentrado')
plt.title('Valores con Recuperación Superior a 96%')
plt.grid(True)
plt.show()