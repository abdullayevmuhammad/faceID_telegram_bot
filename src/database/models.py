# src/database/models.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime
from .session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    full_name = Column(String, nullable=True)
    passport = Column(String, unique=True, nullable=False, index=True)
    photo_id = Column(String, nullable=True)         # Telegram file_id
    photo_path = Column(String, nullable=True)       # local file path (optional)
    faceid_status = Column(String, default="pending")# pending/ok/error
    synced = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)
