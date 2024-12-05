from database import SessionLocal
from models import ToDoItem
from datetime import datetime, timezone
from apscheduler.schedulers.background import BackgroundScheduler

def check_overdue_tasks():
    db = SessionLocal
    try:
        now = datetime.now(timezone.utc)
        overdue_tasks = db.query(ToDoItem).filter(
            ToDoItem.deadline is not None,
            ToDoItem.deadline < now,
            ToDoItem.completed == False
        ).all()
        for task in overdue_tasks:
            print(f"Task {task.title} is overdue!")
    finally:
        db.close()

scheduler = BackgroundScheduler()
scheduler.add_job(check_overdue_tasks, "interval", minutes=60)
scheduler.start()