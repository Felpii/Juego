from views.game import GameView
import tkinter.messagebox as messagebox

class GameController:
    def __init__(self, user_controller):
        self.user_controller = user_controller
        self.current_user = None
        self.game_view = None  # Inicializar game_view
        
    def start_game(self, username, parent_window):
        """Inicia un nuevo juego para el usuario especificado"""
        try:
            self.current_user = username
            print(f"[DEBUG] Iniciando juego para {username} en ventana {parent_window}")
            
            # Crear la vista del juego
            self.game_view = GameView(parent_window, self)
            print("[DEBUG] Vista del juego creada")
            
            # Empaquetar la vista
            self.game_view.pack(expand=True, fill="both")
            print("[DEBUG] Vista empaquetada")
            
            # Actualizar la ventana
            parent_window.update()
            print("[DEBUG] Ventana actualizada")
            
            # Iniciar el juego
            self.game_view.start_game()
            print("[DEBUG] Juego iniciado")
            
            # Forzar el foco en el canvas
            self.game_view.focus_set()
            self.game_view.canvas.focus_set()
            print("[DEBUG] Foco establecido")
            
        except Exception as e:
            print(f"[ERROR] Error al iniciar el juego: {str(e)}")
            import traceback
            traceback.print_exc()
        
    def game_completed(self, time):
        """Se llama cuando el juego se completa"""
        if self.current_user:
            self.user_controller.save_score(self.current_user, int(time))
        self.game_view.game_over()
        
    def get_game_view(self):
        """Devuelve la vista del juego"""
        return self.game_view
        
    def back_to_login(self):
        """Vuelve a la pantalla de login"""
        try:
            if self.game_view and hasattr(self.game_view, 'master'):
                # Obtener la ventana del juego
                game_window = self.game_view.master
                # Obtener la ventana raíz (login)
                root = game_window.nametowidget('.')
                
                # Destruir la ventana del juego
                game_window.destroy()
                
                # Mostrar la ventana de login original
                if hasattr(root, 'deiconify'):
                    root.deiconify()
        except Exception as e:
            print(f"[DEBUG] Error en back_to_login: {e}")
