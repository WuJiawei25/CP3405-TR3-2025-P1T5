from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/api/seats", tags=["seats"])

@router.get("", response_model=list[schemas.SeatOut])
def list_seats(db: Session = Depends(get_db), seat_type: str | None = None, status: str | None = None):
    q = db.query(models.Seat)
    # validate filters (case-insensitive)
    if seat_type:
        try:
            st = models.SeatType(seat_type.lower())
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid seat_type")
        q = q.filter(models.Seat.seat_type == st)
    if status:
        try:
            ss = models.SeatStatus(status.lower())
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid status")
        q = q.filter(models.Seat.status == ss)
    seats = q.order_by(models.Seat.seat_code).all()
    # Coerce Enum -> str for Pydantic Literal types
    out: list[schemas.SeatOut] = []
    for s in seats:
        stype = s.seat_type.value if hasattr(s.seat_type, "value") else str(s.seat_type)
        sstatus = s.status.value if hasattr(s.status, "value") else str(s.status)
        out.append(schemas.SeatOut(id=s.id, seat_code=s.seat_code, seat_type=stype, status=sstatus))
    return out
