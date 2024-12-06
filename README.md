# TODO Application

This is a task management web application built using **FastAPI** for the backend and **HTML/CSS/JavaScript** for the frontend. The app allows you to create, edit, and delete tasks, as well as upload files associated with tasks. All data is stored in a **PostgreSQL** database.

## Features

- **Authentication and Registration**: Users must register and log in to access the functionality.
- **Task Management**: Ability to add, edit, and delete tasks.
- **Task Categories**: Each task can be assigned to a category.
- **Deadlines**: Tasks can have deadlines with specific times.
- **File Upload**: Option to upload and attach files to tasks.
- **Built with FastAPI**: High performance thanks to asynchronous operations.

## Technologies

- **Backend**: FastAPI
- **Frontend**: HTML, CSS, JavaScript
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: JWT (JSON Web Tokens)

## Installation

### 1. Clone the repository:
`git clone https://github.com/yourusername/todo-app.git`

### 2. Create a virtual environment:
`python -m venv .venv`

### 3. Activate the virtual environment:
On Windows: `.venv\Scripts\activate`
On macOS/Linux: `source .venv/bin/activate`

### 4. Install the dependencies:
`pip install -r requirements.txt`

### 5. Set up the database:
This application uses SQLite as the database, which doesn't require a separate server. By default, SQLite will store the database in a local file named app.db. You don’t need any additional setup to start using it.

### 6. Run the application:
Start the FastAPI development server: `uvicorn main:app --reload`

## Endpoints
### Authentication
- **POST /login**: User login to obtain a JWT token.
- **POST /register**: User registration.

### Task Management
- **GET /todos/**: Fetch all tasks.
- **POST /todos/**: Create a new task.
- **PUT /todos/{todo_id}**: Edit a task.
- **DELETE /todos/{todo_id}**: Delete a task.

### File Upload
- **POST /todos/{todo_id}/upload/**: Upload a file to a task.
- **GET /todos/{todo_id}/download/**: Download a file associated with a task.

## Frontend
The frontend consists of a simple HTML form to interact with the backend via API requests. It allows users to login, add tasks, view tasks, select deadlines, and upload files.

## Authentication
To authenticate and interact with the application, users must first register an account and then log in to obtain a JWT (JSON Web Token). This token is required for accessing all protected routes in the application, such as creating tasks and uploading files.

### Register a User
Send a POST request to /register with the user's username and password.

### Login
Send a POST request to /login with the user's username and password to obtain a JWT.
### Use JWT for Authenticated Routes
Include the obtained JWT in the Authorization header as a Bearer token for subsequent API requests.
`Authorization: Bearer YOUR_JWT_TOKEN`

## Testing
You can test the app using the browser or tools like Postman or curl to interact with the API. Ensure you pass the Authorization header for protected routes.
