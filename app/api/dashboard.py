from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database.db import get_db
from app.models.user import User
from app.models.assessment import Assessment
from app.models.result import Result
from app.models.question import Question
from app.services.auth import get_current_user, require_admin

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/candidate")
async def candidate_dashboard(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    results_q = await db.execute(select(Result).where(Result.user_id == current_user.id))
    results = results_q.scalars().all()

    assessments_q = await db.execute(select(Assessment).where(Assessment.is_active == True))
    all_assessments = assessments_q.scalars().all()

    completed_ids = {r.assessment_id for r in results}
    available = [a for a in all_assessments if a.id not in completed_ids]

    avg_score = sum(r.percentage for r in results) / len(results) if results else 0
    best_score = max((r.percentage for r in results), default=0)

    return {
        "fullname": current_user.fullname,
        "total_assessments": len(all_assessments),
        "completed": len(results),
        "available": len(available),
        "avg_score": round(avg_score, 2),
        "best_score": round(best_score, 2),
        "recent_results": [{"assessment_id": r.assessment_id, "score": r.score,
                             "percentage": r.percentage, "status": r.status,
                             "submitted_at": r.submitted_at} for r in results[-5:]],
        "available_assessments": [{"id": a.id, "title": a.title, "duration": a.duration,
                                    "total_marks": a.total_marks, "difficulty": a.difficulty,
                                    "category": a.category} for a in available[:6]]
    }

@router.get("/admin")
async def admin_dashboard(db: AsyncSession = Depends(get_db), admin: User = Depends(require_admin)):
    total_users = await db.execute(select(func.count(User.id)))
    total_assessments = await db.execute(select(func.count(Assessment.id)))
    total_results = await db.execute(select(func.count(Result.id)))
    avg_score = await db.execute(select(func.avg(Result.percentage)))

    recent_results = await db.execute(
        select(Result, User.fullname, Assessment.title)
        .join(User).join(Assessment).order_by(Result.submitted_at.desc()).limit(10)
    )
    rows = recent_results.all()

    return {
        "total_users": total_users.scalar(),
        "total_assessments": total_assessments.scalar(),
        "total_results": total_results.scalar(),
        "avg_score": round(avg_score.scalar() or 0, 2),
        "recent_results": [{"fullname": name, "assessment": title, "score": r.score,
                             "percentage": r.percentage, "status": r.status,
                             "submitted_at": r.submitted_at} for r, name, title in rows]
    }

@router.get("/analytics")
async def analytics(db: AsyncSession = Depends(get_db), admin: User = Depends(require_admin)):
    assessments_q = await db.execute(select(Assessment))
    assessments = assessments_q.scalars().all()

    data = []
    for a in assessments:
        stats = await db.execute(
            select(func.count(Result.id), func.avg(Result.percentage),
                   func.max(Result.percentage), func.min(Result.percentage))
            .where(Result.assessment_id == a.id)
        )
        count, avg, high, low = stats.one()
        data.append({"title": a.title, "participants": count or 0,
                     "avg": round(avg or 0, 2), "highest": round(high or 0, 2), "lowest": round(low or 0, 2)})
    return data
