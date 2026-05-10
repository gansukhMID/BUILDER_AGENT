from decimal import Decimal
import pytest
from ecommerce_core.models import (
    ProductTemplate, ProductVariant, Partner, Address, AddressType,
    SaleOrder, PaymentTransaction, PaymentState,
)


def _order(session, suffix=""):
    partner = Partner(name="Pay User", email=f"pay{suffix}@test.com")
    billing = Address(partner=partner, address_type=AddressType.billing)
    shipping = Address(partner=partner, address_type=AddressType.shipping)
    session.add_all([partner, billing, shipping])
    session.flush()
    order = SaleOrder(partner_id=partner.id,
                      billing_address_id=billing.id,
                      shipping_address_id=shipping.id)
    session.add(order)
    session.flush()
    return order


def _txn(session, amount="100.00", suffix=""):
    order = _order(session, suffix)
    tx = PaymentTransaction(order_id=order.id, provider="stripe",
                            amount=Decimal(amount))
    session.add(tx)
    session.flush()
    return tx


def test_initial_state_is_draft(session):
    tx = _txn(session, suffix="a")
    assert tx.state == PaymentState.draft


def test_authorize_transitions_to_authorized(session):
    tx = _txn(session, suffix="b")
    tx.authorize(provider_ref="pi_abc")
    assert tx.state == PaymentState.authorized
    assert tx.provider_ref == "pi_abc"


def test_capture_after_authorize(session):
    tx = _txn(session, suffix="c")
    tx.authorize()
    tx.capture()
    assert tx.state == PaymentState.captured


def test_happy_path_draft_to_captured(session):
    tx = _txn(session, suffix="d")
    tx.authorize(provider_ref="pi_happy")
    tx.capture()
    assert tx.state == PaymentState.captured


def test_fail_from_pending(session):
    tx = _txn(session, suffix="e")
    tx.state = PaymentState.pending
    tx.fail(error_message="card declined")
    assert tx.state == PaymentState.failed
    assert tx.error_message == "card declined"


def test_fail_from_authorized(session):
    tx = _txn(session, suffix="f")
    tx.authorize()
    tx.fail()
    assert tx.state == PaymentState.failed


def test_refund_happy(session):
    tx = _txn(session, "50.00", suffix="g")
    tx.state = PaymentState.captured
    tx.refund(Decimal("30.00"))
    assert tx.state == PaymentState.refunded
    assert tx.refunded_amount == Decimal("30.00")


def test_refund_full_amount(session):
    tx = _txn(session, "75.00", suffix="h")
    tx.state = PaymentState.captured
    tx.refund(Decimal("75.00"))
    assert tx.state == PaymentState.refunded


def test_refund_exceeds_amount_raises(session):
    tx = _txn(session, "50.00", suffix="i")
    tx.state = PaymentState.captured
    with pytest.raises(ValueError, match="exceeds"):
        tx.refund(Decimal("99.00"))


def test_capture_from_draft_raises(session):
    tx = _txn(session, suffix="j")
    with pytest.raises((ValueError, Exception)):
        tx.capture()  # draft → captured is invalid
