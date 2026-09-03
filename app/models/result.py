from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database.db import Base

class ResultStatus(str, enum.Enum):
    pass_ = "pass"
    fail = "fail"

class Result(Base):
    __tablename__ = "results"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    score = Column(Float, default=0)
    percentage = Column(Float, default=0)
    status = Column(Enum(ResultStatus), default=ResultStatus.fail)
    answers = Column(String(5000), default="{}")
    time_taken = Column(Integer, default=0)
    submitted_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="results")
    assessment = relationship("Assessment", back_populates="results")
