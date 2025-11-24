from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.employee import Employee
from ..schemas.employee import EmployeeCreate, EmployeeRead
from ..utils.security import get_password_hash, decode_access_token
from .auth_router import oauth2_scheme

router = APIRouter(prefix="/employees", tags=["employees"])


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Employee:
    token_data = decode_access_token(token)
    if token_data is None or token_data.email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(Employee).filter(Employee.email == token_data.email).first()
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado o inactivo")
    return user


def get_current_admin(user: Employee = Depends(get_current_user)) -> Employee:
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Se requiere rol administrador")
    return user


@router.get("/", response_model=list[EmployeeRead])
def list_employees(
    db: Session = Depends(get_db),
    _: Employee = Depends(get_current_admin),
):
    employees = db.query(Employee).all()
    return employees


@router.post("/", response_model=EmployeeRead, status_code=status.HTTP_201_CREATED)
def create_employee(
    employee_in: EmployeeCreate,
    db: Session = Depends(get_db),
    _: Employee = Depends(get_current_admin),
):
    existing = db.query(Employee).filter(Employee.email == employee_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email ya registrado")

    hashed_password = get_password_hash(employee_in.password)
    db_employee = Employee(
        name=employee_in.name,
        email=employee_in.email,
        password_hash=hashed_password,
        role=employee_in.role,
        is_active=employee_in.is_active,
    )
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee
