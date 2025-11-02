from passlib.context import CryptContext
import secrets

# Use pbkdf2_sha256 to avoid bcrypt's 72-byte limit and dependency on bcrypt C backend
pwd_ctx = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

MAX_PW_BYTES = 4096  # generous defensive limit

def hash_password(pw: str) -> str:
    if isinstance(pw, str) and len(pw.encode("utf-8")) > MAX_PW_BYTES:
        raise ValueError("Password too long")
    return pwd_ctx.hash(pw)

def verify_password(pw: str, hashed: str) -> bool:
    try:
        return pwd_ctx.verify(pw, hashed)
    except Exception:
        return False

def new_token() -> str:
    return secrets.token_hex(32)
