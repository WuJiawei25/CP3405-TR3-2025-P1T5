from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from .. import models, schemas
from ..utils import hash_password, verify_password, new_token
from sqlalchemy.exc import IntegrityError
import logging

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/signup", response_model=schemas.UserOut)
def signup(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    # normalize email and basic password validation
    email = payload.email.strip().lower()
    if len(payload.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    if db.query(models.User).filter(models.User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = models.User(name=payload.name, email=email, password_hash=hash_password(payload.password))
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError as ie:
        db.rollback()
        # Handle race condition duplicate (UNIQUE constraint) separately
        msg = str(ie.orig).lower()
        if "unique" in msg and "users" in msg and "email" in msg:
            raise HTTPException(status_code=400, detail="Email already registered (race condition)")
        logging.exception("IntegrityError during signup for %s", email)
        raise HTTPException(status_code=500, detail="Database integrity error during signup")
    except Exception as e:
        db.rollback()
        logging.exception("Unexpected DB error during signup for %s", email)
        raise HTTPException(status_code=500, detail="Failed to create user: internal error")
    return user

@router.post("/login", response_model=schemas.TokenResponse)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # issue token
    token = models.Token(user_id=user.id, token=new_token())
    db.add(token)
    try:
        db.commit()
        db.refresh(token)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to issue token")
    return schemas.TokenResponse(token=token.token)

def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)) -> models.User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token_value = authorization.split()[1]
    token = db.query(models.Token).filter_by(token=token_value).first()
    if not token:
        raise HTTPException(status_code=401, detail="Invalid token")
    return token.user

@router.get("/me", response_model=schemas.UserOut)
def me(user: models.User = Depends(get_current_user)):
    return user
