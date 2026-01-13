"""
Módulo de entrada/salida para cargar circuitos desde Excel.

Soporta el formato de matriz donde:
- Filas = equipos
- Columnas numéricas = flujos
- Valores: 1 = entrada, -1 = salida, 0 = no conectado
"""

import pandas as pd
from typing import Dict, Tuple, Set, List, Optional
from .equipos import Flujo, Equipo, Celda, Suma


def cargar_circuito_excel(
    archivo: str,
    hoja: Optional[str] = None,
    id_simulacion: int = 1
) -> Tuple[Dict[str, Equipo], Dict[int, Flujo]]:
    """
    Carga un circuito desde archivo Excel.
    
    Args:
        archivo: Ruta al archivo Excel
        hoja: Nombre de la hoja (None = primera hoja)
        id_simulacion: ID de simulación a cargar (columna 'Simulacion')
    
    Returns:
        equipos: Dict {nombre: Equipo}
        flujos: Dict {id: Flujo}
    
    Formato esperado del Excel:
        Simulacion | tipo | Equipo | sp masa | sp cuf | 4 | 5 | 6 | ...
        1          | celda| Jameson| 0.08    | 0.68   | 1 |-1 |-1 | ...
    """
    if hoja:
        df = pd.read_excel(archivo, sheet_name=hoja)
    else:
        df = pd.read_excel(archivo)
    
    # Filtrar por simulación
    df_sim = df[df["Simulacion"] == id_simulacion]
    
    # Identificar columnas de flujos (después de 'sp cuf')
    columnas = list(df.columns)
    idx_sp_cuf = columnas.index("sp cuf")
    columnas_flujos = columnas[idx_sp_cuf + 1:]
    
    equipos = {}
    flujos = {}
    
    for _, row in df_sim.iterrows():
        # Crear equipo según tipo
        tipo = row["tipo"].lower()
        if tipo == "celda":
            equipo = Celda(nombre=row["Equipo"])
        elif tipo == "suma":
            equipo = Suma(nombre=row["Equipo"])
        else:
            raise ValueError(f"Tipo de equipo desconocido: {tipo}")
        
        # Definir flujos de entrada (valor = 1)
        for col in columnas_flujos:
            if row[col] == 1:
                id_flujo = int(col)
                if id_flujo not in flujos:
                    flujos[id_flujo] = Flujo(id=id_flujo)
                flujos[id_flujo].nombre = f"Alim {row['Equipo']}"
                equipo.flujos_entrada.append(id_flujo)
        
        # Definir flujos de salida (valor = -1)
        salida_count = 0
        for col in columnas_flujos:
            if row[col] == -1:
                id_flujo = int(col)
                if id_flujo not in flujos:
                    flujos[id_flujo] = Flujo(id=id_flujo)
                
                if salida_count == 0:
                    flujos[id_flujo].nombre = f"Conc {row['Equipo']}"
                else:
                    flujos[id_flujo].nombre = f"Rel {row['Equipo']}"
                
                equipo.flujos_salida.append(id_flujo)
                salida_count += 1
        
        # Asignar split factors
        equipo.split_factor = [row["sp masa"], row["sp cuf"]]
        equipos[row["Equipo"]] = equipo
    
    return equipos, flujos


def cargar_multiples_simulaciones(
    archivo: str,
    hoja: Optional[str] = None
) -> Dict[int, Tuple[Dict[str, Equipo], Dict[int, Flujo]]]:
    """
    Carga todas las simulaciones de una hoja Excel.
    
    Returns:
        Dict {id_simulacion: (equipos, flujos)}
    """
    if hoja:
        df = pd.read_excel(archivo, sheet_name=hoja)
    else:
        df = pd.read_excel(archivo)
    
    ids_simulacion = df["Simulacion"].unique()
    resultado = {}
    
    for id_sim in ids_simulacion:
        equipos, flujos = cargar_circuito_excel(archivo, hoja, int(id_sim))
        resultado[int(id_sim)] = (equipos, flujos)
    
    return resultado


def identificar_flujos_globales(
    equipos: Dict[str, Equipo],
    flujos_relave: Optional[Set[int]] = None
) -> Tuple[Set[int], Set[int], Set[int], Set[int]]:
    """
    Identifica los tipos de flujo en el circuito.
    
    Args:
        equipos: Diccionario de equipos
        flujos_relave: IDs de flujos que son relave final (opcional)
    
    Returns:
        entrada: Flujos de alimentación al circuito
        salida: Todos los flujos de salida
        salida_conc: Flujos de concentrado final
        internos: Flujos que conectan equipos
    """
    if flujos_relave is None:
        flujos_relave = set()
    
    entradas = set()
    salidas = set()
    
    for equipo in equipos.values():
        entradas.update(equipo.flujos_entrada)
        salidas.update(equipo.flujos_salida)
    
    # Flujos de entrada global = entran pero no salen de ningún equipo
    flujos_entrada = entradas - salidas
    
    # Flujos de salida global = salen pero no entran a ningún equipo
    flujos_salida = salidas - entradas
    
    # Concentrado final = salida - relaves
    flujos_salida_conc = flujos_salida - flujos_relave
    
    # Flujos internos = conectan equipos
    flujos_internos = entradas & salidas
    
    return flujos_entrada, flujos_salida, flujos_salida_conc, flujos_internos


def crear_circuito_desde_dict(config: dict) -> Tuple[Dict[str, Equipo], Dict[int, Flujo]]:
    """
    Crea un circuito desde un diccionario de configuración.
    
    Alternativa al Excel para definir circuitos programáticamente.
    
    Args:
        config: Diccionario con estructura:
            {
                'equipos': [
                    {
                        'nombre': 'Jameson 1',
                        'tipo': 'celda',
                        'entrada': [4],
                        'salida': [5, 6],
                        'split_factor': [0.0825, 0.6872]
                    },
                    ...
                ]
            }
    
    Returns:
        equipos, flujos
    """
    equipos = {}
    flujos = {}
    
    for eq_config in config['equipos']:
        tipo = eq_config['tipo'].lower()
        
        if tipo == 'celda':
            equipo = Celda(nombre=eq_config['nombre'])
        elif tipo == 'suma':
            equipo = Suma(nombre=eq_config['nombre'])
        else:
            raise ValueError(f"Tipo desconocido: {tipo}")
        
        # Flujos de entrada
        for id_flujo in eq_config['entrada']:
            if id_flujo not in flujos:
                flujos[id_flujo] = Flujo(id=id_flujo)
            equipo.flujos_entrada.append(id_flujo)
        
        # Flujos de salida
        for id_flujo in eq_config['salida']:
            if id_flujo not in flujos:
                flujos[id_flujo] = Flujo(id=id_flujo)
            equipo.flujos_salida.append(id_flujo)
        
        # Split factors
        equipo.split_factor = eq_config.get('split_factor', [0, 0])
        
        equipos[eq_config['nombre']] = equipo
    
    return equipos, flujos
