# app/dependencies/user_dependencies.py
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies.database_dependency import get_db
from app.services import user_service


def get_user_or_404(user_id: int, db: Session = Depends(get_db)):
    usuario = user_service.buscar_usuario_por_id(db, user_id)
    if usuario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return usuario