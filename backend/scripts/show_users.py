from backend.database.session import SessionAuth
from backend.models.auth_models import AuthUser

def show_users():
    s = SessionAuth()
    try:
        users = s.query(AuthUser).all()
        if not users:
            print("No users found in auth database")
            return
        for u in users:
            print(f"id={u.id}, username={u.username}, role={u.role}, phone={u.phone}")
    finally:
        s.close()

if __name__ == '__main__':
    show_users()
