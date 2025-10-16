import json
from sqlalchemy.orm import Session
from .database import SessionLocal, engine, Base
from . import models
from pathlib import Path

def run():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        # Only seed if no seats
        if db.query(models.Seat).count() == 0:
            data = json.loads(Path(__file__).with_name("seat_seed.json").read_text(encoding="utf-8"))
            for s in data:
                seat = models.Seat(seat_code=s["seat_code"], seat_type=s["seat_type"], status=s["status"])
                db.add(seat)
            db.commit()
            print(f"Seeded {len(data)} seats")
        else:
            print("Seats already present; skip seeding.")
    finally:
        db.close()

if __name__ == "__main__":
    run()
