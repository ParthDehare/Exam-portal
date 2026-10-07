import json
from google import genai
from pydantic import BaseModel, Field
from typing import List
from config import settings
from fastapi import HTTPException

# Define the expected output structure for the AI
class QuestionOutput(BaseModel):
    question_text: str = Field(description="The actual question text")
    option_a: str = Field(description="First option")
    option_b: str = Field(description="Second option")
    option_c: str = Field(description="Third option")
    option_d: str = Field(description="Fourth option")
    correct_answer: str = Field(description="The correct option, strictly one of: option_a, option_b, option_c, option_d")
    explanation: str = Field(description="Detailed explanation of the answer")

class QuestionListOutput(BaseModel):
    questions: List[QuestionOutput]

def generate_questions(topic: str, difficulty: str, count: int = 5) -> List[dict]:
    if not settings.gemini_api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY is not configured in .env")

    client = genai.Client(api_key=settings.gemini_api_key)
    
    prompt = f"Generate {count} {difficulty} multiple-choice questions about '{topic}'. Ensure options are realistic and explanation is clear."
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config={
                'response_mime_type': 'application/json',
                'response_schema': QuestionListOutput,
            },
        )
        
        # Parse the JSON response
        data = json.loads(response.text)
        return data.get("questions", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Generation failed: {str(e)}")

def generate_learning_plan(assessment_title: str, wrong_answers: list) -> str:
    if not settings.gemini_api_key:
        return "AI Learning Plan cannot be generated because GEMINI_API_KEY is not configured in the server environment."

    client = genai.Client(api_key=settings.gemini_api_key)
    
    # Summarize wrong topics
    topics = {}
    for w in wrong_answers:
        t = w.get("topic", "General")
        topics[t] = topics.get(t, 0) + 1
        
    prompt = f"The student just took a test called '{assessment_title}'. They made mistakes in the following topics: {', '.join([f'{t} ({c} errors)' for t, c in topics.items()])}. Based on this, write a concise, encouraging 3-step personalized study plan to help them improve. Format it in clean HTML (using <ul>, <li>, <strong>, etc. without markdown blocks like ```html)."
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        logger.error(f"AI Plan Generation failed: {e}")
        return "Sorry, we couldn't generate a learning plan at this time."
