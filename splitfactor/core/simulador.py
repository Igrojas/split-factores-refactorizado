"""
Simulador de circuitos de flotación.

Contiene:
- Simulación normal (determinística)
- Simulación Monte Carlo (variación de split factors)
"""

import copy
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
import numpy as np
import pandas as pd

from .equipos import Equipo, Flujo, copiar_estado
from .io import identificar_flujos_globales


@dataclass
class ConfiguracionMC:
    """
    Configuración para simulación Monte Carlo.
    
    Atributos:
        equipos_objetivo: Lista de nombres de equipos a variar
        rangos: Dict con rangos por equipo y tipo de split
                {'Jameson 1': {'masa': (0.02, 0.7), 'cuf': (0.02, 0.9)}}
        n_iteraciones: Número de iteraciones Monte Carlo
        ley_min: Filtro mínimo de ley de concentrado final
        ley_max: Filtro máximo de ley de concentrado final
    """
    equipos_objetivo: List[str]
    rangos: Dict[str, Dict[str, Tuple[float, float]]]
    n_iteraciones: int = 100_000
    ley_min: Optional[float] = None
    ley_max: Optional[float] = None
    
    @classmethod
    def default(cls, equipos: List[str]):
        """Crea configuración por defecto para lista de equipos."""
        rangos = {
            eq: {'masa': (0.02, 0.7), 'cuf': (0.02, 0.9)}
            for eq in equipos
        }
        return cls(equipos_objetivo=equipos, rangos=rangos)


class Simulador:
    """
    Simulador de circuitos de flotación.
    
    Atributos:
        equipos: Diccionario de equipos del circuito
        flujos: Diccionario de flujos
        flujos_relave: Set de IDs de flujos que son relave final
        iteraciones_convergencia: Iteraciones para convergencia en reciclos
    """
    
    def __init__(
        self,
        equipos: Dict[str, Equipo],
        flujos: Dict[int, Flujo],
        flujos_relave: Optional[Set[int]] = None,
        iteraciones_convergencia: int = 100
    ):
        self.equipos = equipos
        self.flujos = flujos
        self.flujos_relave = flujos_relave or set()
        self.iteraciones_convergencia = iteraciones_convergencia
        
        # Identificar flujos globales
        self.f_entrada, self.f_salida, self.f_salida_conc, self.f_internos = \
            identificar_flujos_globales(equipos, flujos_relave)
    
    def establecer_alimentacion(self, id_flujo: int, masa: float, ley: float):
        """
        Establece las condiciones de alimentación.
        
        Args:
            id_flujo: ID del flujo de alimentación
            masa: Masa de alimentación
            ley: Ley de cobre (%)
        """
        if id_flujo in self.flujos:
            self.flujos[id_flujo].masa = masa
            self.flujos[id_flujo].ley = ley
            self.flujos[id_flujo].actualizar_contenido_fino()
    
    def ejecutar_iteracion(self):
        """Ejecuta una iteración de cálculo sobre todos los equipos."""
        for equipo in self.equipos.values():
            equipo.calcular(self.flujos)
    
    def simular(self) -> Dict:
        """
        Ejecuta simulación hasta convergencia.
        
        Returns:
            Diccionario con resultados principales
        """
        # Iterar hasta convergencia
        for _ in range(self.iteraciones_convergencia):
            self.ejecutar_iteracion()
        
        return self._calcular_resultados()
    
    def _calcular_resultados(self) -> Dict:
        """Calcula métricas principales del circuito."""
        # Flujo de alimentación (primer flujo de entrada)
        id_alim = list(self.f_entrada)[0]
        alim = self.flujos[id_alim]
        
        # Sumar concentrados finales
        masa_conc = sum(self.flujos[i].masa for i in self.f_salida_conc)
        cuf_conc = sum(self.flujos[i].contenido_fino for i in self.f_salida_conc)
        
        # Calcular métricas
        recuperacion = (cuf_conc / alim.contenido_fino * 100) if alim.contenido_fino > 0 else 0
        mass_pull = (masa_conc / alim.masa * 100) if alim.masa > 0 else 0
        ley_conc = (cuf_conc / masa_conc * 100) if masa_conc > 0 else 0
        razon_enriquecimiento = recuperacion / mass_pull if mass_pull > 0 else 0
        
        # Error de balance
        masa_salida = sum(self.flujos[i].masa for i in self.f_salida)
        cuf_salida = sum(self.flujos[i].contenido_fino for i in self.f_salida)
        
        return {
            'recuperacion': recuperacion,
            'mass_pull': mass_pull,
            'ley_concentrado': ley_conc,
            'razon_enriquecimiento': razon_enriquecimiento,
            'error_masa': alim.masa - masa_salida,
            'error_cuf': alim.contenido_fino - cuf_salida,
            'flujos': {k: {'masa': v.masa, 'ley': v.ley} for k, v in self.flujos.items()}
        }
    
    def simular_montecarlo(
        self,
        config: ConfiguracionMC,
        alimentacion: Dict[int, Dict[str, float]],
        mostrar_progreso: bool = True
    ) -> pd.DataFrame:
        """
        Ejecuta simulación Monte Carlo.
        
        Args:
            config: Configuración de Monte Carlo
            alimentacion: {id_flujo: {'masa': val, 'ley': val}}
            mostrar_progreso: Mostrar barra de progreso
        
        Returns:
            DataFrame con resultados de todas las iteraciones
        """
        resultados = []
        
        # Configurar iterador con o sin progreso
        if mostrar_progreso:
            try:
                from tqdm import trange
                iterador = trange(config.n_iteraciones, desc="Monte Carlo")
            except ImportError:
                iterador = range(config.n_iteraciones)
                print(f"Ejecutando {config.n_iteraciones} iteraciones...")
        else:
            iterador = range(config.n_iteraciones)
        
        for i in iterador:
            # Copiar estado limpio
            equipos_mc, flujos_mc = copiar_estado(self.equipos, self.flujos)
            
            # Establecer alimentación
            for id_flujo, valores in alimentacion.items():
                if id_flujo in flujos_mc:
                    flujos_mc[id_flujo].masa = valores['masa']
                    flujos_mc[id_flujo].ley = valores['ley']
                    flujos_mc[id_flujo].actualizar_contenido_fino()
            
            # Sortear split factors para equipos objetivo
            split_info = {}
            for nombre_eq in config.equipos_objetivo:
                if nombre_eq in equipos_mc:
                    rangos = config.rangos[nombre_eq]
                    sp_masa = np.random.uniform(*rangos['masa'])
                    sp_cuf = np.random.uniform(*rangos['cuf'])
                    equipos_mc[nombre_eq].split_factor = [sp_masa, sp_cuf]
                    
                    split_info[f"{nombre_eq}_sp_masa"] = sp_masa
                    split_info[f"{nombre_eq}_sp_cuf"] = sp_cuf
            
            # Crear simulador temporal
            sim_temp = Simulador(
                equipos_mc, flujos_mc,
                self.flujos_relave,
                self.iteraciones_convergencia
            )
            
            # Ejecutar simulación
            try:
                resultado = sim_temp.simular()
                
                # Verificar leyes válidas (< 36%)
                leyes_validas = all(
                    v['ley'] < 36 for v in resultado['flujos'].values()
                )
                if not leyes_validas:
                    continue
                
                fila = {
                    'iteracion': i,
                    'recuperacion': resultado['recuperacion'],
                    'mass_pull': resultado['mass_pull'],
                    'ley_concentrado': resultado['ley_concentrado'],
                    'razon_enriquecimiento': resultado['razon_enriquecimiento'],
                    **split_info
                }
                
                # Agregar flujos individuales
                for id_f, vals in resultado['flujos'].items():
                    fila[f'flujo_{id_f}_masa'] = vals['masa']
                    fila[f'flujo_{id_f}_ley'] = vals['ley']
                
                resultados.append(fila)
                
            except Exception:
                continue
        
        # Crear DataFrame
        df = pd.DataFrame(resultados)
        
        # Aplicar filtros de ley
        if config.ley_min is not None:
            df = df[df['ley_concentrado'] >= config.ley_min]
        if config.ley_max is not None:
            df = df[df['ley_concentrado'] <= config.ley_max]
        
        return df


def simular_escenarios(
    archivo_excel: str,
    hoja: str,
    alimentacion: Dict[int, Dict[str, float]],
    flujos_relave: Optional[Set[int]] = None
) -> pd.DataFrame:
    """
    Simula todos los escenarios (Simulacion 1, 2, 3...) de una hoja Excel.
    
    Args:
        archivo_excel: Ruta al archivo
        hoja: Nombre de la hoja
        alimentacion: Condiciones de alimentación
        flujos_relave: IDs de flujos de relave
    
    Returns:
        DataFrame con resultados por escenario
    """
    from .io import cargar_multiples_simulaciones
    
    simulaciones = cargar_multiples_simulaciones(archivo_excel, hoja)
    resultados = []
    
    for id_sim, (equipos, flujos) in simulaciones.items():
        sim = Simulador(equipos, flujos, flujos_relave)
        
        # Establecer alimentación
        for id_flujo, valores in alimentacion.items():
            sim.establecer_alimentacion(id_flujo, valores['masa'], valores['ley'])
        
        resultado = sim.simular()
        resultado['simulacion'] = id_sim
        resultados.append(resultado)
    
    # Convertir a DataFrame
    df = pd.DataFrame([
        {
            'simulacion': r['simulacion'],
            'recuperacion': r['recuperacion'],
            'mass_pull': r['mass_pull'],
            'ley_concentrado': r['ley_concentrado'],
            'razon_enriquecimiento': r['razon_enriquecimiento']
        }
        for r in resultados
    ])
    
    return df
