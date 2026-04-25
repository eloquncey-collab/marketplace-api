from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import UserCreate, UserResponse, Token
from app.models import User
from app.auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    email_user = db.query(User).filter(User.email == user_data.email).first()
    name_user = db.query(User).filter(User.username == user_data.username).first()
    if email_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    if name_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed = hash_password(user_data.password)
    
    new_user = User(username=user_data.username,
                    email=user_data.email, 
                    hashed_password=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=Token)
def login(user_data: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_data.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(user.id)
    return {"access_token": access_token, "token_type": "bearer"}
         