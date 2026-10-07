from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.db import get_db
from app.models.user import User
from app.services.auth import hash_password, verify_password, create_access_token, get_current_user
from app.services.schemas import UserRegister, UserLogin, Token, UserOut

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

def _set_auth_cookie(response: Response, token: str):
    response.set_cookie(
        key="access_token",
        value=f"Bearer {token}",
        httponly=True,
        samesite="lax",
        secure=False,  # Set to True in production with HTTPS
        max_age=3600
    )

@router.post("/register", response_model=Token, status_code=201)
async def register(data: UserRegister, response: Response, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(fullname=data.fullname, email=data.email, password=hash_password(data.password), role=data.role)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Send Welcome Email
    from app.services.email import email_service
    html_content = f"""
    <h2>Welcome to MockExam Pro, {user.fullname}!</h2>
    <p>Your account has been successfully created as a <strong>{user.role}</strong>.</p>
    <p>You can now log in and start using the platform.</p>
    """
    await email_service.send_email(to_email=user.email, subject="Welcome to MockExam Pro", html_content=html_content)
    
    token = create_access_token({"sub": user.email, "role": user.role})
    _set_auth_cookie(response, token)
    return Token(access_token=token, token_type="bearer", user=UserOut.model_validate(user))

@router.post("/login", response_model=Token)
async def login(data: UserLogin, response: Response, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token({"sub": user.email, "role": user.role})
    _set_auth_cookie(response, token)
    return Token(access_token=token, token_type="bearer", user=UserOut.model_validate(user))

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"detail": "Logged out successfully"}

@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)):
    return UserOut.model_validate(current_user)
