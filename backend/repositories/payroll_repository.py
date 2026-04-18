from backend.models.salary import Salary
from backend.models.attendance import Attendance


def get_all_salaries(session):
    return session.query(Salary).order_by(Salary.id).all()


def get_all_attendance(session):
    return session.query(Attendance).order_by(Attendance.work_date.desc()).all()


def get_salary_by_employee(session, employee_id):
    return session.query(Salary).filter(Salary.employee_id == employee_id).order_by(Salary.effective_date.desc()).all()


def get_attendance_by_employee(session, employee_id):
    return session.query(Attendance).filter(Attendance.employee_id == employee_id).order_by(Attendance.work_date.desc()).all()


def get_recent_salary(session):
    return session.query(Salary).order_by(Salary.effective_date.desc()).limit(100).all()


def get_recent_attendance(session):
    return session.query(Attendance).order_by(Attendance.work_date.desc()).limit(100).all()


def add_salary(session, salary_data: dict):
    s = Salary(
        employee_id=salary_data.get('employee_id'),
        base_salary=salary_data.get('base_salary') or salary_data.get('amount'),
        bonus=salary_data.get('bonus'),
        deductions=salary_data.get('deductions'),
        amount=salary_data.get('amount') or salary_data.get('base_salary'),
        effective_date=salary_data.get('effective_date'),
    )
    session.add(s)
    session.commit()
    session.refresh(s)
    return s


def update_salary(session, salary_id, updates: dict):
    s = session.query(Salary).filter(Salary.id == salary_id).one_or_none()
    if s is None:
        return None
    for k, v in updates.items():
        # map allowed keys
        if k in ('employee_id', 'base_salary', 'bonus', 'deductions', 'amount', 'effective_date'):
            setattr(s, k, v)
    session.add(s)
    session.commit()
    session.refresh(s)
    return s


def delete_salary(session, salary_id):
    s = session.query(Salary).filter(Salary.id == salary_id).one_or_none()
    if s is None:
        return False
    session.delete(s)
    session.commit()
    return True


def add_attendance(session, att_data: dict):
    a = Attendance(
        employee_id=att_data.get('employee_id'),
        work_date=att_data.get('work_date'),
        work_days=att_data.get('work_days', att_data.get('hours', 0)),
        absent_days=att_data.get('absent_days', 0),
        leave_days=att_data.get('leave_days', att_data.get('leave_hours', 0)),
    )
    session.add(a)
    session.commit()
    session.refresh(a)
    return a


def update_attendance(session, att_id, updates: dict):
    a = session.query(Attendance).filter(Attendance.id == att_id).one_or_none()
    if a is None:
        return None
    for k, v in updates.items():
        if k in ('employee_id', 'work_date', 'work_days', 'absent_days', 'leave_days'):
            setattr(a, k, v)
    session.add(a)
    session.commit()
    session.refresh(a)
    return a


def delete_attendance(session, att_id):
    a = session.query(Attendance).filter(Attendance.id == att_id).one_or_none()
    if a is None:
        return False
    session.delete(a)
    session.commit()
    return True
