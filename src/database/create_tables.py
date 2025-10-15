# src/database/models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from .session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    passport = Column(String, unique=True, nullable=False)
    photo_id = Column(String, nullable=True)
    face_vector = Column(String, nullable=True)  # kelajakda embedding saqlanadi
    role = Column(String, default="user")  # 'user' yoki 'admin'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    attendances = relationship("Attendance", back_populates="user")

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    action = Column(String, default="login")  # login / logout / check
    similarity = Column(Float, nullable=True)  # yuz moslik foizi

    user = relationship("User", back_populates="attendances")
