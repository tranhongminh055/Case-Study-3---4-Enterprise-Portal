from datetime import date
from sqlalchemy import func
from backend.models.employee import Employee
from backend.models.salary import Salary
from backend.models.attendance import Attendance


def anniversary_alerts(sql_session):
    today = date.today()
    return sql_session.query(Employee).filter(
        Employee.hire_date.isnot(None),
        func.month(Employee.hire_date) == today.month,
        func.day(Employee.hire_date) == today.day,
    ).all()


def abnormal_salary_alerts(mysql_session, threshold=200000):
    return mysql_session.query(Salary).filter(Salary.amount > threshold).all()


def excessive_leave_alerts(mysql_session, threshold_days=5):
    grouped = {}
    attendance_rows = mysql_session.query(Attendance).all()
    for row in attendance_rows:
        grouped.setdefault(row.employee_id, 0)
        grouped[row.employee_id] += row.leave_days or 0
    return [
        {"employee_id": employee_id, "leave_days": total}
        for employee_id, total in grouped.items()
        if total >= threshold_days
    ]
