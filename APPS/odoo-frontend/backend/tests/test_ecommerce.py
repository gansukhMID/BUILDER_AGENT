def test_products(client):
    r = client.get("/ecommerce/products")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_product_not_found(client):
    r = client.get("/ecommerce/products/99999")
    assert r.status_code == 404


def test_orders(client):
    r = client.get("/ecommerce/orders")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_order_not_found(client):
    r = client.get("/ecommerce/orders/99999")
    assert r.status_code == 404


def test_coupons(client):
    r = client.get("/ecommerce/coupons")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_stats(client):
    r = client.get("/stats")
    assert r.status_code == 200
    data = r.json()
    for key in ["users", "active_memberships", "warehouses", "open_pickings", "products", "open_orders"]:
        assert key in data
        assert isinstance(data[key], int)
