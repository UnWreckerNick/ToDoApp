from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
from config import DATABASE_URL, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

app = FastAPI()
Base = declarative_base()

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class ToDoItem(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    completed = Column(String, default=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

Base.metadata.create_all(bind=engine)

class RegisterUser(BaseModel):
    username: str
    password: str

class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category_id: Optional[int] = None

class ToDoUpdate(BaseModel):
    title: str = None
    description: str = None
    completed: bool = None

class CategoryCreate(BaseModel):
    name: str

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc)+ timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        return payload
    except JWTError:
        return None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: SessionLocal = Depends(get_db)):
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")
    return user

@app.post("/register/")
def register_user(user: RegisterUser, db: SessionLocal = Depends(get_db)):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_password = hash_password(user.password)
    new_user = User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully", "user_id": new_user.id}

@app.post("/login/")
def login_user(user_login: RegisterUser, db: SessionLocal = Depends(get_db)):
    user = db.query(User).filter(User.username == user_login.username).first()
    if not user or not pwd_context.verify(user_login.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username and/or password")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/todos/")
def create_todo(
        todo: TodoCreate,
        db: SessionLocal = Depends(get_db),
        current_user: User = Depends(get_current_user)
        ):
    category = db.query(Category).filter(Category.id == todo.category_id, Category.user_id == current_user.id).first()
    if todo.category_id and not category:
        raise HTTPException(status_code=400, detail="Invalid category")
    db_todo = ToDoItem(
        title=todo.title,
        description=todo.description,
        user_id=current_user.id,
        category_id=todo.category_id
    )
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.post("/categories/")
def create_category(category: CategoryCreate, db: SessionLocal = Depends(get_db), current_user: User = Depends(get_current_user)):
    if db.query(Category).filter(Category.name == category.name, Category.user_id == current_user.id).first():
        raise HTTPException(status_code=400, detail="Category already exists")
    new_category = Category(name=category.name, user_id=current_user.id)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

@app.get("/todos/all/")
def read_all_todos(skip: int = 0, limit: int = 10, db: SessionLocal = Depends(get_db)):
    todos = db.query(ToDoItem).offset(skip).limit(limit).all()
    return todos

@app.get("/todos/")
def read_user_todos(current_user: User = Depends(get_current_user), db: SessionLocal = Depends(get_db)):
    users = db.query(ToDoItem).filter(ToDoItem.user_id == current_user.id).all()
    return users

@app.get("/categories/")
def read_categories(db: SessionLocal = Depends(get_db), current_user: SessionLocal = Depends(get_current_user)):
    categories = db.query(Category).filter(Category.user_id == current_user.id).all()
    return categories

@app.get("/todos/category/{category_id}")
def get_todos_by_category(category_id: int, db: SessionLocal = Depends(get_db), current_user: SessionLocal = Depends(get_current_user)):
    todos = db.query(ToDoItem).filter(ToDoItem.user_id == current_user.id, ToDoItem.category_id == category_id).all()
    return todos

@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, todo: ToDoUpdate, db: SessionLocal = Depends(get_db)):
    db_todo = db.query(ToDoItem).filter(ToDoItem.id == todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="ToDo not found!")
    update_data = todo.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_todo, key, value)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: SessionLocal = Depends(get_db)):
    db_todo = db.query(ToDoItem).filter(ToDoItem.id == todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="ToDo not found!")
    db.delete(db_todo)
    db.commit()
    return {"message": "ToDo deleted"}

@app.delete("/categories/{category_id}")
def delete_category(category_id: int, db: SessionLocal = Depends(get_db), current_user: SessionLocal = Depends(get_current_user)):
    category = db.query(Category).filter(Category.name == category_id, Category.user_id == current_user.id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found!")
    db.delete(category)
    db.commit()
    return {"message": "Category deleted"}