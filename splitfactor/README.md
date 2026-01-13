# splitfactor

Simulación de circuitos de flotación usando el método de Split Factor.

## Instalación

```bash
# Clonar o copiar el directorio
cd splitfactor

# Instalar dependencias
pip install pandas numpy matplotlib seaborn tqdm openpyxl
```

## Estructura

```
splitfactor/
├── core/
│   ├── equipos.py      # Clases: Flujo, Celda, Suma
│   ├── io.py           # Carga desde Excel o dict
│   └── simulador.py    # Simulador normal y Monte Carlo
├── viz/
│   └── graficas.py     # Funciones de visualización
├── examples/
│   ├── ejemplo_simple.py
│   ├── ejemplo_montecarlo.py
│   └── ejemplo_circuito_programatico.py
├── main.py             # CLI principal
└── README.md
```

## Uso Rápido

### Desde Python

```python
from splitfactor.core import cargar_circuito_excel, Simulador

# Cargar circuito desde Excel
equipos, flujos = cargar_circuito_excel('circuito.xlsx', hoja='Sim Dia')

# Crear simulador
sim = Simulador(equipos, flujos, flujos_relave={9})

# Establecer alimentación
sim.establecer_alimentacion(4, masa=23.84, ley=2.5167)

# Ejecutar
resultado = sim.simular()

print(f"Recuperación: {resultado['recuperacion']:.2f}%")
print(f"Ley Conc: {resultado['ley_concentrado']:.2f}%")
```

### Monte Carlo

```python
from splitfactor.core import ConfiguracionMC

# Configurar Monte Carlo
config = ConfiguracionMC(
    equipos_objetivo=['Jameson 1'],
    rangos={
        'Jameson 1': {
            'masa': (0.02, 0.70),
            'cuf': (0.02, 0.90)
        }
    },
    n_iteraciones=100_000,
    ley_min=10,
    ley_max=30
)

# Ejecutar
alimentacion = {4: {'masa': 23.84, 'ley': 2.5167}}
df_mc = sim.simular_montecarlo(config, alimentacion)
```

### Desde línea de comandos

```bash
# Simulación normal
python main.py normal -a datos.xlsx -j "Sim Dia" -o resultados.xlsx

# Monte Carlo
python main.py mc -a datos.xlsx -j "Sim MC Dia" -n 100000 \
    --equipos "Jameson 1" \
    --rango-masa-min 0.02 --rango-masa-max 0.70 \
    --rango-cuf-min 0.02 --rango-cuf-max 0.90 \
    --ley-min 10 --ley-max 30 \
    -o resultados_mc.xlsx -g grafica.png
```

## Formato Excel

El archivo Excel debe tener el siguiente formato:

| Simulacion | tipo  | Equipo    | sp masa | sp cuf | 4 | 5  | 6  | 7 | ... |
|------------|-------|-----------|---------|--------|---|----|----|---|-----|
| 1          | celda | Jameson 1 | 0.0825  | 0.6872 | 1 | -1 | -1 | 0 | ... |
| 1          | suma  | Mezclador | 0.0     | 0.0    | 0 | 0  | 1  |-1 | ... |

Donde:
- `Simulacion`: ID del escenario
- `tipo`: "celda" o "suma"
- `Equipo`: Nombre del equipo
- `sp masa`, `sp cuf`: Split factors
- Columnas numéricas: Flujos (1 = entrada, -1 = salida, 0 = no conectado)

## Definir circuito sin Excel

```python
from splitfactor.core import crear_circuito_desde_dict, Simulador

config = {
    'equipos': [
        {
            'nombre': 'Jameson 1',
            'tipo': 'celda',
            'entrada': [1],
            'salida': [2, 3],
            'split_factor': [0.08, 0.70]
        },
        {
            'nombre': 'Scavenger',
            'tipo': 'celda',
            'entrada': [3],
            'salida': [4, 5],
            'split_factor': [0.25, 0.90]
        }
    ]
}

equipos, flujos = crear_circuito_desde_dict(config)
sim = Simulador(equipos, flujos, flujos_relave={5})
```

## Visualización

```python
from splitfactor.viz import (
    graficar_recuperacion_ley,
    graficar_splits,
    graficar_top_n,
    crear_figura_resumen
)

# Gráfica simple
graficar_recuperacion_ley(df_mc)

# Split factors coloreados por razón de enriquecimiento
graficar_splits(df_mc, 'Jameson 1', color_por='razon_enriquecimiento')

# Top 10 mejores simulaciones
ax, df_top = graficar_top_n(df_mc, n=10, criterio='razon_enriquecimiento')

# Figura resumen (2 subplots)
fig = crear_figura_resumen(df_mc, df_normal, df_test, equipo_split='Jameson 1')
```

## Métricas Calculadas

- **Recuperación**: % de Cu recuperado en concentrado
- **Mass Pull**: % de masa que va a concentrado
- **Ley Concentrado**: Ley de Cu en concentrado final
- **Razón Enriquecimiento**: Recuperación / Mass Pull

## Autor

Desarrollado para simulación de circuitos de limpieza en flotación de cobre.
