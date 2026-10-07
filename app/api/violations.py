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

class FaceVerifyRequest(BaseModel):
    assessment_id: int
    image_base64: str

@router.post("/verify-face")
async def verify_face(data: FaceVerifyRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    from app.services.vision import detect_faces
    
    result = detect_faces(data.image_base64)
    
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result.get("message"))
        
    # If it's a violation, auto-log it
    if result.get("is_violation"):
        violation = Violation(
            user_id=current_user.id, 
            assessment_id=data.assessment_id, 
            violation_type=result.get("violation_type")
        )
        db.add(violation)
        await db.commit()
        
    return result

@router.get("/{assessment_id}")
async def get_violations(assessment_id: int, db: AsyncSession = Depends(get_db), admin: User = Depends(require_admin)):
    result = await db.execute(
        select(Violation, User.fullname).join(User).where(Violation.assessment_id == assessment_id)
    )
    rows = result.all()
    return [{"id": v.id, "fullname": name, "violation_type": v.violation_type, "timestamp": v.timestamp} for v, name in rows]
