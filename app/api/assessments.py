from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from pydantic import BaseModel
from app.database.db import get_db
from app.models.assessment import Assessment
from app.models.question import Question
from app.models.result import Result
from app.models.user import User
from app.services.auth import get_current_user, require_admin

router = APIRouter(prefix="/api/assessments", tags=["Assessments"])

class AssessmentCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    duration: int
    total_marks: int
    passing_marks: int
    difficulty: Optional[str] = "medium"
    category: Optional[str] = ""

class AssessmentOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    duration: int
    total_marks: int
    passing_marks: int
    difficulty: str
    category: Optional[str]
    is_active: bool
    model_config = {"from_attributes": True}

@router.get("/", response_model=list[AssessmentOut])
async def list_assessments(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Assessment).where(Assessment.is_active == True))
    return result.scalars().all()

@router.get("/{assessment_id}", response_model=AssessmentOut)
async def get_assessment(assessment_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Assessment).where(Assessment.id == assessment_id))
    assessment = result.scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return assessment

@router.post("/", response_model=AssessmentOut, status_code=201)
async def create_assessment(data: AssessmentCreate, db: AsyncSession = Depends(get_db), admin: User = Depends(require_admin)):
    assessment = Assessment(**data.model_dump())
    db.add(assessment)
    await db.commit()
    await db.refresh(assessment)
    return assessment

@router.put("/{assessment_id}", response_model=AssessmentOut)
async def update_assessment(assessment_id: int, data: AssessmentCreate, db: AsyncSession = Depends(get_db), admin: User = Depends(require_admin)):
    result = await db.execute(select(Assessment).where(Assessment.id == assessment_id))
    assessment = result.scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    for k, v in data.model_dump().items():
        setattr(assessment, k, v)
    await db.commit()
    await db.refresh(assessment)
    return assessment

@router.delete("/{assessment_id}")
async def delete_assessment(assessment_id: int, db: AsyncSession = Depends(get_db), admin: User = Depends(require_admin)):
    result = await db.execute(select(Assessment).where(Assessment.id == assessment_id))
    assessment = result.scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    await db.delete(assessment)
    await db.commit()
    return {"message": "Deleted successfully"}

@router.get("/{assessment_id}/questions")
async def get_questions(assessment_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Question).where(Question.assessment_id == assessment_id))
    questions = result.scalars().all()
    # Hide correct answers for candidates
    if current_user.role != "admin":
        return [{"id": q.id, "question_text": q.question_text, "question_type": q.question_type,
                 "option_a": q.option_a, "option_b": q.option_b, "option_c": q.option_c,
                 "option_d": q.option_d, "marks": q.marks, "topic": q.topic} for q in questions]
    return questions
