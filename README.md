# Split Factor - Simulación de Circuitos de Flotación

Sistema de simulación de circuitos de flotación usando el método de Split Factor, con análisis Monte Carlo y visualizaciones avanzadas.

## 🚀 Inicio Rápido

### Clonar el Repositorio

```bash
git clone https://github.com/Igrojas/split-factores-refactorizado.git
cd split-factores-refactorizado
```

### Instalación de Dependencias

```bash
# Instalar dependencias
pip install -r requirements.txt
```

O si prefieres instalar manualmente:

```bash
pip install pandas numpy matplotlib seaborn tqdm openpyxl
```

## 📁 Estructura del Proyecto

```
split-factores-refactorizado/
├── splitfactor/          # Paquete principal
│   ├── core/            # Módulos core (equipos, io, simulador)
│   ├── viz/             # Visualizaciones
│   └── examples/        # Ejemplos de uso
├── data/                # Datos de entrada y resultados
│   ├── caso 1/
│   ├── caso 2/
│   ├── caso 3/
│   └── caso 4/
├── sim_3.py            # Script de simulación caso 3
├── sim_n.py            # Script de simulación caso 4
└── requirements.txt    # Dependencias del proyecto
```

## 💻 Uso

### Ejecutar Simulación Caso 3

```bash
python sim_3.py
```

### Ejecutar Simulación Caso 4

```bash
python sim_n.py
```

### Uso Programático

```python
from splitfactor.core import cargar_circuito_excel, Simulador

# Cargar circuito desde Excel
equipos, flujos = cargar_circuito_excel(
    archivo="data/caso 3/simulacion_caso_3.xlsx",
    hoja="Sim Promedio",
    id_simulacion=1
)

# Crear simulador
sim = Simulador(equipos=equipos, flujos=flujos, flujos_relave={9})

# Establecer alimentación
sim.establecer_alimentacion(id_flujo=4, masa=22.84, ley=2.16)

# Ejecutar simulación
resultado = sim.simular()
print(f"Recuperación: {resultado['recuperacion']:.2f}%")
```

## 📊 Análisis Monte Carlo

```python
from splitfactor.core import ConfiguracionMC

config = ConfiguracionMC(
    equipos_objetivo=['Jameson 1'],
    rangos={
        'Jameson 1': {
            'masa': (0.01, 0.4),
            'cuf': (0.5, 0.95)
        }
    },
    n_iteraciones=10_000,
    ley_min=2,
    ley_max=35
)

df_mc = sim.simular_montecarlo(
    config=config,
    alimentacion={4: {'masa': 22.84, 'ley': 2.16}}
)
```

## 🔧 Configuración

Los scripts `sim_3.py` y `sim_n.py` tienen una sección de configuración al inicio donde puedes modificar:

- Archivos de entrada (circuitos y split factors)
- Parámetros de simulación
- Configuración Monte Carlo
- Filtros y análisis
- Opciones de visualización

## 📦 Requisitos

- Python 3.8+
- pandas
- numpy
- matplotlib
- seaborn
- openpyxl
- tqdm

Ver `requirements.txt` para la lista completa.

## 🐛 Solución de Problemas

### Error al clonar

Si tienes problemas de permisos al clonar:

1. Verifica que tengas acceso al repositorio
2. Asegúrate de tener Git instalado: `git --version`
3. Intenta clonar con HTTPS:
   ```bash
   git clone https://github.com/Igrojas/split-factores-refactorizado.git
   ```

### Error de dependencias

Si faltan dependencias:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Archivos Excel no se abren

Los archivos Excel están incluidos en el repositorio. Si no se descargan correctamente:

```bash
git lfs pull  # Si usas Git LFS
# O simplemente
git pull
```

## 📝 Notas

- Los archivos Excel pueden ser grandes. El clonado puede tardar unos minutos.
- Los resultados de las simulaciones se guardan en `data/caso X/`
- Las gráficas se guardan en la raíz del proyecto

## 📄 Licencia

Este proyecto es de uso interno.

## 👤 Autor

Desarrollado para simulación de circuitos de limpieza en flotación de cobre.
