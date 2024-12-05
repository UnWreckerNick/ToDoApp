from fastapi import FastAPI
from database import Base, engine
from routes import todos, categories, users

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(todos.router)
app.include_router(categories.router)
app.include_router(users.router)