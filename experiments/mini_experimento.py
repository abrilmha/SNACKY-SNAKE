from __future__ import annotations

import csv
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Iterable

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent import astar, flood_fill

GRID_SIZE = 5
ROOT_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT_DIR / "results"
METRICS_DIR = RESULTS_DIR / "metrics"
LOGS_DIR = RESULTS_DIR / "logs"


@dataclass
class StepRecord:
    paso: int
    cabeza: tuple[int, int]
    accion: str
    ruta: int
    espacio: int
    puntaje: int
    comida: tuple[int, int] | None
    vivo: bool


@dataclass
class ScenarioResult:
    nombre: str
    pasos_ejecutados: int
    puntaje: int
    movimientos: int
    eficiencia: float | str
    vivo: bool
    pasos: list[StepRecord]


def vecinos(pos: tuple[int, int]) -> dict[str, tuple[int, int]]:
    return {
        "arriba": (pos[0] - 1, pos[1]),
        "abajo": (pos[0] + 1, pos[1]),
        "izquierda": (pos[0], pos[1] - 1),
        "derecha": (pos[0], pos[1] + 1),
    }



def mostrar_grid(
    snake: list[tuple[int, int]],
    food: tuple[int, int] | None,
    size: int,
    bloqueados_extra: set[tuple[int, int]] | None = None,
) -> None:
    grid = [["." for _ in range(size)] for _ in range(size)]
    bloqueados_extra = bloqueados_extra or set()

    for x, y in bloqueados_extra:
        if 0 <= x < size and 0 <= y < size:
            grid[x][y] = "#"

    if food is not None:
        fx, fy = food
        grid[fx][fy] = "F"

    for x, y in snake[1:]:
        grid[x][y] = "o"

    hx, hy = snake[0]
    grid[hx][hy] = "H"

    for fila in grid:
        print(" ".join(fila))


def decidir_movimiento(
    snake: list[tuple[int, int]],
    food: tuple[int, int] | None,
    bloqueados_extra: set[tuple[int, int]],
) -> tuple[str, tuple[int, int] | None, int, int]:
    cabeza = snake[0]
    if food is None:
        return "sin_comida", None, 0, 0

    cuerpo = set(snake[1:]) | bloqueados_extra
    ruta = astar(cabeza, food, cuerpo, GRID_SIZE, GRID_SIZE)

    if ruta and len(ruta) > 1:
        siguiente = ruta[1]
        futura_serpiente = [siguiente] + snake[:-1]
        futuros_bloqueados = set(futura_serpiente[1:]) | bloqueados_extra
        espacio = flood_fill(siguiente, futuros_bloqueados, GRID_SIZE, GRID_SIZE)
        if espacio > len(snake) + 1:
            return _accion_desde(cabeza, siguiente), siguiente, len(ruta) - 1, espacio

    mejor: tuple[int, int] | None = None
    mejor_espacio = -1
    mejor_accion = "sin_movimiento"

    for accion, vecino in vecinos(cabeza).items():
        if vecino in cuerpo or not (0 <= vecino[0] < GRID_SIZE and 0 <= vecino[1] < GRID_SIZE):
            continue
        futura_serpiente = [vecino] + snake[:-1]
        futuros_bloqueados = set(futura_serpiente[1:]) | bloqueados_extra
        espacio = flood_fill(vecino, futuros_bloqueados, GRID_SIZE, GRID_SIZE)
        if espacio > mejor_espacio:
            mejor_espacio = espacio
            mejor = vecino
            mejor_accion = accion

    return mejor_accion, mejor, 1 if mejor else 0, max(mejor_espacio, 0)


def _accion_desde(origen: tuple[int, int], destino: tuple[int, int]) -> str:
    if destino[0] < origen[0]:
        return "arriba"
    if destino[0] > origen[0]:
        return "abajo"
    if destino[1] < origen[1]:
        return "izquierda"
    return "derecha"


def simular_escenario(
    nombre: str,
    snake_inicial: list[tuple[int, int]],
    comida_inicial: tuple[int, int] | None,
    bloqueados_extra: set[tuple[int, int]] | None = None,
    comida_siguiente: Iterable[tuple[int, int] | None] | None = None,
    max_pasos: int = 8,
) -> ScenarioResult:
    snake = list(snake_inicial)
    food = comida_inicial
    bloqueados_extra = bloqueados_extra or set()
    comidas = list(comida_siguiente or [])
    registros: list[StepRecord] = []
    score = 0
    movimientos = 0
    vivo = True

    print("\n" + "=" * 60)
    print(f"ESCENARIO: {nombre}")
    print("=" * 60)

    for paso in range(max_pasos):
        print(f"\n--- Paso {paso} ---")
        print("Estado actual:")
        mostrar_grid(snake, food, GRID_SIZE, bloqueados_extra)

        accion, siguiente, ruta, espacio = decidir_movimiento(snake, food, bloqueados_extra)
        if siguiente is None:
            vivo = False
            registros.append(
                StepRecord(paso, snake[0], accion, ruta, espacio, score, food, vivo)
            )
            print("\nAccion: no hay movimiento seguro")
            break

        print(f"\nAccion elegida: {accion}")
        nueva_cabeza = siguiente
        nueva_serpiente = [nueva_cabeza] + snake[:-1]
        movimientos += 1

        if food is not None and nueva_cabeza == food:
            score += 1
            food = comidas.pop(0) if comidas else None
            if food is not None:
                print(f"Comida consumida. Nueva comida: {food}")
            else:
                print("Comida consumida. No quedan mas objetivos.")

        snake = nueva_serpiente
        registros.append(
            StepRecord(paso, snake[0], accion, ruta, espacio, score, food, vivo)
        )

        print("Nuevo estado:")
        mostrar_grid(snake, food, GRID_SIZE, bloqueados_extra)

        if food is None:
            break

    eficiencia: float | str = round(movimientos / score, 2) if score else "—"
    return ScenarioResult(nombre, len(registros), score, movimientos, eficiencia, vivo, registros)


def crear_salidas(resultados: list[ScenarioResult]) -> tuple[Path, Path]:
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    reporte_json = METRICS_DIR / f"mini_experimento_{timestamp}.json"
    reporte_csv = METRICS_DIR / f"mini_experimento_{timestamp}.csv"
    reporte_txt = LOGS_DIR / f"mini_experimento_{timestamp}.txt"

    payload = {
        "timestamp": timestamp,
        "grid_size": GRID_SIZE,
        "resultados": [
            {
                **asdict(resultado),
                "pasos": [asdict(paso) for paso in resultado.pasos],
            }
            for resultado in resultados
        ],
    }

    with reporte_json.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)

    with reporte_csv.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["escenario", "pasos", "puntaje", "movimientos", "eficiencia", "vivo"])
        for resultado in resultados:
            writer.writerow(
                [
                    resultado.nombre,
                    resultado.pasos_ejecutados,
                    resultado.puntaje,
                    resultado.movimientos,
                    resultado.eficiencia,
                    resultado.vivo,
                ]
            )

    lineas = [
        "Mini experimento SnackySnake",
        f"Fecha: {timestamp}",
        "",
    ]
    for resultado in resultados:
        lineas.extend(
            [
                f"Escenario: {resultado.nombre}",
                f"  Pasos ejecutados: {resultado.pasos_ejecutados}",
                f"  Puntaje: {resultado.puntaje}",
                f"  Movimientos: {resultado.movimientos}",
                f"  Eficiencia: {resultado.eficiencia}",
                f"  Vivo al final: {resultado.vivo}",
                "",
            ]
        )

    reporte_txt.write_text("\n".join(lineas), encoding="utf-8")
    return reporte_json, reporte_csv


def main() -> None:
    print("\n--- MINI EXPERIMENTO: AGENTE SNAKE ---")
    escenarios = [
        (
            "Ruta directa",
            [(2, 2), (2, 1)],
            (0, 4),
            set(),
            [(4, 4)],
        ),
        (
            "Fallback por Flood Fill",
            [(2, 2), (2, 1), (1, 1)],
            (0, 0),
            {(1, 2), (2, 3), (3, 2)},
            [(4, 0)],
        ),
        (
            "Sin ruta segura",
            [(2, 2), (2, 1), (1, 1), (1, 2)],
            (0, 0),
            {(0, 1), (1, 0), (2, 0), (0, 2)},
            [],
        ),
    ]

    resultados = [
        simular_escenario(nombre, snake, food, bloqueados, comida_siguiente=comidas)
        for nombre, snake, food, bloqueados, comidas in escenarios
    ]

    reporte_json, reporte_csv = crear_salidas(resultados)

    print("\nRESUMEN FINAL")
    print("-" * 60)
    for resultado in resultados:
        print(
            f"{resultado.nombre}: pasos={resultado.pasos_ejecutados}, "
            f"puntaje={resultado.puntaje}, movimientos={resultado.movimientos}, "
            f"eficiencia={resultado.eficiencia}, vivo={resultado.vivo}"
        )

    print("\nArchivos generados:")
    print(f"- {reporte_json}")
    print(f"- {reporte_csv}")
    print(f"- {LOGS_DIR}")


if __name__ == "__main__":
    main()
