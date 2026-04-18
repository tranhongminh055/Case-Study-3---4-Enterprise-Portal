import urllib.request
import urllib.error

url = 'http://localhost:8000/employees/22'
req = urllib.request.Request(url, method='DELETE')
try:
    with urllib.request.urlopen(req) as res:
        print('STATUS', res.status)
        print(res.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print('HTTP', e.code)
    print(e.read().decode('utf-8'))
except Exception as e:
    print('ERR', e)
