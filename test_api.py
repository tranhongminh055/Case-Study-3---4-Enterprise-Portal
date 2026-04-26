import requests
import json

BASE_URL = "http://localhost:8000"

def test_auth_register():
    url = f"{BASE_URL}/auth/register"
    payload = {
        "username": "testuser@example.com",
        "password": "TestPass123!",
        "phone": "+84123456789",
        "role": "Admin"
    }
    response = requests.post(url, json=payload)
    print(f"Register: {response.status_code}")
    if response.status_code == 201:
        print("User registered successfully")
    elif response.status_code == 409:
        print("User already exists")
    else:
        print(f"Unexpected status: {response.text}")

def test_auth_login():
    url = f"{BASE_URL}/auth/login"
    payload = {
        "username": "testuser@example.com",
        "password": "TestPass123!"
    }
    response = requests.post(url, json=payload)
    print(f"Login: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print("Login successful, got token")
        return token
    else:
        print(f"Login failed: {response.text}")
        return None

def test_get_employees(token):
    url = f"{BASE_URL}/employees"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    print(f"Get Employees: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Got {len(data)} employees")
    else:
        print(f"Failed: {response.text}")

def test_create_employee(token):
    url = f"{BASE_URL}/employees"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "first_name": "Nguyen",
        "last_name": "Van A",
        "email": "nguyen.a@example.com",
        "phone": "+84123456789",
        "hire_date": "2023-01-01",
        "department_id": 1,
        "position_id": 1,
        "status": "active"
    }
    response = requests.post(url, json=payload, headers=headers)
    print(f"Create Employee: {response.status_code}")
    if response.status_code == 201:
        data = response.json()
        employee_id = data.get("id")
        print(f"Employee created with ID: {employee_id}")
        return employee_id
    else:
        print(f"Failed: {response.text}")
        return None

def test_get_departments():
    url = f"{BASE_URL}/departments"
    response = requests.get(url)
    print(f"Get Departments: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Got {len(data)} departments")
    else:
        print(f"Failed: {response.text}")

def test_create_department():
    url = f"{BASE_URL}/departments"
    payload = {
        "name": "IT Department",
        "description": "Information Technology"
    }
    response = requests.post(url, json=payload)
    print(f"Create Department: {response.status_code}")
    if response.status_code == 201:
        data = response.json()
        dept_id = data.get("id")
        print(f"Department created with ID: {dept_id}")
        return dept_id
    else:
        print(f"Failed: {response.text}")
        return None

def test_get_positions():
    url = f"{BASE_URL}/positions"
    response = requests.get(url)
    print(f"Get Positions: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Got {len(data)} positions")
    else:
        print(f"Failed: {response.text}")

def test_create_position():
    url = f"{BASE_URL}/positions"
    payload = {
        "title": "Developer",
        "grade": "Junior",
        "description": "Software Developer"
    }
    response = requests.post(url, json=payload)
    print(f"Create Position: {response.status_code}")
    if response.status_code == 201:
        data = response.json()
        pos_id = data.get("id")
        print(f"Position created with ID: {pos_id}")
        return pos_id
    else:
        print(f"Failed: {response.text}")
        return None

if __name__ == "__main__":
    print("Starting API Tests...")
    print("=" * 50)

    # Test Auth
    test_auth_register()
    token = test_auth_login()

    if token:
        # Test Employee APIs
        test_get_employees(token)
        test_create_employee(token)

        # Test Department APIs
        test_get_departments()
        test_create_department()

        # Test Position APIs
        test_get_positions()
        test_create_position()

    print("=" * 50)
    print("API Tests completed!")</content>
<parameter name="filePath">d:\Case Study 3\test_api.py