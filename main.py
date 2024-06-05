import pygame
import random

# Inicialización de Pygame
pygame.init()

# Constantes de configuración
SCREEN_WIDTH, SCREEN_HEIGHT = 500, 500
GRID_SIZE = 6
CELL_SIZE = SCREEN_WIDTH // GRID_SIZE
FPS = 1

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Configuración de la pantalla
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Gato y Ratón")

# Cargar imágenes
cat_image = pygame.image.load('assets/cat.png')
mouse_image = pygame.image.load('assets/mouse.png')
exit_image = pygame.image.load('assets/exit.png')

# Escalar imágenes al tamaño de las celdas
cat_image = pygame.transform.scale(cat_image, (CELL_SIZE, CELL_SIZE))
mouse_image = pygame.transform.scale(mouse_image, (CELL_SIZE, CELL_SIZE))
exit_image = pygame.transform.scale(exit_image, (CELL_SIZE, CELL_SIZE))

# Clases para el gato y el ratón
class Cat:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.last_moves = []

    def move(self, new_pos):
        self.x, self.y = new_pos
        if len(self.last_moves) >= 2:
            self.last_moves.pop(0)
        self.last_moves.append(new_pos)

class Mouse:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.last_moves = []

    def move(self, new_pos):
        self.x, self.y = new_pos
        if len(self.last_moves) >= 2:
            self.last_moves.pop(0)
        self.last_moves.append(new_pos)

# Función para dibujar el tablero y las entidades
def draw_board(cat, mouse, exit_pos):
    screen.fill(WHITE)
    for x in range(0, SCREEN_WIDTH, CELL_SIZE):
        for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, BLACK, rect, 1)
    screen.blit(exit_image, (exit_pos[1] * CELL_SIZE, exit_pos[0] * CELL_SIZE))
    screen.blit(cat_image, (cat.y * CELL_SIZE, cat.x * CELL_SIZE))
    screen.blit(mouse_image, (mouse.y * CELL_SIZE, mouse.x * CELL_SIZE))
    pygame.display.flip()

def minimax(cat_pos, mouse_pos, exit_pos, depth, is_maximizing, last_moves_cat=None, last_moves_mouse=None):
    if cat_pos == mouse_pos:
        return 20 + depth
    if mouse_pos == exit_pos:
        return -20 - depth
    if depth == 0:
        return manhattan_distance(mouse_pos, exit_pos) - manhattan_distance(cat_pos, mouse_pos)

    if is_maximizing:
        max_eval = float('-inf')
        for move in get_valid_moves(cat_pos, is_cat=True, last_moves=last_moves_cat):
            evaluation = minimax(move, mouse_pos, exit_pos, depth - 1, False, last_moves_cat, last_moves_mouse)
            max_eval = max(max_eval, evaluation)
        return max_eval
    else:
        min_eval = float('inf')
        for move in get_valid_moves(mouse_pos, is_cat=False, last_moves=last_moves_mouse):
            evaluation = minimax(cat_pos, move, exit_pos, depth - 1, True, last_moves_cat, last_moves_mouse)
            min_eval = min(min_eval, evaluation)
        return min_eval

def get_best_move(pos, target_pos, exit_pos, is_cat, last_moves_cat=None, last_moves_mouse=None):
    best_move = None
    best_value = float('-inf') if is_cat else float('inf')
    for move in get_valid_moves(pos, is_cat, last_moves_cat if is_cat else last_moves_mouse):
        if is_cat:
            move_value = minimax(move, target_pos, exit_pos, 3, False, last_moves_cat, last_moves_mouse)
            if move_value > best_value:
                best_value = move_value
                best_move = move
        else:
            move_value = minimax(target_pos, move, exit_pos, 3, True, last_moves_cat, last_moves_mouse)
            if move_value < best_value:
                best_value = move_value
                best_move = move
    return best_move

def get_valid_moves(pos, is_cat, last_moves=None):
    moves = []
    if is_cat:
        # Movimientos del gato (arriba, abajo, izquierda, derecha y saltos de dos cuadros)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                      (-2, 0), (2, 0), (0, -2), (0, 2)]
    else:
        # Movimientos del ratón (arriba, abajo, izquierda, derecha, y diagonales)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                      (-1, -1), (-1, 1), (1, -1), (1, 1)]
    for d in directions:
        new_pos = (pos[0] + d[0], pos[1] + d[1])
        if 0 <= new_pos[0] < GRID_SIZE and 0 <= new_pos[1] < GRID_SIZE:
            if last_moves is None or new_pos not in last_moves:
                moves.append(new_pos)
    return moves

def manhattan_distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# Inicialización de posiciones
cat = Cat(random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
mouse = Mouse(random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
exit_pos = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))

while exit_pos == (cat.x, cat.y) or exit_pos == (mouse.x, mouse.y):
    exit_pos = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))

# Bucle principal del juego
running = True
clock = pygame.time.Clock()
pygame.display.flip()

round_counter = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Movimiento del ratón
    mouse_move = get_best_move((mouse.x, mouse.y), (cat.x, cat.y), exit_pos, False, cat.last_moves, mouse.last_moves)
    if mouse_move:
        mouse.move(mouse_move)

    # Verificar si el ratón ha ganado
    if (mouse.x, mouse.y) == exit_pos:
        print("¡El ratón ha ganado!")
        running = False

    # Movimiento del gato
    cat_move = get_best_move((cat.x, cat.y), (mouse.x, mouse.y), exit_pos, True, cat.last_moves, mouse.last_moves)
    if cat_move:
        cat.move(cat_move)

    # Verificar si el gato ha ganado
    if (cat.x, cat.y) == (mouse.x, mouse.y):
        print("¡El gato ha ganado!")
        running = False

    # Incrementar contador de rondas y verificar empate
    round_counter += 1
    if round_counter >= 13:
        print("¡Empate!")
        running = False

    # Dibuja el tablero y las entidades
    draw_board(cat, mouse, exit_pos)

    # Control de la velocidad del juego
    clock.tick(FPS)

pygame.quit()
