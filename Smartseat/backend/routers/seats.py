from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/api/seats", tags=["seats"])

@router.get("", response_model=list[schemas.SeatOut])
def list_seats(db: Session = Depends(get_db), seat_type: str | None = None, status: str | None = None):
    q = db.query(models.Seat)
    if seat_type:
        q = q.filter(models.Seat.seat_type == seat_type)
    if status:
        q = q.filter(models.Seat.status == status)
    return q.order_by(models.Seat.seat_code).all()
