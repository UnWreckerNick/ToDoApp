from fastapi import APIRouter, Depends, HTTPException
from app.schemas import RegisterUser
from app.database import SessionLocal
from app.auth import hash_password, create_access_token, pwd_context
from app.models import User
from app.database import get_db

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register/")
def register_user(user: RegisterUser, db: SessionLocal = Depends(get_db)):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_password = hash_password(user.password)
    new_user = User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully", "user_id": new_user.id}

@router.post("/login/")
def login_user(user_login: RegisterUser, db: SessionLocal = Depends(get_db)):
    user = db.query(User).filter(User.username == user_login.username).first()
    if not user or not pwd_context.verify(user_login.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username and/or password")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}