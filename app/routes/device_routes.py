from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies.database_dependency import get_db
from app.schemas.device_schema import DeviceCreate, DevicePatch, DeviceResponse, DeviceUpdate
from app.schemas.loan_schema import LoanDetailResponse
from app.services import device_service, loan_service

router = APIRouter(prefix="/devices", tags=["Devices"])


@router.get(
    "",
    response_model=List[DeviceResponse],
    summary="Listar dispositivos",
    description="Lista los dispositivos registrados, con filtros opcionales por tipo, marca, disponibilidad o texto libre.",
    response_description="Lista de dispositivos",
)
def listar_dispositivos(
    device_type: Optional[str] = Query(None, description="Filtrar por tipo de dispositivo, ej: laptop"),
    brand: Optional[str] = Query(None, description="Filtrar por marca, ej: lenovo"),
    is_available: Optional[bool] = Query(None, description="Filtrar por disponibilidad"),
    search: Optional[str] = Query(None, description="Busqueda libre por nombre, serial o tipo"),
    db: Session = Depends(get_db),
):
    return device_service.get_devices(db, device_type, brand, is_available, search)


@router.get(
    "/{device_id}",
    response_model=DeviceResponse,
    summary="Obtener un dispositivo",
    response_description="Dispositivo encontrado",
    responses={404: {"description": "Dispositivo no encontrado"}},
)
def obtener_dispositivo(device_id: int, db: Session = Depends(get_db)):
    return device_service.get_device_or_404(db, device_id)


@router.get(
    "/{device_id}/loans",
    response_model=List[LoanDetailResponse],
    summary="Historial de prestamos de un dispositivo",
    response_description="Prestamos asociados al dispositivo, con datos de usuario",
    responses={404: {"description": "Dispositivo no encontrado"}},
)
def historial_prestamos_dispositivo(device_id: int, db: Session = Depends(get_db)):
    device_service.get_device_or_404(db, device_id)
    return loan_service.get_device_loans(db, device_id)


@router.post(
    "",
    response_model=DeviceResponse,
    status_code=201,
    summary="Registrar un dispositivo",
    response_description="Dispositivo creado",
    responses={400: {"description": "Numero de serie duplicado"}, 422: {"description": "Error de validacion"}},
)
def crear_dispositivo(device: DeviceCreate, db: Session = Depends(get_db)):
    return device_service.create_device(db, device)


@router.put(
    "/{device_id}",
    response_model=DeviceResponse,
    summary="Reemplazar un dispositivo",
    description="Reemplaza todos los campos del dispositivo.",
    response_description="Dispositivo actualizado",
    responses={404: {"description": "Dispositivo no encontrado"}, 400: {"description": "Numero de serie duplicado"}},
)
def actualizar_dispositivo(device_id: int, device: DeviceUpdate, db: Session = Depends(get_db)):
    return device_service.update_device(db, device_id, device)


@router.patch(
    "/{device_id}",
    response_model=DeviceResponse,
    summary="Actualizar parcialmente un dispositivo",
    response_description="Dispositivo actualizado",
    responses={404: {"description": "Dispositivo no encontrado"}, 400: {"description": "Numero de serie duplicado"}},
)
def parchar_dispositivo(device_id: int, device: DevicePatch, db: Session = Depends(get_db)):
    return device_service.patch_device(db, device_id, device)


@router.delete(
    "/{device_id}",
    status_code=204,
    summary="Eliminar un dispositivo",
    responses={404: {"description": "Dispositivo no encontrado"}},
)
def eliminar_dispositivo(device_id: int, db: Session = Depends(get_db)):
    device_service.delete_device(db, device_id)
