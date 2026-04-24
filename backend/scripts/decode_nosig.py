import sys
import jwt

if len(sys.argv) < 2:
    print('Usage: python -m backend.scripts.decode_nosig <token>')
    sys.exit(1)

token = sys.argv[1]
try:
    p = jwt.decode(token, options={"verify_signature": False, "verify_exp": False})
    print('Payload:', p)
except Exception as e:
    print('Error decoding without verify:', type(e), e)
