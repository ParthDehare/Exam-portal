from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from pydantic import BaseModel
from app.database.db import get_db
from app.models.question import Question, QuestionType
from app.services.auth import get_current_user, require_admin
from app.models.user import User

router = APIRouter(prefix="/api/questions", tags=["Questions"])

class QuestionCreate(BaseModel):
    assessment_id: int
    question_text: str
    question_type: Optional[QuestionType] = QuestionType.mcq
    option_a: Optional[str] = None
    option_b: Optional[str] = None
    option_c: Optional[str] = None
    option_d: Optional[str] = None
    correct_answer: str
    marks: Optional[int] = 1
    topic: Optional[str] = None
    explanation: Optional[str] = None

class QuestionOut(BaseModel):
    id: int
    assessment_id: int
    question_text: str
    question_type: QuestionType
    option_a: Optional[str]
    option_b: Optional[str]
    option_c: Optional[str]
    option_d: Optional[str]
    correct_answer: str
    marks: int
    topic: Optional[str]
    explanation: Optional[str]
    model_config = {"from_attributes": True}

@router.post("/", response_model=QuestionOut, status_code=201)
async def create_question(data: QuestionCreate, db: AsyncSession = Depends(get_db), admin: User = Depends(require_admin)):
    question = Question(**data.model_dump())
    db.add(question)
    await db.commit()
    await db.refresh(question)
    return question

@router.put("/{question_id}", response_model=QuestionOut)
async def update_question(question_id: int, data: QuestionCreate, db: AsyncSession = Depends(get_db), admin: User = Depends(require_admin)):
    result = await db.execute(select(Question).where(Question.id == question_id))
    question = result.scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    for k, v in data.model_dump().items():
        setattr(question, k, v)
    await db.commit()
    await db.refresh(question)
    return question

@router.delete("/{question_id}")
async def delete_question(question_id: int, db: AsyncSession = Depends(get_db), admin: User = Depends(require_admin)):
    result = await db.execute(select(Question).where(Question.id == question_id))
    question = result.scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    await db.delete(question)
    await db.commit()
    return {"message": "Deleted"}
