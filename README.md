# Juego Laberinto POE

## Descripción
Juego de laberinto con elementos de acertijo desarrollado en Python usando el patrón MVC.

## Características
- Sistema de login y registro de usuarios
- Base de datos MySQL para almacenar puntajes
- Laberinto con meta falsa y verdadera
- Sistema de tiempo para medir el rendimiento
- Diseño orientado a eventos (POE)

## Estructura del Proyecto
```
juego/
├── models/
│   ├── user.py
│   └── score.py
├── views/
│   ├── login.py
│   ├── game.py
│   └── leaderboard.py
├── controllers/
│   ├── user_controller.py
│   └── game_controller.py
├── database/
│   └── database.py
├── config/
│   └── config.py
└── main.py
```

## Requisitos
- Python 3.8+
- MySQL Server
- phpMyAdmin
- tkinter (incluido en Python)
- mysql-connector-python
- threading

## Instalación
1. Instalar las dependencias:
```bash
pip install mysql-connector-python
```

2. Configurar la base de datos MySQL
3. Ejecutar `main.py`
