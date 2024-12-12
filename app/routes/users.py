from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from app.schemas import RegisterUser
from app.database import SessionLocal
from app.auth import hash_password, create_access_token, pwd_context
from app.models import User
from app.database import get_db

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register/")
def register_user(user: RegisterUser, db: SessionLocal = Depends(get_db)):
    try:
        RegisterUser(**user.model_dump())
        if db.query(User).filter(User.username == user.username).first():
            raise HTTPException(status_code=400, detail="Username already exists")
        hashed_password = hash_password(user.password)
        new_user = User(username=user.username, hashed_password=hashed_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"message": "User registered successfully", "user_id": new_user.id}
    except ValidationError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

@router.post("/login/")
def login_user(user_login: RegisterUser, db: SessionLocal = Depends(get_db)):
    user = db.query(User).filter(User.username == user_login.username).first()
    if not user or not pwd_context.verify(user_login.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username and/or password")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.delete("/{user_id}")
def delete_user(user_id: int, db: SessionLocal = Depends(get_db)):
    db_todo = db.query(User).filter(User.id == user_id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="User not found!")
    db.delete(db_todo)
    db.commit()
    return {"message": "User deleted"}