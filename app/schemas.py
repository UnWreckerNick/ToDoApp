from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
import re

class RegisterUser(BaseModel):
    username: str
    password: str

    @field_validator("username")
    def validate_username_length(cls, value):
        if len(value) < 3 or len(value) > 32:
            raise ValueError("Username must be at least 3 characters length and less then 20")
        return value

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