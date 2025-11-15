import json
from sqlalchemy.orm import Session
from .database import SessionLocal, engine, Base
from . import models
from pathlib import Path


def _coerce_seat_enums(db: Session):
    """Ensure all Seat rows have enum-coercible values.
    In SQLite, Enum is stored as string; this function normalizes application-level
    values by reassigning using Python Enum constructors so future reads compare as expected.
    """
    seats = db.query(models.Seat).all()
    changed = 0
    for s in seats:
        # handle both Enum and raw string
        stype_val = s.seat_type.value if hasattr(s.seat_type, "value") else s.seat_type
        status_val = s.status.value if hasattr(s.status, "value") else s.status
        try:
            s.seat_type = models.SeatType(stype_val)
        except Exception:
            # default to standard if unknown
            s.seat_type = models.SeatType.standard
        try:
            s.status = models.SeatStatus(status_val)
        except Exception:
            s.status = models.SeatStatus.available
        changed += 1
    if changed:
        db.commit()


def run():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        # migrate/normalize existing rows first
        _coerce_seat_enums(db)

        # desired seat meta from JSON (used to set types on existing seats too)
        data = json.loads(Path(__file__).with_name("seat_seed.json").read_text(encoding="utf-8"))
        desired_by_code = {s["seat_code"]: s for s in data}

        # Only seed if no seats
        if db.query(models.Seat).count() == 0:
            for s in data:
                seat = models.Seat(
                    seat_code=s["seat_code"],
                    seat_type=models.SeatType(s["seat_type"]),
                    status=models.SeatStatus(s["status"]),
                )
                db.add(seat)
            db.commit()
            print(f"Seeded {len(data)} seats")
        else:
            # Align seat_type to JSON for existing seats (do not override status here)
            seats = db.query(models.Seat).all()
            updates = 0
            for s in seats:
                d = desired_by_code.get(s.seat_code)
                if not d:
                    continue
                desired_type = models.SeatType(d["seat_type"])
                current_type = s.seat_type if hasattr(s.seat_type, "value") else models.SeatType(s.seat_type)
                if current_type != desired_type:
                    s.seat_type = desired_type
                    updates += 1
            if updates:
                db.commit()
                print(f"Aligned seat_type for {updates} seats from JSON meta")
            else:
                print("Seats already present; normalized and skip seeding.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
