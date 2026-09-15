# app/services/user_service.py
# Logica de negocio del recurso "users"

from typing import Optional
from app.data.users_db import obtener_siguiente_id, users_db


def listar_usuarios(role: Optional[str] = None, is_active: Optional[bool] = None):
    resultado = users_db
    if role is not None:
        resultado = [u for u in resultado if u["role"] == role]
    if is_active is not None:
        resultado = [u for u in resultado if u["is_active"] == is_active]
    return resultado


def buscar_usuario_por_id(user_id: int):
    for usuario in users_db:
        if usuario["id"] == user_id:
            return usuario
    return None


def correo_ya_existe(email: str, excluir_id: Optional[int] = None):
    for usuario in users_db:
        if usuario["email"] == email and usuario["id"] != excluir_id:
            return True
    return False


def crear_usuario(datos: dict):
    nuevo_usuario = datos.copy()
    nuevo_usuario["id"] = obtener_siguiente_id()
    users_db.append(nuevo_usuario)
    return nuevo_usuario


def actualizar_usuario_completo(user_id: int, datos: dict):
    usuario = buscar_usuario_por_id(user_id)
    if usuario is None:
        return None
    usuario.update(datos)
    usuario["id"] = user_id
    return usuario


def actualizar_usuario_parcial(user_id: int, datos: dict):
    usuario = buscar_usuario_por_id(user_id)
    if usuario is None:
        return None
    usuario.update(datos)
    return usuario


def eliminar_usuario(user_id: int):
    usuario = buscar_usuario_por_id(user_id)
    if usuario is None:
        return False
    users_db.remove(usuario)
    return True