"""
Módulo de visualización para resultados de simulación.

Gráficas disponibles:
- Nube de recuperación vs ley
- Split factors
- Comparación con test de dilución
- Top N mejores simulaciones
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple


# Configuración visual por defecto
COLORES_DEFAULT = {
    'Día': 'orange',
    'Noche': 'blue',
    'Promedio': 'green'
}

MARCADORES_DEFAULT = {
    'Día': 'D',
    'Noche': 's',
    'Promedio': 'o'
}

import itertools

def generar_colores_top_n(n: int) -> list:
    """
    Genera una lista de 'n' colores distintos para resaltar top-N puntos en un gráfico.
    Se cicla sobre una paleta predefinida si 'n' es mayor que la cantidad de colores base.
    """
    base_colores = [
        '#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231',
        '#911eb4', '#42d4f4', '#f032e6', '#bfef45', '#fabed4',
        '#469990', '#dcbeff', '#9a6324', '#fffac8', '#800000',
        '#aaffc3', '#808000', '#ffd8b1', '#000075', '#a9a9a9'
    ]
    if n <= len(base_colores):
        return base_colores[:n]
    # Si se necesitan más, se repiten cíclicamente
    return list(itertools.islice(itertools.cycle(base_colores), n))


def configurar_estilo():
    """Aplica estilo visual consistente."""
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams['figure.figsize'] = (10, 6)
    plt.rcParams['font.size'] = 11
    plt.rcParams['axes.titlesize'] = 12
    plt.rcParams['axes.labelsize'] = 11


def graficar_recuperacion_ley(
    df: pd.DataFrame,
    col_recuperacion: str = 'recuperacion',
    col_ley: str = 'ley_concentrado',
    titulo: str = 'Recuperación vs Ley de Concentrado',
    color: str = 'RdYlBu',
    color_por: Optional[str] = None,
    alpha: float = 0.5,
    ax: Optional[plt.Axes] = None,
    split_rango: Optional[Tuple[float, float]] = None,
    split_col: Optional[str] = 'Jameson 1_sp_cuf',
    seleccion_color: str = 'RdYlBu',
    gris_alpha: float = 0.18,
) -> plt.Axes:
    """
    Gráfica de dispersión: Recuperación vs Ley de concentrado, 
    permitiendo resaltar puntos seleccionados por rango de split factor.

    Args:
        df: DataFrame con resultados
        col_recuperacion: Nombre de columna de recuperación
        col_ley: Nombre de columna de ley
        titulo: Título del gráfico
        color: Colormap o color de los puntos
        color_por: Columna para colorear puntos según valores
        alpha: Transparencia
        ax: Axes existente (opcional)
        split_rango: Tuple con min y max del split factor para resaltar
        split_col: Nombre de la columna sobre la cual seleccionar el rango
        seleccion_color: Colormap para los puntos seleccionados
        gris_alpha: Transparencia de los puntos fuera de rango (gris)

    Returns:
        Axes del gráfico
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))

    hay_rango = True
    if split_col is None:
        print("No se proporcionó split_col")
        hay_rango = False
    if split_rango is None:
        print("No se proporcionó split_rango")
        hay_rango = False

    # Selección de puntos
    if hay_rango:
        mask = (df[split_col] >= split_rango[0]) & (df[split_col] <= split_rango[1])
        df_sel = df[mask]
        df_rest = df[~mask]
    else:
        print("no hay rango")
        df_sel = df
        df_rest = None

    # Gráfico: primero fondo gris si corresponde
    if df_rest is not None and not df_rest.empty:
        ax.scatter(
            df_rest[col_recuperacion],
            df_rest[col_ley],
            c='lightgray',
            alpha=gris_alpha,
            s=20,
            edgecolors='none',
            label="Fuera de selección"
        )

    # Ahora los puntos seleccionados (color)
    if color_por and color_por in df_sel.columns:
        scatter = ax.scatter(
            df_sel[col_recuperacion],
            df_sel[col_ley],
            c=df_sel[color_por],
            cmap=seleccion_color if hay_rango else color,
            alpha=alpha,
            s=20,
            edgecolors='none',
            label="En selección"
        )
        plt.colorbar(scatter, ax=ax, label=color_por)
    else:
        color_solido = 'steelblue' if color in plt.colormaps() else color
        ax.scatter(
            df_sel[col_recuperacion],
            df_sel[col_ley],
            c=color_solido,
            alpha=alpha,
            s=20,
            edgecolors='none',
            label="En selección" if hay_rango else None
        )

    ax.set_xlabel('Recuperación (%)')
    ax.set_ylabel('Ley de Concentrado (%)')
    ax.set_title(titulo)
    ax.grid(True, alpha=0.3)
    if hay_rango:
        ax.legend()
    return ax


def graficar_splits(
    df: pd.DataFrame,
    equipo: str,
    col_masa: Optional[str] = None,
    col_cuf: Optional[str] = None,
    color_por: Optional[str] = None,
    titulo: Optional[str] = None,
    ax: Optional[plt.Axes] = None,
    split_rango: Optional[Tuple[float, float]] = None,
    split_col: Optional[str] = 'Jameson 1_sp_cuf',
    seleccion_color: str = 'RdYlBu',
    gris_alpha: float = 0.5,
) -> plt.Axes:
    """
    Gráfica de split factors: masa vs contenido fino, 
    permitiendo resaltar puntos seleccionados por rangos.

    Args:
        df: DataFrame con resultados MC
        equipo: Nombre del equipo
        col_masa: Columna de split masa (default: '{equipo}_sp_masa')
        col_cuf: Columna de split cuf (default: '{equipo}_sp_cuf')
        color_por: Columna para colorear puntos
        titulo: Título del gráfico
        ax: Axes existente
        split_rangos: Dict, e.g., {'masa': (min, max), 'cuf': (min, max)}
        seleccion_color: Colormap para los puntos seleccionados
        gris_alpha: Transparencia de los puntos fuera de rango (gris)

    Returns:
        Axes del gráfico
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))

    col_masa = col_masa or f'{equipo}_sp_masa'
    col_cuf = col_cuf or f'{equipo}_sp_cuf'
    titulo = titulo or f'Split Factors - {equipo}'

    hay_rango = True
    if split_col is None:
        print("No se proporcionó split_col")
        hay_rango = False
    if split_rango is None:
        print("No se proporcionó split_rango")
        hay_rango = False

    # Máscara de selección
    if hay_rango and col_masa in df.columns and col_cuf in df.columns:
        mask = (
            (df[col_cuf] >= split_rango[0]) & (df[col_cuf] <= split_rango[1])
        )
        df_sel = df[mask]
        df_rest = df[~mask]
    else:
        df_sel = df
        df_rest = None

    # Fondo: fuera de selección (gris)
    if df_rest is not None and not df_rest.empty:
        ax.scatter(
            df_rest[col_masa],
            df_rest[col_cuf],
            c='lightgray',
            alpha=gris_alpha,
            s=20,
            edgecolors='none',
            label="Fuera de selección"
        )
    # Seleccionados: en color
    if color_por and color_por in df_sel.columns:
        scatter = ax.scatter(
            df_sel[col_masa],
            df_sel[col_cuf],
            c=df_sel[color_por],
            cmap=seleccion_color if hay_rango else 'RdYlBu',
            alpha=0.6,
            s=20,
            edgecolors='none',
            label="En selección"
        )
        plt.colorbar(scatter, ax=ax, label=color_por)
    else:
        ax.scatter(
            df_sel[col_masa],
            df_sel[col_cuf],
            c=seleccion_color if hay_rango else 'RdYlBu',
            alpha=0.5 if not hay_rango else 0.7,
            s=20,
            edgecolors='none',
            label="En selección" if hay_rango else None
        )

    ax.set_xlabel('Split Masa')
    ax.set_ylabel('Split CuF')
    ax.set_title(titulo)
    ax.grid(True, alpha=0.3)
    if hay_rango:
        ax.legend()
    return ax


def graficar_con_test_dilucion(
    df_mc: pd.DataFrame,
    df_test: pd.DataFrame,
    col_rec_mc: str = 'recuperacion',
    col_ley_mc: str = 'ley_concentrado',
    col_rec_test: str = 'Recuperación, Cu%',
    col_ley_test: str = 'Ley acumulada, Cu%',
    ley_alim_test: Optional[float] = None,
    titulo: str = 'Simulación MC vs Test de Dilución',
    ax: Optional[plt.Axes] = None
) -> plt.Axes:
    """
    Gráfica comparando simulación MC con test de dilución.
    
    Args:
        df_mc: DataFrame de Monte Carlo
        df_test: DataFrame de test de dilución
        col_rec_mc, col_ley_mc: Columnas de MC
        col_rec_test, col_ley_test: Columnas de test
        ley_alim_test: Ley de alimentación del test (para leyenda)
        titulo: Título
        ax: Axes existente
    
    Returns:
        Axes del gráfico
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))
    
    # Nube de MC
    ax.scatter(
        df_mc[col_rec_mc],
        df_mc[col_ley_mc],
        c='lightgray',
        alpha=0.5,
        s=15,
        label='Simulación MC'
    )
    
    # Curva de test de dilución
    label_test = 'Test de Dilución'
    if ley_alim_test:
        label_test += f' (Ley Alim = {ley_alim_test:.2f}%)'
    
    sns.lineplot(
        data=df_test,
        x=col_rec_test,
        y=col_ley_test,
        color='royalblue',
        marker='D',
        markersize=8,
        linestyle='--',
        linewidth=2,
        label=label_test,
        ax=ax
    )
    
    ax.set_xlabel('Recuperación (%)')
    ax.set_ylabel('Ley de Concentrado (%)')
    ax.set_title(titulo)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    return ax


def graficar_top_n(
    df: pd.DataFrame,
    n: int = 10,
    criterio: str = 'razon_enriquecimiento',
    col_x: str = 'recuperacion',
    col_y: str = 'ley_concentrado',
    ascendente: bool = False,
    split_rango: Optional[Tuple[float, float]] = None,
    split_col: Optional[str] = 'Jameson 1_sp_cuf',
    ax: Optional[plt.Axes] = None
) -> Tuple[plt.Axes, pd.DataFrame]:
    """
    Destaca las top N simulaciones según un criterio.
    
    Args:
        df: DataFrame con resultados
        n: Número de top a mostrar
        criterio: Columna para ordenar
        col_x, col_y: Columnas para ejes
        ascendente: Orden ascendente (False = mayor es mejor)
        split_rango: Tuple con min y max del split factor para resaltar
        split_col: Nombre de la columna sobre la cual seleccionar el rango
        ax: Axes existente
    
    Returns:
        (Axes, DataFrame con top N)
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))
    
    # Ordenar y obtener top N

    if split_rango is not None and split_col is not None:
        mask = (df[split_col] >= split_rango[0]) & (df[split_col] <= split_rango[1])
        df_sel = df[mask]
        df_rest = df[~mask]
    else:
        df_sel = df
        df_rest = None

    df_sorted = df_sel.sort_values(criterio, ascending=ascendente)
    df_sorted = df_sorted.reset_index(drop=True)
    df_top = df_sorted.head(n).copy()
    
    if df_rest is not None and not df_rest.empty:
        ax.scatter(
            df[col_x],
            df[col_y],
            c='lightgray',
            alpha=0.5,
            s=15,
            label='Resto'
        )
    # Graficar top N con colores
    for i, (idx, row) in enumerate(df_top.iterrows()):
        color = generar_colores_top_n(n)[i]
        ax.scatter(
            row[col_x],
            row[col_y],
            c=color,
            s=100,
            marker='o',
            edgecolors='black',
            linewidth=1.5,
            zorder=10
        )
    
    ax.set_xlabel('Recuperación (%)')
    ax.set_ylabel('Ley de Concentrado (%)')
    # Formatea 'criterio' para tener mayúscula inicial y espacios, e.g., "razon_enriquecimiento" -> "Razón Enriquecimiento"
    criterio_titulo = criterio.replace('_', ' ').title().replace('Razon', 'Razón').replace('Enriquecimiento', 'Enriquecimiento')
    ax.set_title(f'Top {n} por {criterio_titulo}')
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(True, alpha=0.3)
    
    return ax, df_top


def crear_figura_resumen(
    df_mc: pd.DataFrame,
    df_normal: Optional[pd.DataFrame] = None,
    df_test: Optional[pd.DataFrame] = None,
    equipo_split: str = 'Jameson 1',
    turno: str = '',
    figsize: Tuple[int, int] = (14, 6)
) -> plt.Figure:
    """
    Crea figura con 2 subplots: splits y recuperación/ley.
    
    Args:
        df_mc: Resultados Monte Carlo
        df_normal: Resultados simulación normal (opcional)
        df_test: Datos test de dilución (opcional)
        equipo_split: Equipo para graficar splits
        turno: Nombre del turno para título
        figsize: Tamaño de figura
    
    Returns:
        Figura matplotlib
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    
    # Subplot 1: Split factors
    col_masa = f'{equipo_split}_sp_masa'
    col_cuf = f'{equipo_split}_sp_cuf'
    
    if col_masa in df_mc.columns and col_cuf in df_mc.columns:
        graficar_splits(
            df_mc, equipo_split,
            color_por='razon_enriquecimiento',
            titulo=f'Split Factors {equipo_split} - {turno}',
            ax=ax1
        )
    else:
        ax1.text(0.5, 0.5, 'Sin datos de splits', ha='center', va='center')
    
    # Subplot 2: Recuperación vs Ley
    ax2.scatter(
        df_mc['recuperacion'],
        df_mc['ley_concentrado'],
        c='lightgray',
        alpha=0.5,
        s=15,
        label='MC'
    )
    
    # Agregar simulación normal si existe
    if df_normal is not None and not df_normal.empty:
        ax2.scatter(
            df_normal['recuperacion'],
            df_normal['ley_concentrado'],
            c='red',
            marker='*',
            s=200,
            edgecolors='black',
            linewidth=1.5,
            label='Simulación Base',
            zorder=10
        )
    
    # Agregar test de dilución si existe
    if df_test is not None and not df_test.empty:
        sns.lineplot(
            data=df_test,
            x='Recuperación, Cu%',
            y='Ley acumulada, Cu%',
            color='royalblue',
            marker='D',
            markersize=6,
            linestyle='--',
            label='Test Dilución',
            ax=ax2
        )
    
    ax2.set_xlabel('Recuperación (%)')
    ax2.set_ylabel('Ley de Concentrado (%)')
    ax2.set_title(f'Recuperación vs Ley - {turno}')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def guardar_figura(fig: plt.Figure, ruta: str, dpi: int = 150):
    """Guarda figura en archivo."""
    fig.savefig(ruta, dpi=dpi, bbox_inches='tight')
    print(f"Figura guardada: {ruta}")
