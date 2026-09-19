# app/services/user_service.py
from typing import Optional
from sqlalchemy.orm import Session
from app.models.user_model import User


def listar_usuarios(db: Session, role: Optional[str] = None, is_active: Optional[bool] = None, order_by: Optional[str] = None):
    query = db.query(User)
    if role is not None:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    if order_by == "name":
        query = query.order_by(User.name.asc())
    elif order_by == "created_at":
        query = query.order_by(User.created_at.asc())
    return query.all()


def buscar_usuario_por_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def buscar_usuario_por_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def crear_usuario(db: Session, datos: dict):
    nuevo_usuario = User(**datos)
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario


def actualizar_usuario_completo(db: Session, usuario: User, datos: dict):
    for campo, valor in datos.items():
        setattr(usuario, campo, valor)
    db.commit()
    db.refresh(usuario)
    return usuario


def actualizar_usuario_parcial(db: Session, usuario: User, datos: dict):
    for campo, valor in datos.items():
        setattr(usuario, campo, valor)
    db.commit()
    db.refresh(usuario)
    return usuario


def eliminar_usuario(db: Session, usuario: User):
    db.delete(usuario)
    db.commit()