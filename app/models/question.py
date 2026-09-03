from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from app.database.db import Base

class QuestionType(str, enum.Enum):
    mcq = "mcq"
    multiple_select = "multiple_select"
    true_false = "true_false"
    short_answer = "short_answer"
    coding = "coding"

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(Enum(QuestionType), default=QuestionType.mcq)
    option_a = Column(String(500))
    option_b = Column(String(500))
    option_c = Column(String(500))
    option_d = Column(String(500))
    correct_answer = Column(String(500), nullable=False)
    marks = Column(Integer, default=1)
    topic = Column(String(100))
    explanation = Column(Text)

    assessment = relationship("Assessment", back_populates="questions")
