from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.employee import Employee
from ..models.absence import AbsenceRequest
from ..schemas.absence import AbsenceRequestCreate, AbsenceRequestRead
from .employees_router import get_current_user, get_current_admin

router = APIRouter(prefix="/absence-requests", tags=["absence-requests"])


@router.post("/", response_model=AbsenceRequestRead, status_code=status.HTTP_201_CREATED)
def create_absence_request(
    absence_in: AbsenceRequestCreate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    """
    Crea una nueva solicitud de ausencia para el usuario actual.
    """
    if absence_in.end_date < absence_in.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La fecha de fin no puede ser anterior a la fecha de inicio.",
        )

    absence = AbsenceRequest(
        employee_id=current_user.id,
        type=absence_in.type,
        start_date=absence_in.start_date,
        end_date=absence_in.end_date,
        reason=absence_in.reason,
        status="pending",
    )
    db.add(absence)
    db.commit()
    db.refresh(absence)
    return absence


@router.get("/my", response_model=List[AbsenceRequestRead])
def list_my_absence_requests(
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    """
    Lista las solicitudes de ausencia del usuario actual.
    """
    requests = (
        db.query(AbsenceRequest)
        .filter(AbsenceRequest.employee_id == current_user.id)
        .order_by(AbsenceRequest.created_at.desc())
        .all()
    )
    return requests


@router.get("/", response_model=List[AbsenceRequestRead])
def list_absence_requests(
    status_filter: Optional[str] = None,
    employee_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _: Employee = Depends(get_current_admin),
):
    """
    Lista solicitudes de ausencia (solo admin).
    Permite filtrar por estado y empleado.
    """
    query = db.query(AbsenceRequest)

    if status_filter is not None:
        query = query.filter(AbsenceRequest.status == status_filter)

    if employee_id is not None:
        query = query.filter(AbsenceRequest.employee_id == employee_id)

    requests = query.order_by(AbsenceRequest.created_at.desc()).all()
    return requests


@router.post("/{absence_id}/approve", response_model=AbsenceRequestRead)
def approve_absence_request(
    absence_id: int,
    comment: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: Employee = Depends(get_current_admin),
):
    """
    Aprueba una solicitud de ausencia (solo admin).
    """
    absence = db.query(AbsenceRequest).filter(AbsenceRequest.id == absence_id).first()
    if not absence:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud de ausencia no encontrada")

    if absence.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se pueden aprobar solicitudes en estado 'pending'.",
        )

    absence.status = "approved"
    absence.approver_id = admin.id
    absence.decision_comment = comment
    absence.decision_at = datetime.utcnow()

    db.add(absence)
    db.commit()
    db.refresh(absence)
    return absence


@router.post("/{absence_id}/reject", response_model=AbsenceRequestRead)
def reject_absence_request(
    absence_id: int,
    comment: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: Employee = Depends(get_current_admin),
):
    """
    Rechaza una solicitud de ausencia (solo admin).
    """
    absence = db.query(AbsenceRequest).filter(AbsenceRequest.id == absence_id).first()
    if not absence:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud de ausencia no encontrada")

    if absence.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se pueden rechazar solicitudes en estado 'pending'.",
        )

    absence.status = "rejected"
    absence.approver_id = admin.id
    absence.decision_comment = comment
    absence.decision_at = datetime.utcnow()

    db.add(absence)
    db.commit()
    db.refresh(absence)
    return absence
