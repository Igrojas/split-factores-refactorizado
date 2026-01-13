#!/usr/bin/env python3
"""
splitfactor - Main

Punto de entrada principal para simulaciones.
Ejecutar: python main.py --help
"""
#%%
import argparse
import os
import sys
import pandas as pd

from core import (
    cargar_circuito_excel,
    cargar_multiples_simulaciones,
    Simulador,
    ConfiguracionMC,
    simular_escenarios
)
from viz import configurar_estilo, crear_figura_resumen, guardar_figura


def simulacion_normal(args):
    """Ejecuta simulación normal desde Excel."""
    
    print(f"Cargando: {args.archivo}")
    print(f"Hoja: {args.hoja}")
    
    # Parsear alimentación
    alimentacion = {}
    if args.alimentacion:
        for item in args.alimentacion:
            id_f, masa, ley = item.split(',')
            alimentacion[int(id_f)] = {'masa': float(masa), 'ley': float(ley)}
    else:
        alimentacion = {4: {'masa': 23.84, 'ley': 2.5167}}
    
    # Parsear relaves
    flujos_relave = set()
    if args.relaves:
        flujos_relave = set(map(int, args.relaves.split(',')))
    
    # Ejecutar
    df = simular_escenarios(args.archivo, args.hoja, alimentacion, flujos_relave)
    
    print("\nResultados:")
    print(df.to_string(index=False))
    
    # Guardar si se especifica
    if args.salida:
        os.makedirs(os.path.dirname(args.salida) or '.', exist_ok=True)
        df.to_excel(args.salida, index=False)
        print(f"\nGuardado en: {args.salida}")
    
    return df


def simulacion_montecarlo(args):
    """Ejecuta simulación Monte Carlo."""
    
    print(f"Cargando: {args.archivo}")
    print(f"Hoja: {args.hoja}")
    print(f"Iteraciones: {args.n_iter:,}")
    
    # Cargar circuito
    equipos, flujos = cargar_circuito_excel(args.archivo, args.hoja, id_simulacion=1)
    
    # Parsear alimentación
    alimentacion = {}
    if args.alimentacion:
        for item in args.alimentacion:
            id_f, masa, ley = item.split(',')
            alimentacion[int(id_f)] = {'masa': float(masa), 'ley': float(ley)}
    else:
        alimentacion = {4: {'masa': 23.84, 'ley': 2.5167}}
    
    # Parsear relaves
    flujos_relave = set()
    if args.relaves:
        flujos_relave = set(map(int, args.relaves.split(',')))
    
    # Parsear equipos objetivo
    equipos_obj = args.equipos.split(',') if args.equipos else ['Jameson 1']
    
    # Parsear rangos
    rangos = {}
    for eq in equipos_obj:
        rangos[eq] = {
            'masa': (args.rango_masa_min, args.rango_masa_max),
            'cuf': (args.rango_cuf_min, args.rango_cuf_max)
        }
    
    # Configurar MC
    config = ConfiguracionMC(
        equipos_objetivo=equipos_obj,
        rangos=rangos,
        n_iteraciones=args.n_iter,
        ley_min=args.ley_min,
        ley_max=args.ley_max
    )
    
    # Ejecutar
    sim = Simulador(equipos, flujos, flujos_relave)
    df = sim.simular_montecarlo(config, alimentacion)
    
    print(f"\nIteraciones válidas: {len(df):,}")
    
    # Estadísticas
    print("\nEstadísticas:")
    for col in ['recuperacion', 'ley_concentrado', 'razon_enriquecimiento']:
        if col in df.columns:
            print(f"  {col}: {df[col].mean():.2f} ± {df[col].std():.2f}")
    
    # Guardar
    if args.salida:
        os.makedirs(os.path.dirname(args.salida) or '.', exist_ok=True)
        df.to_excel(args.salida, index=False)
        print(f"\nGuardado en: {args.salida}")
    
    # Gráfica
    if args.grafica:
        import matplotlib.pyplot as plt
        configurar_estilo()
        fig = crear_figura_resumen(df, equipo_split=equipos_obj[0])
        guardar_figura(fig, args.grafica)
        plt.show()
    
    return df


def main():
    parser = argparse.ArgumentParser(
        description='Simulación de circuitos de flotación por Split Factor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Simulación normal
  python main.py normal -a datos.xlsx -h "Sim Dia"
  
  # Monte Carlo
  python main.py mc -a datos.xlsx -h "Sim MC Dia" -n 100000 --equipos "Jameson 1"
  
  # Con alimentación personalizada
  python main.py normal -a datos.xlsx --alimentacion "4,23.84,2.5167"
        """
    )
    
    subparsers = parser.add_subparsers(dest='comando', help='Tipo de simulación')
    
    # === Subcomando: normal ===
    p_normal = subparsers.add_parser('normal', help='Simulación determinística')
    p_normal.add_argument('-a', '--archivo', required=True, help='Archivo Excel')
    p_normal.add_argument('-j', '--hoja', default='Sim Dia', help='Nombre de hoja')
    p_normal.add_argument('--alimentacion', nargs='+', 
                          help='Alimentación: "id,masa,ley" (puede repetirse)')
    p_normal.add_argument('--relaves', help='IDs de flujos relave (separados por coma)')
    p_normal.add_argument('-o', '--salida', help='Archivo de salida Excel')
    
    # === Subcomando: mc (Monte Carlo) ===
    p_mc = subparsers.add_parser('mc', help='Simulación Monte Carlo')
    p_mc.add_argument('-a', '--archivo', required=True, help='Archivo Excel')
    p_mc.add_argument('-j', '--hoja', default='Sim MC Dia', help='Nombre de hoja')
    p_mc.add_argument('-n', '--n-iter', type=int, default=100000, 
                      help='Número de iteraciones')
    p_mc.add_argument('--equipos', help='Equipos a variar (separados por coma)')
    p_mc.add_argument('--alimentacion', nargs='+',
                      help='Alimentación: "id,masa,ley"')
    p_mc.add_argument('--relaves', help='IDs de flujos relave')
    p_mc.add_argument('--rango-masa-min', type=float, default=0.02)
    p_mc.add_argument('--rango-masa-max', type=float, default=0.70)
    p_mc.add_argument('--rango-cuf-min', type=float, default=0.02)
    p_mc.add_argument('--rango-cuf-max', type=float, default=0.90)
    p_mc.add_argument('--ley-min', type=float, help='Filtro mínimo de ley')
    p_mc.add_argument('--ley-max', type=float, help='Filtro máximo de ley')
    p_mc.add_argument('-o', '--salida', help='Archivo de salida Excel')
    p_mc.add_argument('-g', '--grafica', help='Guardar gráfica (ruta PNG)')
    
    args = parser.parse_args()
    
    if args.comando == 'normal':
        return simulacion_normal(args)
    elif args.comando == 'mc':
        return simulacion_montecarlo(args)
    else:
        parser.print_help()
        return None


if __name__ == '__main__':
    main()

# %%
