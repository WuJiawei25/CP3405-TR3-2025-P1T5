# Take-A-Seat Backend (FastAPI)

A lightweight Python backend to support your FE prototype (login, profile, location, seat-selection).

## Quickstart

```bash
cd take_a_seat_backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Initialize DB and seed seats from FE layout (48 seats A1..F8 with types & initial booked/available)
python -m take_a_seat_backend.seed

# Run dev server
uvicorn take_a_seat_backend.main:app --reload --port 8000
```

Open Swagger at: http://localhost:8000/docs

## Endpoints

- `POST /api/auth/signup` → create account `{ name, email, password }`
- `POST /api/auth/login` → returns `{ token }` (send as `Authorization: Bearer <token>`)
- `GET /api/users/me` → current user info
- `GET /api/seats?type=quiet&status=available` → list seats
- `POST /api/reservations` → body `{ seat_code, start_time?, end_time? }` (books the seat)
- `GET /api/reservations/mine`
- `DELETE /api/reservations/{id}` → cancels and frees seat
- `POST /api/moderate` → body `{ text }` returns `{ label: "compliant"|"violated" }`

## Minimal FE Integration

### 1) Login (replace current `onclick` redirect)

```html
<script>
async function doLogin() {
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;
  const res = await fetch('http://localhost:8000/api/auth/login', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  if (!res.ok) { alert('Login failed'); return; }
  const data = await res.json();
  localStorage.setItem('token', data.token);
  location.href = 'seat-selection.html';
}
</script>
<button class="login-btn" onclick="doLogin()">Login ></button>
```

### 2) Load seat map

```html
<script>
async function loadSeats() {
  const res = await fetch('http://localhost:8000/api/seats?status=available');
  const seats = await res.json();
  console.log(seats); // render or update classes accordingly
}
document.addEventListener('DOMContentLoaded', loadSeats);
</script>
```

### 3) Reserve a seat

```js
async function reserveSeat(seatCode) {
  const token = localStorage.getItem('token');
  const res = await fetch('http://localhost:8000/api/reservations', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + token
    },
    body: JSON.stringify({ seat_code: seatCode })
  });
  if (res.ok) {
    alert('Booked!'); location.href = 'success.html';
  } else {
    const err = await res.json(); alert(err.detail || 'Failed');
  }
}
```

### 4) Simple moderation (your "compliant/violated" check)

```js
async function checkText(text) {
  const res = await fetch('http://localhost:8000/api/moderate', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text })
  });
  return res.json(); // { label, violated }
}
```

## Notes

- CORS is open for dev; set `allow_origins` appropriately in production.
- DB is SQLite `app.db` by default; override with `DATABASE_URL` env var.
- Passwords are bcrypt-hashed via passlib.
- Reservations are simplified: a seat can be booked once at a time; deleting a reservation frees the seat.
