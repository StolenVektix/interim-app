"""EX-14, EX-20."""

from conftest import create_offer, register_and_login


def test_stack_excludes_closed_out_of_filter_and_already_swiped_offers(client):
    emp_headers = register_and_login(client, "emp20@example.com", "password123", "employeur")
    to_close = create_offer(client, emp_headers, city="Bordeaux").json()
    out_of_filter = create_offer(client, emp_headers, city="Bordeaux", hourly_wage=11).json()
    already_swiped = create_offer(client, emp_headers, city="Bordeaux").json()
    visible = create_offer(client, emp_headers, city="Bordeaux").json()

    client.post(f"/api/offers/{to_close['id']}/close", headers=emp_headers)

    worker_headers = register_and_login(client, "work20@example.com", "password123", "interimaire")
    client.put(
        "/api/filter",
        json={
            "cities": ["Bordeaux"],
            "min_hourly_wage": 13,
            "min_weekly_hours": 30,
            "max_weekly_hours": 40,
            "date_from": "2026-01-01",
            "date_to": "2026-12-31",
        },
        headers=worker_headers,
    )
    client.post(f"/api/offers/{already_swiped['id']}/swipe", json={"direction": "left"}, headers=worker_headers)

    stack = client.get("/api/stack", headers=worker_headers).json()
    ids = [o["id"] for o in stack]

    assert to_close["id"] not in ids
    assert out_of_filter["id"] not in ids
    assert already_swiped["id"] not in ids
    assert visible["id"] in ids


def test_empty_stack_returns_empty_list(client):
    worker_headers = register_and_login(client, "work21@example.com", "password123", "interimaire")
    stack = client.get("/api/stack", headers=worker_headers).json()
    assert stack == []
