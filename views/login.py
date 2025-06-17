import tkinter as tk
from tkinter import ttk, messagebox
import random
import time

class AnimatedBackground(tk.Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.pack(fill="both", expand=True)
        self.config(highlightthickness=0)
        self.circles = []
        self.colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEEAD']
        self.create_background()
        self.animate()
    
    def create_background(self):
        # Crear degradado de fondo
        for i in range(0, 400, 5):
            color = f'#{i//2:02x}{i//3:02x}80'
            self.create_rectangle(0, i, 1000, i+5, fill=color, outline='')
        
        # Crear círculos decorativos
        for _ in range(15):
            x = random.randint(0, 800)
            y = random.randint(0, 600)
            size = random.randint(40, 120)
            color = random.choice(self.colors)
            circle = self.create_oval(x, y, x+size, y+size, fill=color, outline='', width=0)
            self.circles.append({'id': circle, 'dx': random.uniform(-0.5, 0.5), 
                              'dy': random.uniform(-0.5, 0.5), 'x': x, 'y': y})
    
    def animate(self):
        for circle in self.circles:
            circle['x'] += circle['dx']
            circle['y'] += circle['dy']
            
            # Rebotar en los bordes
            coords = self.coords(circle['id'])
            if coords[0] <= 0 or coords[2] >= 800:
                circle['dx'] *= -1
            if coords[1] <= 0 or coords[3] >= 600:
                circle['dy'] *= -1
                
            self.move(circle['id'], circle['dx'], circle['dy'])
        
        self.after(30, self.animate)

class LoginView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Configurar el canvas de fondo animado
        self.bg_canvas = AnimatedBackground(self, width=800, height=600)
        self.bg_canvas.pack(fill="both", expand=True)
        
        # Frame para el formulario de login
        self.form_frame = tk.Frame(self.bg_canvas, bg='white', bd=0, highlightthickness=0)
        self.form_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Estilo para los widgets
        style = ttk.Style()
        style.configure('TLabel', background='white', font=('Helvetica', 10))
        style.configure('TEntry', font=('Helvetica', 10))
        style.configure('TButton', font=('Helvetica', 10, 'bold'))
        
        # Título
        title = tk.Label(self.form_frame, text="LAB-TROLL", 
                        font=('Helvetica', 24, 'bold'), bg='white', fg='#2c3e50')
        title.pack(pady=(20, 30))
        
        # Frame para los campos de entrada
        input_frame = tk.Frame(self.form_frame, bg='white')
        input_frame.pack(padx=40, pady=10)
        
        # Usuario
        tk.Label(input_frame, text="Usuario:", bg='white').grid(row=0, column=0, pady=5, sticky='e')
        self.username_entry = ttk.Entry(input_frame, width=25)
        self.username_entry.grid(row=0, column=1, pady=5, padx=5)
        
        # Contraseña
        tk.Label(input_frame, text="Contraseña:", bg='white').grid(row=1, column=0, pady=5, sticky='e')
        self.password_entry = ttk.Entry(input_frame, show="*", width=25)
        self.password_entry.grid(row=1, column=1, pady=5, padx=5)
        
        # Frame para los botones
        button_frame = tk.Frame(self.form_frame, bg='white')
        button_frame.pack(pady=20)
        
        # Botones
        ttk.Button(button_frame, text="Iniciar Sesión", command=self.login, 
                  style='Accent.TButton').pack(side='left', padx=5)
        ttk.Button(button_frame, text="Registrarse", command=self.register).pack(side='left', padx=5)
        
        # Botón de puntuaciones
        ttk.Button(self.form_frame, text="Ver Puntuaciones", 
                  command=self.show_leaderboard).pack(pady=(0, 20))
        
        # Estilo para el botón de inicio de sesión
        style.configure('Accent.TButton', background='#3498db', foreground='white')
        
        # Enfocar el campo de usuario al inicio
        self.username_entry.focus()
        
        # Configurar el evento de tecla Enter
        self.password_entry.bind('<Return>', lambda e: self.login())
        
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
