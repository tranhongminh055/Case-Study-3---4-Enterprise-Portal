from sqlalchemy import Column, Integer, String, Date, DateTime
from .base import Base


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column("AttendanceID", Integer, primary_key=True, index=True)
    employee_id = Column("EmployeeID", Integer, nullable=False, index=True)
    work_date = Column("AttendanceMonth", Date, nullable=False)
    work_days = Column("WorkDays", Integer, nullable=False, default=0)
    absent_days = Column("AbsentDays", Integer, nullable=True, default=0)
    leave_days = Column("LeaveDays", Integer, nullable=True, default=0)
    created_at = Column("CreatedAt", DateTime, nullable=True)
