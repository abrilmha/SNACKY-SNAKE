"""
SnackySnake — Agente Inteligente con A*
Inteligencia Artificial — UDLAP
Abril Morales Huerta · Anellisse Herrera Maldonado · Sebastián Torres Morales

Controles:
  ESPACIO  — pausar / reanudar
  R        — reiniciar
  +/-      — velocidad
  Q / ESC  — salir
"""

import pygame
import heapq
import random
import time


#  CONFIGURACIÓN

CELL       = 32          # píxeles por celda
COLS       = 20          # columnas del grid
ROWS       = 18          # filas del grid
W          = COLS * CELL
H          = ROWS * CELL
PANEL_H    = 140         # panel inferior de métricas
FPS_BASE   = 2       # velocidad inicial (pasos/seg)

# Paleta
BG         = (15,  17,  21)
GRID_C     = (25,  28,  35)
HEAD_C     = (56, 189, 248)   # azul celeste
BODY_C     = (20, 120, 160)
FOOD_C     = (251,  82,  82)  # rojo
PATH_C     = (255, 200,  60, 60)  # amarillo transparente
TEXT_C     = (200, 210, 220)
DIM_C      = (90, 100, 115)
PANEL_C    = (20,  23,  30)
GREEN_C    = (52, 211, 153)
AMBER_C    = (251, 191,  36)


# 
#  HEURÍSTICA Y A*
#

# distancia Manhattan porque solo nos movemos
# arriba, abajo, izquierda y derecha (4-conectividad)
def manhattan(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

# algoritmo A*
# aquí buscamos la ruta más corta hacia la comida
def astar(start, goal, blocked, cols, rows):
    # Devuelve lista de celdas desde start hasta goal, o None.
    h0 = manhattan(start, goal)
    # usamos un heap para manejar prioridades
    heap = [(h0, 0, start, [start])]
    #revisamos nodos ya visitados para evitar ciclos
    visited = set()

    while heap:
        #heapq devuelve el nodo con menor f = g + h
        f, g, cur, path = heapq.heappop(heap)
        # si ya visitamos esta celda, la ignoramos
        if cur in visited:
            continue
        visited.add(cur)
        # si llegamos a la meta, devolvemos el camino
        if cur == goal:
            return path
        # exploramos vecinos (arriba, abajo, izquierda, derecha)
        for dr, dc in ((-1,0),(1,0),(0,-1),(0,1)):
            nb = (cur[0]+dr, cur[1]+dc)
            # verificamos que el vecino esté dentro del grid, no sea un bloqueado/choque con el cuerpo y no lo hayamos visitado
            if 0 <= nb[0] < rows and 0 <= nb[1] < cols and nb not in blocked and nb not in visited:
                ng = g + 1
                heapq.heappush(heap, (ng + manhattan(nb, goal), ng, nb, path+[nb]))
    return None



#  FLOOD FILL — contar espacios accesibles desde pos

# esta función nos ayuda a evaluar si una ruta nos encierra o no
def flood_fill(pos, blocked, cols, rows):
    visited = {pos}
    queue   = [pos]
    while queue:
        cur = queue.pop()
        for dr, dc in ((-1,0),(1,0),(0,-1),(0,1)):
            nb = (cur[0]+dr, cur[1]+dc)
            if 0 <= nb[0] < rows and 0 <= nb[1] < cols and nb not in blocked and nb not in visited:
                visited.add(nb)
                queue.append(nb)
    return len(visited)



#  AGENTE

class SnakeAgent:
    def __init__(self):
        self.reset()
# el método reset inicializa o reinicia el estado del juego, colocando la serpiente en el centro, generando la primera comida y reseteando las métricas y el historial.
    def reset(self):
        mid_r, mid_c = ROWS//2, COLS//2
        self.snake  = [(mid_r, mid_c), (mid_r, mid_c-1), (mid_r, mid_c-2)]
        self.food   = self._new_food()
        self.score  = 0
        self.moves  = 0
        self.deaths = 0
        self.alive  = True
        self.path   = []
        self.start_time = time.time()
        self.score_history = []   # (tiempo, puntaje)
        self.move_history  = []   # movimientos por comida
# el método _new_food genera una nueva posición para la comida, asegurándose de que no esté ocupada por la serpiente. 
# Primero crea un conjunto de las posiciones ocupadas por la serpiente, luego genera una lista de celdas libres y finalmente elige una al azar.
    def _new_food(self):
        occupied = set(self.snake) if hasattr(self, 'snake') else set()
        free = [(r,c) for r in range(ROWS) for c in range(COLS) if (r,c) not in occupied]
        return random.choice(free) if free else None

    # decidir el próximo movimiento basado en la situación actual
    def decide(self):
        if not self.alive or self.food is None:
            return

        head    = self.snake[0]
        # bloqueamos las celdas ocupadas por el cuerpo de la serpiente (excepto la cabeza) para evitar colisiones
        blocked = set(self.snake[1:])

        # 1) Intentar ruta directa A* hacia la comida
        path = astar(head, self.food, blocked, COLS, ROWS)

        if path and len(path) > 1:
            # Verificar que tomar esa ruta no nos encierra
            # Simulamos el movimiento y hacemos flood fill
            future_snake = [path[1]] + self.snake[:-1]
            future_blocked = set(future_snake[1:])
            space = flood_fill(path[1], future_blocked, COLS, ROWS)

            if space > len(self.snake):      # hay espacio suficiente
                self.path = path
                return

        # 2) Fallback: moverse al vecino con más espacio libre (sobrevivir)
        # si no encontramos ruta segura, intentamos sobrevivir moviéndonos al vecino con más espacio libre
        best_move  = None
        best_space = -1
        for dr, dc in ((-1,0),(1,0),(0,-1),(0,1)):
            nb = (head[0]+dr, head[1]+dc)
            if 0 <= nb[0] < ROWS and 0 <= nb[1] < COLS and nb not in blocked:
                space = flood_fill(nb, blocked, COLS, ROWS)
                if space > best_space:
                    best_space = space
                    best_move  = nb

        if best_move:
            self.path = [head, best_move]
        else:
            self.path = []   # sin salida

    # ejecutar un paso del juego: decidir movimiento, actualizar posición, verificar colisiones, comer comida y actualizar métricas
    def step(self):
        if not self.alive:
            return

        self.decide()
    # si no hay ruta o la ruta es demasiado corta, significa que estamos atrapados o sin opciones, lo que resulta en la muerte de la serpiente.
        if not self.path or len(self.path) < 2:
            self.alive  = False
            self.deaths += 1
            return

        next_pos = self.path[1]
        self.path = self.path[1:]

        # colisión con el cuerpo o paredes
        if next_pos in self.snake or \
           not (0 <= next_pos[0] < ROWS and 0 <= next_pos[1] < COLS):
            self.alive  = False
            self.deaths += 1
            return

        self.snake.insert(0, next_pos)
        self.moves += 1
# si la serpiente come la comida, incrementamos el puntaje, registramos el tiempo y movimientos, y generamos nueva comida.
        if next_pos == self.food:
            self.score += 1
            elapsed = round(time.time() - self.start_time, 1)
            self.score_history.append((elapsed, self.score))
            self.food = self._new_food()
        else:
            self.snake.pop()



#  RENDER

def draw_rounded(surf, color, rect, r=6):
    pygame.draw.rect(surf, color, rect, border_radius=r)

def render(screen, agent, font_sm, font_md, font_lg, path_surf, fps, paused):
    screen.fill(BG)

    # grid de fondo
    for r in range(ROWS):
        for c in range(COLS):
            if (r+c) % 2 == 0:
                pygame.draw.rect(screen, GRID_C, (c*CELL, r*CELL, CELL, CELL))

    # ruta A* (transparente)
    if agent.path:
        for (r,c) in agent.path[1:-1]:
            path_surf.fill((0,0,0,0))
            pygame.draw.rect(path_surf, PATH_C, (c*CELL+4, r*CELL+4, CELL-8, CELL-8), border_radius=4)
            screen.blit(path_surf, (0,0))

    # cuerpo
    for i, (r,c) in enumerate(agent.snake[1:], 1):
        draw_rounded(screen, BODY_C, (c*CELL+2, r*CELL+2, CELL-4, CELL-4), 5)

    # cabeza
    if agent.snake:
        r,c = agent.snake[0]
        draw_rounded(screen, HEAD_C, (c*CELL+1, r*CELL+1, CELL-2, CELL-2), 7)
        # ojos
        eye_size = 4
        pygame.draw.circle(screen, BG, (c*CELL+8,  r*CELL+9),  eye_size)
        pygame.draw.circle(screen, BG, (c*CELL+22, r*CELL+9),  eye_size)

    # comida
    if agent.food:
        fr, fc = agent.food
        cx, cy = fc*CELL + CELL//2, fr*CELL + CELL//2
        pygame.draw.circle(screen, FOOD_C, (cx, cy), CELL//2 - 3)
        pygame.draw.circle(screen, (255,130,130), (cx-3, cy-3), 4)

    # ── panel de métricas ──────────────────────────
    panel_y = H
    pygame.draw.rect(screen, PANEL_C, (0, panel_y, W, PANEL_H))
    pygame.draw.line(screen, GRID_C, (0, panel_y), (W, panel_y), 2)

    elapsed = round(time.time() - agent.start_time, 1)
    eff     = round(agent.moves / agent.score, 1) if agent.score else "—"

    labels = [
        ("PUNTAJE",    str(agent.score),         GREEN_C),
        ("MOVIMIENTOS",str(agent.moves),          TEXT_C),
        ("MOV/COMIDA", str(eff),                  AMBER_C),
        ("TIEMPO (s)", str(elapsed),              TEXT_C),
        ("FPS",        str(fps),                  DIM_C),
    ]

    col_w = W // len(labels)
    for i, (lbl, val, color) in enumerate(labels):
        x = i * col_w + col_w//2
        txt_l = font_sm.render(lbl, True, DIM_C)
        txt_v = font_md.render(val, True, color)
        screen.blit(txt_l, txt_l.get_rect(centerx=x, top=panel_y+12))
        screen.blit(txt_v, txt_v.get_rect(centerx=x, top=panel_y+34))

    # barra de estado
    if not agent.alive:
        msg = font_lg.render("GAME OVER — R para reiniciar", True, FOOD_C)
        screen.blit(msg, msg.get_rect(centerx=W//2, top=panel_y+80))
    elif paused:
        msg = font_lg.render("PAUSADO — ESPACIO para continuar", True, AMBER_C)
        screen.blit(msg, msg.get_rect(centerx=W//2, top=panel_y+80))
    else:
        hint = font_sm.render("ESPACIO pausar  |  R reiniciar  |  +/- velocidad  |  Q salir", True, DIM_C)
        screen.blit(hint, hint.get_rect(centerx=W//2, top=panel_y+85))

    pygame.display.flip()



#  MAIN

def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H + PANEL_H))
    pygame.display.set_caption("SnackySnake — Agente A*")

    font_sm = pygame.font.SysFont("monospace", 12, bold=False)
    font_md = pygame.font.SysFont("monospace", 22, bold=True)
    font_lg = pygame.font.SysFont("monospace", 16, bold=True)

    path_surf = pygame.Surface((W, H), pygame.SRCALPHA)

    clock  = pygame.time.Clock()
    agent  = SnakeAgent()
    fps    = FPS_BASE
    paused = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); return
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    pygame.quit(); return
                if event.key == pygame.K_r:
                    agent = SnakeAgent()
                    paused = False
                if event.key == pygame.K_SPACE:
                    paused = not paused
                if event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    fps = min(fps + 2, 60)
                if event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    fps = max(fps - 2, 2)

        if not paused and agent.alive:
            agent.step()

        render(screen, agent, font_sm, font_md, font_lg, path_surf, fps, paused)
        clock.tick(fps)


if __name__ == "__main__":
    main()
