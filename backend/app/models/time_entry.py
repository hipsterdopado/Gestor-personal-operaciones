from sqlalchemy import Column, Integer, DateTime, String, ForeignKey, func
from sqlalchemy.orm import relationship

from ..database import Base


class TimeEntry(Base):
    __tablename__ = "time_entries"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    clock_in = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    clock_out = Column(DateTime(timezone=True), nullable=True)
    notes = Column(String, nullable=True)

    employee = relationship("Employee", backref="time_entries")
