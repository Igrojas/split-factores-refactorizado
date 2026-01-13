"""
Clases base para simulación de circuitos de flotación usando Split Factor.

Este módulo define los componentes fundamentales:
- Flujo: representa un flujo de material (masa, ley, contenido fino)
- Equipo: clase base para equipos
- Celda: equipo de flotación que separa en concentrado y relave
- Suma: mezclador que combina múltiples flujos
"""

from dataclasses import dataclass
from typing import List, Dict
import copy


@dataclass
class Flujo:
    """
    Representa un flujo de material en el circuito.
    
    Atributos:
        id: Identificador único del flujo
        nombre: Nombre descriptivo
        masa: Masa del flujo (t/h o unidad consistente)
        ley: Ley de cobre (%)
        contenido_fino: Contenido de cobre fino (masa * ley / 100)
    """
    id: int
    nombre: str = ""
    masa: float = 0.0
    ley: float = 0.0
    contenido_fino: float = 0.0
    
    def actualizar_contenido_fino(self):
        """Calcula el contenido fino a partir de masa y ley."""
        self.contenido_fino = self.masa * self.ley / 100
    
    def actualizar_ley(self):
        """Calcula la ley a partir de masa y contenido fino."""
        if self.masa > 0:
            self.ley = self.contenido_fino / self.masa * 100
        else:
            self.ley = 0.0
    
    def __repr__(self):
        return f"Flujo({self.id}, masa={self.masa:.4f}, ley={self.ley:.4f}%)"


class Equipo:
    """
    Clase base para equipos del circuito.
    
    Atributos:
        nombre: Nombre del equipo
        flujos_entrada: Lista de IDs de flujos de entrada
        flujos_salida: Lista de IDs de flujos de salida
        split_factor: [split_masa, split_cuf] para equipos tipo celda
    """
    
    def __init__(self, nombre: str = ""):
        self.nombre = nombre
        self.flujos_entrada: List[int] = []
        self.flujos_salida: List[int] = []
        self.split_factor: List[float] = []
    
    def calcular(self, flujos: Dict[int, Flujo]):
        """Método a sobrescribir en clases hijas."""
        raise NotImplementedError("Implementar en clase hija")
    
    def __repr__(self):
        return f"{self.__class__.__name__}('{self.nombre}')"


class Celda(Equipo):
    """
    Celda de flotación que separa un flujo en concentrado y relave.
    
    El split factor define qué fracción va al concentrado:
    - split_factor[0]: fracción de masa al concentrado
    - split_factor[1]: fracción de contenido fino (Cu) al concentrado
    
    Flujos de salida:
    - flujos_salida[0]: Concentrado
    - flujos_salida[1]: Relave
    """
    
    def calcular(self, flujos: Dict[int, Flujo]):
        """
        Aplica el split factor para calcular los flujos de salida.
        """
        entrada = flujos[self.flujos_entrada[0]]
        entrada.actualizar_contenido_fino()
        
        concentrado = flujos[self.flujos_salida[0]]
        relave = flujos[self.flujos_salida[1]]
        
        sp_masa = self.split_factor[0]
        sp_cuf = self.split_factor[1]
        
        concentrado.masa = entrada.masa * sp_masa
        relave.masa = entrada.masa * (1 - sp_masa)
        
        concentrado.contenido_fino = entrada.contenido_fino * sp_cuf
        relave.contenido_fino = entrada.contenido_fino * (1 - sp_cuf)
        
        concentrado.actualizar_ley()
        relave.actualizar_ley()


class Suma(Equipo):
    """
    Mezclador que combina múltiples flujos de entrada en uno de salida.
    """
    
    def calcular(self, flujos: Dict[int, Flujo]):
        """Suma todos los flujos de entrada en el flujo de salida."""
        salida = flujos[self.flujos_salida[0]]
        salida.masa = 0.0
        salida.contenido_fino = 0.0
        
        for id_entrada in self.flujos_entrada:
            entrada = flujos[id_entrada]
            salida.masa += entrada.masa
            salida.contenido_fino += entrada.contenido_fino
        
        salida.actualizar_ley()


def copiar_estado(equipos: Dict[str, Equipo], flujos: Dict[int, Flujo]):
    """Crea copia profunda de equipos y flujos para simulación independiente."""
    return copy.deepcopy(equipos), copy.deepcopy(flujos)
