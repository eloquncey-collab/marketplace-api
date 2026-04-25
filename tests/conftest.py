import pytest
from fastapi.testclient import TestClient
from main import app
import time
import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.database import Base
from app.database import SessionLocal
from app.models import User
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL_TEST = os.getenv("DATABASE_URL_TEST")


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    engine = create_engine(DATABASE_URL_TEST,pool_pre_ping=True)
    Base.metadata.create_all(engine)
    
    yield 
    Base.metadata.drop_all(engine)

@pytest.fixture(autouse=True)
def override_get_db():
    from app.database import get_db as original_get_db
    from sqlalchemy.orm import sessionmaker
    
    engine = create_engine(DATABASE_URL_TEST, pool_pre_ping=True)
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    
    def get_test_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[original_get_db] = get_test_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client(): 
    with TestClient(app) as c:
        yield c
        
@pytest.fixture
def make_headers(client):
    def _make(is_admin=False):
        u = f"user_{int(time.time_ns())}"
        p = "password123"
        e = f"{u}@example.com"
        r = client.post("/auth/register", json={"username": u,
                                                "email": e,
                                                "password": p})
        assert r.status_code == 201, r.text
        if is_admin:
            engine = create_engine(DATABASE_URL_TEST, pool_pre_ping=True)
            TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
            db = TestingSessionLocal()
            try:
                user = db.query(User).filter(User.username == u).first()
                assert user is not None
                user.is_admin = True
                db.commit()
            finally:
                db.close()
        r = client.post("/auth/login", json={
            "username": u,
            "email": e,
            "password": p
        })
        assert r.status_code == 200
        assert "access_token" in r.json()
        token = r.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    return _make
@pytest.fixture
def admin_headers(make_headers):
    return make_headers(is_admin=True)

@pytest.fixture
def user_headers(make_headers):
    return make_headers(is_admin=False)

