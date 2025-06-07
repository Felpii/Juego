from models.user import User
from database.database import Database
from controllers.game_controller import GameController

class UserController:
    def __init__(self):
        self.db = Database()
        self.game_controller = GameController(self)
        
    def login(self, username, password):
        return self.db.login(username, password)
        
    def register(self, username, password):
        return self.db.register(username, password)
        
    def get_leaderboard(self):
        return self.db.get_leaderboard()
        
    def save_score(self, username, score):
        return self.db.save_score(username, score)
        
    def start_game(self, username):
        """Inicia el juego para el usuario especificado"""
        self.game_controller.start_game(username)
