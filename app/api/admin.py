from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.db import get_db
from app.models.user import User
from app.models.question import Question, QuestionType
from app.models.assessment import Assessment
from app.services.auth import require_admin
import openpyxl, io

router = APIRouter(prefix="/api/admin", tags=["Admin"])

@router.get("/users")
async def list_users(db: AsyncSession = Depends(get_db), admin: User = Depends(require_admin)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return [{"id": u.id, "fullname": u.fullname, "email": u.email, "role": u.role,
             "is_active": u.is_active, "created_at": u.created_at} for u in users]

@router.delete("/users/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db), admin: User = Depends(require_admin)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await db.delete(user)
    await db.commit()
    return {"message": "User deleted"}

@router.post("/import-questions/{assessment_id}")
async def import_questions(assessment_id: int, file: UploadFile = File(...),
                            db: AsyncSession = Depends(get_db), admin: User = Depends(require_admin)):
    content = await file.read()
    wb = openpyxl.load_workbook(io.BytesIO(content))
    ws = wb.active
    added = 0
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row[0]:
            continue
        q = Question(assessment_id=assessment_id, question_text=str(row[0]),
                     option_a=str(row[1]) if row[1] else None,
                     option_b=str(row[2]) if row[2] else None,
                     option_c=str(row[3]) if row[3] else None,
                     option_d=str(row[4]) if row[4] else None,
                     correct_answer=str(row[5]) if row[5] else "",
                     marks=int(row[6]) if row[6] else 1,
                     topic=str(row[7]) if row[7] else None)
        db.add(q)
        added += 1
    await db.commit()
    return {"message": f"{added} questions imported"}
