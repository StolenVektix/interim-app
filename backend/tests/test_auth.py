"""EX-01, EX-02, EX-03."""

from conftest import register_and_login


def test_register_fixes_role_and_login_returns_it(client):
    resp = client.post(
        "/api/auth/register",
        json={"email": "e1@example.com", "password": "password123", "role": "employeur"},
    )
    assert resp.status_code == 201
    assert resp.json()["role"] == "employeur"

    login = client.post("/api/auth/login", json={"email": "e1@example.com", "password": "password123"})
    assert login.status_code == 200
    assert login.json()["role"] == "employeur"


def test_register_rejects_invalid_role(client):
    resp = client.post(
        "/api/auth/register",
        json={"email": "e2@example.com", "password": "password123", "role": "admin"},
    )
    assert resp.status_code == 422
    assert resp.json()["code"] == "VALIDATION_ERROR"


def test_unauthenticated_access_to_protected_route_returns_401(client):
    resp = client.get("/api/offers/mine")
    assert resp.status_code == 401
    assert resp.json()["code"] == "AUTH_REQUIRED"


def test_wrong_role_access_returns_403(client):
    headers = register_and_login(client, "w1@example.com", "password123", "interimaire")
    resp = client.get("/api/offers/mine", headers=headers)
    assert resp.status_code == 403
    assert resp.json()["code"] == "FORBIDDEN"
