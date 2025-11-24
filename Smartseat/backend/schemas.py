from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List, Literal
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    token: str

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class SeatOut(BaseModel):
    id: int
    seat_code: str
    seat_type: Literal["standard", "quiet", "accessible"]
    status: Literal["available", "booked"]
    model_config = ConfigDict(from_attributes=True)

class ReservationCreate(BaseModel):
    seat_code: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class ReservationOut(BaseModel):
    id: int
    seat_code: str
    seat_type: str
    status: str
    start_time: datetime
    end_time: Optional[datetime]
    created_at: datetime

class ForecastDBRequest(BaseModel):
    series_name: str
    steps: int = 12
    order: Optional[List[int]] = None  # [p,d,q]
    seasonal_order: Optional[List[int]] = None  # [P,D,Q,m]
    freq: Optional[str] = None  # e.g., 'M'

class ForecastPoint(BaseModel):
    ts: datetime
    yhat: float
    yhat_lower: Optional[float] = None
    yhat_upper: Optional[float] = None

class ForecastDBResponse(BaseModel):
    run_id: int
    series_name: str
    steps: int
    points: List[ForecastPoint]

class TimeSeriesPointIn(BaseModel):
    ts: datetime
    value: float

class UpsertSeriesRequest(BaseModel):
    series_name: str
    points: List[TimeSeriesPointIn]
    replace: Optional[bool] = False

class UpsertSeriesResponse(BaseModel):
    series_name: str
    inserted: int
    updated: int
    total: int

class AggregationRequest(BaseModel):
    series_daily: Optional[str] = 'seat_usage_daily'
    series_weekly: Optional[str] = 'seat_usage_weekly'
    lookback_days: int = 60
    lookback_weeks: int = 12

class AggregationOutcome(BaseModel):
    daily_points: int
    weekly_points: int

class AggregationResponse(BaseModel):
    series_daily: Optional[str]
    series_weekly: Optional[str]
    outcome: AggregationOutcome
    ran_at: datetime
