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

class AIGenerateRequest(BaseModel):
    assessment_id: int
    topic: str
    difficulty: str = "medium"
    count: int = 5
    auto_save: bool = False

@router.post("/ai/generate", status_code=200)
async def generate_ai_questions(data: AIGenerateRequest, db: AsyncSession = Depends(get_db), admin: User = Depends(require_admin)):
    from app.services.ai import generate_questions
    
    generated = generate_questions(topic=data.topic, difficulty=data.difficulty, count=data.count)
    
    saved_questions = []
    if data.auto_save:
        for q_data in generated:
            q = Question(
                assessment_id=data.assessment_id,
                question_text=q_data["question_text"],
                question_type=QuestionType.mcq,
                option_a=q_data["option_a"],
                option_b=q_data["option_b"],
                option_c=q_data["option_c"],
                option_d=q_data["option_d"],
                correct_answer=q_data["correct_answer"],
                explanation=q_data["explanation"],
                marks=1,
                topic=data.topic
            )
            db.add(q)
            saved_questions.append(q)
        await db.commit()
        for sq in saved_questions:
            await db.refresh(sq)
        return {"message": f"Generated and saved {len(saved_questions)} questions.", "questions": saved_questions}
    
    return {"message": "Generated questions successfully.", "questions": generated}

@router.post("/ai/translate", status_code=200)
async def translate_question(data: dict, current_user: User = Depends(get_current_user)):
    # data should contain 'text' and 'target_language'
    text = data.get("text")
    target_lang = data.get("target_language")
    
    if not text or not target_lang:
        raise HTTPException(status_code=400, detail="Missing text or target_language")
        
    from config import settings
    from google import genai
    
    if not settings.gemini_api_key:
        return {"translated_text": f"[{target_lang}] {text}"} # Mock fallback
        
    try:
        client = genai.Client(api_key=settings.gemini_api_key)
        prompt = f"Translate the following exam question text into {target_lang}. Preserve the technical accuracy and meaning exactly. Return ONLY the translated text without any explanation, markdown, or quotes: \n\n{text}"
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return {"translated_text": response.text.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
