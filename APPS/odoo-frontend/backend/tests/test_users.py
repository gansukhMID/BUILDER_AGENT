def test_list_users_empty(client):
    r = client.get("/users")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_get_user_not_found(client):
    r = client.get("/users/99999")
    assert r.status_code == 404


def test_get_activity_not_found(client):
    r = client.get("/users/99999/activity")
    assert r.status_code == 404


def test_get_orders_not_found(client):
    r = client.get("/users/99999/orders")
    assert r.status_code == 404


def test_user_workflow(client):
    # Register a user first
    r = client.post("/auth/register", json={"email": "u41@test.com", "password": "pass"})
    assert r.status_code == 201
    token = r.json()["access_token"]

    # Get current user from /auth/me
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    user_id = me.json()["id"]

    # List users — should include our user
    users = client.get("/users").json()
    assert any(u["id"] == user_id for u in users)

    # Get user detail
    detail = client.get(f"/users/{user_id}")
    assert detail.status_code == 200
    assert detail.json()["email"] == "u41@test.com"

    # Get activity (may be empty list)
    act = client.get(f"/users/{user_id}/activity")
    assert act.status_code == 200
    assert isinstance(act.json(), list)

    # Get orders (empty list)
    orders = client.get(f"/users/{user_id}/orders")
    assert orders.status_code == 200
    assert isinstance(orders.json(), list)
