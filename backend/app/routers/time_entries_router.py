from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.employee import Employee
from ..models.time_entry import TimeEntry
from ..schemas.time_entry import TimeEntryRead
from .employees_router import get_current_user, get_current_admin

router = APIRouter(prefix="/time-entries", tags=["time-entries"])


def get_open_time_entry(db: Session, employee_id: int) -> Optional[TimeEntry]:
    return (
        db.query(TimeEntry)
        .filter(TimeEntry.employee_id == employee_id, TimeEntry.clock_out.is_(None))
        .order_by(TimeEntry.clock_in.desc())
        .first()
    )


@router.post("/clock-in", response_model=TimeEntryRead, status_code=status.HTTP_201_CREATED)
def clock_in(
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    """
    Crea un nuevo fichaje de entrada para el usuario actual.
    No permite tener otro fichaje abierto.
    """
    open_entry = get_open_time_entry(db, current_user.id)
    if open_entry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya tienes un fichaje abierto. Debes fichar salida antes de volver a fichar entrada.",
        )

    entry = TimeEntry(
        employee_id=current_user.id,
        clock_in=datetime.utcnow(),
        notes=notes,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.post("/clock-out", response_model=TimeEntryRead)
def clock_out(
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    """
    Cierra el último fichaje abierto del usuario actual.
    """
    open_entry = get_open_time_entry(db, current_user.id)
    if not open_entry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No tienes fichajes abiertos para cerrar.",
        )

    open_entry.clock_out = datetime.utcnow()
    db.add(open_entry)
    db.commit()
    db.refresh(open_entry)
    return open_entry


@router.get("/my", response_model=List[TimeEntryRead])
def list_my_time_entries(
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    """
    Lista los fichajes del usuario actual.
    """
    entries = (
        db.query(TimeEntry)
        .filter(TimeEntry.employee_id == current_user.id)
        .order_by(TimeEntry.clock_in.desc())
        .all()
    )
    return entries


@router.get("/", response_model=List[TimeEntryRead])
def list_time_entries(
    employee_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _: Employee = Depends(get_current_admin),
):
    """
    Lista fichajes (solo admin).
    Permite filtrar por employee_id.
    """
    query = db.query(TimeEntry)
    if employee_id is not None:
        query = query.filter(TimeEntry.employee_id == employee_id)

    entries = query.order_by(TimeEntry.clock_in.desc()).all()
    return entries
