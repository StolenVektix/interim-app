"""EX-11, EX-12, EX-13."""

from conftest import create_offer, register_and_login


def test_no_filter_returns_all_open_offers_both_cities_sorted_desc(client):
    emp_headers = register_and_login(client, "emp10@example.com", "password123", "employeur")
    o1 = create_offer(client, emp_headers, city="Bordeaux").json()
    o2 = create_offer(client, emp_headers, city="Paris").json()

    worker_headers = register_and_login(client, "work10@example.com", "password123", "interimaire")
    stack = client.get("/api/stack", headers=worker_headers).json()

    ids = [o["id"] for o in stack]
    assert o1["id"] in ids and o2["id"] in ids
    assert ids.index(o2["id"]) < ids.index(o1["id"])  # plus récent en premier


def test_setting_filter_recomputes_stack_without_resetting_rejections(client):
    emp_headers = register_and_login(client, "emp11@example.com", "password123", "employeur")
    matching = create_offer(client, emp_headers, city="Bordeaux", hourly_wage=13.5, weekly_hours=35).json()
    non_matching = create_offer(client, emp_headers, city="Bordeaux", hourly_wage=11, weekly_hours=35).json()

    worker_headers = register_and_login(client, "work11@example.com", "password123", "interimaire")
    client.post(f"/api/offers/{matching['id']}/swipe", json={"direction": "left"}, headers=worker_headers)

    filter_payload = {
        "cities": ["Bordeaux"],
        "min_hourly_wage": 13,
        "min_weekly_hours": 30,
        "max_weekly_hours": 40,
        "date_from": "2026-01-01",
        "date_to": "2026-12-31",
    }
    resp = client.put("/api/filter", json=filter_payload, headers=worker_headers)
    assert resp.status_code == 200

    stack = client.get("/api/stack", headers=worker_headers).json()
    ids = [o["id"] for o in stack]
    assert matching["id"] not in ids  # déjà rejetée : le changement de filtre ne la fait pas réapparaître
    assert non_matching["id"] not in ids  # hors filtre (11 €/h < 13 €/h minimum)


def test_date_filter_uses_overlap_not_containment(client):
    emp_headers = register_and_login(client, "emp12@example.com", "password123", "employeur")
    overlapping = create_offer(
        client, emp_headers, city="Bordeaux", start_date="2026-08-15", end_date="2026-09-15"
    ).json()
    outside = create_offer(
        client, emp_headers, city="Bordeaux", start_date="2026-11-01", end_date="2026-11-30"
    ).json()

    worker_headers = register_and_login(client, "work12@example.com", "password123", "interimaire")
    client.put(
        "/api/filter",
        json={
            "cities": ["Bordeaux"],
            "min_hourly_wage": 0,
            "min_weekly_hours": 1,
            "max_weekly_hours": 48,
            "date_from": "2026-09-01",
            "date_to": "2026-09-30",
        },
        headers=worker_headers,
    )

    stack = client.get("/api/stack", headers=worker_headers).json()
    ids = [o["id"] for o in stack]
    assert overlapping["id"] in ids  # chevauche la fenêtre (15 août-15 sept vs fenêtre 1-30 sept)
    assert outside["id"] not in ids  # aucun chevauchement (novembre vs septembre)
