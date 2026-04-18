from backend.database.session import SessionMysql
from backend.repositories import payroll_repository as repo


def list_salaries():
    with SessionMysql() as session:
        return repo.get_all_salaries(session)


def list_attendance():
    with SessionMysql() as session:
        records = repo.get_all_attendance(session)
        # Map attendance records to simple dicts expected by frontend
        out = []
        for r in records:
            status = 'Absent' if getattr(r, 'absent_days', 0) and r.absent_days > 0 else 'Present'
            out.append({
                'id': getattr(r, 'id', None),
                'employee_id': getattr(r, 'employee_id', None),
                'work_date': r.work_date.isoformat() if getattr(r, 'work_date', None) else None,
                'status': status,
                'hours': getattr(r, 'work_days', None) or 0,
                'leave_hours': getattr(r, 'leave_days', None) or 0,
            })
        return out


def create_salary(payload: dict):
    with SessionMysql() as session:
        return repo.add_salary(session, payload)


def update_salary(salary_id, payload: dict):
    with SessionMysql() as session:
        return repo.update_salary(session, salary_id, payload)


def delete_salary(salary_id):
    with SessionMysql() as session:
        return repo.delete_salary(session, salary_id)


def create_attendance(payload: dict):
    with SessionMysql() as session:
        return repo.add_attendance(session, payload)


def update_attendance(att_id, payload: dict):
    with SessionMysql() as session:
        return repo.update_attendance(session, att_id, payload)


def delete_attendance(att_id):
    with SessionMysql() as session:
        return repo.delete_attendance(session, att_id)
