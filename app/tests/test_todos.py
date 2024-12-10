import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models import User

client = TestClient(app)

@pytest.fixture(scope="module")
def user_token():
    response = client.post("/users/login/", json={
        "username": "testuser",
        "password": "testpassword"
    })
    assert response.status_code == 200
    response_data = response.json()
    assert "access_token" in response_data
    assert response_data["token_type"] == "bearer"
    return response_data["access_token"]

def test_register():
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.username == "testuser").first()
        if existing_user:
            db.delete(existing_user)
            db.commit()

        response_data = client.post("/users/register/", json={
            "username": "testuser",
            "password": "testpassword"
        })
        assert response_data.status_code == 200
    finally:
        db.close()

def test_login():
    response = client.post("/users/login/", json={
        "username": "testuser",
        "password": "testpassword"
    })
    assert response.status_code == 200
    response_data = response.json()
    assert "access_token" in response_data
    assert response_data["token_type"] == "bearer"

def test_create_todo(user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.post(
        "/todos/",
        json={"title": "Test todo", "description": "Test description"},
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Test todo"
