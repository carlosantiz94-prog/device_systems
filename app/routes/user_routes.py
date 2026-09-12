# app/routes/user_routes.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.dependencies.user_dependencies import get_user_or_404
from app.schemas.user_schema import UserCreate, UserPatch, UserResponse, UserUpdate
from app.services import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=List[UserResponse], summary="Listar usuarios")
def listar_usuarios(
    role: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
):
    return user_service.listar_usuarios(role=role, is_active=is_active)


@router.get("/{user_id}", response_model=UserResponse, summary="Consultar un usuario")
def obtener_usuario(usuario: dict = Depends(get_user_or_404)):
    return usuario


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Registrar un usuario")
def crear_usuario(usuario: UserCreate):
    if user_service.correo_ya_existe(usuario.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Ya existe un usuario registrado con el correo {usuario.email}")
    return user_service.crear_usuario(usuario.model_dump())


@router.put("/{user_id}", response_model=UserResponse, summary="Actualizar un usuario (completo)")
def actualizar_usuario(datos: UserUpdate, usuario_existente: dict = Depends(get_user_or_404)):
    if user_service.correo_ya_existe(datos.email, excluir_id=usuario_existente["id"]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Ya existe un usuario registrado con el correo {datos.email}")
    return user_service.actualizar_usuario_completo(usuario_existente["id"], datos.model_dump())


@router.patch("/{user_id}", response_model=UserResponse, summary="Actualizar un usuario (parcial)")
def actualizar_usuario_parcial(datos: UserPatch, usuario_existente: dict = Depends(get_user_or_404)):
    campos_enviados = datos.model_dump(exclude_unset=True)
    if not campos_enviados:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Debes enviar al menos un campo para actualizar")
    if "email" in campos_enviados and user_service.correo_ya_existe(campos_enviados["email"], excluir_id=usuario_existente["id"]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Ya existe un usuario registrado con el correo {campos_enviados['email']}")
    return user_service.actualizar_usuario_parcial(usuario_existente["id"], campos_enviados)


@router.delete("/{user_id}", status_code=status.HTTP_200_OK, summary="Eliminar un usuario")
def eliminar_usuario(usuario_existente: dict = Depends(get_user_or_404)):
    user_service.eliminar_usuario(usuario_existente["id"])
    return {"detail": f"Usuario con id {usuario_existente['id']} eliminado correctamente"}