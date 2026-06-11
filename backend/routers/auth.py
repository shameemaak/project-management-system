from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from database.db import get_db
from database.models import User
from schemas.user import UserRegister, UserLogin, UserResponse, Token
from auth.jwt_handler import create_access_token
from auth.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/register", response_model=Token)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed = pwd_context.hash(user_data.password)
    user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        hashed_password=hashed
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer", "user": user}

@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not pwd_context.verify(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer", "user": user}

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
