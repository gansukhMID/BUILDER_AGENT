"""Tests for WMS API routers."""


def test_warehouses(client):
    r = client.get("/wms/warehouses")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_locations(client):
    r = client.get("/wms/locations")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_products(client):
    r = client.get("/wms/products")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_inventory(client):
    r = client.get("/wms/inventory")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_pickings(client):
    r = client.get("/wms/pickings")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_picking_not_found(client):
    r = client.get("/wms/pickings/99999")
    assert r.status_code == 404
