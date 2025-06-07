from tkinter import Frame, Canvas, Label
from models.maze import Maze
from threading import Thread
import time

class GameView(Frame):
    def __init__(self, parent, controller):
        print(f"[DEBUG] GameView.__init__ - parent received: {parent}") # Diagnostic print
        if parent is None:
            print("[DEBUG] GameView.__init__ - WARNING: Parent is None. Frame will implicitly use default root.")
        super().__init__(parent)
        self.controller = controller
        self.maze = Maze(40, 30)  # Tamaño del laberinto
        self.cell_size = 20  # Tamaño de cada celda en píxeles
        self.create_widgets()
        self.bind_events()
        
    def create_widgets(self):
        # Canvas para dibujar el laberinto
        self.canvas = Canvas(self, 
                           width=self.maze.width * self.cell_size,
                           height=self.maze.height * self.cell_size,
                           bg='white')
        self.canvas.pack(expand=True, fill="both")
        
        # Etiqueta para mostrar el tiempo
        self.time_label = Label(self, text="Tiempo: 0s")
        self.time_label.pack()
        
    def bind_events(self):
        # Enlazar teclas para mover el jugador
        self.bind_all("<Up>", lambda e: self.move_player(0, -1))
        self.bind_all("<Down>", lambda e: self.move_player(0, 1))
        self.bind_all("<Left>", lambda e: self.move_player(-1, 0))
        self.bind_all("<Right>", lambda e: self.move_player(1, 0))
        
    def move_player(self, dx, dy):
        """Mueve al jugador y actualiza la vista"""
        if self.maze.move_player(dx, dy):
            self.update_view()
            self.controller.game_completed(self.maze.get_time())
            
    def update_view(self):
        """Actualiza la vista del laberinto"""
        self.canvas.delete("all")
        
        # Dibujar paredes
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                if self.maze.get_grid()[y][x] == 1:
                    self.canvas.create_rectangle(
                        x * self.cell_size, y * self.cell_size,
                        (x + 1) * self.cell_size, (y + 1) * self.cell_size,
                        fill='black'
                    )
        
        # Dibujar metas
        fake_goal, true_goal = self.maze.get_goals()
        if fake_goal:
            self.canvas.create_rectangle(
                fake_goal[0] * self.cell_size, fake_goal[1] * self.cell_size,
                (fake_goal[0] + 1) * self.cell_size, (fake_goal[1] + 1) * self.cell_size,
                fill='red'
            )
            
        if true_goal:
            self.canvas.create_rectangle(
                true_goal[0] * self.cell_size, true_goal[1] * self.cell_size,
                (true_goal[0] + 1) * self.cell_size, (true_goal[1] + 1) * self.cell_size,
                fill='green'
            )
        
        # Dibujar jugador
        player_x, player_y = self.maze.get_player_pos()
        self.canvas.create_rectangle(
            player_x * self.cell_size, player_y * self.cell_size,
            (player_x + 1) * self.cell_size, (player_y + 1) * self.cell_size,
            fill='blue'
        )
        
        # Actualizar tiempo
        self.time_label.config(text=f"Tiempo: {int(self.maze.get_time())}s")
        
    def start_game(self):
        """Inicia un nuevo juego"""
        self.maze.generate_maze()
        self.maze.start_timer()
        self.update_view()
        
    def game_over(self):
        """Muestra mensaje de juego terminado"""
        self.maze.game_over = True
        messagebox.showinfo("¡Felicidades!", 
                           f"¡Has completado el laberinto en {int(self.maze.get_time())} segundos!")
