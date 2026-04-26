# API Testing Script using cURL
# Run these commands in terminal to test the APIs

# 1. Register a new user
echo "Registering user..."
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser@example.com",
    "password": "TestPass123!",
    "phone": "+84123456789",
    "role": "Admin"
  }'

echo -e "\n\nLogging in..."
# 2. Login to get token
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser@example.com",
    "password": "TestPass123!"
  }' | jq -r '.access_token')

echo "Token: $TOKEN"

if [ "$TOKEN" != "null" ]; then
  echo -e "\n\nGetting employees..."
  # 3. Get employees list
  curl -X GET http://localhost:8000/employees \
    -H "Authorization: Bearer $TOKEN"

  echo -e "\n\nCreating employee..."
  # 4. Create new employee
  curl -X POST http://localhost:8000/employees \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{
      "first_name": "Nguyen",
      "last_name": "Van A",
      "email": "nguyen.a@example.com",
      "phone": "+84123456789",
      "hire_date": "2023-01-01",
      "department_id": 1,
      "position_id": 1,
      "status": "active"
    }'

  echo -e "\n\nGetting departments..."
  # 5. Get departments
  curl -X GET http://localhost:8000/departments

  echo -e "\n\nCreating department..."
  # 6. Create department
  curl -X POST http://localhost:8000/departments \
    -H "Content-Type: application/json" \
    -d '{
      "name": "IT Department",
      "description": "Information Technology"
    }'

  echo -e "\n\nGetting positions..."
  # 7. Get positions
  curl -X GET http://localhost:8000/positions

  echo -e "\n\nCreating position..."
  # 8. Create position
  curl -X POST http://localhost:8000/positions \
    -H "Content-Type: application/json" \
    -d '{
      "title": "Developer",
      "grade": "Junior",
      "description": "Software Developer"
    }'
else
  echo "Login failed, cannot proceed with authenticated tests"
fi

echo -e "\n\nAPI Testing completed!"</content>
<parameter name="filePath">d:\Case Study 3\test_api_curl.sh