from pydantic import BaseModel, field_validator, Field
from typing import Optional
from datetime import datetime
import re

class RegisterUser(BaseModel):
    username: str = Field(min_length=3, max_length=32, pattern="^[A-Za-z0-9-_]+$")
    password: str

    @field_validator("password")
    def validate_password(cls, value):
        if len(value) < 8 or len(value) > 32:
            raise ValueError("Password must be at least 8 characters long.")
        if not re.search(r'[A-Z]', value):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', value):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not re.search(r'\d', value):
            raise ValueError("Password must contain at least one digit.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValueError("Password must contain at least one special character.")
        return value

class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category_id: Optional[int] = None
    deadline: Optional[datetime] = None

class ToDoUpdate(BaseModel):
    title: str = None
    description: str = None
    completed: bool = None

class CategoryCreate(BaseModel):
    name: str