from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class AbsenceRequestBase(BaseModel):
    type: str = Field(..., description="vacation, sick_leave, permission, training...")
    start_date: date
    end_date: date
    reason: Optional[str] = None


class AbsenceRequestCreate(AbsenceRequestBase):
    pass


class AbsenceRequestRead(AbsenceRequestBase):
    id: int
    employee_id: int
    status: str
    approver_id: Optional[int] = None
    decision_comment: Optional[str] = None
    created_at: datetime
    decision_at: Optional[datetime] = None

    class Config:
        from_attributes = True
