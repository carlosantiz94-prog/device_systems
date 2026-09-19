from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies.database_dependency import get_db
from app.schemas.loan_schema import LoanCreate, LoanDetailResponse, LoanResponse
from app.services import loan_service

router = APIRouter(prefix="/loans", tags=["Loans"])


@router.get(
    "/details",
    response_model=List[LoanDetailResponse],
    summary="Listar prestamos con informacion relacionada",
    description="Combina loans, users y devices mediante JOIN, con filtros opcionales.",
    response_description="Prestamos con datos de usuario y dispositivo",
)
def listar_prestamos_detallados(
    status: Optional[str] = Query(None, description="Filtrar por estado: active, returned, overdue"),
    user_email: Optional[str] = Query(None, description="Filtrar por correo del usuario"),
    device_type: Optional[str] = Query(None, description="Filtrar por tipo de dispositivo"),
    db: Session = Depends(get_db),
):
    return loan_service.get_loans_with_details(db, status, user_email, device_type)


@router.get(
    "",
    response_model=List[LoanResponse],
    summary="Listar prestamos",
    response_description="Lista de prestamos",
)
def listar_prestamos(
    status: Optional[str] = Query(None, description="Filtrar por estado: active, returned, overdue"),
    user_id: Optional[int] = Query(None, description="Filtrar por usuario"),
    device_id: Optional[int] = Query(None, description="Filtrar por dispositivo"),
    user_email: Optional[str] = Query(None, description="Filtrar por correo del usuario (requiere join)"),
    device_type: Optional[str] = Query(None, description="Filtrar por tipo de dispositivo (requiere join)"),
    db: Session = Depends(get_db),
):
    return loan_service.get_loans(db, status, user_id, device_id, user_email, device_type)


@router.get(
    "/{loan_id}",
    response_model=LoanResponse,
    summary="Obtener un prestamo",
    responses={404: {"description": "Prestamo no encontrado"}},
)
def obtener_prestamo(loan_id: int, db: Session = Depends(get_db)):
    return loan_service.get_loan_or_404(db, loan_id)


@router.post(
    "",
    response_model=LoanResponse,
    status_code=201,
    summary="Registrar un prestamo",
    description="Valida que el usuario exista, el dispositivo exista y este disponible; marca el dispositivo como no disponible.",
    response_description="Prestamo creado",
    responses={
        404: {"description": "Usuario o dispositivo no encontrado"},
        409: {"description": "El dispositivo no esta disponible"},
    },
)
def crear_prestamo(loan: LoanCreate, db: Session = Depends(get_db)):
    return loan_service.create_loan(db, loan)


@router.patch(
    "/{loan_id}/return",
    response_model=LoanResponse,
    summary="Registrar la devolucion de un prestamo",
    description="Marca el prestamo como returned, asigna la fecha de devolucion y libera el dispositivo.",
    response_description="Prestamo devuelto",
    responses={
        404: {"description": "Prestamo no encontrado"},
        409: {"description": "El prestamo ya fue devuelto"},
    },
)
def devolver_prestamo(loan_id: int, db: Session = Depends(get_db)):
    return loan_service.return_loan(db, loan_id)
