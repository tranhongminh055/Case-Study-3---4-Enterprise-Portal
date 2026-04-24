from backend.database.session import SessionAuth
from backend.models.auth_models import AuthToken

def show_tokens():
    s = SessionAuth()
    try:
        toks = s.query(AuthToken).all()
        for t in toks:
            print(f"id={t.id}, user_id={t.user_id}, jti={t.jti}, revoked={t.revoked}, expires_at={t.expires_at}")
    finally:
        s.close()

if __name__ == '__main__':
    show_tokens()
