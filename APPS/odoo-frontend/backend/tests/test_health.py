def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_stats(client):
    r = client.get("/stats")
    assert r.status_code == 200
    data = r.json()
    assert "users" in data
    assert "warehouses" in data


def test_wms_health(client):
    r = client.get("/wms/health")
    assert r.status_code == 200


def test_ecommerce_health(client):
    r = client.get("/ecommerce/health")
    assert r.status_code == 200


def test_users_health(client):
    r = client.get("/users/health")
    assert r.status_code == 200
