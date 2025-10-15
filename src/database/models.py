# src/database/models.py
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    full_name = Column(String, nullable=True)  # ✅ endi bor!
    passport = Column(String, nullable=False)
    photo_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)