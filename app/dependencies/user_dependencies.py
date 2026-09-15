# app/dependencies/user_dependencies.py
# Funciones reutilizables inyectadas con Depends()

from fastapi import Header, HTTPException, status
from app.services import user_service


def get_user_or_404(user_id: int):
    usuario = user_service.buscar_usuario_por_id(user_id)
    if usuario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return usuario


def obtener_configuracion_api():
    return {"app_name": "device_systems", "version": "2.0.0"}


def verificar_api_key(x_api_key: str = Header(default=None)):
    api_key_esperada = "device_systems_secret"
    if x_api_key is not None and x_api_key != api_key_esperada:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="X-API-Key invalida")
    return x_api_key