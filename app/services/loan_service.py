from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import and_
from sqlalchemy.orm import Session, joinedload

from app.models.device_model import Device
from app.models.loan_model import Loan
from app.models.user_model import User
from app.schemas.loan_schema import DeviceBasic, LoanCreate, LoanDetailResponse, UserBasic


def _to_detail_response(loan: Loan) -> LoanDetailResponse:
    return LoanDetailResponse(
        loan_id=loan.id,
        status=loan.status,
        loan_date=loan.loan_date,
        return_date=loan.return_date,
        user=UserBasic.model_validate(loan.user),
        device=DeviceBasic.model_validate(loan.device),
    )


def get_loans(
    db: Session,
    status_filter: Optional[str] = None,
    user_id: Optional[int] = None,
    device_id: Optional[int] = None,
    user_email: Optional[str] = None,
    device_type: Optional[str] = None,
) -> List[Loan]:
    query = db.query(Loan)

    needs_join = user_email is not None or device_type is not None
    if needs_join:
        query = query.join(User, Loan.user_id == User.id).join(Device, Loan.device_id == Device.id)

    conditions = []
    if status_filter is not None:
        conditions.append(Loan.status == status_filter)
    if user_id is not None:
        conditions.append(Loan.user_id == user_id)
    if device_id is not None:
        conditions.append(Loan.device_id == device_id)
    if user_email is not None:
        conditions.append(User.email.ilike(f"%{user_email}%"))
    if device_type is not None:
        conditions.append(Device.device_type.ilike(f"%{device_type}%"))

    if conditions:
        query = query.where(and_(*conditions))

    return query.order_by(Loan.id).all()


def get_loan_or_404(db: Session, loan_id: int) -> Loan:
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prestamo no encontrado")
    return loan


def create_loan(db: Session, loan_data: LoanCreate) -> Loan:
    user = db.query(User).filter(User.id == loan_data.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    device = db.query(Device).filter(Device.id == loan_data.device_id).first()
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispositivo no encontrado")

    if not device.is_available:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El dispositivo no esta disponible para prestamo",
        )

    loan = Loan(user_id=loan_data.user_id, device_id=loan_data.device_id, status="active")
    device.is_available = False
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan


def return_loan(db: Session, loan_id: int) -> Loan:
    loan = get_loan_or_404(db, loan_id)

    if loan.status == "returned":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este prestamo ya fue devuelto",
        )

    loan.status = "returned"
    loan.return_date = datetime.utcnow()
    loan.device.is_available = True

    db.commit()
    db.refresh(loan)
    return loan


def get_loans_with_details(
    db: Session,
    status_filter: Optional[str] = None,
    user_email: Optional[str] = None,
    device_type: Optional[str] = None,
) -> List[LoanDetailResponse]:
    query = (
        db.query(Loan)
        .join(User, Loan.user_id == User.id)
        .join(Device, Loan.device_id == Device.id)
        .options(joinedload(Loan.user), joinedload(Loan.device))
    )

    conditions = []
    if status_filter is not None:
        conditions.append(Loan.status == status_filter)
    if user_email is not None:
        conditions.append(User.email.ilike(f"%{user_email}%"))
    if device_type is not None:
        conditions.append(Device.device_type.ilike(f"%{device_type}%"))

    if conditions:
        query = query.where(and_(*conditions))

    loans = query.order_by(Loan.id).all()
    return [_to_detail_response(loan) for loan in loans]


def get_user_loans(db: Session, user_id: int) -> List[LoanDetailResponse]:
    loans = (
        db.query(Loan)
        .join(Device, Loan.device_id == Device.id)
        .options(joinedload(Loan.user), joinedload(Loan.device))
        .where(Loan.user_id == user_id)
        .order_by(Loan.id)
        .all()
    )
    return [_to_detail_response(loan) for loan in loans]


def get_device_loans(db: Session, device_id: int) -> List[LoanDetailResponse]:
    loans = (
        db.query(Loan)
        .join(User, Loan.user_id == User.id)
        .options(joinedload(Loan.user), joinedload(Loan.device))
        .where(Loan.device_id == device_id)
        .order_by(Loan.id)
        .all()
    )
    return [_to_detail_response(loan) for loan in loans]
