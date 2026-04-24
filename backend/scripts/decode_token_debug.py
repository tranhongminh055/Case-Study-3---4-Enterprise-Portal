import sys
from backend.utils.jwt_utils import decode_token

if len(sys.argv) < 2:
    print('Usage: python -m backend.scripts.decode_token_debug <token>')
    sys.exit(1)

token = sys.argv[1]
try:
    p = decode_token(token)
    print('Decoded payload:')
    print(p)
except Exception as e:
    print('Decode error:', type(e), e)
