from views.game import GameView
import tkinter.messagebox as messagebox

class GameController:
    def __init__(self, user_controller):
        self.user_controller = user_controller
        self.current_user = None
        self.game_view = None # Inicializar game_view
        
    def start_game(self, username, parent_window): # Añadir parent_window
        """Inicia un nuevo juego para el usuario especificado"""
        self.current_user = username
        # Pasar parent_window a GameView
        self.game_view = GameView(parent_window, self) 
        self.game_view.start_game()
        
    def game_completed(self, time):
        """Se llama cuando el juego se completa"""
        if self.current_user:
            self.user_controller.save_score(self.current_user, int(time))
        self.game_view.game_over()
        
    def get_game_view(self):
        """Devuelve la vista del juego"""
        return self.game_view
