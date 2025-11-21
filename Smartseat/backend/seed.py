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
        _coerce_seat_enums(db)
        data = json.loads(Path(__file__).with_name("seat_seed.json").read_text(encoding="utf-8"))
        desired_by_code = {s["seat_code"]: s for s in data}

        existing = {s.seat_code: s for s in db.query(models.Seat).all()}
        inserted = 0
        updated_type = 0

        # 如果数据库为空保持原始批量插入逻辑
        if not existing:
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
            # 增量插入缺失座位
            for code, meta in desired_by_code.items():
                if code not in existing:
                    seat = models.Seat(
                        seat_code=meta["seat_code"],
                        seat_type=models.SeatType(meta["seat_type"]),
                        status=models.SeatStatus(meta["status"]),
                    )
                    db.add(seat)
                    inserted += 1
            if inserted:
                db.commit()
                print(f"Inserted {inserted} new seats")
            # 对已有座位仅同步 seat_type（不覆盖 status）
            for code, seat in existing.items():
                meta = desired_by_code.get(code)
                if not meta:
                    continue
                desired_type = models.SeatType(meta["seat_type"])
                current_type = seat.seat_type if hasattr(seat.seat_type, "value") else models.SeatType(seat.seat_type)
                if current_type != desired_type:
                    seat.seat_type = desired_type
                    updated_type += 1
            if updated_type:
                db.commit()
                print(f"Aligned seat_type for {updated_type} existing seats")
            if not inserted and not updated_type:
                print("Seats already present; normalized and no new changes.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
