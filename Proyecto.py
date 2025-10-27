import pygame
import random
import sys
import time

# Inicializar Pygame
pygame.init()

# Constantes de configuración
WIDTH, HEIGHT = 600, 700  # Ancho y alto de la ventana (espacio extra para UI)
GRID_SIZE = 10  # Tamaño de la cuadrícula (10x10)
CELL_SIZE = 50  # Tamaño de cada celda en píxeles
NUM_MINES = 15  # Número de minas (configurable)
FPS = 30  # Frames por segundo para animaciones

# Colores coherentes para la interfaz
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Fuente para texto
FONT = pygame.font.SysFont("Arial", 24)
SMALL_FONT = pygame.font.SysFont("Arial", 18)

class Minesweeper:
    """
    Clase principal del juego Buscaminas. Maneja la lógica del juego, la interfaz y las mecánicas.
    """
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Buscaminas Simplificado")
        self.clock = pygame.time.Clock()
        
        # Estado del juego
        self.grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]  # 0: vacío, -1: mina
        self.revealed = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]  # Celdas reveladas
        self.flagged = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]  # Celdas marcadas
        self.mines = []  # Lista de posiciones de minas
        self.game_over = False
        self.won = False
        self.start_time = time.time()  # Temporizador
        self.score = 0  # Puntuación basada en tiempo
        
        # Animaciones: diccionario para opacidad de celdas reveladas
        self.reveal_animation = {}  # {(x, y): opacidad}
        
        # Generar minas y calcular números adyacentes
        self.generate_mines()
        self.calculate_numbers()
        
        # Botón de reinicio
        self.reset_button = pygame.Rect(WIDTH // 2 - 50, HEIGHT - 60, 100, 40)
        
        # Modo fácil (menos minas, activable al inicio)
        self.easy_mode = False  # Por defecto, modo normal

    def generate_mines(self):
        """
        Genera minas aleatorias en la cuadrícula, evitando posiciones ya ocupadas.
        Usa random.sample para asegurar unicidad.
        """
        positions = [(i, j) for i in range(GRID_SIZE) for j in range(GRID_SIZE)]
        self.mines = random.sample(positions, NUM_MINES if not self.easy_mode else NUM_MINES // 2)
        for x, y in self.mines:
            self.grid[x][y] = -1  # -1 indica mina

    def calculate_numbers(self):
        """
        Calcula el número de minas adyacentes para cada celda no mina.
        Usa un algoritmo de búsqueda en las 8 direcciones adyacentes.
        """
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if self.grid[i][j] != -1:
                    count = 0
                    for dx, dy in directions:
                        ni, nj = i + dx, j + dy
                        if 0 <= ni < GRID_SIZE and 0 <= nj < GRID_SIZE and self.grid[ni][nj] == -1:
                            count += 1
                    self.grid[i][j] = count

    def reveal_cell(self, x, y):
        """
        Revela una celda. Si es una mina, termina el juego. Si es 0, revela recursivamente las adyacentes.
        Incluye animación de fade-in para innovación visual.
        """
        if self.revealed[x][y] or self.flagged[x][y]:
            return
        
        self.revealed[x][y] = True
        self.reveal_animation[(x, y)] = 0  # Inicia animación con opacidad 0
        
        if self.grid[x][y] == -1:
            self.game_over = True
            return
        
        if self.grid[x][y] == 0:
            # Revelación recursiva para celdas vacías (algoritmo de búsqueda DFS)
            directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
            for dx, dy in directions:
                ni, nj = x + dx, y + dy
                if 0 <= ni < GRID_SIZE and 0 <= nj < GRID_SIZE and not self.revealed[ni][nj]:
                    self.reveal_cell(ni, nj)
        
        self.check_win()

    def check_win(self):
        """
        Verifica si el jugador ha ganado al revelar todas las celdas no minadas.
        """
        revealed_count = sum(sum(row) for row in self.revealed)
        total_cells = GRID_SIZE * GRID_SIZE
        if revealed_count == total_cells - len(self.mines):
            self.won = True
            self.game_over = True
            self.score = int((time.time() - self.start_time) * 100)  # Puntuación inversa al tiempo

    def flag_cell(self, x, y):
        """
        Marca o desmarca una celda como mina (clic derecho).
        """
        if not self.revealed[x][y]:
            self.flagged[x][y] = not self.flagged[x][y]

    def reset_game(self):
        """
        Reinicia el juego: resetea todas las variables y genera nuevas minas.
        """
        self.__init__()
        if self.easy_mode:
            self.generate_mines()  # Regenerar con menos minas si es modo fácil

    def draw(self):
        """
        Dibuja la interfaz del juego: cuadrícula, botones, texto y animaciones.
        """
        self.screen.fill(WHITE)
        
        # Dibujar cuadrícula
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                rect = pygame.Rect(j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if self.revealed[i][j]:
                    # Animación de revelación
                    alpha = self.reveal_animation.get((i, j), 255)
                    if alpha < 255:
                        alpha += 10  # Incremento gradual
                        self.reveal_animation[(i, j)] = alpha
                    
                    color = GREEN if self.grid[i][j] == 0 else BLUE
                    pygame.draw.rect(self.screen, color, rect)
                    if self.grid[i][j] > 0:
                        text = FONT.render(str(self.grid[i][j]), True, BLACK)
                        self.screen.blit(text, (j * CELL_SIZE + 20, i * CELL_SIZE + 15))
                    elif self.grid[i][j] == -1:
                        pygame.draw.circle(self.screen, RED, (j * CELL_SIZE + 25, i * CELL_SIZE + 25), 15)
                else:
                    pygame.draw.rect(self.screen, GRAY, rect)
                    if self.flagged[i][j]:
                        pygame.draw.polygon(self.screen, YELLOW, [(j * CELL_SIZE + 10, i * CELL_SIZE + 10),
                                                                  (j * CELL_SIZE + 40, i * CELL_SIZE + 10),
                                                                  (j * CELL_SIZE + 25, i * CELL_SIZE + 35)])
                pygame.draw.rect(self.screen, BLACK, rect, 1)
        
        # Dibujar botón de reinicio
        pygame.draw.rect(self.screen, DARK_GRAY, self.reset_button)
        reset_text = SMALL_FONT.render("Reiniciar", True, WHITE)
        self.screen.blit(reset_text, (self.reset_button.x + 10, self.reset_button.y + 10))
        
        # Dibujar texto de estado
        elapsed_time = time.time() - self.start_time
        time_text = SMALL_FONT.render(f"Tiempo: {int(elapsed_time)}s", True, BLACK)
        self.screen.blit(time_text, (10, HEIGHT - 50))
        
        if self.game_over:
            if self.won:
                status_text = FONT.render(f"¡Ganaste! Puntuación: {self.score}", True, GREEN)
            else:
                status_text = FONT.render("¡Perdiste! Clic en Reiniciar", True, RED)
            self.screen.blit(status_text, (WIDTH // 2 - 150, HEIGHT - 100))
        
        pygame.display.flip()

    def handle_events(self):
        """
        Maneja eventos de entrada: clics del mouse, cierre de ventana.
        Controla errores como clics fuera de la cuadrícula.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if self.reset_button.collidepoint(x, y):
                    self.reset_game()
                elif y < GRID_SIZE * CELL_SIZE:  # Dentro de la cuadrícula
                    grid_x, grid_y = y // CELL_SIZE, x // CELL_SIZE
                    if event.button == 1:  # Clic izquierdo
                        if not self.game_over:
                            self.reveal_cell(grid_x, grid_y)
                    elif event.button == 3:  # Clic derecho
                        if not self.game_over:
                            self.flag_cell(grid_x, grid_y)
                else:
                    # Mensaje de error para clics inválidos (fuera de la cuadrícula)
                    print("Clic fuera de la cuadrícula. Intenta en las celdas.")

# Función principal
def main():
    """
    Bucle principal del juego. Inicializa el juego y maneja el loop de actualización.
    """
    game = Minesweeper()
    
    # Preguntar por modo fácil al inicio (innovación)
    print("¿Modo fácil? (menos minas) [y/n]: ", end="")
    if input().lower() == 'y':
        game.easy_mode = True
        game.reset_game()
    
    while True:
        game.handle_events()
        game.draw()
        game.clock.tick(FPS)

if __name__ == "__main__":
    main()
