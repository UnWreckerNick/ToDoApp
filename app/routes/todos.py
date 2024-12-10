from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from starlette.responses import StreamingResponse
from app.schemas import TodoCreate, ToDoUpdate
from app.database import SessionLocal, get_db
from app.models import ToDoItem, Category
from app.auth import get_current_user
from datetime import datetime, timedelta, timezone
from app.config import MAX_FILE_SIZE
from app.cache import get_cached_todos, cache_todo

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
        category_id=todo.category_id,
        deadline=todo.deadline
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
    cached_todos = get_cached_todos(current_user.id)
    if cached_todos:
        return cached_todos
    todos = db.query(ToDoItem).filter(ToDoItem.user_id == current_user.id).all()
    cached_todos(current_user.id, todos)
    return todos

@router.get("/upcoming/")
def get_upcoming_deadlines(days: int = 7, db: SessionLocal = Depends(get_db), current_user = Depends(get_current_user)):
    now = datetime.now(timezone.utc)
    upcoming = now + timedelta(days=days)
    todos = db.query(ToDoItem).filter(
        ToDoItem.user_id == current_user.id,
        ToDoItem.deadline is not None,
        ToDoItem.deadline.between(now, upcoming)
    ).all()
    return todos

@router.put("/{todo_id}")
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

@router.delete("/{todo_id}")
def delete_todo(todo_id: int, db: SessionLocal = Depends(get_db)):
    db_todo = db.query(ToDoItem).filter(ToDoItem.id == todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="ToDo not found!")
    db.delete(db_todo)
    db.commit()
    return {"message": "ToDo deleted"}

@router.post("/{todo_id}/upload/")
def upload_file(
        todo_id: int,
        file: UploadFile = File(...),
        db: SessionLocal = Depends(get_db),
        current_user = Depends(get_current_user)
):
    todo = db.query(ToDoItem).filter(ToDoItem.id == todo_id, ToDoItem.user_id == current_user.id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="ToDo not found")
    file_content = file.file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File is too large")
    todo.file_data = file_content
    db.commit()
    return {"message": "File uploaded successfully", "filename": file.filename}

@router.get("/{todo_id}/download/")
def download_file(
        todo_id: int,
        db: SessionLocal = Depends(get_db),
        current_user = Depends(get_current_user)
):
    todo = db.query(ToDoItem).filter(ToDoItem.id == todo_id, ToDoItem.user_id == current_user.id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="ToDo not found")
    if not todo.file_data:
        raise HTTPException(status_code=404, detail="File not found")
    return StreamingResponse(
        iter([todo.file_data]),
        headers={"Content-Deposition": f"attachment; filename=todo_{todo_id}_file"},
        media_type="application/octet-stream"
    )