from tkinter import Frame, Canvas, Label, Button, messagebox, PhotoImage, Scrollbar
from models.maze import Maze
from threading import Thread
import time
import os
from PIL import Image, ImageTk, ImageDraw

class GameView(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.maze = Maze(41, 29)  # Tamaño del laberinto
        self.cell_size = 21  # Tamaño de cada celda en píxeles
        
        # Configurar el frame principal
        self.pack(expand=True, fill="both")
        
        # Inicializar diccionario de imágenes
        self.images = {}
        self.load_images()
        self.create_widgets()
        self.bind_events()
        
        # Asegurarse de que todo se muestre correctamente
        self.update_idletasks()
        self.focus_set()
        self.canvas.focus_set()
        
        # Actualizar la vista
        self.update_view()
        
    def load_images(self):
        """
        Carga las imágenes del juego desde la carpeta assets/images del proyecto.
        Las imágenes se buscan en la ruta relativa al directorio del proyecto.
        """
        import os
        from pathlib import Path
        
        # Obtener la ruta absoluta del directorio del proyecto
        project_dir = Path(__file__).resolve().parent.parent  # Sube dos niveles desde views/ a la raíz del proyecto
        
        # Construir la ruta a la carpeta de imágenes
        assets_dir = project_dir / 'assets' / 'images'
        
        # Crear la carpeta si no existe
        assets_dir.mkdir(parents=True, exist_ok=True)
        
        # Diccionario de imágenes con sus rutas
        image_files = {
            'grass': 'cesped.png',
            'wall': 'muro.png',
            'player': 'gorila.png',
            'goal': 'bananna.png',
            'fake_goal': 'bananna.png'
        }
        
        # Inicializar diccionario de imágenes
        self.images = {}
        
        print(f"Buscando imágenes en: {assets_dir}")
        
        # Cargar cada imagen
        for img_name, filename in image_files.items():
            img_path = assets_dir / filename
            try:
                if img_path.exists() and img_path.is_file():
                    print(f"Cargando imagen: {img_path}")
                    # Cargar imagen desde archivo
                    img = Image.open(img_path)
                    # Convertir a modo RGBA si es necesario
                    if img.mode != 'RGBA':
                        img = img.convert('RGBA')
                    # Redimensionar si es necesario
                    if img.size != (self.cell_size, self.cell_size):
                        img = img.resize((self.cell_size, self.cell_size), Image.Resampling.LANCZOS)
                    # Crear PhotoImage y mantener una referencia
                    photo_img = ImageTk.PhotoImage(img)
                    self.images[img_name] = photo_img
                    print(f"Imagen cargada correctamente: {img_name} - Tamaño: {img.size}")
                else:
                    print(f"ADVERTENCIA: No se encontró la imagen: {img_path}")
                    self.images[img_name] = None
            except Exception as e:
                print(f"ERROR cargando imagen {img_path}: {e}")
                import traceback
                traceback.print_exc()
                self.images[img_name] = None
                
        # Verificar qué imágenes se cargaron
        print("\nResumen de imágenes cargadas:")
        for name, img in self.images.items():
            status = "Cargada" if img is not None else "No disponible"
            print(f"- {name}: {status}")
            
        # Si no se cargaron imágenes, mostrar sugerencia
        if not any(self.images.values()):
            print("\n¡No se cargaron imágenes! Asegúrate de que:")
            print(f"1. La carpeta de imágenes existe en: {assets_dir}")
            print("2. Los archivos de imagen tienen los nombres correctos:")
            for name, filename in image_files.items():
                print(f"   - {name}: {filename}")
        
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
        
        # Frame para el canvas del juego con fondo
        self.canvas_frame = Frame(self.main_frame, bd=2, relief="sunken")
        self.canvas_frame.pack(expand=True, fill="both")
        
        # Configurar el grid para que el canvas se expanda
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)
        
        # Canvas para mostrar el juego
        self.canvas = Canvas(self.canvas_frame, 
                           width=800,  # Ancho fijo inicial
                           height=600,  # Alto fijo inicial
                           bg='#2c3e50',
                           highlightthickness=0)
        
        # Configurar scrollbars
        self.h_scroll = Scrollbar(self.canvas_frame, orient="horizontal", command=self.canvas.xview)
        self.v_scroll = Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=self.h_scroll.set, 
                            yscrollcommand=self.v_scroll.set)
        
        # Posicionar widgets con grid
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scroll.grid(row=0, column=1, sticky="ns")
        self.h_scroll.grid(row=1, column=0, sticky="we")
        
        # Configurar el canvas para que ocupe todo el espacio disponible
        self.canvas.pack_propagate(False)
        
        # Configurar el manejo del foco
        self.canvas.focus_set()
        self.canvas.bind("<1>", lambda e: self.canvas.focus_set())
        
        # Configurar el tamaño mínimo del canvas
        self.canvas.config(width=800, height=600)
        
        # Forzar la actualización de la geometría
        self.update_idletasks()
            
        # Vincular eventos para mantener el foco en el canvas
        self.canvas.bind("<Button-1>", lambda e: self.canvas.focus_set())
        self.canvas.bind("<Enter>", lambda e: self.canvas.focus_set())
        self.canvas.bind("<Leave>", lambda e: self.canvas.focus_set())
        
    def _on_mousewheel(self, event):
        """Maneja el desplazamiento con la rueda del mouse"""
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")
    
    def _on_shift_mousewheel(self, event):
        """Maneja el desplazamiento horizontal con Shift + rueda del mouse"""
        if event.num == 4 or event.delta > 0:
            self.canvas.xview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.xview_scroll(1, "units")
    
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
        
        # Configurar eventos de desplazamiento
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Shift-MouseWheel>", self._on_shift_mousewheel)
        
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
        """Actualiza la vista del laberinto con las imágenes cargadas"""
        if not hasattr(self, 'canvas') or not self.canvas or not hasattr(self, 'images'):
            print("No se puede actualizar la vista: canvas o imágenes no están disponibles")
            return
            
        # Limpiar el canvas
        self.canvas.delete("all")
        
        try:
            # Obtener el estado actual del laberinto
            player_x, player_y = self.maze.get_player_pos()
            fake_goal, true_goal = self.maze.get_goals()
            grid = self.maze.get_grid()  # Obtener la cuadrícula del laberinto
            
            # Calcular el tamaño total del laberinto en píxeles
            maze_width = len(grid[0]) * self.cell_size
            maze_height = len(grid) * self.cell_size
            
            # Ajustar el tamaño del canvas al tamaño del laberinto
            self.canvas.config(
                width=min(800, maze_width),  # Máximo 800px de ancho
                height=min(600, maze_height)  # Máximo 600px de alto
            )
            
            # Dibujar el fondo de césped
            if 'grass' in self.images and self.images['grass']:
                grass_img = self.images['grass']
                for y in range(0, maze_height, grass_img.height()):
                    for x in range(0, maze_width, grass_img.width()):
                        self.canvas.create_image(x, y, 
                                               image=grass_img, 
                                               anchor='nw', 
                                               tags='background')
            
            # Dibujar muros
            if 'wall' in self.images and self.images['wall']:
                for y in range(len(grid)):
                    for x in range(len(grid[0])):
                        if grid[y][x] == 1:  # Si es un muro
                            self.canvas.create_image(
                                x * self.cell_size,
                                y * self.cell_size,
                                image=self.images['wall'],
                                anchor='nw',
                                tags='wall'
                            )
            
            # Mostrar metas
            if true_goal and 'goal' in self.images and self.images['goal']:
                tx, ty = true_goal
                self.canvas.create_image(
                    tx * self.cell_size,
                    ty * self.cell_size,
                    image=self.images['goal'],
                    anchor='nw',
                    tags='goal'
                )
            
            if fake_goal and 'fake_goal' in self.images and self.images['fake_goal']:
                fx, fy = fake_goal
                self.canvas.create_image(
                    fx * self.cell_size,
                    fy * self.cell_size,
                    image=self.images['fake_goal'],
                    anchor='nw',
                    tags='fake_goal'
                )
            
            # Mostrar jugador (encima de todo)
            if 'player' in self.images and self.images['player']:
                self.canvas.create_image(
                    player_x * self.cell_size, 
                    player_y * self.cell_size,
                    image=self.images['player'], 
                    anchor='nw', 
                    tags='player'
                )
            
            # Configurar la región de desplazamiento para que coincida con el tamaño del laberinto
            self.canvas.config(scrollregion=(0, 0, maze_width, maze_height))
            
            # Ajustar la vista para que el jugador esté visible
            self._center_view(player_x, player_y)
            
        except Exception as e:
            print(f"Error al actualizar la vista: {e}")
            import traceback
            traceback.print_exc()
        
        # Actualizar tiempo si existe el label
        if hasattr(self, 'time_label'):
            self.time_label.config(text=f"Tiempo: {int(self.maze.get_time())}s")
    
    def _center_view(self, player_x, player_y):
        """Centra la vista en la posición del jugador"""
        if not hasattr(self, 'canvas'):
            return
            
        # Obtener el tamaño del canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:  # Si el canvas no tiene tamaño aún
            return
            
        # Calcular la posición del jugador en píxeles
        player_px = player_x * self.cell_size
        player_py = player_y * self.cell_size
        
        # Calcular el desplazamiento para centrar al jugador
        x_offset = max(0, player_px - (canvas_width // 2))
        y_offset = max(0, player_py - (canvas_height // 2))
        
        # Aplicar el desplazamiento
        self.canvas.xview_moveto(x_offset / (self.maze.width * self.cell_size))
        self.canvas.yview_moveto(y_offset / (self.maze.height * self.cell_size))
    
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
