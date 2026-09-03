from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.db import Base

class Assessment(Base):
    __tablename__ = "assessments"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    duration = Column(Integer, nullable=False)  # minutes
    total_marks = Column(Integer, nullable=False)
    passing_marks = Column(Integer, nullable=False)
    difficulty = Column(String(20), default="medium")
    category = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    questions = relationship("Question", back_populates="assessment", cascade="all, delete")
    results = relationship("Result", back_populates="assessment", cascade="all, delete")
