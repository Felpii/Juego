import random
from threading import Thread
import time

class Maze:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[1] * width for _ in range(height)]  # 1 = pared, 0 = camino
        self.player_pos = (1, 1)
        self.fake_goal = None
        self.true_goal = None
        self.time_start = None
        self.time_elapsed = 0
        self.game_over = False
        
    def generate_maze(self):
        """Genera el laberinto usando el algoritmo de DFS"""
        def dfs(x, y):
            self.grid[y][x] = 0
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            random.shuffle(directions)
            
            for dx, dy in directions:
                nx, ny = x + dx * 2, y + dy * 2
                if 0 <= nx < self.width and 0 <= ny < self.height and self.grid[ny][nx] == 1:
                    self.grid[y + dy][x + dx] = 0
                    dfs(nx, ny)
        
        # Iniciar desde una posición aleatoria
        start_x = random.randrange(1, self.width, 2)
        start_y = random.randrange(1, self.height, 2)
        dfs(start_x, start_y)
        
        # Colocar meta falsa y verdadera
        self.place_goals()
        
    def place_goals(self):
        """Coloca la meta falsa y verdadera en posiciones aleatorias"""
        # Meta falsa
        while True:
            x = random.randrange(1, self.width, 2)
            y = random.randrange(1, self.height, 2)
            if self.grid[y][x] == 0:
                self.fake_goal = (x, y)
                break
                
        # Meta verdadera
        while True:
            x = random.randrange(1, self.width, 2)
            y = random.randrange(1, self.height, 2)
            if self.grid[y][x] == 0 and (x, y) != self.fake_goal:
                self.true_goal = (x, y)
                break
                
    def start_timer(self):
        """Inicia el temporizador en un hilo separado"""
        self.time_start = time.time()
        self.game_over = False
        
        def timer_thread():
            while not self.game_over:
                self.time_elapsed = time.time() - self.time_start
                time.sleep(0.1)
        
        Thread(target=timer_thread, daemon=True).start()
        
    def move_player(self, dx, dy):
        """Mueve al jugador en la dirección especificada"""
        x, y = self.player_pos
        nx, ny = x + dx, y + dy
        print(f"Intentando mover de ({x}, {y}) a ({nx}, {ny})")
        
        if 0 <= nx < self.width and 0 <= ny < self.height:
            if self.grid[ny][nx] == 0 or (nx, ny) == self.true_goal:
                print(f"Movimiento válido a ({nx}, {ny})")
                self.player_pos = (nx, ny)
                
                # Si llega a la meta falsa, la eliminamos
                if (nx, ny) == self.fake_goal:
                    print("¡Encontraste la meta falsa!")
                    self.grid[ny][nx] = 0
                    self.fake_goal = None
                    
                # Si llega a la meta verdadera, termina el juego
                if (nx, ny) == self.true_goal:
                    print("¡Encontraste la meta verdadera!")
                    self.game_over = True
                    return True
                return True  # Movimiento exitoso pero el juego no ha terminado
            else:
                print(f"Movimiento inválido: hay una pared en ({nx}, {ny})")
        else:
            print(f"Movimiento inválido: ({nx}, {ny}) está fuera de los límites")
        
        return False
        
    def get_time(self):
        """Devuelve el tiempo transcurrido en segundos"""
        return self.time_elapsed
        
    def get_player_pos(self):
        """Devuelve la posición actual del jugador"""
        return self.player_pos
        
    def get_grid(self):
        """Devuelve la cuadrícula del laberinto"""
        return self.grid
        
    def get_goals(self):
        """Devuelve las posiciones de las metas"""
        return self.fake_goal, self.true_goal
