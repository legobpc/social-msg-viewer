import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

# Use SQLite test database (in-memory or file-based for persistence)
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///./test.db")
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the default database dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

# Automatically create and drop tables before/after the test module
@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_register():
    """Test user registration"""
    res = client.post("/auth/register", data={"username": "testuser", "password": "testpass"})
    assert res.status_code == 200
    assert res.json() == {"message": "User registered"}


def test_login_success():
    """Test login with correct credentials"""
    res = client.post("/auth/login", data={"username": "testuser", "password": "testpass"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_failure():
    """Test login with incorrect credentials"""
    res = client.post("/auth/login", data={"username": "wrong", "password": "wrong"})
    assert res.status_code == 401


def test_me_unauthorized():
    """Test accessing /auth/me without a token"""
    res = client.get("/auth/me")
    assert res.status_code == 401


def test_me_authorized():
    """Test accessing /auth/me with a valid token"""
    login = client.post("/auth/login", data={"username": "testuser", "password": "testpass"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/auth/me", headers=headers)
    assert res.status_code == 200
    assert res.json() == {"username": "testuser"}


def test_refresh_token():
    """Test token refresh using refresh cookie"""
    login = client.post("/auth/login", data={"username": "testuser", "password": "testpass"})
    client.cookies = login.cookies  # Set cookies for session

    res = client.post("/auth/refresh")
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_logout():
    """Test logout clears refresh token"""
    res = client.post("/auth/logout")
    assert res.status_code == 200
    assert res.json() == {"message": "Logged out successfully"}
