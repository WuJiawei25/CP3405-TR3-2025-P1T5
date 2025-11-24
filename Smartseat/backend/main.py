from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import engine, Base
from backend import models
from backend.routers import auth, users, seats, reservations, moderation, forecast, demo
import logging

app = FastAPI(title="Take-A-Seat Backend", version="0.1.0")

# CORS for local dev; tighten in prod
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# create tables safely
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    logging.exception("Failed to create DB tables: %s", e)

# Routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(seats.router)
app.include_router(reservations.router)
app.include_router(moderation.router)
app.include_router(forecast.router)
app.include_router(demo.router)

@app.get("/")
def root():
    return {"ok": True, "service": "take-a-seat", "docs": "/docs"}


if __name__ == "__main__":
    # allow running `python backend/main.py` in IDEs like PyCharm
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)

