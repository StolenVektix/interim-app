"""EX-05 à EX-10, EX-22."""

from conftest import create_offer, register_and_login


def test_create_valid_offer_persists_open_with_id_and_timestamp(client):
    headers = register_and_login(client, "emp1@example.com", "password123", "employeur")
    resp = create_offer(client, headers)
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "open"
    assert body["id"] is not None
    assert body["created_at"] is not None


def test_missing_or_out_of_bounds_fields_return_422_and_persist_nothing(client):
    headers = register_and_login(client, "emp2@example.com", "password123", "employeur")
    resp = create_offer(client, headers, weekly_hours=60)  # borne max = 48
    assert resp.status_code == 422
    assert resp.json()["code"] == "VALIDATION_ERROR"
    assert "weekly_hours" in resp.json()["fields"]

    listed = client.get("/api/offers/mine", headers=headers)
    assert listed.json() == []


def test_end_date_before_start_date_returns_invalid_period(client):
    headers = register_and_login(client, "emp3@example.com", "password123", "employeur")
    resp = create_offer(client, headers, start_date="2026-09-30", end_date="2026-09-01")
    assert resp.status_code == 422
    assert resp.json()["code"] == "INVALID_PERIOD"


def test_close_offer_removes_from_stack_but_keeps_applications(client):
    emp_headers = register_and_login(client, "emp4@example.com", "password123", "employeur")
    offer_id = create_offer(client, emp_headers).json()["id"]

    worker_headers = register_and_login(client, "work1@example.com", "password123", "interimaire")
    client.post(f"/api/offers/{offer_id}/swipe", json={"direction": "right"}, headers=worker_headers)

    close_resp = client.post(f"/api/offers/{offer_id}/close", headers=emp_headers)
    assert close_resp.status_code == 200
    assert close_resp.json()["status"] == "closed"

    stack = client.get("/api/stack", headers=worker_headers).json()
    assert all(o["id"] != offer_id for o in stack)

    applications = client.get(f"/api/offers/{offer_id}/applications", headers=emp_headers).json()
    assert len(applications) == 1


def test_only_owner_can_modify_or_close_offer(client):
    emp_headers = register_and_login(client, "emp5@example.com", "password123", "employeur")
    other_headers = register_and_login(client, "emp6@example.com", "password123", "employeur")
    offer_id = create_offer(client, emp_headers).json()["id"]

    resp = client.post(f"/api/offers/{offer_id}/close", headers=other_headers)
    assert resp.status_code == 403

    resp2 = client.patch(f"/api/offers/{offer_id}", json={"title": "Hack"}, headers=other_headers)
    assert resp2.status_code == 403
