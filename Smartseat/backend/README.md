# CP3405-TR3-2025-P1T5 – Take-A-Seat (Smart Seat Reservation & Analytics)

## 1. Overview
Take-A-Seat is a smart classroom / study-space seat reservation and analytics platform. It enables:
- Students to quickly reserve, modify, or cancel a seat (<30 seconds flow goal)
- Lecturers to view real-time occupancy heatmaps and detect anomalies before class
- Administrators to analyze historical usage, weekly/daily trends, and forecast future demand

The project demonstrates design thinking (iterative improvement), data aggregation, simple forecasting (SARIMAX), and multi-role UX.

## 2. Core Features
Student Portal:
- Sign up / login (token-based auth)
- Browse seats by status / type
- Create, view, cancel reservations

Lecturer Dashboard (demo data endpoint):
- Live courses list with presence counts
- Weekly attendance trend chart
- Forecasted future seat usage
- Seat heatmap grid (synthetic or model-backed)

Admin / Analytics:
- Time-series aggregation (daily / weekly) of reservations
- Basic forecasting pipeline placeholder (SARIMAX trained offline)
- Moderation endpoint (rule-based text compliance demo)

Shared:
- Token-based authentication (Bearer tokens)
- Enum-backed seat types & statuses
- SQLite persistence with SQLAlchemy ORM

## 3. Architecture
Layers:
- Frontend: Static HTML/CSS/JS pages (student / lecturer / admin views) consuming REST endpoints.
- Backend: FastAPI application with modular routers under `backend/routers/`.
- Database: SQLite (`Smartseat/app.db`) via SQLAlchemy; can swap to Postgres by setting `DATABASE_URL`.
- Analytics: Aggregation + time-series seeding and simple SARIMAX model loaded from `sarimax_model.pkl` if present.

Directory Highlights:
```
Smartseat/
  backend/
    main.py            # FastAPI app composition
    app.py             # Minimal standalone SARIMAX forecast API (demo)
    models.py          # SQLAlchemy ORM models & enums
    schemas.py         # Pydantic request/response models
    routers/           # Modular route handlers (auth, users, seats, reservations, forecast, demo,...)
    utils.py           # Password hashing & token helpers
    database.py        # Engine/session creation & env-based DB URL
    seed.py            # Seed seats + sample time series
    aggregator.py      # Daily/weekly reservation aggregation logic
    aggregate_cli.py   # CLI wrapper to run aggregation
    tests_smoke.py     # Automated auth flow smoke test
    tests_simple.py    # Basic import + root endpoint test
    requirements.txt   # Python dependencies
```

## 4. Technology Stack
Backend:
- FastAPI, Uvicorn
- SQLAlchemy 2.x
- Pydantic v2
- passlib (pbkdf2_sha256 hashing)
- statsmodels (SARIMAX forecasting)
- pandas / numpy (data prep)

Frontend:
- Static HTML/CSS/JS assets (no build step required) inside project root.

Testing:
- FastAPI TestClient based smoke tests.

## 5. Setup & Local Development
### 5.1 Prerequisites
- Python 3.11+ (recommended, project tested with 3.13 locally via compiled pyc files present)
- macOS / Linux / Windows OK

### 5.2 Clone & Create Virtual Environment
```bash
git clone <your-repo-url>
cd P1T5/Smartseat/backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 5.3 Initialize Database & Seed
```bash
python seed.py  # creates tables + inserts seats + sample time series
```

### 5.4 Run Backend
Option A – Main consolidated API (recommended for FE integration):
```bash
uvicorn backend.main:app --reload --port 8000
```
Docs: http://127.0.0.1:8000/docs

Option B – Minimal forecast-only demo API (`app.py`):
```bash
uvicorn backend.app:app --reload --port 8100
```
Forecast endpoint: POST /forecast

### 5.5 Environment Variables (Optional)
Set `DATABASE_URL` to use Postgres etc. Example:
```bash
export DATABASE_URL=postgresql+psycopg://user:pass@host/dbname
```

## 6. Authentication Flow
1. POST /api/auth/signup -> create account
2. POST /api/auth/login -> returns token
3. Use `Authorization: Bearer <token>` header for protected endpoints (e.g., /api/users/me, reservation endpoints)
Tokens stored in `tokens` table; simple hex string (not JWT). Expiry/Revocation not yet implemented.

## 7. API Endpoint Summary
Base URL (local): `http://127.0.0.1:8000`

Root & Status:
- GET `/` -> service info
- GET `/status` (from `app.py` if that app is launched) -> model load status

Auth (`/api/auth`):
- POST `/signup` – Request: `{name, email, password}`; Response: user object. Validations: unique email, password length >=6.
- POST `/login` – Request: `{email, password}`; Response: `{token}`; Issues a new bearer token.
- GET `/me` – Auth required; Returns current user.

Users (`/api/users`):
- GET `/me` – same as auth `/me` (redundant for convenience).

Seats (`/api/seats`):
- GET `` `/api/seats` with optional query `seat_type`, `status` – Returns list of seats filtered by enums.
  Seat types: `standard|quiet|accessible`; Status: `available|booked`.

Reservations (`/api/reservations`):
- GET `/mine` – Auth required; Lists reservations for current user (id, seat_code, seat_type, status, times).
- POST `` – Auth required; Body: `{seat_code, start_time?, end_time?}`; Creates reservation & marks seat booked.
- DELETE `/{reservation_id}` – Auth required; Cancels reservation; frees seat.

Moderation (`/api/moderate`):
- POST `` – Body: `{text}`; Returns `{label: "violated"|"compliant", violated: bool}` using keyword match (demo only).

Forecast Management (`/api/forecast`):
- POST `/series` – Upsert bulk time series points for a named series. Body: `{series_name, replace?, points:[{ts, value}]}`.
- GET `/series/{series_name}` – Metadata (count, start, end).
- GET `/series/{series_name}/points` – Raw points list.
- POST `/aggregate` – Trigger reservation aggregation into daily/weekly series. Body: `{lookback_days, lookback_weeks, series_daily?, series_weekly?}`.

Demo (`/demo`):
- GET `/lecturer_data` – Returns synthetic lecturer dashboard dataset (personalized greeting if Bearer token supplied). Includes courses, attendance trend, forecast, heatmap grids.

Forecast (Standalone App `app.py`):
- POST `/forecast` – Body: `{steps}`; Response: `{forecast: [float...]}` from loaded SARIMAX model or 503 if missing.

Data Models & Pydantic Schemas: See `backend/models.py` and `backend/schemas.py` for full field types.

## 8. Data Seeding & Aggregation
- `seed.py` creates seats from `seat_seed.json` and a baseline monthly time series `seat_usage`.
- `aggregate_cli.py` or API `/api/forecast/aggregate` aggregates reservations into daily & weekly series for analytics/forecast training.

Run manual aggregation:
```bash
python aggregate_cli.py --days 90 --weeks 16
```

## 9. Forecasting
- SARIMAX model file `sarimax_model.pkl` optionally loaded (if trained via an external script like `train_dummy_sarimax.py`).
- If absent, demo endpoints fall back to synthetic random data.
- Future: integrate live training & anomaly detection.

## 10. Testing
Smoke test (auth round-trip):
```bash
python tests_smoke.py
```
Basic import test:
```bash
python tests_simple.py
```
Expected outputs: successful signup/login, hashed password verification, protected endpoint accessible.

## 11. CI/CD (GitHub Actions)
Workflow (created under `.github/workflows/ci.yml`):
- Triggers: push & pull_request on main (adjust as needed)
- Steps: checkout → setup Python → install deps → seed DB → run smoke test → (future) run lint & coverage.
Add screenshots of successful runs (workflow list & single run details) to submission.

## 12. Frontend Usage
Open HTML pages (e.g., `B02_home.html`, `B03_seat_selection.html`) in a browser. Ensure backend running on `http://127.0.0.1:8000` or adjust fetch URLs if hard-coded.

## 13. Demo Video Guide (Summary)
Suggested flow (3–5 min): intro → student seat booking & cancel → lecturer heatmap + anomaly rationale → admin analytics & forecast → architecture → future work.

## 14. Submission Artifact Checklist (English + Chinese Summary)
Provide:
- Week 9 PPT (progress, architecture, iterations)
- GitHub repo link (ensure README + workflow present)
- CI/CD screenshots (Actions runs)
- Project board & Issues screenshots (show lifecycle & labels)
- Frontend & admin UI screenshots (annotated)
- FigJam/Figma links + iteration screenshots
- Demo video (mp4 or hosted link)
- Deployment URL (if hosted) OR local run instructions (this README)
- API endpoint summary (section 7 here or separate PDF)
- Additional docs: ER diagram, data flow, risk & future roadmap
- Any creative artifacts (user research summary, performance test results, etc.)

## 15. How to Submit Each Item
Recommended formats:
- PPT: `Week9_Deliverables_<Team>.pptx`
- Screenshots: Put in `/docs/screenshots/` with clear names (e.g., `student_flow.png`, `actions_run.png`)
- Figma/FigJam: Share view-only link + backup PNG exports in `/docs/design/`
- Demo video: `demo.mp4` or YouTube unlisted link + thumbnail
- API docs: Export OpenAPI from /docs (FastAPI) via "Download JSON" → convert to HTML or PDF; store in `/docs/api/`
- ER Diagram: `er_diagram.png` in `/docs/architecture/`
- CI/CD: commit `.github/workflows/ci.yml` and screenshot run results
- Forecast model: optional – include training script & explanation in `/docs/analytics/forecast.md`

## 16. Future Improvements
- JWT-based expiring tokens & refresh flow
- Role-based access control (student / lecturer / admin)
- Real anomaly detection (statistical thresholds or ML)
- Real-time seat updates (WebSockets)
- Migration to Postgres & containerization (Docker)
- Dashboard with richer charts and predictive insights

## 17. Contributing
1. Create feature branch: `git checkout -b feature/<short-name>`
2. Commit with conventional messages: `feat: add reservation cancellation reason`
3. Open Pull Request linking related Issue.
4. Ensure CI passes before review.

## 18. License
If required for course: add a simple license (e.g., MIT) – currently unspecified.

## 19. Troubleshooting
Common issues:
- Import errors: ensure you run commands from `Smartseat/backend` or add repo root to `PYTHONPATH`.
- DB lock on SQLite: avoid concurrent writes; use single process during tests.
- Missing model file: forecast endpoints fallback to synthetic data.

## 20. Quick Start (One-Liner)
```bash
cd Smartseat/backend && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && python seed.py && uvicorn backend.main:app --reload
```

---
Prepared for CP3405 Design Thinking III – Team P1T5.
