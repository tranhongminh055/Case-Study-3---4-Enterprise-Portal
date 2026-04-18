from typing import List
from fastapi import APIRouter
from backend.services import payroll_service
from backend.utils.orm import serialize_list
from fastapi import HTTPException
from pydantic import BaseModel


class SalaryCreate(BaseModel):
    employee_id: int
    base_salary: float | None = None
    bonus: float | None = None
    deductions: float | None = None
    amount: float | None = None
    effective_date: str


class SalaryUpdate(BaseModel):
    base_salary: float | None = None
    bonus: float | None = None
    deductions: float | None = None
    amount: float | None = None
    effective_date: str | None = None


class AttendanceCreate(BaseModel):
    employee_id: int
    work_date: str
    work_days: int | None = 0
    absent_days: int | None = 0
    leave_days: int | None = 0


class AttendanceUpdate(BaseModel):
    work_date: str | None = None
    work_days: int | None = None
    absent_days: int | None = None
    leave_days: int | None = None

router = APIRouter(tags=["payroll"])


@router.get("/salaries", response_model=List[dict])
def get_salaries():
    return serialize_list(payroll_service.list_salaries())


@router.get("/attendance", response_model=List[dict])
def get_attendance():
    # payroll_service.list_attendance() already returns plain dicts
    # (mapped from Attendance model). Return directly to avoid
    # serializing objects twice which can cause errors.
    return payroll_service.list_attendance()


@router.post('/salaries')
def post_salary(payload: SalaryCreate):
    obj = payroll_service.create_salary(payload.dict())
    if not obj:
        raise HTTPException(status_code=500, detail='Failed to create salary')
    from backend.utils.orm import serialize_model
    return serialize_model(obj)


@router.put('/salaries/{salary_id}')
def put_salary(salary_id: int, payload: SalaryUpdate):
    obj = payroll_service.update_salary(salary_id, payload.dict(exclude_unset=True))
    if obj is None:
        raise HTTPException(status_code=404, detail='Salary not found')
    from backend.utils.orm import serialize_model
    return serialize_model(obj)


@router.delete('/salaries/{salary_id}')
def del_salary(salary_id: int):
    ok = payroll_service.delete_salary(salary_id)
    if not ok:
        raise HTTPException(status_code=404, detail='Salary not found')
    return {'deleted': True}


@router.post('/attendance')
def post_attendance(payload: AttendanceCreate):
    obj = payroll_service.create_attendance(payload.dict())
    if not obj:
        raise HTTPException(status_code=500, detail='Failed to create attendance')
    # return as dict
    return {
        'id': getattr(obj, 'id', None),
        'employee_id': getattr(obj, 'employee_id', None),
        'work_date': getattr(obj, 'work_date').isoformat() if getattr(obj, 'work_date', None) else None,
        'work_days': getattr(obj, 'work_days', None),
        'absent_days': getattr(obj, 'absent_days', None),
        'leave_days': getattr(obj, 'leave_days', None),
    }


@router.put('/attendance/{att_id}')
def put_attendance(att_id: int, payload: AttendanceUpdate):
    obj = payroll_service.update_attendance(att_id, payload.dict(exclude_unset=True))
    if obj is None:
        raise HTTPException(status_code=404, detail='Attendance not found')
    return {
        'id': getattr(obj, 'id', None),
        'employee_id': getattr(obj, 'employee_id', None),
        'work_date': getattr(obj, 'work_date').isoformat() if getattr(obj, 'work_date', None) else None,
        'work_days': getattr(obj, 'work_days', None),
        'absent_days': getattr(obj, 'absent_days', None),
        'leave_days': getattr(obj, 'leave_days', None),
    }


@router.delete('/attendance/{att_id}')
def del_attendance(att_id: int):
    ok = payroll_service.delete_attendance(att_id)
    if not ok:
        raise HTTPException(status_code=404, detail='Attendance not found')
    return {'deleted': True}
