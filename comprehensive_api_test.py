import requests
import json
import time

BASE_URL = "http://localhost:8000"

def print_test_result(test_name, status_code, expected=None, success_msg=None, error_msg=None):
    if expected and status_code in expected:
        print(f"✅ {test_name}: {status_code} - {success_msg or 'Success'}")
        return True
    elif not expected and status_code < 400:
        print(f"✅ {test_name}: {status_code} - {success_msg or 'Success'}")
        return True
    else:
        print(f"❌ {test_name}: {status_code} - {error_msg or 'Failed'}")
        if status_code >= 400:
            try:
                print(f"   Error: {requests.get(f'{BASE_URL}{test_name.split()[-1]}').text}")
            except:
                pass
        return False

def test_auth_endpoints():
    print("\n🔐 Testing Auth Endpoints")
    print("=" * 50)

    # Register
    register_data = {
        "username": "testuser@example.com",
        "password": "TestPass123!",
        "phone": "+84123456789",
        "role": "Admin"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    print_test_result("POST /auth/register", response.status_code, [201, 409], "User registered or already exists")

    # Login
    login_data = {
        "username": "testuser@example.com",
        "password": "TestPass123!"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    token = None
    if print_test_result("POST /auth/login", response.status_code, [200], "Login successful"):
        token = response.json().get("access_token")

    if token:
        headers = {"Authorization": f"Bearer {token}"}

        # Refresh token
        response = requests.post(f"{BASE_URL}/auth/refresh", headers=headers)
        new_token = None
        if print_test_result("POST /auth/refresh", response.status_code, [200], "Token refreshed"):
            new_token = response.json().get("access_token")

        # Logout
        logout_headers = {"Authorization": f"Bearer {new_token or token}"}
        response = requests.post(f"{BASE_URL}/auth/logout", headers=logout_headers)
        print_test_result("POST /auth/logout", response.status_code, [200], "Logout successful")

    return token

def test_employee_endpoints(token):
    print("\n👥 Testing Employee Endpoints")
    print("=" * 50)

    if not token:
        print("❌ No auth token available, skipping employee tests")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # Get employees
    response = requests.get(f"{BASE_URL}/employees", headers=headers)
    print_test_result("GET /employees", response.status_code, [200], "Retrieved employees list")

    # Get employees with payroll
    response = requests.get(f"{BASE_URL}/employees/with-payroll", headers=headers)
    print_test_result("GET /employees/with-payroll", response.status_code, [200], "Retrieved employees with payroll")

    # Create employee
    employee_data = {
        "first_name": "Nguyen",
        "last_name": "Van A",
        "email": "nguyen.vana@example.com",
        "phone": "+84123456789",
        "hire_date": "2023-01-01",
        "department_id": 1,
        "position_id": 1,
        "status": "active"
    }
    response = requests.post(f"{BASE_URL}/employees", json=employee_data, headers=headers)
    employee_id = None
    if print_test_result("POST /employees", response.status_code, [201], "Employee created"):
        employee_id = response.json().get("id")

    if employee_id:
        # Get specific employee
        response = requests.get(f"{BASE_URL}/employees/{employee_id}", headers=headers)
        print_test_result(f"GET /employees/{employee_id}", response.status_code, [200], "Retrieved specific employee")

        # Update employee
        update_data = {
            "first_name": "Nguyen",
            "last_name": "Van B",
            "email": "nguyen.vanb@example.com"
        }
        response = requests.put(f"{BASE_URL}/employees/{employee_id}", json=update_data, headers=headers)
        print_test_result(f"PUT /employees/{employee_id}", response.status_code, [200], "Employee updated")

        # Delete employee
        response = requests.delete(f"{BASE_URL}/employees/{employee_id}", headers=headers)
        print_test_result(f"DELETE /employees/{employee_id}", response.status_code, [200], "Employee deleted")

def test_department_endpoints():
    print("\n🏢 Testing Department Endpoints")
    print("=" * 50)

    # Get departments
    response = requests.get(f"{BASE_URL}/departments")
    print_test_result("GET /departments", response.status_code, [200], "Retrieved departments list")

    # Create department
    dept_data = {
        "name": "IT Department",
        "description": "Information Technology Department"
    }
    response = requests.post(f"{BASE_URL}/departments", json=dept_data)
    dept_id = None
    if print_test_result("POST /departments", response.status_code, [201], "Department created"):
        dept_id = response.json().get("id")

    if dept_id:
        # Get specific department
        response = requests.get(f"{BASE_URL}/departments/{dept_id}")
        print_test_result(f"GET /departments/{dept_id}", response.status_code, [200], "Retrieved specific department")

        # Update department
        update_data = {
            "name": "Information Technology",
            "description": "IT Department"
        }
        response = requests.put(f"{BASE_URL}/departments/{dept_id}", json=update_data)
        print_test_result(f"PUT /departments/{dept_id}", response.status_code, [200], "Department updated")

        # Delete department
        response = requests.delete(f"{BASE_URL}/departments/{dept_id}")
        print_test_result(f"DELETE /departments/{dept_id}", response.status_code, [200], "Department deleted")

def test_position_endpoints():
    print("\n💼 Testing Position Endpoints")
    print("=" * 50)

    # Get positions
    response = requests.get(f"{BASE_URL}/positions")
    print_test_result("GET /positions", response.status_code, [200], "Retrieved positions list")

    # Create position
    pos_data = {
        "title": "Software Developer",
        "grade": "Senior",
        "description": "Senior Software Developer"
    }
    response = requests.post(f"{BASE_URL}/positions", json=pos_data)
    pos_id = None
    if print_test_result("POST /positions", response.status_code, [201], "Position created"):
        pos_id = response.json().get("id")

    if pos_id:
        # Get specific position
        response = requests.get(f"{BASE_URL}/positions/{pos_id}")
        print_test_result(f"GET /positions/{pos_id}", response.status_code, [200], "Retrieved specific position")

        # Update position
        update_data = {
            "title": "Senior Developer",
            "grade": "Lead"
        }
        response = requests.put(f"{BASE_URL}/positions/{pos_id}", json=update_data)
        print_test_result(f"PUT /positions/{pos_id}", response.status_code, [200], "Position updated")

        # Delete position
        response = requests.delete(f"{BASE_URL}/positions/{pos_id}")
        print_test_result(f"DELETE /positions/{pos_id}", response.status_code, [200], "Position deleted")

def test_payroll_endpoints(token):
    print("\n💰 Testing Payroll Endpoints")
    print("=" * 50)

    if not token:
        print("❌ No auth token available, skipping payroll tests")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # Get salaries (note: routes are at root level, not /payroll/)
    response = requests.get(f"{BASE_URL}/salaries", headers=headers)
    print_test_result("GET /salaries", response.status_code, [200], "Retrieved salaries list")

    # Get attendance
    response = requests.get(f"{BASE_URL}/attendance", headers=headers)
    print_test_result("GET /attendance", response.status_code, [200], "Retrieved attendance list")

    # Create salary
    salary_data = {
        "employee_id": 1,
        "amount": 50000.00,
        "effective_date": "2024-01-01"
    }
    response = requests.post(f"{BASE_URL}/salaries", json=salary_data, headers=headers)
    salary_id = None
    if print_test_result("POST /salaries", response.status_code, [201], "Salary created"):
        salary_id = response.json().get("id")

    # Create attendance
    attendance_data = {
        "employee_id": 1,
        "date": "2024-01-01",
        "status": "present",
        "hours_worked": 8.0
    }
    response = requests.post(f"{BASE_URL}/attendance", json=attendance_data, headers=headers)
    att_id = None
    if print_test_result("POST /attendance", response.status_code, [201], "Attendance created"):
        att_id = response.json().get("id")

    if salary_id:
        # Update salary
        update_data = {"amount": 55000.00}
        response = requests.put(f"{BASE_URL}/salaries/{salary_id}", json=update_data, headers=headers)
        print_test_result(f"PUT /salaries/{salary_id}", response.status_code, [200], "Salary updated")

        # Delete salary
        response = requests.delete(f"{BASE_URL}/salaries/{salary_id}", headers=headers)
        print_test_result(f"DELETE /salaries/{salary_id}", response.status_code, [200], "Salary deleted")

    if att_id:
        # Update attendance
        update_data = {"status": "absent"}
        response = requests.put(f"{BASE_URL}/attendance/{att_id}", json=update_data, headers=headers)
        print_test_result(f"PUT /attendance/{att_id}", response.status_code, [200], "Attendance updated")

        # Delete attendance
        response = requests.delete(f"{BASE_URL}/attendance/{att_id}", headers=headers)
        print_test_result(f"DELETE /attendance/{att_id}", response.status_code, [200], "Attendance deleted")

    # Get employee history
    response = requests.get(f"{BASE_URL}/1/history", headers=headers)
    print_test_result("GET /1/history", response.status_code, [200], "Retrieved employee history")

def test_reports_endpoints():
    print("\n📊 Testing Reports Endpoints")
    print("=" * 50)

    # Get reports
    response = requests.get(f"{BASE_URL}/reports")
    print_test_result("GET /reports", response.status_code, [200], "Retrieved reports")

def test_alerts_endpoints():
    print("\n🚨 Testing Alerts Endpoints")
    print("=" * 50)

    # Get alerts
    response = requests.get(f"{BASE_URL}/alerts")
    print_test_result("GET /alerts", response.status_code, [200], "Retrieved alerts")

def main():
    print("🚀 Comprehensive API Testing for Enterprise Integration Case Study")
    print("=" * 80)

    # Test auth endpoints first to get token
    token = test_auth_endpoints()

    # Get a fresh token for other tests (since logout invalidated the previous one)
    login_data = {
        "username": "testuser@example.com",
        "password": "TestPass123!"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        token = response.json().get("access_token")
        print("🔑 Got fresh token for remaining tests")
    else:
        print("❌ Could not get fresh token for tests")
        token = None

    # Test all other endpoints
    test_employee_endpoints(token)
    test_department_endpoints()
    test_position_endpoints()
    test_payroll_endpoints(token)
    test_reports_endpoints()
    test_alerts_endpoints()

    print("\n" + "=" * 80)
    print("✅ Comprehensive API Testing Completed!")
    print("📊 Summary: All major endpoints have been tested")
    print("🔗 API Server: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")

if __name__ == "__main__":
    main()