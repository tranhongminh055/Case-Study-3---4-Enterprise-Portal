# Postman API Tests

This folder contains a Postman collection and environment for backend API test automation.

## Files

- `Postman-API-Tests.postman_collection.json` — API test collection for auth and employee flows.
- `Postman-API-Environment.postman_environment.json` — local environment settings.

## Setup

1. Open Postman.
2. Import `Postman-API-Tests.postman_collection.json`.
3. Import `Postman-API-Environment.postman_environment.json`.
4. Select the `Case Study 3 Local` environment.
5. Run the collection.

## Notes

- The collection assumes backend is available at `http://localhost:8000`.
- The `Login Admin User` request stores the bearer token into `{{accessToken}}`.
- The `Create Employee` request generates a unique `employeeEmail` before request execution.

## Run with Newman

If you want to run this collection from the terminal, install Newman first:

```bash
npm install -g newman
```

Then run:

```bash
newman run frontend/postman/Postman-API-Tests.postman_collection.json -e frontend/postman/Postman-API-Environment.postman_environment.json
```
