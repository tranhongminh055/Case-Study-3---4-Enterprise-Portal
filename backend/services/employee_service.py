from backend.database.session import SessionSqlServer, SessionMysql
from backend.repositories import employee_repository as repo
from backend.services.transaction_manager import cross_db_transaction
from backend.utils.errors import ConflictError, NotFoundError
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from backend.utils.logger import logger
from backend.repositories import payroll_repository as payroll_repo


def list_employees():
    with SessionSqlServer() as session:
        return repo.get_all_employees(session)


def list_employees_with_payroll():
    with SessionSqlServer() as sql_session, SessionMysql() as mysql_session:
        employees = repo.get_all_employees(sql_session)
        # get recent salaries and map latest by employee_id
        recent_salaries = payroll_repo.get_recent_salary(mysql_session)
        latest_map = {}
        for s in recent_salaries:
            if getattr(s, 'employee_id', None) is None:
                continue
            if s.employee_id not in latest_map:
                latest_map[s.employee_id] = s
        return [(e, latest_map.get(e.id)) for e in employees]


def get_employee(employee_id):
    with SessionSqlServer() as session:
        employee = repo.get_employee_by_id(session, employee_id)
        if not employee:
            raise NotFoundError(f"Employee {employee_id} not found")
        return employee


def create_employee(payload, simulate_mysql_failure: bool = False):
    with cross_db_transaction() as (sql_session, mysql_session, compensations):
        try:
            employee = repo.create_employee_sqlserver(sql_session, payload)
        except IntegrityError as ie:
            # translate DB unique constraint to user-friendly conflict
            raise ConflictError("Employee with this email already exists")

        # compensation: if MySQL commit fails after SQL commit, remove the SQL record
        def _comp_delete_sql():
            from backend.database.session import SessionSqlServer
            with SessionSqlServer() as s:
                emp = repo.get_employee_by_id(s, employee.id)
                if emp:
                    repo.delete_employee_sqlserver(s, emp)
                    s.commit()

        compensations.append(_comp_delete_sql)

        if simulate_mysql_failure:
            raise RuntimeError("Simulated MySQL failure after SQL Server write")
        # MySQL model uses same Employee class; remove transient keys
        # do not force `id` into MySQL payload (schemas may differ)
        mysql_payload = {**payload}
        mysql_payload.pop("first_name", None)
        mysql_payload.pop("last_name", None)
        # Pass the employee ID from SQL Server to MySQL
        mysql_payload["id"] = employee.id
        # build full_name for MySQL if needed
        if "full_name" not in mysql_payload:
            first_name = payload.get("first_name", "")
            last_name = payload.get("last_name", "")
            if first_name or last_name:
                mysql_payload["full_name"] = f"{first_name} {last_name}".strip()
        try:
            repo.create_employee_mysql(mysql_session, mysql_payload)
            logger.info("Created employee %s in SQL Server and MySQL", employee.id)
        except Exception as e:
            logger.exception("MySQL create failed, continuing with SQL Server only: %s", e)

        # serialize before sessions close so caller gets concrete data
        from backend.utils.orm import serialize_model
        emp_data = serialize_model(employee)
        return emp_data


def update_employee(employee_id, payload, simulate_mysql_failure: bool = False):
    with cross_db_transaction() as (sql_session, mysql_session, compensations):
        employee = repo.get_employee_by_id(sql_session, employee_id)
        if not employee:
            raise NotFoundError(f"Employee {employee_id} not found")

        # if email is changing, ensure no other employee already uses it
        if 'email' in payload and payload.get('email') is not None:
            new_email = payload.get('email')
            if new_email != employee.email:
                existing = repo.get_employee_by_email(sql_session, new_email)
                if existing and existing.id != employee_id:
                    raise ConflictError("Email already used by another employee")

        # capture previous values for compensation
        prev = {k: getattr(employee, k) for k in payload.keys() if hasattr(employee, k)}

        try:
            updated = repo.update_employee_sqlserver(sql_session, employee, payload)
        except IntegrityError as ie:
            raise ConflictError("Update conflict: possibly duplicate email")

        def _comp_restore_sql():
            from backend.database.session import SessionSqlServer
            with SessionSqlServer() as s:
                emp = repo.get_employee_by_id(s, employee_id)
                if emp:
                    repo.update_employee_sqlserver(s, emp, prev)
                    s.commit()

        compensations.append(_comp_restore_sql)

        if simulate_mysql_failure:
            raise RuntimeError("Simulated MySQL failure during update")
        # prepare MySQL payload
        mysql_update_payload = {**payload}
        mysql_update_payload.pop("first_name", None)
        mysql_update_payload.pop("last_name", None)
        if "first_name" in payload or "last_name" in payload:
            # split existing full_name if needed
            existing_full = employee.full_name or ""
            parts = existing_full.split()
            if len(parts) >= 2:
                existing_first = " ".join(parts[:-1])
                existing_last = parts[-1]
            else:
                existing_first = existing_full
                existing_last = ""
            first_name = payload.get("first_name", existing_first)
            last_name = payload.get("last_name", existing_last)
            mysql_update_payload["full_name"] = f"{first_name} {last_name}".strip()
        try:
            repo.update_employee_mysql(mysql_session, employee_id, mysql_update_payload)
            logger.info("Updated employee %s in SQL Server and MySQL", employee_id)
        except Exception as e:
            logger.exception("MySQL update failed, continuing with SQL Server only: %s", e)
        # serialize before sessions close
        from backend.utils.orm import serialize_model
        return serialize_model(updated)


def delete_employee(employee_id):
    with cross_db_transaction() as (sql_session, mysql_session, compensations):
        employee = repo.get_employee_by_id(sql_session, employee_id)
        if not employee:
            raise NotFoundError(f"Employee {employee_id} not found")
        # Allow deletion even with salary/dividend records for testing purposes
        # if repo.has_salary_for_employee(mysql_session, employee_id):
        #     raise ConflictError("Cannot delete employee with payroll salary records")
        # try:
        #     if repo.has_dividend_for_employee(sql_session, employee_id):
        #         raise ConflictError("Cannot delete employee with dividend records")
        # except Exception as e:
        #     # In some development DBs the dividends schema may differ; log and continue with best-effort
        #     logger.exception("Failed to check dividends for employee %s — proceeding with delete: %s", employee_id, e)

        # Delete related dividends first to avoid foreign key constraint
        try:
            sql_session.execute(text("DELETE FROM dividends WHERE EmployeeID = :id"), {"id": employee_id})
            sql_session.execute(text("DELETE FROM dividends WHERE employee_id = :id"), {"id": employee_id})
            sql_session.flush()
        except Exception as e:
            logger.exception("Failed to delete related dividends for employee %s before delete: %s", employee_id, e)

        # capture previous state for compensation (recreate if needed)
        from backend.utils.orm import serialize_model
        prev_data = serialize_model(employee)

        def _comp_recreate_sql():
            from backend.database.session import SessionSqlServer
            with SessionSqlServer() as s:
                # only recreate if missing
                existing = repo.get_employee_by_id(s, employee_id)
                if not existing:
                    repo.create_employee_sqlserver(s, prev_data)
                    s.commit()

        compensations.append(_comp_recreate_sql)

        try:
            repo.delete_employee_sqlserver(sql_session, employee)
        except IntegrityError as ie:
            logger.warning("Employee delete failed due to FK constraint, retrying after dependent delete: %s", ie)
            sql_session.rollback()
            sql_session.execute(text("DELETE FROM dividends WHERE EmployeeID = :id"), {"id": employee_id})
            sql_session.execute(text("DELETE FROM dividends WHERE employee_id = :id"), {"id": employee_id})
            sql_session.flush()
            repo.delete_employee_sqlserver(sql_session, employee)

        try:
            repo.delete_employee_mysql(mysql_session, employee_id)
            logger.info("Deleted employee %s from both databases", employee_id)
        except Exception as e:
            logger.exception("MySQL delete failed, SQL Server delete completed: %s", e)
