from tkinter import Tk, Button, Toplevel
from views.login import LoginView
from controllers.user_controller import UserController
from controllers.game_controller import GameController
from views.game import GameView
import tkinter.messagebox as messagebox

def main():
    root = Tk()
    root.title("Juego Laberinto POE")
    
    # Inicializar los controladores
    user_controller = UserController()
    game_controller = GameController(user_controller)
    
    # Mostrar la vista de login
    login_view = LoginView(root, user_controller)
    login_view.pack(expand=True, fill="both")
    
    # Función para iniciar el juego
    def start_game(username):
        # TEST: No ocultar la ventana de login temporalmente
        # root.withdraw()  
        game_window = Toplevel(root) # Usar Toplevel en lugar de Tk()
        game_window.title("Juego Laberinto")
        game_window.geometry("800x600")
        
        # Iniciar el juego, pasando game_window como el padre para la GameView
        game_controller.start_game(username, game_window)
        game_view = game_controller.get_game_view()
        if game_view: # Asegurarse que game_view no es None
            game_view.pack(expand=True, fill="both")
        else:
            print("Error: game_view es None, no se puede empaquetar.")
        
        # Función para volver al login
        def back_to_login():
            game_window.destroy()
            # TEST: No mostrar nuevamente la ventana de login ya que no se ocultó
            # root.deiconify()  
        
        # Botón para volver al login
        back_button = Button(game_window, text="Volver al Login", command=back_to_login)
        back_button.pack()
        
        # No se necesita game_window.mainloop() para Toplevel
    
    # Agregar función al controlador de usuarios
    user_controller.start_game = start_game
    
    root.mainloop()

if __name__ == "__main__":
    main()
