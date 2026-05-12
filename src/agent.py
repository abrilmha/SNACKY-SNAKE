"""
SnakeAgent — módulo compartido con lógica de A* y Flood Fill

Este módulo contiene la lógica central del agente inteligente que juega Snake:
- Algoritmo A* para encontrar rutas óptimas hacia la comida
- Flood Fill para evaluar si una ruta nos encierra
- Clase SnakeAgent que maneja el estado y comportamiento del agente

Inteligencia Artificial — UDLAP
Abril Morales Huerta · Anellisse Herrera Maldonado · Sebastián Torres Morales
"""

import heapq
import random
import time


def manhattan(a, b):
    """
    Calcula la distancia Manhattan entre dos posiciones.
    
    Usada como heurística h(n) en el algoritmo A*.
    La distancia Manhattan es la suma de las diferencias absolutas en coordenadas.
    Es admisible porque nunca subestima la distancia real en un grid 4-conectado.
    
    Args:
        a: tupla (fila, columna) de la posición inicial
        b: tupla (fila, columna) de la posición final
    
    Returns:
        int: distancia Manhattan entre a y b
    
    Ejemplo:
        manhattan((2, 2), (0, 4)) = |2-0| + |2-4| = 2 + 2 = 4
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(start, goal, blocked, cols, rows):
    """
    Algoritmo A* para encontrar la ruta más corta desde 'start' a 'goal'.

    A* es una búsqueda informada que combina:
    - g(n): costo real desde el inicio hasta el nodo n (número de pasos)
    - h(n): heurística estimada desde n hasta la meta (distancia Manhattan)
    - f(n) = g(n) + h(n): función de evaluación total

    El algoritmo explora primero los nodos con menor f(n), garantizando
    encontrar la ruta óptima si h(n) es admisible.

    Args:
        start: tupla (fila, col) de la posición inicial (cabeza de la serpiente)
        goal: tupla (fila, col) de la posición objetivo (comida)
        blocked: conjunto de posiciones bloqueadas (cuerpo de la serpiente)
        cols: número de columnas del grid
        rows: número de filas del grid

    Returns:
        list: lista de posiciones (ruta) desde start hasta goal, o None si no existe ruta

    Ejemplo:
        ruta = astar((2, 2), (0, 4), {(2, 1), (1, 1)}, 5, 5)
        # Retorna: [(2, 2), (1, 2), (0, 2), (0, 3), (0, 4)]
    """
    h0 = manhattan(start, goal)  # estimación inicial de distancia a la meta
    counter = 0  # contador para desempate cuando dos nodos tienen igual f(n)
    heap = [(h0, counter, start, [start])]  # (f, contador, posición actual, camino)
    visited = set()  # nodos ya explorados

    while heap:
        f, _, cur, path = heapq.heappop(heap)  # extraer nodo con menor f(n)

        if cur in visited:  # si ya fue explorado, saltar
            continue
        visited.add(cur)  # marcar como explorado

        if cur == goal:  #
            return path

        # explorar los 4 vecinos (arriba, abajo, izquierda, derecha)
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nb = (cur[0] + dr, cur[1] + dc)  # posición vecina

            # verificar que el vecino es válido
            if 0 <= nb[0] < rows and 0 <= nb[1] < cols and nb not in blocked and nb not in visited:
                ng = len(path)  # g(n): costo real hasta este nodo
                counter += 1
                new_f = ng + manhattan(nb, goal)  # f(n) = g(n) + h(n)
                heapq.heappush(heap, (new_f, counter, nb, path + [nb]))

    return None  # no se encontró ruta


def flood_fill(pos, blocked, cols, rows):
    """
    Algoritmo Flood Fill para contar espacios accesibles desde una posición.

    Este algoritmo recorre recursivamente (usando una pila) todas las posiciones
    alcanzables desde 'pos' sin pasar por obstáculos. Se usa para evaluar si
    un movimiento potencial nos encierra en una región muy pequeña.

    Estrategia del agente:
    - Si la ruta A* hacia la comida deja mucho espacio libre (> len(snake) + 3),
      seguir esa ruta es seguro
    - Si no, hacer un fallback: moverse hacia el vecino con más espacio libre

    Args:
        pos: tupla (fila, col) desde donde comenzar el flood fill
        blocked: conjunto de posiciones bloqueadas (cuerpo de serpiente)
        cols: número de columnas del grid
        rows: número de filas del grid

    Returns:
        int: cantidad total de celdas alcanzables desde pos (incluyendo pos)

    Ejemplo:
        # En un grid 5x5 con la serpiente encerrada
        espacio = flood_fill((2, 2), {bloqueados}, 5, 5)
        # Retorna: 8 (sólo 8 celdas son alcanzables)
    """
    visited = {pos}  # empezar con la posición actual
    queue = [pos]  # cola para exploración (LIFO = pila)

    while queue:
        cur = queue.pop()  # sacar última posición (LIFO)

        # explorar los 4 vecinos (4-conectividad)
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nb = (cur[0] + dr, cur[1] + dc)

            # si el vecino es válido y no fue visitado, agregarlo
            if 0 <= nb[0] < rows and 0 <= nb[1] < cols and nb not in blocked and nb not in visited:
                visited.add(nb)
                queue.append(nb)

    return len(visited)  # retornar el total de celdas alcanzables


class SnakeAgent:
    """
    Agente inteligente que juega Snake de forma autónoma.

    Usa una estrategia de dos fases:
    1. A* → buscar la ruta óptima hacia la comida
    2. Flood Fill → verificar que la ruta no nos encierra

    Si la ruta segura no existe, recurre a un fallback que prioriza moverse
    hacia el vecino con más espacio libre (supervivencia).

    Atributos:
        rows: número de filas del grid (altura)
        cols: número de columnas del grid (ancho)
        snake: lista de posiciones (fila, col), primer elemento es cabeza
        food: tupla (fila, col) de la posición actual de la comida
        score: cantidad de veces que comió
        moves: cantidad total de movimientos realizados
        deaths: cantidad de veces que murió
        alive: booleano, True si la serpiente sigue viva
        path: lista de posiciones a seguir (ruta calculada por A*)
        start_time: marca de tiempo cuando comenzó el juego
        score_history: lista de (tiempo, puntaje) para análisis
        move_history: lista de movimientos por comida
    """

    def __init__(self, rows=10, cols=10):
        """
        Inicializar el agente en un grid de dimensiones rows x cols.

        Args:
            rows: número de filas (por defecto 10)
            cols: número de columnas (por defecto 10)
        """
        self.rows = rows
        self.cols = cols
        self.moves = None
        self.reset()

    def reset(self):
        """
        Reiniciar el estado del juego a su posición inicial.

        - Coloca la serpiente en el centro del grid (longitud 3)
        - Genera la primera comida en una posición aleatoria
        - Resetea todas las métricas (score, moves, deaths)
        - Inicializa el temporizador
        """
        mid_r, mid_c = self.rows // 2, self.cols // 2
        self.snake = [(mid_r, mid_c), (mid_r, mid_c - 1), (mid_r, mid_c - 2)]
        self.food = self._new_food()
        self.score = 0
        self.moves = 0
        self.deaths = 0
        self.alive = True
        self.path = []
        self.start_time = time.time()
        self.score_history = []
        self.move_history = []

    def _new_food(self):
        """
        Generar una nueva posición para la comida.

        Selecciona aleatoriamente una celda libre (no ocupada por la serpiente).

        Returns:
            tupla (fila, col) de la nueva posición de comida, o None si no hay espacio
        """
        occupied = set(self.snake) if hasattr(self, "snake") else set()
        free = [(r, c) for r in range(self.rows) for c in range(self.cols) if (r, c) not in occupied]
        return random.choice(free) if free else None

    def decide(self):
        """
        Decidir el próximo movimiento basado en la situación actual.

        Estrategia:
        1. Si ya hay una ruta válida en progreso, no recalcular
        2. Intentar A* para llegar a la comida
        3. Si A* encuentra ruta, verificar con Flood Fill que no encierra
        4. Si ruta es segura, usarla; si no, fallback a supervivencia
        5. En fallback: moverse al vecino con más espacio libre

        Esta función actualiza self.path con la ruta a seguir.
        """
        if not self.alive or self.food is None:
            return

        # si ya estamos siguiendo una ruta válida, no calcular nueva
        if self.path and len(self.path) > 1:
            return

        head = self.snake[0]
        # el cuerpo está bloqueado, excepto la última celda que se libera cuando nos movemos
        blocked = set(self.snake[1:-1])

        # FASE 1: intentar ruta A* hacia la comida
        path = astar(head, self.food, blocked, self.cols, self.rows)

        if path and len(path) > 1:
            # FASE 2: verificar que la ruta no nos encierra
            future_snake = [path[1]] + self.snake[:-1]
            future_blocked = set(future_snake[1:])
            space = flood_fill(path[1], future_blocked, self.cols, self.rows)

            # si hay suficiente espacio, la ruta es segura
            if space > len(self.snake) + 3:
                self.path = path
                return

        # FALLBACK: si no hay ruta segura, buscar supervivencia
        # mover al vecino con más espacio libre disponible
        best_move = None
        best_space = -1

        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nb = (head[0] + dr, head[1] + dc)

            # verificar que el vecino está dentro del grid y no es cuerpo
            if 0 <= nb[0] < self.rows and 0 <= nb[1] < self.cols and nb not in blocked:
                # simular el movimiento y evaluar espacio disponible
                future_snake = [nb] + self.snake[:-1]
                future_blocked = set(future_snake[1:-1])

                space = flood_fill(nb, future_blocked, self.cols, self.rows)

                # elegir el vecino que deja más espacio
                if space > best_space:
                    best_space = space
                    best_move = nb

        # establecer la ruta al mejor movimiento o dejar vacía si no hay opciones
        if best_move:
            self.path = [head, best_move]
        else:
            self.path = []

    def step(self):
        """
        Ejecutar un paso del juego.

        Secuencia:
        1. Decidir movimiento (A* + Flood Fill)
        2. Si no hay movimiento válido, morir
        3. Mover la cabeza a la nueva posición
        4. Verificar colisiones (cuerpo, paredes)
        5. Si come comida, incrementar score y generar nueva
        6. Si no come, remover la última parte de la cola

        Actualiza:
        - self.alive: False si hay colisión
        - self.snake: posición actualizada
        - self.score: incrementado si come
        - self.moves: incrementado por cada movimiento
        - self.deaths: incrementado si muere
        """
        if not self.alive:
            return

        self.decide()

        # si no hay ruta válida, la serpiente muere (atrapada)
        if not self.path or len(self.path) < 2:
            self.alive = False
            self.deaths += 1
            return

        next_pos = self.path[1]
        self.path = self.path[1:]

        # verificar colisiones
        if next_pos in self.snake or not (0 <= next_pos[0] < self.rows and 0 <= next_pos[1] < self.cols):
            self.alive = False
            self.deaths += 1
            return

        # mover la cabeza a la nueva posición
        self.snake.insert(0, next_pos)
        self.moves += 1

        # verificar si comió
        if next_pos == self.food:
            self.score += 1
            elapsed = round(time.time() - self.start_time, 1)
            self.score_history.append((elapsed, self.score))
            self.food = self._new_food()
        else:
            # si no comió, remover la cola (la serpiente no crece)
            self.snake.pop()

