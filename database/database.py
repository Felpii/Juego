import mysql.connector
from config.config import DB_CONFIG

class Database:
    def __init__(self):
        self.connection = mysql.connector.connect(**DB_CONFIG)
        self.cursor = self.connection.cursor()
        self.create_tables()
        
    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS usarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS puntajes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                score INT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES usarios(id)
            )
        ''')
        
        self.connection.commit()
        
    def login(self, username, password):
        self.cursor.execute('''
            SELECT id FROM usarios 
            WHERE username = %s AND password = %s
        ''', (username, password))
        return self.cursor.fetchone() is not None
        
    def register(self, username, password):
        try:
            self.cursor.execute('''
                INSERT INTO usarios (username, password) 
                VALUES (%s, %s)
            ''', (username, password))
            self.connection.commit()
            return True
        except mysql.connector.Error as err:
            print(f"Error al registrar usuario/nusuario ya existe: {err}")
            return False
            
    def get_leaderboard(self):
        self.cursor.execute('''
            SELECT u.username, s.score  
            FROM usarios u 
            JOIN puntajes s ON u.id = s.user_id 
            ORDER BY s.score ASC 
            LIMIT 10
        ''')
        return self.cursor.fetchall()
        
    def save_score(self, username, score):
        try:
            self.cursor.execute('''
                SELECT id FROM usarios WHERE username = %s
            ''', (username,))
            user_id = self.cursor.fetchone()[0]
            
            self.cursor.execute('''
                INSERT INTO puntajes (user_id, score) 
                VALUES (%s, %s)
            ''', (user_id, score))
            self.connection.commit()
            return True
        except mysql.connector.Error as err:
            print(f"Error al guardar puntuación: {err}")
            return False
