from decimal import Decimal
from datetime import date, timedelta
from ecommerce_core.models import Coupon, DiscountType


def test_is_valid_basic(session):
    c = Coupon(code="SAVE10", discount_type=DiscountType.percentage,
               discount_value=Decimal("10"))
    session.add(c)
    session.flush()
    assert c.is_valid(Decimal("100"))


def test_is_valid_inactive(session):
    c = Coupon(code="INACTIVE", discount_type=DiscountType.fixed,
               discount_value=Decimal("5"), active=False)
    session.add(c)
    session.flush()
    assert not c.is_valid(Decimal("100"))


def test_is_valid_expired(session):
    c = Coupon(code="EXPIRED", discount_type=DiscountType.fixed,
               discount_value=Decimal("5"),
               expiry_date=date.today() - timedelta(days=1))
    session.add(c)
    session.flush()
    assert not c.is_valid(Decimal("100"))


def test_is_valid_not_expired(session):
    c = Coupon(code="FRESH", discount_type=DiscountType.fixed,
               discount_value=Decimal("5"),
               expiry_date=date.today() + timedelta(days=7))
    session.add(c)
    session.flush()
    assert c.is_valid(Decimal("100"))


def test_is_valid_usage_limit_reached(session):
    c = Coupon(code="LIMIT2", discount_type=DiscountType.fixed,
               discount_value=Decimal("5"),
               usage_limit=2, used_count=2)
    session.add(c)
    session.flush()
    assert not c.is_valid(Decimal("100"))


def test_is_valid_unlimited(session):
    c = Coupon(code="UNLIMITED", discount_type=DiscountType.fixed,
               discount_value=Decimal("5"),
               usage_limit=None, used_count=999)
    session.add(c)
    session.flush()
    assert c.is_valid(Decimal("100"))


def test_is_valid_below_min_order(session):
    c = Coupon(code="MIN50C", discount_type=DiscountType.fixed,
               discount_value=Decimal("10"),
               min_order_amount=Decimal("50"))
    session.add(c)
    session.flush()
    assert not c.is_valid(Decimal("30"))
    assert c.is_valid(Decimal("50"))


def test_compute_discount_percentage(session):
    c = Coupon(code="PCT20C", discount_type=DiscountType.percentage,
               discount_value=Decimal("20"))
    session.add(c)
    session.flush()
    assert c.compute_discount(Decimal("100")) == Decimal("20")


def test_compute_discount_fixed(session):
    c = Coupon(code="FIX5C", discount_type=DiscountType.fixed,
               discount_value=Decimal("5"))
    session.add(c)
    session.flush()
    assert c.compute_discount(Decimal("100")) == Decimal("5")


def test_compute_discount_fixed_capped_at_subtotal(session):
    c = Coupon(code="BIGFIX", discount_type=DiscountType.fixed,
               discount_value=Decimal("50"))
    session.add(c)
    session.flush()
    assert c.compute_discount(Decimal("30")) == Decimal("30")
