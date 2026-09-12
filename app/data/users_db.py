# app/data/users_db.py
# Simulación de base de datos en memoria para el recurso "users"

users_db = [
    {"id": 1, "name": "Ana Torres", "email": "ana@correo.com", "role": "admin", "is_active": True},
    {"id": 2, "name": "Luis Ramirez", "email": "luis@correo.com", "role": "user", "is_active": True},
    {"id": 3, "name": "Camilo Sarrazola", "email": "camilo@correo.com", "role": "support", "is_active": False},
]

_contador = {"siguiente_id": 4}


def obtener_siguiente_id():
    id_actual = _contador["siguiente_id"]
    _contador["siguiente_id"] += 1
    return id_actual