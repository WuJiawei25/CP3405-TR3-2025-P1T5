from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import String, Integer, ForeignKey, DateTime, UniqueConstraint, Text, Enum
from sqlalchemy.sql import func
from .database import Base
import enum
from datetime import datetime
from typing import Optional

class SeatType(str, enum.Enum):
    standard = "standard"
    quiet = "quiet"
    accessible = "accessible"

class SeatStatus(str, enum.Enum):
    available = "available"
    booked = "booked"

class ReservationStatus(str, enum.Enum):
    active = "active"
    cancelled = "cancelled"

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    tokens = relationship("Token", back_populates="user", cascade="all, delete-orphan")
    reservations = relationship("Reservation", back_populates="user", cascade="all, delete-orphan")

class Token(Base):
    __tablename__ = "tokens"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User", back_populates="tokens")

class Seat(Base):
    __tablename__ = "seats"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    seat_code: Mapped[str] = mapped_column(String(10), unique=True, index=True)  # e.g., A1
    seat_type: Mapped[SeatType] = mapped_column(Enum(SeatType), default=SeatType.standard)
    status: Mapped[SeatStatus] = mapped_column(Enum(SeatStatus), default=SeatStatus.available)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    reservations = relationship("Reservation", back_populates="seat")

class Reservation(Base):
    __tablename__ = "reservations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    seat_id: Mapped[int] = mapped_column(ForeignKey("seats.id"))
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[ReservationStatus] = mapped_column(Enum(ReservationStatus), default=ReservationStatus.active)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="reservations")
    seat = relationship("Seat", back_populates="reservations")

    __table_args__ = (
        UniqueConstraint("seat_id", "status", name="uq_seat_active_when_reserved"),
    )
