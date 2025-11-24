from pydantic import BaseModel, EmailStr


class EmployeeBase(BaseModel):
    name: str
    email: EmailStr
    role: str = "worker"
    is_active: bool = True


class EmployeeCreate(EmployeeBase):
    password: str  # lo recibimos en texto plano al crear


class EmployeeRead(EmployeeBase):
    id: int

    class Config:
        from_attributes = True  # equivale al antiguo orm_mode = True
