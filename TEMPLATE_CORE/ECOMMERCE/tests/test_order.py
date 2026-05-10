from decimal import Decimal
import pytest
from ecommerce_core.models import (
    ProductTemplate, ProductVariant, Partner, Address, AddressType,
    SaleOrder, SaleOrderLine, OrderState, Coupon, DiscountType,
)


def _setup(session, email_suffix=""):
    tmpl = ProductTemplate(name="Item", list_price=Decimal("10"))
    v = ProductVariant(template=tmpl, sku=f"ITEM-ORD{email_suffix}", default_price=Decimal("10"))
    partner = Partner(name="Alice", email=f"alice{email_suffix}@test.com")
    billing = Address(partner=partner, address_type=AddressType.billing, city="NY")
    shipping = Address(partner=partner, address_type=AddressType.shipping, city="NY")
    session.add_all([tmpl, v, partner, billing, shipping])
    session.flush()
    order = SaleOrder(
        partner_id=partner.id,
        billing_address_id=billing.id,
        shipping_address_id=shipping.id,
    )
    session.add(order)
    session.flush()
    return order, v


def test_confirm_happy_path(session):
    order, v = _setup(session, "1")
    line = SaleOrderLine(order=order, variant=v, qty=Decimal("2"),
                         unit_price=Decimal("10"), tax_rate=Decimal("0.1"))
    session.add(line)
    session.flush()
    order.confirm()
    assert order.state == OrderState.confirmed


def test_confirm_no_lines_raises(session):
    order, _ = _setup(session, "2")
    with pytest.raises(ValueError, match="no lines"):
        order.confirm()


def test_cancel_from_draft(session):
    order, _ = _setup(session, "3")
    order.cancel()
    assert order.state == OrderState.cancelled


def test_cancel_from_shipped_raises(session):
    order, v = _setup(session, "4")
    line = SaleOrderLine(order=order, variant=v, qty=Decimal("1"), unit_price=Decimal("10"))
    session.add(line)
    session.flush()
    order.state = OrderState.shipped
    with pytest.raises(ValueError):
        order.cancel()


def test_mark_shipped(session):
    order, v = _setup(session, "5")
    line = SaleOrderLine(order=order, variant=v, qty=Decimal("1"), unit_price=Decimal("10"))
    session.add(line)
    session.flush()
    order.state = OrderState.processing
    order.mark_shipped("TRACK-123")
    assert order.state == OrderState.shipped
    assert order.tracking_number == "TRACK-123"


def test_mark_delivered(session):
    order, _ = _setup(session, "6")
    order.state = OrderState.shipped
    order.mark_delivered()
    assert order.state == OrderState.delivered


def test_computed_properties(session):
    order, v = _setup(session, "7")
    line = SaleOrderLine(order=order, variant=v, qty=Decimal("2"),
                         unit_price=Decimal("10"), tax_rate=Decimal("0.1"),
                         discount_amount=Decimal("1"))
    session.add(line)
    session.flush()
    assert line.subtotal == Decimal("19")       # 10*2 - 1
    assert line.tax_amount == Decimal("2.0")    # 10*2*0.1
    assert order.subtotal == Decimal("19")
    assert order.tax_total == Decimal("2.0")
    assert order.total == Decimal("21.0")


def test_apply_coupon(session):
    order, v = _setup(session, "8")
    line = SaleOrderLine(order=order, variant=v, qty=Decimal("2"), unit_price=Decimal("50"))
    coupon = Coupon(code="ORD20C", discount_type=DiscountType.percentage,
                    discount_value=Decimal("20"))
    session.add_all([line, coupon])
    session.flush()
    order.apply_coupon("ORD20C", session)
    assert order.coupon_id == coupon.id
    assert order.coupon_discount == Decimal("20")   # 20% of 100
    assert coupon.used_count == 1


def test_apply_coupon_invalid_code_raises(session):
    order, _ = _setup(session, "9")
    with pytest.raises(ValueError, match="not found"):
        order.apply_coupon("GHOST", session)


def test_default_billing_and_shipping(session):
    partner = Partner(name="Bob", email="bob.order@test.com")
    billing = Address(partner=partner, address_type=AddressType.billing, city="LA")
    shipping = Address(partner=partner, address_type=AddressType.shipping, city="SF")
    session.add_all([partner, billing, shipping])
    session.flush()
    assert partner.default_billing.city == "LA"
    assert partner.default_shipping.city == "SF"
