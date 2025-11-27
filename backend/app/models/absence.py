from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from ..database import Base


class AbsenceRequest(Base):
    __tablename__ = "absence_requests"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)

    # Tipo de ausencia: vacation, sick_leave, permission, training...
    type = Column(String, nullable=False)

    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    # pending | approved | rejected
    status = Column(String, nullable=False, default="pending")

    approver_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    reason = Column(String, nullable=True)
    decision_comment = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    decision_at = Column(DateTime(timezone=True), nullable=True)

    employee = relationship("Employee", foreign_keys=[employee_id], backref="absence_requests")
    approver = relationship("Employee", foreign_keys=[approver_id], backref="approved_absence_requests")
