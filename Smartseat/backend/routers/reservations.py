from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta, timezone
from ..database import get_db
from .. import models, schemas
from .auth import get_current_user

router = APIRouter(prefix="/api/reservations", tags=["reservations"])

@router.get("/mine", response_model=list[schemas.ReservationOut])
def my_reservations(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    res = []
    for r in db.query(models.Reservation).filter_by(user_id=user.id).order_by(models.Reservation.created_at.desc()).all():
        res.append(schemas.ReservationOut(
            id=r.id, seat_code=r.seat.seat_code, seat_type=r.seat.seat_type.value if hasattr(r.seat.seat_type, "value") else r.seat.seat_type, 
            status=r.status.value if hasattr(r.status, "value") else r.status, start_time=r.start_time, end_time=r.end_time, created_at=r.created_at
        ))
    return res

@router.post("", response_model=schemas.ReservationOut)
def create_reservation(payload: schemas.ReservationCreate, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    seat = db.query(models.Seat).filter_by(seat_code=payload.seat_code).first()
    if not seat:
        raise HTTPException(status_code=404, detail="Seat not found")
    if seat.status == models.SeatStatus.booked:
        raise HTTPException(status_code=409, detail="Seat already booked")
    # Optional time window
    start = payload.start_time or datetime.now(timezone.utc)
    end = payload.end_time
    # Mark seat booked & create reservation (simple model)
    seat.status = models.SeatStatus.booked
    r = models.Reservation(user_id=user.id, seat_id=seat.id, start_time=start, end_time=end, status=models.ReservationStatus.active)
    db.add(r)
    db.commit()
    db.refresh(r)
    return schemas.ReservationOut(
        id=r.id, seat_code=seat.seat_code, seat_type=seat.seat_type.value if hasattr(seat.seat_type, "value") else seat.seat_type,
        status=r.status.value if hasattr(r.status, "value") else r.status, start_time=r.start_time, end_time=r.end_time, created_at=r.created_at
    )

@router.delete("/{reservation_id}")
def cancel_reservation(reservation_id: int, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    r = db.query(models.Reservation).filter_by(id=reservation_id, user_id=user.id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Reservation not found")
    if r.status == models.ReservationStatus.cancelled:
        return {"ok": True}
    r.status = models.ReservationStatus.cancelled
    # free the seat
    seat = r.seat
    seat.status = models.SeatStatus.available
    db.commit()
    return {"ok": True}
