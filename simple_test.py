import requests

BASE_URL = "http://localhost:8000"

print("Testing API endpoints...")

# Test register
response = requests.post(f"{BASE_URL}/auth/register", json={
    "username": "test@example.com",
    "password": "Test123!",
    "phone": "+1234567890",
    "role": "Admin"
})
print(f"Register: {response.status_code}")

# Test login
response = requests.post(f"{BASE_URL}/auth/login", json={
    "username": "test@example.com",
    "password": "Test123!"
})
print(f"Login: {response.status_code}")
if response.status_code == 200:
    token = response.json()["access_token"]
    print("Got token")

    # Test get employees
    response = requests.get(f"{BASE_URL}/employees", headers={"Authorization": f"Bearer {token}"})
    print(f"Get employees: {response.status_code}")

print("Test completed!")