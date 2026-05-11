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
├── src/
│   └── snaky_snake.py       # Código principal del agente
├── experiments/
│   └── mini_experimento.py  # Experimento simple entrada→decisión→salida
├── results/
│   └── (capturas y métricas generadas al correr el sistema)
└── README.md
```

---

## Dependencias

- Python 3.10 o superior
- pygame 2.6+

Instalar dependencias:

```bash
pip install pygame
```

---

## Cómo ejecutar

### Juego completo con interfaz visual

```bash
python src/snaky_snake.py
```

### Mini experimento (entrada → decisión → salida)

```bash
python experiments/mini_experimento.py
```

---

## Ejemplo de ejecución

Al correr `mini_experimento.py`:

```
ENTRADA
  S=serpiente  F=comida

 . . . . F
 . . . . .
 . s S . .
 . . . . .
 . . . . .

DECISION  (ruta A* marcada con *)
 . . * * F
 . . * . .
 . s S . .
 . . . . .
 . . . . .

  f(n) = g(n) + h(n)  →  costo=4 pasos
  accion elegida: moverse a (1, 2)

SALIDA
 . . . . F
 . . S . .
 . . s . .
 . . . . .
 . . . . .

  nueva cabeza: (1, 2)  |  cuerpo: [(2, 2)]
```

---

## Controles del juego

| Tecla | Acción |
|-------|--------|
| `ESPACIO` | Pausar / Reanudar |
| `R` | Reiniciar |
| `+` | Aumentar velocidad |
| `-` | Disminuir velocidad |
| `Q` / `ESC` | Salir |

---

## Métricas en tiempo real

El panel inferior muestra durante la ejecución:

| Métrica | Descripción |
|---------|-------------|
| **Puntaje** | Cantidad de comidas recolectadas |
| **Movimientos** | Total de pasos ejecutados |
| **Mov/Comida** | Eficiencia promedio del agente |
| **Tiempo** | Segundos de supervivencia |

---

## Arquitectura del agente

```
Percepción → Estado → Decisión → Acción
```

| Componente | Detalle |
|------------|---------|
| **Percepción** | Posición de cabeza, cuerpo, comida y paredes |
| **Estado S** | `(cabeza, comida, cuerpo, tamaño)` |
| **Decisión** | A* + verificación Flood Fill |
| **Acción** | ↑ ↓ ← → |
| **Fallback** | Máximo espacio libre por Flood Fill |

---

## Técnicas de IA utilizadas

- **A\* (A-estrella)** — búsqueda informada con heurística admisible
- **Distancia Manhattan** — heurística h(n)
- **Flood Fill** — evaluación de espacios accesibles para supervivencia
