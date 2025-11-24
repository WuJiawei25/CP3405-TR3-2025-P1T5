from __future__ import annotations
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from sqlalchemy.orm import Session
from . import models

# Helpers

def _floor_to_day(dt: datetime) -> datetime:
    return datetime(dt.year, dt.month, dt.day)


def _monday_of_week(dt: datetime) -> datetime:
    # Monday=0 .. Sunday=6
    d = _floor_to_day(dt)
    return d - timedelta(days=d.weekday())


def aggregate_daily(db: Session, lookback_days: int = 60, series_name: str = 'seat_usage_daily') -> int:
    """Aggregate reservations by start_date over the past N days into timeseries."""
    end = _floor_to_day(datetime.now())
    start = end - timedelta(days=lookback_days)
    # Load reservations within window by start_time
    q = db.query(models.Reservation).filter(models.Reservation.start_time >= start, models.Reservation.start_time < end + timedelta(days=1))
    rows = q.all()
    bucket = defaultdict(int)
    for r in rows:
        d = _floor_to_day(r.start_time or r.created_at)
        bucket[d] += 1
    # Upsert into timeseries
    inserted = 0
    for i in range(lookback_days):
        day = start + timedelta(days=i)
        val = bucket.get(day, 0)
        existing = db.query(models.TimeSeriesPoint).filter(models.TimeSeriesPoint.series_name==series_name, models.TimeSeriesPoint.ts==day).first()
        if existing:
            existing.value = float(val)
        else:
            db.add(models.TimeSeriesPoint(series_name=series_name, ts=day, value=float(val)))
            inserted += 1
    db.commit()
    return inserted


def aggregate_weekly(db: Session, lookback_weeks: int = 12, series_name: str = 'seat_usage_weekly') -> int:
    """Aggregate reservations by ISO week (Monday) over the past N weeks into timeseries."""
    today = _floor_to_day(datetime.now())
    this_monday = _monday_of_week(today)
    start_monday = this_monday - timedelta(weeks=lookback_weeks)
    # Load reservations within window
    q = db.query(models.Reservation).filter(models.Reservation.start_time >= start_monday, models.Reservation.start_time < this_monday + timedelta(days=7))
    rows = q.all()
    bucket = defaultdict(int)
    for r in rows:
        d = _monday_of_week(r.start_time or r.created_at)
        bucket[d] += 1
    inserted = 0
    for w in range(lookback_weeks):
        wk = start_monday + timedelta(weeks=w)
        val = bucket.get(wk, 0)
        existing = db.query(models.TimeSeriesPoint).filter(models.TimeSeriesPoint.series_name==series_name, models.TimeSeriesPoint.ts==wk).first()
        if existing:
            existing.value = float(val)
        else:
            db.add(models.TimeSeriesPoint(series_name=series_name, ts=wk, value=float(val)))
            inserted += 1
    db.commit()
    return inserted


def aggregate_usage(db: Session, lookback_days: int = 60, lookback_weeks: int = 12, series_daily: str = 'seat_usage_daily', series_weekly: str = 'seat_usage_weekly') -> tuple[int,int]:
    d = aggregate_daily(db, lookback_days=lookback_days, series_name=series_daily) if lookback_days>0 else 0
    w = aggregate_weekly(db, lookback_weeks=lookback_weeks, series_name=series_weekly) if lookback_weeks>0 else 0
    return d, w

