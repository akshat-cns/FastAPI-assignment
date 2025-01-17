import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db(): #Mock databse
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_register_user():
    response = client.post(
        "/register",
        json={"username": "testuser", "password": "password123"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"


def test_register_duplicate_user():
    response = client.post(
        "/register",
        json={"username": "testuser", "password": "password123"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already registered"


def test_login_user():
    response = client.post(
        "/login",
        json={"username": "consultadd", "password": "consultadd"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_invalid_user():
    response = client.post(
        "/login",
        json={"username": "invaliduser", "password": "password123"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_add_event():
    login_response = client.post(
        "/login",
        json={"username": "testuser", "password": "password123"}
    )
    token = login_response.json()["access_token"]

    response = client.post(
        "/admin/events",
        json={
            "title": "Test Event",
            "description": "This is a test event",
            "date": "2025-01-20T12:00:00",
            "available_tickets": 100
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Test Event"
    assert response.json()["available_tickets"] == 100


def test_update_event():
    login_response = client.post(
        "/login",
        json={"username": "testuser", "password": "password123"}
    )
    token = login_response.json()["access_token"]

    create_response = client.post(
        "/admin/events",
        json={
            "title": "Test Event",
            "description": "This is a test event",
            "date": "2025-01-20T12:00:00",
            "available_tickets": 100
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    event_id = create_response.json()["id"]

    # Update evnt
    response = client.put(
        f"/admin/events/{event_id}",
        json={
            "title": "Updated Event",
            "description": "Updated ",
            "date": "2025-01-21T12:00:00",
            "available_tickets": 150
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Event"
    assert response.json()["available_tickets"] == 150


def test_delete_event():
    login_response = client.post(
        "/login",
        json={"username": "testuser", "password": "password123"}
    )
    token = login_response.json()["access_token"]

    # Create eveNT
    create_response = client.post(
        "/admin/events",
        json={
            "title": "Event to Delete",
            "description": "This will be deleted",
            "date": "2025-01-22T12:00:00",
            "available_tickets": 50
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    event_id = create_response.json()["id"]

    response = client.delete(
        f"/admin/events/{event_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["id"] == event_id


def test_delete_nonexistent_event():
    # Get a token for authentication
    login_response = client.post(
        "/login",
        json={"username": "testuser", "password": "password123"}
    )
    token = login_response.json()["access_token"]

    response = client.delete(
        "/admin/events/9999",  # Non-existent event ID
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Event not found."
