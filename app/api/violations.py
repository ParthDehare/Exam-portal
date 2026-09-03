from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from app.database.db import get_db
from app.models.violation import Violation
from app.models.result import Result
from app.models.assessment import Assessment
from app.models.user import User
from app.services.auth import get_current_user, require_admin

router = APIRouter(prefix="/api/violations", tags=["Violations"])

class ViolationCreate(BaseModel):
    assessment_id: int
    violation_type: str

@router.post("/")
async def log_violation(data: ViolationCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    violation = Violation(user_id=current_user.id, assessment_id=data.assessment_id, violation_type=data.violation_type)
    db.add(violation)
    await db.commit()
    return {"message": "Violation logged"}

@router.get("/{assessment_id}")
async def get_violations(assessment_id: int, db: AsyncSession = Depends(get_db), admin: User = Depends(require_admin)):
    result = await db.execute(
        select(Violation, User.fullname).join(User).where(Violation.assessment_id == assessment_id)
    )
    rows = result.all()
    return [{"id": v.id, "fullname": name, "violation_type": v.violation_type, "timestamp": v.timestamp} for v, name in rows]
