import heapq

GRID_SIZE = 5
snake = [(2, 2), (2, 1)]  # cabeza, cuerpo
food = (0, 4)

def heuristica(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def vecinos(pos):
    return {
        "arriba": (pos[0]-1, pos[1]),
        "abajo": (pos[0]+1, pos[1]),
        "izquierda": (pos[0], pos[1]-1),
        "derecha": (pos[0], pos[1]+1)
    }

def es_valido(pos, bloqueados):
    return 0 <= pos[0] < GRID_SIZE and 0 <= pos[1] < GRID_SIZE and pos not in bloqueados

def astar(inicio, meta, bloqueados):
    heap = [(heuristica(inicio, meta), 0, inicio, [inicio])]
    visitados = set()
    
    while heap:
        f, g, actual, camino = heapq.heappop(heap)
        
        if actual in visitados:
            continue
        visitados.add(actual)
        
        if actual == meta:
            return camino
        
        for vecino in vecinos(actual).values():
            if es_valido(vecino, bloqueados):
                heapq.heappush(heap, (g+1+heuristica(vecino, meta), g+1, vecino, camino+[vecino]))
    
    return None

# --- GRID VISUAL ---
def mostrar_grid(snake, food, size):
    grid = [["." for _ in range(size)] for _ in range(size)]
    
    fx, fy = food
    grid[fx][fy] = "F" #F para la comida
    
    for x, y in snake[1:]:
        grid[x][y] = "o" #o para el cuerpo
    
    hx, hy = snake[0]
    grid[hx][hy] = "H" #H para la cabeza
    
    for fila in grid:
        print(" ".join(fila))

# --- SIMULACIÓN ---
print("\n--- MINI EXPERIMENTO: AGENTE SNAKE ---")

for paso in range(3):
    print("\n----------------------")
    print(f"Paso {paso}")
    
    # Estado actual
    print("\nEstado actual:")
    mostrar_grid(snake, food, GRID_SIZE)
    
    # Decisión
    ruta = astar(snake[0], food, set(snake[1:]))
    
    if ruta is None:
        print("\nAcción: No hay ruta segura")
        break
    
    siguiente = ruta[1]
    acciones = vecinos(snake[0])
    accion = [k for k,v in acciones.items() if v == siguiente][0]
    
    print(f"\nAcción elegida: {accion}")
    
    # Nuevo estado
    nueva_snake = [siguiente] + snake[:-1]
    
    print("\nNuevo estado:")
    mostrar_grid(nueva_snake, food, GRID_SIZE)
    
    # actualizar
    snake = nueva_snake
