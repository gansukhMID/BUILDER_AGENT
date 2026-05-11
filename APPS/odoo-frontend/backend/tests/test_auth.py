from __future__ import annotations


def test_register(client):
    r = client.post("/auth/register", json={"email": "test@example.com", "password": "secret123"})
    assert r.status_code == 201
    data = r.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_register_duplicate(client):
    client.post("/auth/register", json={"email": "dup@example.com", "password": "pass"})
    r = client.post("/auth/register", json={"email": "dup@example.com", "password": "pass"})
    assert r.status_code == 400


def test_login_success(client):
    client.post("/auth/register", json={"email": "login@example.com", "password": "mypass"})
    r = client.post("/auth/login", json={"email": "login@example.com", "password": "mypass"})
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_login_wrong_password(client):
    client.post("/auth/register", json={"email": "wp@example.com", "password": "correct"})
    r = client.post("/auth/login", json={"email": "wp@example.com", "password": "wrong"})
    assert r.status_code == 401


def test_me(client):
    r1 = client.post("/auth/register", json={"email": "me@example.com", "password": "pass"})
    token = r1.json()["access_token"]
    r2 = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200
    assert r2.json()["email"] == "me@example.com"


def test_me_no_token(client):
    r = client.get("/auth/me")
    assert r.status_code == 401
