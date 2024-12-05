from fastapi import APIRouter, Depends, HTTPException
from schemas import TodoCreate, ToDoUpdate
from database import SessionLocal
from models import ToDoItem, Category
from auth import get_current_user
from database import get_db

router = APIRouter(prefix="/todos", tags=["Todos"])

@router.post("/")
def create_todo(
        todo: TodoCreate,
        db: SessionLocal = Depends(get_db),
        current_user = Depends(get_current_user)
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

@router.get("/all/")
def read_all_todos(skip: int = 0, limit: int = 10, db: SessionLocal = Depends(get_db)):
    todos = db.query(ToDoItem).offset(skip).limit(limit).all()
    return todos

@router.get("/")
def read_user_todos(current_user = Depends(get_current_user), db: SessionLocal = Depends(get_db)):
    users = db.query(ToDoItem).filter(ToDoItem.user_id == current_user.id).all()
    return users

@router.put("/todos/{todo_id}")
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

@router.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: SessionLocal = Depends(get_db)):
    db_todo = db.query(ToDoItem).filter(ToDoItem.id == todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="ToDo not found!")
    db.delete(db_todo)
    db.commit()
    return {"message": "ToDo deleted"}