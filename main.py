from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from database import Base, engine
from routes import todos, categories, users

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(todos.router)
app.include_router(categories.router)
app.include_router(users.router)