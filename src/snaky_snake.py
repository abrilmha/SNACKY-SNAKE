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

import time
import pygame
from agent import SnakeAgent


#  CONFIGURACIÓN

CELL       = 32          # píxeles por celda
COLS       = 10         # columnas del grid
ROWS       = 10          # filas del grid
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


# Las funciones A*, Flood Fill y la clase SnakeAgent
# se importan desde agent.py para mantener código compartido



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
    agent  = SnakeAgent(ROWS, COLS)
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
                    agent = SnakeAgent(ROWS, COLS)
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
