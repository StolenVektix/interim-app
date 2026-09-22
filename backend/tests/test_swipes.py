"""EX-15 à EX-19, EX-21, et le scénario de référence de bout en bout."""

from conftest import create_offer, register_and_login


def test_swipe_left_persists_rejection_and_removes_from_stack(client):
    emp = register_and_login(client, "emp30@example.com", "password123", "employeur")
    offer = create_offer(client, emp).json()
    worker = register_and_login(client, "work30@example.com", "password123", "interimaire")

    resp = client.post(f"/api/offers/{offer['id']}/swipe", json={"direction": "left"}, headers=worker)
    assert resp.status_code == 200
    assert resp.json()["result"] == "rejected"

    stack = client.get("/api/stack", headers=worker).json()
    assert all(o["id"] != offer["id"] for o in stack)


def test_swipe_right_creates_pending_application_and_returns_offer_detail(client):
    emp = register_and_login(client, "emp31@example.com", "password123", "employeur")
    offer = create_offer(client, emp).json()
    worker = register_and_login(client, "work31@example.com", "password123", "interimaire")

    resp = client.post(f"/api/offers/{offer['id']}/swipe", json={"direction": "right"}, headers=worker)
    assert resp.status_code == 200
    body = resp.json()
    assert body["result"] == "applied"
    assert body["offer"]["id"] == offer["id"]

    applications = client.get(f"/api/offers/{offer['id']}/applications", headers=emp).json()
    assert len(applications) == 1
    assert applications[0]["status"] == "pending"


def test_swipe_right_on_offer_closed_meanwhile_returns_409_and_creates_nothing(client):
    emp = register_and_login(client, "emp32@example.com", "password123", "employeur")
    offer = create_offer(client, emp).json()
    worker = register_and_login(client, "work32@example.com", "password123", "interimaire")

    client.post(f"/api/offers/{offer['id']}/close", headers=emp)

    resp = client.post(f"/api/offers/{offer['id']}/swipe", json={"direction": "right"}, headers=worker)
    assert resp.status_code == 409
    assert resp.json()["code"] == "OFFER_CLOSED"

    applications = client.get(f"/api/offers/{offer['id']}/applications", headers=emp).json()
    assert applications == []


def test_replaying_a_swipe_is_idempotent(client):
    emp = register_and_login(client, "emp33@example.com", "password123", "employeur")
    offer = create_offer(client, emp).json()
    worker = register_and_login(client, "work33@example.com", "password123", "interimaire")

    first = client.post(f"/api/offers/{offer['id']}/swipe", json={"direction": "right"}, headers=worker)
    second = client.post(f"/api/offers/{offer['id']}/swipe", json={"direction": "right"}, headers=worker)

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["result"] == "applied"

    applications = client.get(f"/api/offers/{offer['id']}/applications", headers=emp).json()
    assert len(applications) == 1  # EX-21: pas de doublon


def test_reference_scenario_end_to_end(client):
    emp = register_and_login(client, "emp_ref@example.com", "password123", "employeur")
    offer1 = create_offer(
        client,
        emp,
        title="Préparateur de commandes",
        hourly_wage=13.5,
        weekly_hours=35,
        start_date="2026-09-01",
        end_date="2026-09-30",
        city="Bordeaux",
    ).json()

    worker = register_and_login(client, "work_ref@example.com", "password123", "interimaire")
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
        headers=worker,
    )

    stack = client.get("/api/stack", headers=worker).json()
    assert offer1["id"] in [o["id"] for o in stack]

    client.post(f"/api/offers/{offer1['id']}/swipe", json={"direction": "left"}, headers=worker)

    # "rafraîchit, se déconnecte, se reconnecte" -> nouvelle session, même exclusion persistée en base
    worker = register_and_login(client, "work_ref@example.com", "password123", "interimaire")
    stack_after_relogin = client.get("/api/stack", headers=worker).json()
    assert offer1["id"] not in [o["id"] for o in stack_after_relogin]

    offer2 = create_offer(client, emp, title="Manutentionnaire", hourly_wage=11, weekly_hours=35, city="Bordeaux").json()
    stack_with_offer2 = client.get("/api/stack", headers=worker).json()
    assert offer2["id"] not in [o["id"] for o in stack_with_offer2]

    offer3 = create_offer(client, emp, title="Cariste", hourly_wage=14, weekly_hours=35, city="Bordeaux").json()
    stack_with_offer3 = client.get("/api/stack", headers=worker).json()
    assert offer3["id"] in [o["id"] for o in stack_with_offer3]

    swipe_resp = client.post(f"/api/offers/{offer3['id']}/swipe", json={"direction": "right"}, headers=worker)
    assert swipe_resp.json()["result"] == "applied"

    applications = client.get(f"/api/offers/{offer3['id']}/applications", headers=emp).json()
    assert len(applications) == 1
