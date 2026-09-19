# app/routes/user_routes.py
# CRUD completo del recurso "users", ahora persistido en base de datos

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.dependencies.database_dependency import get_db
from app.dependencies.user_dependencies import get_user_or_404
from app.models.user_model import User
from app.schemas.user_schema import UserCreate, UserPatch, UserResponse, UserUpdate
from app.services import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "",
    response_model=List[UserResponse],
    summary="Listar usuarios",
    description="Devuelve los usuarios almacenados en la base de datos. Permite filtrar por rol/estado y ordenar por nombre o fecha de creación.",
    response_description="Lista de usuarios que cumplen el filtro",
)
def listar_usuarios(
    role: Optional[str] = Query(None, description="Filtrar por rol: admin, support o user"),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado activo/inactivo"),
    order_by: Optional[str] = Query(None, description="Ordenar por: name o created_at"),
    db: Session = Depends(get_db),
):
    return user_service.listar_usuarios(db, role=role, is_active=is_active, order_by=order_by)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Consultar un usuario",
    description="Devuelve un usuario puntual a partir de su id.",
    response_description="Datos del usuario encontrado",
)
def obtener_usuario(usuario: User = Depends(get_user_or_404)):
    return usuario


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un usuario",
    description="Crea un nuevo usuario en la base de datos, validando que el correo no exista.",
    response_description="Usuario creado, con su id y fecha de creación asignados por la base de datos",
)
def crear_usuario(usuario: UserCreate, db: Session = Depends(get_db)):
    if user_service.buscar_usuario_por_email(db, usuario.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un usuario registrado con el correo {usuario.email}",
        )
    return user_service.crear_usuario(db, usuario.model_dump())


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Actualizar un usuario (reemplazo completo)",
    description="Reemplaza TODOS los campos de un usuario existente.",
    response_description="Usuario con los datos actualizados",
)
def actualizar_usuario(
    datos: UserUpdate,
    usuario_existente: User = Depends(get_user_or_404),
    db: Session = Depends(get_db),
):
    otro_usuario = user_service.buscar_usuario_por_email(db, datos.email)
    if otro_usuario and otro_usuario.id != usuario_existente.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un usuario registrado con el correo {datos.email}",
        )
    return user_service.actualizar_usuario_completo(db, usuario_existente, datos.model_dump())


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Actualizar un usuario (parcial)",
    description="Modifica solo los campos enviados en el body. Debe enviarse al menos uno.",
    response_description="Usuario con los campos modificados",
)
def actualizar_usuario_parcial(
    datos: UserPatch,
    usuario_existente: User = Depends(get_user_or_404),
    db: Session = Depends(get_db),
):
    campos_enviados = datos.model_dump(exclude_unset=True)

    if not campos_enviados:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debes enviar al menos un campo para actualizar",
        )

    if "email" in campos_enviados:
        otro_usuario = user_service.buscar_usuario_por_email(db, campos_enviados["email"])
        if otro_usuario and otro_usuario.id != usuario_existente.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un usuario registrado con el correo {campos_enviados['email']}",
            )

    return user_service.actualizar_usuario_parcial(db, usuario_existente, campos_enviados)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="Eliminar un usuario",
    description="Elimina un usuario existente de la base de datos.",
    response_description="Mensaje de confirmación de la eliminación",
)
def eliminar_usuario(
    usuario_existente: User = Depends(get_user_or_404),
    db: Session = Depends(get_db),
):
    user_service.eliminar_usuario(db, usuario_existente)
    return {"detail": f"Usuario con id {usuario_existente.id} eliminado correctamente"}
