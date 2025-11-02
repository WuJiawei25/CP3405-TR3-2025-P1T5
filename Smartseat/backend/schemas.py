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
