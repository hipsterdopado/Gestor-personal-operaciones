from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TimeEntryBase(BaseModel):
    clock_in: datetime
    clock_out: Optional[datetime] = None
    notes: Optional[str] = None


class TimeEntryRead(TimeEntryBase):
    id: int
    employee_id: int

    class Config:
        from_attributes = True
