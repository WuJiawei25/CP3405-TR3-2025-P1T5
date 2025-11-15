from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from pathlib import Path

# Prefer env DATABASE_URL; otherwise use an absolute sqlite path anchored to project root (Smartseat/app.db)
_env_url = os.getenv("DATABASE_URL")
if _env_url:
    DB_URL = _env_url
else:
    # backend/database.py -> backend -> Smartseat
    proj_root = Path(__file__).resolve().parents[1]
    DB_URL = f"sqlite:///{(proj_root / 'app.db').as_posix()}"

connect_args = {"check_same_thread": False} if DB_URL.startswith("sqlite") else {}

engine = create_engine(DB_URL, echo=False, future=True, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
Base = declarative_base()

def get_db():
    from sqlalchemy.orm import Session
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
