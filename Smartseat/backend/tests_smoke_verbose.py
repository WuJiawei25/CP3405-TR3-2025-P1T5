# Verbose smoke test for auth flow with explicit, flushed prints for reliable output
import sys
import pathlib
import traceback
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
        db.query(models.Token).filter(models.Token.user_id == u.id).delete()
        db.query(models.Reservation).filter(models.Reservation.user_id == u.id).delete()
        db.delete(u)
        db.commit()


def run():
    try:
        print('--- SMOKE TEST VERBOSE START ---', flush=True)
        email = f"smoketest+{uuid.uuid4().hex[:8]}@example.com"
        password = "secret123"
        print("TEST EMAIL", email, flush=True)

        db = SessionLocal()
        try:
            cleanup_email(db, email)
        finally:
            db.close()

        print("-> SIGNUP", flush=True)
        r = client.post("/api/auth/signup", json={"name": "Smoke Tester", "email": email, "password": password})
        print("signup status:", r.status_code, flush=True)
        print("signup body:", r.text, flush=True)
        if r.status_code != 200:
            print("Signup failed", flush=True)
            print('--- SMOKE TEST VERBOSE END (FAILED) ---', flush=True)
            return

        print("-> VERIFY HASH STORED", flush=True)
        db = SessionLocal()
        try:
            u = db.query(models.User).filter(models.User.email == email).first()
            if not u:
                print("User missing after signup", flush=True)
                print('--- SMOKE TEST VERBOSE END (FAILED) ---', flush=True)
                return
            print("db password hash prefix:", u.password_hash[:20], flush=True)
            print("verify_password returns:", verify_password(password, u.password_hash), flush=True)
        finally:
            db.close()

        print("-> LOGIN", flush=True)
        r = client.post("/api/auth/login", json={"email": email, "password": password})
        print("login status:", r.status_code, flush=True)
        print("login body:", r.text, flush=True)
        if r.status_code != 200:
            print("Login failed", flush=True)
            print('--- SMOKE TEST VERBOSE END (FAILED) ---', flush=True)
            return
        token = r.json().get("token")
        print("token len:", len(token) if token else None, flush=True)

        print("-> PROTECTED /api/users/me", flush=True)
        headers = {"Authorization": f"Bearer {token}"}
        r = client.get("/api/users/me", headers=headers)
        print("me status:", r.status_code, flush=True)
        print("me body:", r.text, flush=True)

        if r.status_code == 200:
            print("SMOKE TEST PASSED", flush=True)
            print('--- SMOKE TEST VERBOSE END (PASSED) ---', flush=True)
        else:
            print("SMOKE TEST FAILED", flush=True)
            print('--- SMOKE TEST VERBOSE END (FAILED) ---', flush=True)
    except Exception:
        traceback.print_exc()
        print('--- SMOKE TEST VERBOSE END (EXCEPTION) ---', flush=True)

if __name__ == '__main__':
    run()
