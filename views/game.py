from tkinter import Frame, Canvas, Label, Button, messagebox, PhotoImage, Scrollbar
from models.maze import Maze
from threading import Thread
import time
import os
import sys
import platform
from queue import Queue, Empty
import winsound
from PIL import Image, ImageTk, ImageDraw

class GameView(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.maze = Maze(41, 29)  # Tamaño del laberinto
        self.cell_size = 21  # Tamaño de cada celda en píxeles
        
        # Inicializar sistema de sonido
        try:
            import winsound
            # Probar si el sistema de sonido está disponible
            winsound.Beep(1000, 100)  # Beep corto para probar
        except:
            pass  # El sistema de sonido podría no estar disponible, pero continuamos de todos modos
        
        # Inicializar atributos de sonido
        self.sound_queue = Queue()
        self.sound_thread = None
        self.sound_running = False  # Inicialmente desactivado
        
        # Cargar sonidos
        self.sounds = {}
        self.load_sounds()
        
        # Iniciar sistema de sonido
        self.sound_running = True  # Activar el sistema de sonido
        print("[DEBUG] Sistema de sonido activado")
        
        # Iniciar hilo de sonido
        self.start_sound_thread()
        print("[DEBUG] Hilo de sonido iniciado")
        
        # Reproducir música de fondo si está disponible
        if 'background' in self.sounds:
            print("[DEBUG] Intentando reproducir música de fondo...")
            self.queue_sound('background')
        else:
            print("[ADVERTENCIA] No se encontró el archivo de música de fondo")
        
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
        
    def get_sound_path(self, filename):
        """Obtiene la ruta completa al archivo de sonido"""
        # Obtener la ruta absoluta del directorio del proyecto
        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Construir la ruta al archivo de sonido
        sound_path = os.path.join(project_dir, 'assets', 'sounds', filename)
        # Convertir a ruta absoluta normalizada
        return os.path.normpath(sound_path)
    
    def load_sounds(self):
        """Carga los sonidos del juego"""
        sound_files = {
            'win': 'win.wav',
            'background': 'background.wav'
        }
        
        sounds_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'sounds')
        
        # Verificar si el directorio de sonidos existe
        if not os.path.exists(sounds_dir):
            return
            
        # Cargar cada sonido
        for sound_name, filename in sound_files.items():
            sound_path = os.path.join(sounds_dir, filename)
            
            # Verificar si el archivo existe y no está vacío
            try:
                if os.path.exists(sound_path) and os.path.getsize(sound_path) > 0:
                    self.sounds[sound_name] = sound_path
            except:
                continue
    
    def play_sound(self, sound_type):
        """Reproduce un efecto de sonido en segundo plano"""
        if not self.sound_running:
            print(f"[WARN] Intento de reproducir sonido con sonido deshabilitado: {sound_type}")
        
            return
            
        if sound_type not in self.sounds:
            print(f"[ERROR] Tipo de sonido no válido: {sound_type}")
            return
            
        sound_file = self.sounds[sound_type]
        
        if not sound_file:
            print(f"[ERROR] Ruta de sonido no definida para: {sound_type}")
            return
            
        if not os.path.exists(sound_file):
            print(f"[ERROR] El archivo de sonido no existe: {sound_file}")
            return
            
        print(f"\n=== INTENTANDO REPRODUCIR SONIDO: {sound_type} ===")
        print(f"Archivo: {sound_file}")
        print(f"Tamaño: {os.path.getsize(sound_file)} bytes")
        
        # Primero intentar reproducir directamente en el hilo principal
        print("\n[PRUEBA] Reproduciendo en el hilo principal...")
        try:
            import winsound
            flags = winsound.SND_FILENAME
            if sound_type == 'background':
                flags |= winsound.SND_LOOP | winsound.SND_ASYNC
            else:
                flags |= winsound.SND_ASYNC
                
            print(f"[PRUEBA] Intentando con flags: {flags}")
            winsound.PlaySound(sound_file, flags)
            print("[PRUEBA] Reproducción directa exitosa")
            return  # Si funcionó, salir
            
        except Exception as e:
            print(f"[PRUEBA] Error en reproducción directa: {e}")
            import traceback
            traceback.print_exc()
        
        # Si la reproducción directa falla, intentar en un hilo separado
        print("\n[INTENTO 2] Probando en un hilo separado...")
        try:
            def play():
                try:
                    import winsound
                    print(f"[HILO] Iniciando reproducción de {sound_type}")
                    flags = winsound.SND_FILENAME
                    if sound_type == 'background':
                        flags |= winsound.SND_LOOP | winsound.SND_ASYNC
                    else:
                        flags |= winsound.SND_ASYNC
                    
                    print(f"[HILO] Reproduciendo con flags: {flags}")
                    winsound.PlaySound(sound_file, flags)
                    print("[HILO] Reproducción exitosa")
                    
                except Exception as e:
                    print(f"[HILO] Error al reproducir sonido: {e}")
                    import traceback
                    traceback.print_exc()
            
            # Iniciar el hilo de reproducción
            sound_thread = Thread(target=play, daemon=True)
            sound_thread.start()
            print("[INFO] Hilo de reproducción iniciado")
            
        except Exception as e:
            print(f"[ERROR] Error al iniciar hilo de sonido: {e}")
            import traceback
            traceback.print_exc()
            
        print(f"=== FIN DE INTENTO DE REPRODUCCIÓN: {sound_type} ===\n")
    
    def start_sound_thread(self):
        """Inicia el hilo para manejar la reproducción de sonidos"""
        # Asegurarse de que el sistema de sonido esté activo
        if not hasattr(self, 'sound_running') or not self.sound_running:
            self.sound_running = True
        
        # Verificar si el hilo ya está en ejecución
        if hasattr(self, 'sound_thread') and self.sound_thread is not None:
            if self.sound_thread.is_alive():
                return
        
        # Asegurarse de que la cola existe
        if not hasattr(self, 'sound_queue'):
            self.sound_queue = Queue()
        
        def sound_worker():
            while self.sound_running:
                try:
                    # Obtener el siguiente sonido de la cola (espera hasta 1 segundo)
                    try:
                        sound_type = self.sound_queue.get(timeout=1)
                        self.play_sound(sound_type)
                        self.sound_queue.task_done()
                    except Empty:
                        continue
                        
                except Exception:
                    break
                    import traceback
                    traceback.print_exc()
            
            print("[INFO] Hilo de sonido finalizado")
        
        try:
            # Iniciar el hilo
            self.sound_thread = Thread(target=sound_worker, daemon=True)
            self.sound_thread.start()
            print("[INFO] Hilo de sonido iniciado correctamente")
        except Exception as e:
            print(f"[ERROR] No se pudo iniciar el hilo de sonido: {e}")
            self.sound_running = False
    
    def queue_sound(self, sound_type):
        """Agrega un sonido a la cola de reproducción"""
        # Verificar si el sistema de sonido está activo
        if not hasattr(self, 'sound_running') or not self.sound_running:
            self.sound_running = True
            self.start_sound_thread()
            
            if not hasattr(self, 'sound_running') or not self.sound_running:
                return False
            
        if sound_type not in self.sounds:
            return False
            
        sound_file = self.sounds[sound_type]
        if not sound_file or not os.path.exists(sound_file):
            return False
            
        try:
            # Si es el sonido de fondo, detener cualquier sonido actual primero
            if sound_type == 'background':
                try:
                    import winsound
                    winsound.PlaySound(None, winsound.SND_PURGE)
                except:
                    pass
            
            # Agregar a la cola
            self.sound_queue.put(sound_type, block=False)
            return True
            
        except:
            return False
    
    def stop_sounds(self):
        """Detiene todos los sonidos"""
        try:
            # Detener cualquier sonido que se esté reproduciendo
            winsound.PlaySound(None, winsound.SND_PURGE)
            
            # Limpiar la cola de sonidos
            while not self.sound_queue.empty():
                try:
                    self.sound_queue.get_nowait()
                except Empty:
                    break
                    
            # Establecer la bandera para detener el hilo de sonido
            self.sound_running = False
            
            # Si hay un hilo de sonido, esperar a que termine
            if hasattr(self, 'sound_thread') and self.sound_thread:
                self.sound_thread.join(timeout=0.1)
                
            print("[DEBUG] Todos los sonidos han sido detenidos")
            
        except Exception as e:
            print(f"[ERROR] Error al detener los sonidos: {e}")
    
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
        """Mueve al jugador en la dirección especificada"""
        if self.maze.game_over:
            return False
            
        old_x, old_y = self.maze.get_player_pos()
        moved = self.maze.move_player(dx, dy)
        
        if moved:
            print(f"[INFO] Jugador movido a ({old_x + dx}, {old_y + dy})")
            
            # Reproducir sonido de movimiento
            self.queue_sound('move')
            
            # Verificar si el jugador ganó
            if self.maze.game_over:
                print("[INFO] ¡Juego completado!")
                self.queue_sound('win')
                self.controller.game_completed(self.maze.get_time())
            
            # Actualizar la vista
            self.update_view()
            
            # Forzar la actualización de la interfaz
            self.update_idletasks()
            
        return moved
            
    def update_view(self):
        """Actualiza la vista del laberinto con las imágenes cargadas"""
        if not hasattr(self, 'canvas') or not self.canvas or not self.canvas.winfo_exists() or not hasattr(self, 'images'):
            print("No se puede actualizar la vista: canvas no existe o imágenes no están disponibles")
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
        # Detener cualquier sonido que esté reproduciéndose
        self.stop_sounds()
        
        # Generar un nuevo laberinto
        self.maze.generate_maze()
        
        # Iniciar el temporizador
        self.maze.start_timer()
        
        # Actualizar la vista
        self.update_view()
        
        # Iniciar la actualización periódica del tiempo
        self.update_timer()
        
        # Reproducir música de fondo (asegurarse de que el sonido esté en la cola)
        print("[DEBUG] Iniciando música de fondo...")
        self.queue_sound('background')
        
        # Imprimir información de depuración
        print("[DEBUG] Sonidos disponibles:", self.sounds)
        print("[DEBUG] Ruta de background:", self.sounds.get('background'))
        print("[DEBUG] Archivo existe:", os.path.exists(self.sounds.get('background', '')) if self.sounds.get('background') else 'No definido')
        
    def update_timer(self):
        """Actualiza el contador de tiempo"""
        if not self.maze.game_over:
            self.time_label.config(text=f"Tiempo: {int(self.maze.get_time())}s")
            # Programar la próxima actualización en 100ms
            self.after(100, self.update_timer)
        
    def game_over(self):
        """Maneja la finalización del juego con una pantalla personalizada"""
        self.timer_running = False
        
        # Crear un canvas para la pantalla de game over
        self.overlay = Canvas(self, bg='#404040', highlightthickness=0)
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # No usamos transparencia directamente, usamos un color sólido oscuro
        # ya que Tkinter no soporta bien la transparencia en todas las plataformas
        
        # Crear un frame para el contenido
        content_frame = Frame(self.overlay, bg='white', bd=0, highlightthickness=0)
        content_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Título
        title = Label(content_frame, text="¡FELICIDADES!", 
                     font=('Helvetica', 24, 'bold'), 
                     bg='white', fg='#2c3e50')
        title.pack(pady=(20, 10), padx=40)
        
        # Mensaje
        message = Label(content_frame, 
                      text=f"Has completado el laberinto en\n{int(self.maze.get_time())} segundos!",
                      font=('Helvetica', 14), 
                      bg='white', fg='#34495e',
                      justify='center')
        message.pack(pady=(0, 20), padx=40)
        
        # Frame para los botones
        button_frame = Frame(content_frame, bg='white')
        button_frame.pack(pady=(0, 20))
        
        # Botón de jugar de nuevo
        play_again_btn = Button(button_frame, text="Jugar de nuevo",
                              font=('Helvetica', 12, 'bold'),
                              bg='#3498db', fg='white',
                              activebackground='#2980b9',
                              activeforeground='white',
                              bd=0, padx=20, pady=10,
                              command=self._restart_game)
        play_again_btn.pack(side='left', padx=10)
        
        # Botón de salir
        exit_btn = Button(button_frame, text="Salir al menú",
                        font=('Helvetica', 12),
                        bg='#e74c3c', fg='white',
                        activebackground='#c0392b',
                        activeforeground='white',
                        bd=0, padx=20, pady=10,
                        command=self.controller.back_to_login)
        exit_btn.pack(side='left', padx=10)
        
        # Animación de entrada
        content_frame.place_configure(relx=0.5, rely=0.4, anchor='center')
        
        # Establecer el foco en el botón de jugar de nuevo de manera segura
        def set_focus():
            if content_frame.winfo_children():
                play_again_btn.focus_set()
        
        # Programar el enfoque para después de que la interfaz se haya actualizado
        self.after(100, set_focus)
        
        # Efecto de fade in
        self.overlay.alpha = 0
        self._fade_in()
    
    def _fade_in(self):
        """Efecto de fade in para la pantalla de game over"""
        if not hasattr(self.overlay, 'alpha'):
            self.overlay.alpha = 0
            
        if self.overlay.alpha < 1.0:
            self.overlay.alpha += 0.05
            # Usamos una escala de grises para el fade in
            intensity = int(64 + (191 * self.overlay.alpha))
            color = f'#{intensity:02x}{intensity:02x}{intensity:02x}'
            self.overlay.config(bg=color)
            self.after(20, self._fade_in)
    
    def _restart_game(self):
        """Reinicia el juego"""
        # Destruir el overlay
        if hasattr(self, 'overlay') and self.overlay.winfo_exists():
            self.overlay.destroy()
        # Reiniciar el juego
        self.start_game()
    
    def __del__(self):
        """Limpia los recursos al destruir la ventana"""
        try:
            # Detener el temporizador si existe
            if hasattr(self, 'timer_running'):
                self.timer_running = False
            
            # Detener y limpiar el sistema de sonido
            self.sound_running = False
            
            # Detener cualquier sonido que se esté reproduciendo
            try:
                import winsound
                winsound.PlaySound(None, winsound.SND_PURGE)
            except:
                pass
            
            # Limpiar la cola de sonidos
            if hasattr(self, 'sound_queue'):
                while not self.sound_queue.empty():
                    try:
                        self.sound_queue.get_nowait()
                    except Empty:
                        break
            
            # Esperar a que el hilo de sonido termine
            if hasattr(self, 'sound_thread') and self.sound_thread is not None:
                self.sound_thread.join(timeout=0.5)
            
            # Limpiar referencias
            if hasattr(self, 'sounds'):
                self.sounds.clear()
            
            # Limpiar el canvas
            if hasattr(self, 'canvas') and self.canvas is not None:
                self.canvas.delete("all")
                
        except:
            pass
