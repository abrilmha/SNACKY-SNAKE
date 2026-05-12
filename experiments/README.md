# Mini Experimento — SnackySnake

## Descripción

El **mini experimento** es un script que prueba la inteligencia del agente Snake en **escenarios controlados**. En lugar de jugar el juego completo, simula tres situaciones específicas que evalúan diferentes capacidades:

1. **Ruta directa** — ¿puede el agente seguir A* hacia la comida?
2. **Fallback por Flood Fill** — ¿evita quedar encerrado?
3. **Sin ruta segura** — ¿sobrevive cuando no hay opción óptima?

Cada escenario corre automáticamente y genera **métricas** (CSV, JSON, TXT) en la carpeta `results/`.

---

## Escenarios de Prueba

### **1 - Ruta directa**

**Objetivo:** Verificar que A* encuentra y sigue correctamente una ruta hacia la comida.

```
Grid inicial (5x5):
. . . . F    ← Comida en (0, 4)
. . . . .
. o H . .    ← Serpiente en (2, 2)
. . . . .
. . . . .

Secuencia esperada:
→ Cabeza sube (A*)
→ Cabeza sigue derecha
→ Come comida en (0, 4)
→ Nueva comida aparece en (4, 4)
→ Continúa persiguiendo
```

**Métricas:**
-  Pasos ejecutados
-  Puntaje (comidas consumidas)
-  Movimientos totales
-  Eficiencia (movimientos / comida)
-  Estado final (vivo: True)

---

### 2 - **Fallback por Flood Fill**

**Objetivo:** Verificar que el agente reconoce cuando una ruta segura no existe y activa el fallback.

```
Grid inicial (5x5):
F . . . .    ← Comida en (0, 0)
. o # . .    ← Serpiente rodeada de obstáculos
. o H # .    ← # = obstáculos adicionales
. . # . .
. . . . .

Situación:
- A* encuentra ruta hacia la comida
- **Pero Flood Fill detecta < 4 espacios libres**
- Fallback: moverse al vecino con más espacio
- Si no hay movimiento seguro → muerte inmediata
```

**Métricas:**
-  Pasos muy reducidos (1-2)
-  Puntaje = 0 (nunca come)
-  Estado final (vivo: False)
- Demuestra que el algoritmo es **conservador**, evitando movimientos innecesarios.

---

### 3 - **Sin ruta segura**

**Objetivo:** Verificar comportamiento cuando el agente está en una trampa potencial.

```
Grid inicial (5x5):
F # # . .    ← Comida bloqueada intencionalmente
# o o . .    ← Serpiente sin acceso directo
# o H . .    ← Muchos obstáculos
. . . . .
. . . . .

Situación:
- No hay ruta A* viable inicialmente
- El agente recurre a fallback (máximo espacio)
- Intenta escapar explorando los 4 vecinos
- Puede o no lograr alcanzar la comida
```

**Métricas:**
-  Pasos moderados (hasta 8)
-  Puntaje variable (depende del espacio disponible)
-  Demuestra **capacidad de supervivencia** sin ruta óptima

---

## Cómo ejecutar

### Desde la raíz del proyecto:
```bash
python experiments/mini_experimento.py
```

### Output esperado:
```
--- MINI EXPERIMENTO: AGENTE SNAKE ---

============================================================
ESCENARIO: Ruta directa
============================================================

--- Paso 0 ---
Estado actual:
. . . . F
. . . . .
. o H . .
. . . . .
. . . . .

Accion elegida: arriba
...

RESUMEN FINAL
------------------------------------------------------------
Ruta directa: pasos=8, puntaje=2, movimientos=8, eficiencia=4.0, vivo=True
Fallback por Flood Fill: pasos=1, puntaje=0, movimientos=0, eficiencia=—, vivo=False
Sin ruta segura: pasos=8, puntaje=0, movimientos=8, eficiencia=—, vivo=True

Archivos generados:
- C:\...\results\metrics\mini_experimento_YYYYMMDD_HHMMSS.json
- C:\...\results\metrics\mini_experimento_YYYYMMDD_HHMMSS.csv
- C:\...\results\logs\mini_experimento_YYYYMMDD_HHMMSS.txt
```

---

## Archivos generados

Cada ejecución crea tres archivos con **timestamp YYYYMMDD_HHMMSS**:

###  `mini_experimento_*.csv`
Resumen de resultados en formato tabular:

```csv
escenario,pasos,puntaje,movimientos,eficiencia,vivo
Ruta directa,8,2,8,4.0,True
Fallback por Flood Fill,1,0,0,—,False
Sin ruta segura,8,0,8,—,True
```

###  `mini_experimento_*.json`
Datos completos incluyendo historial de cada paso:

```json
{
  "timestamp": "20260511_194704",
  "grid_size": 5,
  "resultados": [
    {
      "nombre": "Ruta directa",
      "pasos_ejecutados": 8,
      "puntaje": 2,
      "movimientos": 8,
      "eficiencia": 4.0,
      "vivo": true,
      "pasos": [
        {
          "paso": 0,
          "cabeza": [2, 2],
          "accion": "arriba",
          "ruta": 4,
          "espacio": 24,
          "puntaje": 0,
          "comida": [0, 4],
          "vivo": true
        },
        ...
      ]
    }
  ]
}
```

###  `mini_experimento_*.txt`
Resumen legible en texto plano:

```
Mini experimento SnackySnake
Fecha: 20260511_194704

Escenario: Ruta directa
  Pasos ejecutados: 8
  Puntaje: 2
  Movimientos: 8
  Eficiencia: 4.0
  Vivo al final: True
...
```

---

## Interpretación de métricas

| Métrica | Qué significa | Ejemplo |
|---------|--------------|---------|
| **pasos** | Cantidad de iteraciones ejecutadas | 8 (máximo configurado) |
| **puntaje** | Comidas consumidas | 2 (comió 2 veces) |
| **movimientos** | Total de movimientos realizados | 8 |
| **eficiencia** | Movimientos por comida (ideal: bajo) | 4.0 (8 movs / 2 comidas) |
| **vivo** | ¿Sobrevivió al final? | True = sí, False = se quedó atrapado |

### Análisis por escenario:

**Ruta directa:**
- Alta eficiencia 
- Puntaje > 0
- Vivo: True
- **Interpretación:** A* funciona correctamente

**Fallback por Flood Fill:**
- Pasos = 1 (detectó peligro)
- Eficiencia = — (no comió)
- Vivo: False (**fue conservador**)
- **Interpretación:** Flood Fill funcionó, evitó trampa

**Sin ruta segura:**
- Pasos = 8 (intentó escapar)
- Variable en eficiencia (depende del espacio)
- Vivo: True o False (según la situación)
- **Interpretación:** Fallback se activo
---

## Qué valida estos experimentos

### Algoritmo A*
- ¿Encuentra caminos válidos?
- ¿Respeta obstáculos?
- ¿Es óptimo?

###  Flood Fill
- ¿Detecta espacios disponibles?
- ¿Evita trampas?
- ¿Es conservador cuando es necesario?

###  Fallback de supervivencia
- ¿Se activa cuando no hay ruta segura?
- ¿Elige el mejor vecino libre?
- ¿Mantiene el agente vivo?

###  Integración
- ¿Funcionan A* + Flood Fill juntos?
- ¿Las decisiones son coherentes?
- ¿El agente aprende a sobrevivir?

---


