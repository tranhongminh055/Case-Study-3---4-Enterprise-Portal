"""Simple script to perform login and call /employees using urllib (no external deps).
"""
import json
import urllib.request


def post_json(url, payload):
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')
    with urllib.request.urlopen(req) as resp:
        return resp.read().decode('utf-8'), resp.getcode()


def get_with_bearer(url, token):
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {token}'}, method='GET')
    with urllib.request.urlopen(req) as resp:
        return resp.read().decode('utf-8'), resp.getcode()


if __name__ == '__main__':
    login_url = 'http://127.0.0.1:8000/auth/login'
    employees_url = 'http://127.0.0.1:8000/employees'
    print('Logging in as bootstrap admin...')
    body, status = post_json(login_url, {'username': 'admin@example.com', 'password': 'Admin123!'})
    print('Login status:', status)
    print(body)
    try:
        token = json.loads(body).get('access_token')
        if not token:
            print('No token returned')
        else:
            print('\nCalling /employees with token...')
            body2, status2 = get_with_bearer(employees_url, token)
            print('Employees status:', status2)
            print(body2)
    except Exception as e:
        print('Error parsing login response or calling employees:', e)
