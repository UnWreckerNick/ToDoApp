from pydantic import BaseModel
from typing import Optional

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