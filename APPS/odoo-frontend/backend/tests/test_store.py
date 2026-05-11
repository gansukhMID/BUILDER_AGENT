"""Tests for the /store router."""
from __future__ import annotations

import random
import pytest
from decimal import Decimal

from ecommerce_core.models.product import ProductTemplate, ProductVariant
from ecommerce_core.models.coupon import Coupon, DiscountType
from ecommerce_core.models.partner import Partner, Address, AddressType


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _unique_sku() -> str:
    return f"TW-{random.randint(100000, 999999)}"


def _create_product(db) -> tuple[ProductTemplate, ProductVariant]:
    tmpl = ProductTemplate(name="Test Widget", list_price=Decimal("50.00"))
    db.add(tmpl)
    db.flush()
    variant = ProductVariant(template_id=tmpl.id, sku=_unique_sku(), default_price=Decimal("50.00"))
    db.add(variant)
    db.flush()
    return tmpl, variant


def _create_coupon(db, code: str = "TEST10") -> Coupon:
    coupon = Coupon(
        code=code,
        discount_type=DiscountType.percentage,
        discount_value=Decimal("10"),
        min_order_amount=Decimal("0"),
        usage_limit=None,
        used_count=0,
    )
    db.add(coupon)
    db.flush()
    return coupon


def _register_and_login(client) -> str:
    """Register a user and return the bearer token."""
    import random
    email = f"storeuser{random.randint(10000, 99999)}@example.com"
    resp = client.post("/auth/register", json={"email": email, "password": "testpassword"})
    assert resp.status_code == 201
    return resp.json()["access_token"]


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Public — products
# ---------------------------------------------------------------------------


def test_store_list_products_public(client):
    r = client.get("/store/products")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_store_get_product_not_found(client):
    r = client.get("/store/products/99999")
    assert r.status_code == 404


def test_store_get_product_with_variants(client):
    from tests.conftest import TestSessionLocal

    db = TestSessionLocal()
    try:
        tmpl, variant = _create_product(db)
        db.commit()
        product_id = tmpl.id
    finally:
        db.close()

    r = client.get(f"/store/products/{product_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == product_id
    assert data["name"] == "Test Widget"
    assert "variants" in data
    assert len(data["variants"]) >= 1


# ---------------------------------------------------------------------------
# Public — coupon validation
# ---------------------------------------------------------------------------


def test_store_validate_coupon_found(client):
    from tests.conftest import TestSessionLocal

    db = TestSessionLocal()
    try:
        _create_coupon(db, code="STORETEST10")
        db.commit()
    finally:
        db.close()

    r = client.post("/store/coupons/validate", json={"code": "STORETEST10"})
    assert r.status_code == 200
    data = r.json()
    assert data["valid"] is True
    assert data["discount_type"] == "percentage"
    assert data["discount_value"] == 10.0


def test_store_validate_coupon_not_found(client):
    r = client.post("/store/coupons/validate", json={"code": "NOTEXIST"})
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# Auth-protected — orders require JWT
# ---------------------------------------------------------------------------


def test_store_create_order_requires_auth(client):
    r = client.post("/store/orders", json={"lines": [{"variant_id": 1, "qty": 1}]})
    assert r.status_code == 401


def test_store_list_orders_requires_auth(client):
    r = client.get("/store/orders")
    assert r.status_code == 401


def test_store_get_order_requires_auth(client):
    r = client.get("/store/orders/1")
    assert r.status_code == 401


# ---------------------------------------------------------------------------
# Auth-protected — order create & list
# ---------------------------------------------------------------------------


def test_store_create_and_list_orders(client):
    from tests.conftest import TestSessionLocal

    db = TestSessionLocal()
    try:
        tmpl, variant = _create_product(db)
        db.commit()
        variant_id = variant.id
    finally:
        db.close()

    token = _register_and_login(client)
    headers = _auth_headers(token)

    # Create order
    resp = client.post(
        "/store/orders",
        json={"lines": [{"variant_id": variant_id, "qty": 2}]},
        headers=headers,
    )
    assert resp.status_code == 201
    order_data = resp.json()
    assert "id" in order_data
    assert order_data["reference"].startswith("SO-")
    assert order_data["state"] == "draft"
    assert order_data["total_amount"] == 100.0  # 2 x 50.00

    # List orders — should contain the new order
    resp2 = client.get("/store/orders", headers=headers)
    assert resp2.status_code == 200
    orders = resp2.json()
    assert isinstance(orders, list)
    assert any(o["id"] == order_data["id"] for o in orders)


def test_store_create_order_with_coupon(client):
    from tests.conftest import TestSessionLocal

    db = TestSessionLocal()
    try:
        tmpl, variant = _create_product(db)
        _create_coupon(db, code="STORECOUPON")
        db.commit()
        variant_id = variant.id
    finally:
        db.close()

    token = _register_and_login(client)
    headers = _auth_headers(token)

    resp = client.post(
        "/store/orders",
        json={"lines": [{"variant_id": variant_id, "qty": 1}], "coupon_code": "STORECOUPON"},
        headers=headers,
    )
    assert resp.status_code == 201
    # 10% off 50.00 = 5.00 discount, total = 45.00
    assert resp.json()["total_amount"] == pytest.approx(45.0, abs=0.01)


def test_store_create_order_invalid_variant(client):
    token = _register_and_login(client)
    headers = _auth_headers(token)

    resp = client.post(
        "/store/orders",
        json={"lines": [{"variant_id": 999999, "qty": 1}]},
        headers=headers,
    )
    assert resp.status_code == 404


def test_store_create_order_invalid_coupon(client):
    from tests.conftest import TestSessionLocal

    db = TestSessionLocal()
    try:
        tmpl, variant = _create_product(db)
        db.commit()
        variant_id = variant.id
    finally:
        db.close()

    token = _register_and_login(client)
    headers = _auth_headers(token)

    resp = client.post(
        "/store/orders",
        json={"lines": [{"variant_id": variant_id, "qty": 1}], "coupon_code": "BADCOUPON"},
        headers=headers,
    )
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# Auth-protected — order detail & 403 for wrong user
# ---------------------------------------------------------------------------


def test_store_get_order_detail(client):
    from tests.conftest import TestSessionLocal

    db = TestSessionLocal()
    try:
        tmpl, variant = _create_product(db)
        db.commit()
        variant_id = variant.id
    finally:
        db.close()

    token = _register_and_login(client)
    headers = _auth_headers(token)

    create_resp = client.post(
        "/store/orders",
        json={"lines": [{"variant_id": variant_id, "qty": 1}]},
        headers=headers,
    )
    assert create_resp.status_code == 201
    order_id = create_resp.json()["id"]

    detail_resp = client.get(f"/store/orders/{order_id}", headers=headers)
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert detail["id"] == order_id
    assert "lines" in detail
    assert "coupon_discount" in detail


def test_store_get_order_403_for_other_user(client):
    from tests.conftest import TestSessionLocal

    db = TestSessionLocal()
    try:
        tmpl, variant = _create_product(db)
        db.commit()
        variant_id = variant.id
    finally:
        db.close()

    # User A creates an order
    token_a = _register_and_login(client)
    create_resp = client.post(
        "/store/orders",
        json={"lines": [{"variant_id": variant_id, "qty": 1}]},
        headers=_auth_headers(token_a),
    )
    assert create_resp.status_code == 201
    order_id = create_resp.json()["id"]

    # User B tries to access User A's order
    token_b = _register_and_login(client)
    detail_resp = client.get(f"/store/orders/{order_id}", headers=_auth_headers(token_b))
    assert detail_resp.status_code == 403


def test_store_get_order_not_found(client):
    token = _register_and_login(client)
    r = client.get("/store/orders/999999", headers=_auth_headers(token))
    assert r.status_code == 404
