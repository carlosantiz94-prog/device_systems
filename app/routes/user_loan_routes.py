from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies.database_dependency import get_db
from app.dependencies.user_dependencies import get_user_or_404
from app.models.user_model import User
from app.schemas.loan_schema import LoanDetailResponse
from app.services import loan_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/{user_id}/loans",
    response_model=List[LoanDetailResponse],
    summary="Historial de prestamos de un usuario",
    description="Lista los prestamos asociados a un usuario, con los datos del dispositivo relacionado.",
    response_description="Prestamos del usuario, con datos del dispositivo",
    responses={404: {"description": "Usuario no encontrado"}},
)
def historial_prestamos_usuario(
    usuario: User = Depends(get_user_or_404),
    db: Session = Depends(get_db),
):
    return loan_service.get_user_loans(db, usuario.id)
