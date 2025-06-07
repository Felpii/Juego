from tkinter import Frame, Label, Entry, Button, messagebox
from tkinter import ttk

class LoginView(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.create_widgets()
        
    def create_widgets(self):
        # Configurar el estilo
        style = ttk.Style()
        style.configure("TLabel", padding=10)
        style.configure("TEntry", padding=10)
        style.configure("TButton", padding=10)
        
        # Etiquetas y campos de entrada
        Label(self, text="Usuario:").grid(row=0, column=0, padx=5, pady=5)
        self.username_entry = Entry(self)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)
        
        Label(self, text="Contraseña:").grid(row=1, column=0, padx=5, pady=5)
        self.password_entry = Entry(self, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Botones
        Button(self, text="Iniciar Sesión", command=self.login).grid(row=2, column=0, columnspan=2, pady=10)
        Button(self, text="Registrarse", command=self.register).grid(row=3, column=0, columnspan=2, pady=10)
        
        # Botón para ver puntuaciones
        Button(self, text="Ver Puntuaciones", command=self.show_leaderboard).grid(row=4, column=0, columnspan=2, pady=10)
        
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if self.controller.login(username, password):
            messagebox.showinfo("Éxito", "Inicio de sesión exitoso")
            self.controller.start_game(username)
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")
            
    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if self.controller.register(username, password):
            messagebox.showinfo("Éxito", "Registro exitoso")
        else:
            messagebox.showerror("Error", "Error al registrar usuario \n usuario ya existe")
            
    def show_leaderboard(self):
        scores = self.controller.get_leaderboard()
        if scores:
            leaderboard_text = "\n".join([f"{user}: {score} segundos" for user, score in scores])
            messagebox.showinfo("Puntuaciones", leaderboard_text)
        else:
            messagebox.showinfo("Puntuaciones", "No hay puntuaciones registradas")
