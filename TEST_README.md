# Comprehensive Automation Test Guide

This guide provides instructions for running comprehensive **automation tests** for the entire project (backend + frontend).

## Prerequisites

1. **Node.js** (v16 or higher)
2. **Python** (v3.8 or higher)
3. **MySQL** database running
4. **SQL Server** database running (optional, for full testing)

## Setup

### 1. Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Install Frontend Dependencies
```bash
cd frontend
npm install
```

### 3. Setup Environment Variables
Copy `.env` file to backend folder with database connections:
```
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=enterprise_db

SQLSERVER_HOST=localhost
SQLSERVER_USER=sa
SQLSERVER_PASSWORD=your_password
SQLSERVER_DATABASE=enterprise_db

FRONTEND_ORIGIN=http://localhost:5174,http://localhost:5175
```

### 4. Initialize Database
```bash
cd backend/scripts
python init_auth_db.py
```

## Running Automation Tests

### Option 1: Run Full Automation Suite (Recommended)

1. **Start Backend Server**
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

2. **Start Frontend Server** (in new terminal)
```bash
cd frontend
npm run dev
```

3. **Run Cypress Tests** (in new terminal)
```bash
cd frontend
npx cypress run --spec "cypress/e2e/comprehensive_test.cy.js"
```

### Option 2: Run Tests with Docker

If you have Docker setup:

```bash
# Build and run with docker-compose
docker-compose up --build

# Then run tests
cd frontend
npx cypress run --spec "cypress/e2e/comprehensive_test.cy.js"
```

## Test Coverage

The test suite covers:

### Authentication
- ✅ Login (valid/invalid credentials)
- ✅ Register (new user, validation)
- ✅ Logout
- ✅ OTP verification

### Employee Management
- ✅ View all employees
- ✅ Create employee
- ✅ Update employee
- ✅ Delete employee
- ✅ Search/filter employees

### Department Management
- ✅ View departments
- ✅ Create department
- ✅ Update department
- ✅ Delete department

### Position Management
- ✅ View positions
- ✅ Create position
- ✅ Update position
- ✅ Delete position

### Payroll Management
- ✅ View payroll records
- ✅ Calculate payroll
- ✅ Generate payroll reports

### Reports
- ✅ Employee reports
- ✅ Payroll reports
- ✅ Department reports

### Alerts
- ✅ View alerts
- ✅ Create alerts
- ✅ Update alert status

### Integration Tests
- ✅ Full user workflow (register → login → CRUD → logout)
- ✅ API + UI integration
- ✅ Error handling

## Test Files Structure

```
frontend/cypress/
├── test-suite/
│   ├── testcases.js              # Test case definitions
│   └── generate_test.js          # Script to generate Cypress tests
└── e2e/
    └── comprehensive_test.cy.js  # Generated automation test file
```

## Running Individual Test Suites

### Backend API Tests Only
```bash
cd frontend
npx cypress run --spec "cypress/e2e/comprehensive_test.cy.js" --grep "API"
```

### Frontend UI Tests Only
```bash
cd frontend
npx cypress run --spec "cypress/e2e/comprehensive_test.cy.js" --grep "UI"
```

### Specific Module Tests
```bash
# Employees only
npx cypress run --spec "cypress/e2e/comprehensive_test.cy.js" --grep "Employee"

# Authentication only
npx cypress run --spec "cypress/e2e/comprehensive_test.cy.js" --grep "Authentication"
```

## Troubleshooting

### Backend Not Starting
- Check database connections in `.env`
- Ensure MySQL/SQL Server is running
- Run `python init_auth_db.py` to initialize auth database

### Frontend Not Loading
- Check if backend is running on port 8000
- Verify CORS settings
- Check browser console for errors

### Tests Failing
- Ensure all services are running
- Check test data (admin user: mt1479233@gmail.com / admin123)
- Verify database has required tables/data
- Check Cypress configuration in `cypress.config.js`

### Database Issues
- Ensure MySQL and SQL Server databases exist
- Check connection strings in `.env`
- Run database migrations if needed

## CI/CD Integration

For automated testing in CI/CD:

```yaml
# GitHub Actions example
- name: Run E2E Tests
  run: |
    cd backend && pip install -r requirements.txt
    cd ../frontend && npm install
    cd ..
    # Start services in background
    uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
    cd frontend && npm run dev &
    sleep 10
    npx cypress run --spec "cypress/e2e/comprehensive_test.cy.js"
```

## Performance Testing

For load testing, consider using:
- Artillery.js for API load testing
- k6 for comprehensive performance testing
- Lighthouse for frontend performance

## Security Testing

Additional security tests to consider:
- SQL injection attempts
- XSS prevention
- Authentication bypass attempts
- Rate limiting tests
- Input validation tests