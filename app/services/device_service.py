from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.device_model import Device
from app.schemas.device_schema import DeviceCreate, DevicePatch, DeviceUpdate


def get_devices(
    db: Session,
    device_type: Optional[str] = None,
    brand: Optional[str] = None,
    is_available: Optional[bool] = None,
    search: Optional[str] = None,
):
    query = db.query(Device)

    if device_type is not None:
        query = query.filter(Device.device_type.ilike(device_type))
    if brand is not None:
        query = query.filter(Device.brand.ilike(brand))
    if is_available is not None:
        query = query.filter(Device.is_available == is_available)
    if search is not None:
        like_term = f"%{search}%"
        query = query.filter(
            or_(
                Device.name.ilike(like_term),
                Device.serial_number.ilike(like_term),
                Device.device_type.ilike(like_term),
            )
        )

    return query.order_by(Device.id).all()


def get_device_or_404(db: Session, device_id: int) -> Device:
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispositivo no encontrado")
    return device


def _validar_serial_no_duplicado(db: Session, serial_number: str, exclude_device_id: Optional[int] = None) -> None:
    query = db.query(Device).filter(Device.serial_number == serial_number)
    if exclude_device_id is not None:
        query = query.filter(Device.id != exclude_device_id)
    if query.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un dispositivo con ese numero de serie",
        )


def create_device(db: Session, device_data: DeviceCreate) -> Device:
    _validar_serial_no_duplicado(db, device_data.serial_number)
    device = Device(**device_data.model_dump())
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


def update_device(db: Session, device_id: int, device_data: DeviceUpdate) -> Device:
    device = get_device_or_404(db, device_id)
    _validar_serial_no_duplicado(db, device_data.serial_number, exclude_device_id=device_id)
    for field, value in device_data.model_dump().items():
        setattr(device, field, value)
    db.commit()
    db.refresh(device)
    return device


def patch_device(db: Session, device_id: int, device_data: DevicePatch) -> Device:
    device = get_device_or_404(db, device_id)
    updates = device_data.model_dump(exclude_unset=True)
    if "serial_number" in updates:
        _validar_serial_no_duplicado(db, updates["serial_number"], exclude_device_id=device_id)
    for field, value in updates.items():
        setattr(device, field, value)
    db.commit()
    db.refresh(device)
    return device


def delete_device(db: Session, device_id: int) -> None:
    device = get_device_or_404(db, device_id)
    db.delete(device)
    db.commit()
