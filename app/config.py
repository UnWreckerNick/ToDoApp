from dotenv import load_dotenv
import os

load_dotenv()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = os.path.join(BASE_DIR, 'todo.db')
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
MAX_FILE_SIZE = 2 * 1024 * 1024