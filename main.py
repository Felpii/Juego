from tkinter import Tk, Toplevel, Button
from Views.login import LoginView
from controllers.user_controller import UserController
from controllers.game_controller import GameController

def main():
    root = Tk()
    root.title("Juego Laberinto")
    
    
    # Inicializar los controladores
    user_controller = UserController()
    game_controller = GameController(user_controller)
    
    # Mostrar la vista de login
    login_view = LoginView(root, user_controller)
    login_view.pack(expand=True, fill="both")
    
    # Guardar referencia a la vista de login
    login_view = None
    
    # Función para iniciar el juego
    def start_game(username):
        nonlocal login_view
        
        # Guardar referencia a la vista de login
        login_view = LoginView(root, user_controller)
        
        # Ocultar la ventana de login
        root.withdraw()  
        
        # Crear nueva ventana para el juego
        game_window = Toplevel(root)
        game_window.title("Juego Laberinto")
        game_window.geometry("900x700")
        
        # Iniciar el juego, pasando game_window como el padre para la GameView
        game_controller.start_game(username, game_window)
        
        # Configurar qué pasa cuando se cierra la ventana
        def on_closing():
            # Destruir la ventana del juego
            game_window.destroy()
            # Mostrar la ventana de login original
            root.deiconify()
            
        game_window.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Configurar la función en el controlador de usuarios
    user_controller.start_game = start_game
    
    # Iniciar el bucle principal
    root.mainloop()

if __name__ == "__main__":
    main()
