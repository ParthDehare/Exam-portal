from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.db import get_db
from app.models.user import User
from app.models.result import Result
from app.models.question import Question
from app.models.assessment import Assessment
from app.services.auth import get_current_user
import json

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.post("/{result_id}/ai-plan")
async def generate_learning_plan(result_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    from app.services.ai import generate_learning_plan as ai_generate_plan
    
    # Fetch result
    result_q = await db.execute(select(Result).where(Result.id == result_id))
    result = result_q.scalar_one_or_none()
    
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
        
    # Check authorization (only the user who took it, or admin)
    if result.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
        
    # Fetch assessment details
    assessment_q = await db.execute(select(Assessment).where(Assessment.id == result.assessment_id))
    assessment = assessment_q.scalar_one_or_none()
    
    # Build a profile of wrong answers
    wrong_answers = []
    answers_dict = result.answers
    
    questions_q = await db.execute(select(Question).where(Question.assessment_id == result.assessment_id))
    questions = questions_q.scalars().all()
    
    for q in questions:
        user_ans = answers_dict.get(str(q.id))
        if user_ans != q.correct_answer:
            wrong_answers.append({
                "topic": q.topic or "General",
                "question": q.question_text,
                "user_chose": user_ans,
                "correct_was": q.correct_answer
            })
            
    if not wrong_answers:
        return {"plan": "Perfect score! No specific learning plan needed, keep up the great work."}
        
    # Generate the plan using the AI service
    plan = ai_generate_plan(assessment.title, wrong_answers)
    return {"plan": plan}
