# Simple test to verify FastAPI app imports and TestClient behavior
import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

print('SIMPLE TEST START', flush=True)
try:
    from fastapi.testclient import TestClient
    from backend.main import app
    client = TestClient(app)
    print('TestClient created', flush=True)
    r = client.get('/')
    print('GET / status:', r.status_code, flush=True)
    print('GET / body:', r.text, flush=True)
except Exception as e:
    print('EXCEPTION during simple test:', file=sys.stderr)
    import traceback
    traceback.print_exc()
    sys.exit(1)
print('SIMPLE TEST END', flush=True)

