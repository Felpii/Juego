from tkinter import Frame, Canvas, Label, Button, messagebox
from models.maze import Maze
from threading import Thread
import time

class GameView(Frame):
    def __init__(self, parent, controller):
        print(f"[DEBUG] GameView.__init__ - parent received: {parent}")
        if parent is None:
            print("[DEBUG] GameView.__init__ - WARNING: Parent is None. Frame will implicitly use default root.")
        super().__init__(parent)
        self.controller = controller
        self.maze = Maze(40, 30)  # Tamaño del laberinto
        self.cell_size = 20  # Tamaño de cada celda en píxeles
        self.create_widgets()
        self.bind_events()
        # Asegurar que el canvas pueda recibir el foco
        self.pack(expand=True, fill="both")
        self.focus_set()
        self.update()  # Forzar la actualización de la interfaz
        self.canvas.focus_set()
        
    def create_widgets(self):
        # Frame principal que contendrá todo
        self.main_frame = Frame(self)
        self.main_frame.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Frame para la barra superior (tiempo y botón)
        self.top_bar = Frame(self.main_frame)
        self.top_bar.pack(fill="x", pady=(0, 10))
        
        # Botón para volver al menú principal
        self.back_button = Button(self.top_bar, text="Volver al Menú", 
                                command=self.controller.back_to_login,
                                font=('Arial', 10))
        self.back_button.pack(side="right")
        
        # Etiqueta para mostrar el tiempo
        self.time_label = Label(self.top_bar, text="Tiempo: 0s", 
                              font=('Arial', 12, 'bold'))
        self.time_label.pack(side="left")
        
        # Frame para el canvas del juego
        self.canvas_frame = Frame(self.main_frame, bd=2, relief="sunken")
        self.canvas_frame.pack(expand=True, fill="both")
        
        # Canvas para dibujar el laberinto
        self.canvas = Canvas(self.canvas_frame, 
                           width=self.maze.width * self.cell_size,
                           height=self.maze.height * self.cell_size,
                           bg='white',
                           highlightthickness=0)
        self.canvas.pack(expand=True, padx=5, pady=5)
        
        # Configurar el foco para que se mantenga en el canvas
        def set_focus(event=None):
            self.canvas.focus_set()
            
        # Vincular eventos para mantener el foco en el canvas
        self.canvas.bind("<Button-1>", set_focus)
        self.bind("<Enter>", set_focus)
        
        # Asegurarse de que el canvas tenga el foco inicial
        set_focus()
        
    def bind_events(self):
        # Función para manejar el movimiento
        def on_key_press(event):
            moved = False
            if event.keysym in ('Up', 'w'):
                moved = self.move_player(0, -1)
            elif event.keysym in ('Down', 's'):
                moved = self.move_player(0, 1)
            elif event.keysym in ('Left', 'a'):
                moved = self.move_player(-1, 0)
            elif event.keysym in ('Right', 'd'):
                moved = self.move_player(1, 0)
            
            if moved:
                # Actualizar la vista solo si hubo movimiento
                self.update_view()
        
        # Vincular eventos de teclado al canvas
        self.canvas.bind_all("<KeyPress>", on_key_press)
        
        # Asegurarse de que el canvas tenga el foco
        self.canvas.focus_set()
        
        # Mensaje de ayuda
        print("Controles: Usa las flechas o WASD para moverte")
        
    def move_player(self, dx, dy):
        """Mueve al jugador y actualiza la vista"""
        # Guardar la posición anterior
        old_x, old_y = self.maze.get_player_pos()
        
        # Intentar mover al jugador
        moved = self.maze.move_player(dx, dy)
        
        # Si el jugador se movió, actualizar la vista
        if moved:
            # Verificar si el juego terminó
            if self.maze.game_over:
                self.controller.game_completed(self.maze.get_time())
            return True
            
        return False
            
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
        # Iniciar la actualización periódica del tiempo
        self.update_timer()
        
    def update_timer(self):
        """Actualiza el contador de tiempo"""
        if not self.maze.game_over:
            self.time_label.config(text=f"Tiempo: {int(self.maze.get_time())}s")
            # Programar la próxima actualización en 100ms
            self.after(100, self.update_timer)
        
    def game_over(self):
        """Maneja la finalización del juego"""
        self.timer_running = False
        # Usar try/except para evitar errores si la ventana ya fue cerrada
        try:
            messagebox.showinfo("¡Felicidades!", 
                             f"¡Has completado el laberinto en {int(self.maze.get_time())} segundos!")
            self.controller.back_to_login()
        except Exception as e:
            print(f"[DEBUG] Error en game_over: {e}")
