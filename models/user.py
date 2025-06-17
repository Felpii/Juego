class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password  # En un proyecto real, la contraseña debería estar hasheada
        
    def to_dict(self):
        return {
            'username': self.username,
            'password': self.password
        }
