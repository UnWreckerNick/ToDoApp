from fastapi import APIRouter, Depends, HTTPException
from schemas import CategoryCreate
from database import SessionLocal
from models import ToDoItem, Category
from auth import get_current_user
from database import get_db

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.post("/categories/")
def create_category(category: CategoryCreate, db: SessionLocal = Depends(get_db), current_user = Depends(get_current_user)):
    if db.query(Category).filter(Category.name == category.name, Category.user_id == current_user.id).first():
        raise HTTPException(status_code=400, detail="Category already exists")
    new_category = Category(name=category.name, user_id=current_user.id)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

@router.get("/categories/")
def read_categories(db: SessionLocal = Depends(get_db), current_user: SessionLocal = Depends(get_current_user)):
    categories = db.query(Category).filter(Category.user_id == current_user.id).all()
    return categories

@router.get("/todos/category/{category_id}")
def get_todos_by_category(category_id: int, db: SessionLocal = Depends(get_db), current_user: SessionLocal = Depends(get_current_user)):
    todos = db.query(ToDoItem).filter(ToDoItem.user_id == current_user.id, ToDoItem.category_id == category_id).all()
    return todos

@router.delete("/categories/{category_id}")
def delete_category(category_id: int, db: SessionLocal = Depends(get_db), current_user: SessionLocal = Depends(get_current_user)):
    category = db.query(Category).filter(Category.name == category_id, Category.user_id == current_user.id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found!")
    db.delete(category)
    db.commit()
    return {"message": "Category deleted"}