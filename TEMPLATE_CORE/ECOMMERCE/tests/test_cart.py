from decimal import Decimal
import pytest
from ecommerce_core.models import (
    ProductTemplate, ProductVariant, Cart, CartLine, CartStatus,
    Coupon, DiscountType,
)


def _variant(session, name, price, sku):
    tmpl = ProductTemplate(name=name, list_price=Decimal(price))
    v = ProductVariant(template=tmpl, sku=sku, default_price=Decimal(price))
    session.add_all([tmpl, v])
    session.flush()
    return v


def test_add_line_new(session):
    v = _variant(session, "Mug", "12.00", "MUG-CT-1")
    cart = Cart(session_token="cart-tok-1")
    session.add(cart)
    session.flush()
    cart.add_line(v, Decimal("2"))
    session.flush()
    assert len(cart.lines) == 1
    assert cart.lines[0].qty == Decimal("2")


def test_add_line_upsert(session):
    v = _variant(session, "Pen", "3.00", "PEN-CT-1")
    cart = Cart(session_token="cart-tok-2")
    session.add(cart)
    session.flush()
    cart.add_line(v, Decimal("1"))
    cart.add_line(v, Decimal("2"))
    assert len(cart.lines) == 1
    assert cart.lines[0].qty == Decimal("3")


def test_remove_line(session):
    v = _variant(session, "Cup", "5.00", "CUP-CT-1")
    cart = Cart(session_token="cart-tok-3")
    session.add(cart)
    session.flush()
    cart.add_line(v, Decimal("1"))
    cart.remove_line(v)
    assert len(cart.lines) == 0


def test_remove_line_noop(session):
    v = _variant(session, "Plate", "8.00", "PLT-CT-1")
    cart = Cart(session_token="cart-tok-4")
    session.add(cart)
    session.flush()
    cart.remove_line(v)  # should not raise
    assert len(cart.lines) == 0


def test_compute_totals_no_coupon(session):
    v = _variant(session, "Book", "20.00", "BOOK-CT-1")
    cart = Cart(session_token="cart-tok-5")
    session.add(cart)
    session.flush()
    cart.add_line(v, Decimal("3"))
    session.flush()
    totals = cart.compute_totals()
    assert totals["subtotal"] == Decimal("60.00")
    assert totals["discount"] == Decimal("0")
    assert totals["total"] == Decimal("60.00")


def test_compute_totals_with_coupon(session):
    v = _variant(session, "Bag", "50.00", "BAG-CT-1")
    c = Coupon(code="BAG10C", discount_type=DiscountType.percentage,
               discount_value=Decimal("10"))
    cart = Cart(session_token="cart-tok-6", coupon=c)
    session.add_all([cart, c])
    session.flush()
    cart.add_line(v, Decimal("1"))
    session.flush()
    totals = cart.compute_totals()
    assert totals["subtotal"] == Decimal("50.00")
    assert totals["discount"] == Decimal("5.00")
    assert totals["total"] == Decimal("45.00")


def test_cart_status_default(session):
    cart = Cart(session_token="cart-tok-7")
    session.add(cart)
    session.flush()
    assert cart.status == CartStatus.active


def test_checkout_raises_not_implemented(session):
    cart = Cart(session_token="cart-tok-8")
    session.add(cart)
    session.flush()
    with pytest.raises(NotImplementedError):
        cart.checkout(None, 1, 1)
