# Smoke test for core auth flow: signup -> login -> /api/users/me
import sys
import pathlib
# Ensure repository root is on sys.path so `import backend` works when running this script directly
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from backend.main import app
from backend.database import SessionLocal
from backend import models
from backend.utils import verify_password
import uuid

client = TestClient(app)

def cleanup_email(db, email):
    u = db.query(models.User).filter(models.User.email == email).first()
    if u:
        # delete tokens, reservations then user
        db.query(models.Token).filter(models.Token.user_id == u.id).delete()
        db.query(models.Reservation).filter(models.Reservation.user_id == u.id).delete()
        db.delete(u)
        db.commit()


def run():
    email = f"smoketest+{uuid.uuid4().hex[:8]}@example.com"
    password = "secret123"
    db = SessionLocal()
    try:
        cleanup_email(db, email)
    finally:
        db.close()

    # Signup
    r = client.post("/api/auth/signup", json={"name": "Smoke Tester", "email": email, "password": password})
    if r.status_code != 200:
        print("Signup failed:", r.status_code, r.text)
        sys.exit(2)
    user = r.json()
    print("Signup OK ->", user)

    # Verify password stored hashed
    db = SessionLocal()
    try:
        u = db.query(models.User).filter(models.User.email == email).first()
        if not u:
            print("User not found in DB after signup")
            sys.exit(3)
        if u.password_hash == password:
            print("Password stored in plaintext! BAD")
            sys.exit(4)
        if not verify_password(password, u.password_hash):
            print("Hashed password did not verify")
            sys.exit(5)
        print("Password hashing OK")
    finally:
        db.close()

    # Login
    r = client.post("/api/auth/login", json={"email": email, "password": password})
    if r.status_code != 200:
        print("Login failed:", r.status_code, r.text)
        sys.exit(6)
    token = r.json().get("token")
    if not token:
        print("No token returned")
        sys.exit(7)
    print("Login OK, token len:", len(token))

    # Call protected endpoint
    headers = {"Authorization": f"Bearer {token}"}
    r = client.get("/api/users/me", headers=headers)
    if r.status_code != 200:
        print("/api/users/me failed:", r.status_code, r.text)
        sys.exit(8)
    print("Protected endpoint OK ->", r.json())

    print("SMOKE TEST PASSED")

if __name__ == '__main__':
    run()
