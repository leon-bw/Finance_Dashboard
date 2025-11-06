import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.auth import get_password_hash
from app.database import Base, get_db
from app.main import app
from app.models import User

load_dotenv()


TEST_DATABASE_URL = "sqlite:///test_finance_app.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})

TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(test_db):
    # Create a test user
    user = User(
        username="testuser",
        email="test@test.com",
        first_name="Test",
        last_name="User",
        hashed_password=get_password_hash("test1234"),
        monthly_budget=3500,
        currency_preference="GBP",
        is_active=True,
        is_demo=False,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_demo_user(test_db):
    # Create a test user
    demo_user = User(
        username="demo",
        email="demo@myfinancecoach.com",
        first_name="Demo",
        last_name="User",
        hashed_password=get_password_hash("demo1234"),
        monthly_budget=3500,
        currency_preference="GBP",
        is_active=True,
        is_demo=True,
    )
    test_db.add(demo_user)
    test_db.commit()
    test_db.refresh(demo_user)
    return demo_user


@pytest.fixture(scope="function")
def authenticated_client(client, test_user):
    response = client.post(
        "auth/login", data={"username": "testuser", "password": "test1234"}
    )
    token = response.json()["access_token"]

    client.headers = {**client.headers, "Authorisation": f"Bearer {token}"}
    return client
