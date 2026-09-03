from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
import json
from pydantic import BaseModel
from app.database.db import get_db
from app.models.result import Result, ResultStatus
from app.models.assessment import Assessment
from app.models.question import Question
from app.models.violation import Violation
from app.services.auth import get_current_user, require_admin
from app.models.user import User

router = APIRouter(prefix="/api/results", tags=["Results"])

class SubmitExam(BaseModel):
    assessment_id: int
    answers: dict
    time_taken: Optional[int] = 0

# /my and /leaderboard MUST be before /{result_id} to avoid routing conflicts
@router.get("/my")
async def my_results(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Result, Assessment.title).join(Assessment).where(Result.user_id == current_user.id))
    rows = result.all()
    return [{"id": r.id, "assessment_title": title, "score": r.score, "percentage": r.percentage,
             "status": r.status, "submitted_at": r.submitted_at} for r, title in rows]

@router.get("/leaderboard/{assessment_id}")
async def leaderboard(assessment_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(Result, User.fullname).join(User).where(Result.assessment_id == assessment_id).order_by(Result.score.desc()).limit(20)
    )
    rows = result.all()
    return [{"rank": i+1, "fullname": name, "score": r.score, "percentage": r.percentage, "status": r.status}
            for i, (r, name) in enumerate(rows)]

@router.post("/submit")
async def submit_exam(data: SubmitExam, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Allow multiple submissions for practice/testing

    assessment_result = await db.execute(select(Assessment).where(Assessment.id == data.assessment_id))
    assessment = assessment_result.scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    questions_result = await db.execute(select(Question).where(Question.assessment_id == data.assessment_id))
    questions = questions_result.scalars().all()

    score = 0
    for q in questions:
        user_answer = data.answers.get(str(q.id), "")
        if str(user_answer).strip().lower() == str(q.correct_answer).strip().lower():
            score += q.marks

    percentage = (score / assessment.total_marks * 100) if assessment.total_marks > 0 else 0
    status = ResultStatus.pass_ if score >= assessment.passing_marks else ResultStatus.fail

    result = Result(user_id=current_user.id, assessment_id=data.assessment_id,
                    score=score, percentage=round(percentage, 2), status=status,
                    answers=json.dumps(data.answers), time_taken=data.time_taken)
    db.add(result)
    await db.commit()
    await db.refresh(result)

    topic_analysis = {}
    for q in questions:
        topic = q.topic or "General"
        if topic not in topic_analysis:
            topic_analysis[topic] = {"correct": 0, "total": 0}
        topic_analysis[topic]["total"] += 1
        if str(data.answers.get(str(q.id), "")).strip().lower() == str(q.correct_answer).strip().lower():
            topic_analysis[topic]["correct"] += 1

    return {"result_id": result.id, "score": score, "percentage": round(percentage, 2),
            "status": status, "total_marks": assessment.total_marks,
            "passing_marks": assessment.passing_marks, "topic_analysis": topic_analysis}

@router.get("/{result_id}")
async def get_result(result_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Result).where(Result.id == result_id))
    r = result.scalar_one_or_none()
    if not r or (r.user_id != current_user.id and current_user.role != "admin"):
        raise HTTPException(status_code=404, detail="Result not found")

    assessment_result = await db.execute(select(Assessment).where(Assessment.id == r.assessment_id))
    assessment = assessment_result.scalar_one_or_none()
    questions_result = await db.execute(select(Question).where(Question.assessment_id == r.assessment_id))
    questions = questions_result.scalars().all()
    answers = json.loads(r.answers or "{}")

    question_report = [{"id": q.id, "question_text": q.question_text, "correct_answer": q.correct_answer,
                        "user_answer": answers.get(str(q.id), ""), "marks": q.marks, "topic": q.topic,
                        "explanation": q.explanation,
                        "is_correct": str(answers.get(str(q.id), "")).strip().lower() == str(q.correct_answer).strip().lower()}
                       for q in questions]

    return {"result_id": r.id, "score": r.score, "percentage": r.percentage, "status": r.status,
            "time_taken": r.time_taken, "submitted_at": r.submitted_at,
            "assessment": {"title": assessment.title, "total_marks": assessment.total_marks,
                           "passing_marks": assessment.passing_marks},
            "questions": question_report}
