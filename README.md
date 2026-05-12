# SnackySnake — Agente Inteligente con A*

**Inteligencia Artificial — Universidad de las Américas Puebla**  
- Abril Morales Huerta - 181278
- Anellisse Herrera Maldonado - 181565
- Sebastián Torres Morales - 179763

---

## Descripción

SnackySnake es un agente inteligente que juega Snake de forma autónoma usando el algoritmo **A\*** para encontrar la ruta óptima hacia la comida, combinado con **Flood Fill** para evitar quedarse encerrado.

El agente toma decisiones en cada paso siguiendo la función:

```
a* = argmin f(s, a)   donde   f(n) = g(n) + h(n)
```

- `g(n)` — costo acumulado desde la cabeza hasta el nodo n  
- `h(n)` — heurística: distancia Manhattan hacia la comida  

Si la ruta óptima pone en riesgo la supervivencia, el agente activa un modo de **fallback por flood fill** que prioriza moverse hacia el área con más espacio libre.

---

## Estructura del repositorio

```
SnackySnake/              
├── requirements.txt             # Dependencias (pygame 2.6.1)
│
├── src/
│   ├── agent.py                 # 
│   │   ├── manhattan()          #    - Heurística A*
│   │   ├── astar()              #    - Algoritmo de búsqueda
│   │   ├── flood_fill()         #    - Evaluación de espacios
│   │   └── class SnakeAgent     #    - Agente inteligente
│   │
│   └── snaky_snake.py           #  Juego principal con pygame
│
├── experiments/
│   ├── README.md                #  Documentación de experimentos
│   └── mini_experimento.py      #  3 escenarios de prueba
│       ├── "Ruta directa"
│       ├── "Fallback por Flood Fill"
│       └── "Sin ruta segura"
│
└── results/
    ├── README.md                # Info sobre resultados
    ├── metrics/                 # CSV y JSON generados
    ├── logs/                    # Resúmenes en TXT
```


## Dependencias

- **Python:** 3.10 a 3.13
- **pygame:** 2.6.1

## Cómo correr el proyecto

Si vas a clonar el repositorio desde cero, estos son los pasos recomendados.

### 1. Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd SNACKY-SNAKE
```

Si ya tienes la carpeta en tu equipo, solo abre una terminal dentro de `SNACKY-SNAKE`.

### 2. Instalar dependencias

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Ejecutar el juego principal

```bash
python src/snaky_snake.py
```

Controles del juego:
- `ESPACIO` para pausar o reanudar
- `R` para reiniciar la partida
- `+` y `-` para subir o bajar la velocidad
- `Q` o `ESC` para salir

### 4. Ejecutar el mini experimento

```bash
python experiments/mini_experimento.py
```

Ese script corre tres escenarios de prueba:
1. Ruta directa: verifica que A* encuentre la comida.
2. Fallback por Flood Fill: comprueba que el agente no se meta en trampas.
3. Sin ruta segura: prueba el comportamiento de supervivencia.

Al terminar, se generan archivos en `results/` con métricas en CSV, JSON y TXT.

---

## Métricas en tiempo real (juego principal)

El panel inferior muestra durante la ejecución:

| Métrica | Descripción |
|---------|-------------|
| **PUNTAJE** | Comidas recolectadas |
| **MOVIMIENTOS** | Total de pasos ejecutados |
| **MOV/COMIDA** | Eficiencia (movimientos ÷ comidas) |
| **TIEMPO (s)** | Segundos de supervivencia |
| **FPS** | Velocidad actual (configurable con +/-) |

---

## Arquitectura del agente

### Ciclo de decisión

```
┌─────────────────────────────────────────┐
│ PERCEPCIÓN (posición de todo)           │
├─────────────────────────────────────────┤
│ ESTADO (cabeza, comida, cuerpo, grid)   │
├─────────────────────────────────────────┤
│ DECISIÓN:                               │
│  1. A* → buscar ruta a comida           │
│  2. Flood Fill → verificar seguridad    │
│  3. Si es seguro → usar ruta A*         │
│  4. Si no → FALLBACK (máximo espacio)   │
├─────────────────────────────────────────┤
│ ACCIÓN (↑ ↓ ← →)                       │
├─────────────────────────────────────────┤
│ EJECUCIÓN  (movimiento + colisiones)    │
└─────────────────────────────────────────┘
```

### Componentes principales

| Componente | Ubicación | Función |
|-----------|-----------|---------|
| **manhattan(a, b)** | `src/agent.py` | Heurística h(n) para A* |
| **astar(...)** | `src/agent.py` | Búsqueda informada de rutas |
| **flood_fill(...)** | `src/agent.py` | Evaluación de espacios libres |
| **SnakeAgent** | `src/agent.py` | Agente con método `step()` |
| **snaky_snake.py** | `src/` | Interfaz visual (pygame) |
| **mini_experimento.py** | `experiments/` | Testing de escenarios |

### Estrategia del agente

**FASE 1: Búsqueda óptima**
- Usar A* para encontrar la ruta más corta a la comida
- Heurística: distancia Manhattan (siempre subestima)
- Garantiza ruta óptima si existe

**FASE 2: Validación de seguridad**
- Simular el primer paso de la ruta A*
- Usar Flood Fill para contar espacio accesible  
- Si espacio >= len(snake) + 3 → ruta es segura

**FASE 3: Fallback (si no hay ruta segura)**
- Evaluar los 4 vecinos de la cabeza
- Para cada vecino, calcular espacio libre con Flood Fill
- Mover al vecino con **máximo espacio** (supervivencia)

---

## Técnicas de IA utilizadas

###  A* (A-Estrella)
- **Tipo:** Algoritmo de búsqueda informada
- **Función:** f(n) = g(n) + h(n)
  - g(n): costo real (número de pasos)
  - h(n): heurística (distancia Manhattan)
- **Garantía:** Encuentra la ruta óptima si h(n) es admisible
- **Complejidad:** O(n log n) en el peor caso

### Distancia Manhattan
- **Definición:** |x₁ - x₂| + |y₁ - y₂|
- **Uso:** Heurística h(n) para A*
- **Propiedad:** Admisible en grids 4-conectados (nunca subestima)
- **Ejemplo:** Manhattan((2,2), (0,4)) = |2-0| + |2-4| = 4

### Flood Fill
- **Tipo:** DFS (Depth-First Search) iterativo
- **Función:** Contar espacios alcanzables desde una posición
- **Uso:** Validar si una ruta nos encierra
- **Estrategia:** Si espacio libre < len(serpiente) + 3 → ruta insegura


---

