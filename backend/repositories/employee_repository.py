from sqlalchemy.exc import SQLAlchemyError
from backend.models.employee import Employee
from backend.models.salary import Salary
from backend.models.dividend import Dividend


def _build_full_name(payload):
    first_name = payload.get("first_name", "")
    last_name = payload.get("last_name", "")
    first_name = first_name.strip() if first_name else ""
    last_name = last_name.strip() if last_name else ""
    if first_name and last_name:
        return f"{first_name} {last_name}"
    return first_name or last_name or payload.get("full_name", "")


def get_all_employees(session):
    return session.query(Employee).order_by(Employee.id).all()


def get_employee_by_id(session, employee_id):
    return session.query(Employee).filter(Employee.id == employee_id).first()


def get_employee_by_email(session, email):
    return session.query(Employee).filter(Employee.email == email).first()


def create_employee_sqlserver(session, payload):
    payload = payload.copy()
    payload["full_name"] = _build_full_name(payload)
    # ensure DB non-nullable fields are present; some schemas require DateOfBirth
    if payload.get("date_of_birth") is None:
        # fallback to hire_date if available to avoid NULL insert errors
        if payload.get("hire_date") is not None:
            payload["date_of_birth"] = payload.get("hire_date")
        else:
            payload["date_of_birth"] = None
    payload.pop("first_name", None)
    payload.pop("last_name", None)
    employee = Employee(**payload)
    session.add(employee)
    session.flush()
    return employee


def create_employee_mysql(session, payload):
    # Always use fallback for MySQL since schema may differ
    from sqlalchemy import text
    # MySQL employees_payroll table columns: EmployeeID, FullName, DepartmentID, PositionID, Status, SyncedAt
    full_name = payload.get('full_name') or _build_full_name(payload)
    employee_id = payload.get('id')  # Must get EmployeeID from payload
    
    params = {
        'EmployeeID': employee_id,
        'FullName': full_name,
        'DepartmentID': payload.get('department_id'),
        'PositionID': payload.get('position_id'),
        'Status': payload.get('status') or 'active',
    }
    # Insert only into columns that exist in MySQL employees_payroll
    sql = text(
        "INSERT INTO employees_payroll (EmployeeID, FullName, DepartmentID, PositionID, Status) VALUES (:EmployeeID, :FullName, :DepartmentID, :PositionID, :Status)"
    )
    session.execute(sql, params)
    session.flush()
    # try to return a lightweight object compatible with caller expectations
    class SimpleObj:
        pass

    obj = SimpleObj()
    obj.id = employee_id
    obj.full_name = full_name
    obj.email = payload.get('email')
    obj.hire_date = payload.get('hire_date')
    obj.department_id = payload.get('department_id')
    obj.position_id = payload.get('position_id')
    obj.status = payload.get('status') or 'active'
    return obj


def update_employee_sqlserver(session, employee, payload):
    payload = payload.copy()
    if "first_name" in payload or "last_name" in payload:
        payload["full_name"] = _build_full_name(payload)
        payload.pop("first_name", None)
        payload.pop("last_name", None)
    for field, value in payload.items():
        setattr(employee, field, value)
    session.flush()
    return employee


def update_employee_mysql(session, employee_id, payload):
    # Always use fallback for MySQL
    from sqlalchemy import text
    updates = []
    params = {'id': employee_id}
    
    # MySQL employees_payroll only has: EmployeeID, FullName, DepartmentID, PositionID, Status, SyncedAt
    # Build full_name from first_name/last_name if provided
    if 'first_name' in payload or 'last_name' in payload or 'full_name' in payload:
        full = payload.get('full_name') or _build_full_name(payload)
        updates.append('FullName = :FullName')
        params['FullName'] = full
    
    if 'department_id' in payload:
        updates.append('DepartmentID = :DepartmentID')
        params['DepartmentID'] = payload.get('department_id')
    
    if 'position_id' in payload:
        updates.append('PositionID = :PositionID')
        params['PositionID'] = payload.get('position_id')
    
    if 'status' in payload:
        updates.append('Status = :Status')
        params['Status'] = payload.get('status')
    
    if updates:
        sql = text(f"UPDATE employees_payroll SET {', '.join(updates)} WHERE EmployeeID = :id")
        session.execute(sql, params)
        session.flush()
    
    # return lightweight object
    class SimpleObj:
        pass

    obj = SimpleObj()
    obj.id = employee_id
    return obj


def delete_employee_sqlserver(session, employee):
    session.delete(employee)
    session.flush()


def delete_employee_mysql(session, employee_id):
    # Always use fallback for MySQL
    from sqlalchemy import text
    try:
        session.execute(text("DELETE FROM employees_payroll WHERE EmployeeID = :id"), {'id': employee_id})
        session.flush()
    except Exception:
        # swallow; caller will log/handle
        pass


def has_salary_for_employee(session, employee_id):
    return session.query(Salary).filter(Salary.employee_id == employee_id).first() is not None


def has_dividend_for_employee(session, employee_id):
    return session.query(Dividend).filter(Dividend.employee_id == employee_id).first() is not None
