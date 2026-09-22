import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import deps
from app.database import Base
from app.main import app


@pytest.fixture()
def db_session(tmp_path):
    db_path = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[deps.get_db] = override_get_db
    yield testing_session_local
    app.dependency_overrides.clear()


@pytest.fixture()
def client(db_session):
    return TestClient(app)


def register_and_login(client: TestClient, email: str, password: str, role: str) -> dict:
    client.post("/api/auth/register", json={"email": email, "password": password, "role": role})
    resp = client.post("/api/auth/login", json={"email": email, "password": password})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def create_offer(client: TestClient, headers: dict, **overrides):
    payload = {
        "title": "Préparateur de commandes",
        "description": "Préparation de commandes en entrepôt.",
        "hourly_wage": 13.5,
        "weekly_hours": 35,
        "start_date": "2026-09-01",
        "end_date": "2026-09-30",
        "city": "Bordeaux",
    }
    payload.update(overrides)
    return client.post("/api/offers", json=payload, headers=headers)
