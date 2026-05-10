from __future__ import annotations
from decimal import Decimal
from typing import Optional, TYPE_CHECKING
import enum
from sqlalchemy import ForeignKey, Numeric, Enum as SAEnum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session
from ecommerce_core.db import Base
from ecommerce_core.mixins import TimestampMixin
from ecommerce_core.utils.state_machine import StateMachine, InvalidTransition

ORDER_TRANSITIONS: dict[str, list[str]] = {
    "draft":      ["confirmed", "cancelled"],
    "confirmed":  ["processing", "cancelled"],
    "processing": ["shipped"],
    "shipped":    ["delivered"],
    "delivered":  ["refunded"],
    "cancelled":  [],
    "refunded":   [],
}

_order_sm = StateMachine(ORDER_TRANSITIONS)


class OrderState(str, enum.Enum):
    draft      = "draft"
    confirmed  = "confirmed"
    processing = "processing"
    shipped    = "shipped"
    delivered  = "delivered"
    cancelled  = "cancelled"
    refunded   = "refunded"


class SaleOrder(Base, TimestampMixin):
    """Confirmed customer order. Created from Cart.checkout()."""
    __tablename__ = "sale_order"

    id: Mapped[int] = mapped_column(primary_key=True)
    partner_id: Mapped[int] = mapped_column(ForeignKey("partner.id"), nullable=False)
    billing_address_id: Mapped[int] = mapped_column(ForeignKey("address.id"), nullable=False)
    shipping_address_id: Mapped[int] = mapped_column(ForeignKey("address.id"), nullable=False)
    shipping_method_id: Mapped[Optional[int]] = mapped_column(ForeignKey("shipping_method.id"), nullable=True)
    coupon_id: Mapped[Optional[int]] = mapped_column(ForeignKey("coupon.id"), nullable=True)
    state: Mapped[OrderState] = mapped_column(SAEnum(OrderState), default=OrderState.draft, nullable=False)
    tracking_number: Mapped[Optional[str]] = mapped_column(nullable=True)
    coupon_discount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"))
    shipping_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"))
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    partner: Mapped["Partner"] = relationship("Partner")
    billing_address: Mapped["Address"] = relationship("Address", foreign_keys=[billing_address_id])
    shipping_address: Mapped["Address"] = relationship("Address", foreign_keys=[shipping_address_id])
    shipping_method: Mapped[Optional["ShippingMethod"]] = relationship("ShippingMethod")
    coupon: Mapped[Optional["Coupon"]] = relationship("Coupon")
    lines: Mapped[list["SaleOrderLine"]] = relationship(
        "SaleOrderLine", back_populates="order", cascade="all, delete-orphan"
    )
    payment_transactions: Mapped[list["PaymentTransaction"]] = relationship(
        "PaymentTransaction", back_populates="order"
    )

    @property
    def subtotal(self) -> Decimal:
        return sum((line.subtotal for line in self.lines), Decimal("0"))

    @property
    def tax_total(self) -> Decimal:
        return sum((line.tax_amount for line in self.lines), Decimal("0"))

    @property
    def total(self) -> Decimal:
        return self.subtotal - self.coupon_discount + self.tax_total + self.shipping_amount

    def confirm(self) -> None:
        """Transition to confirmed. Raises ValueError if no lines."""
        if not self.lines:
            raise ValueError("Cannot confirm an order with no lines.")
        _order_sm.apply(self, "state", "confirmed")

    def cancel(self) -> None:
        """Transition to cancelled. Raises ValueError from shipped/delivered/refunded."""
        try:
            _order_sm.apply(self, "state", "cancelled")
        except InvalidTransition as e:
            raise ValueError(str(e)) from e

    def mark_shipped(self, tracking_number: str) -> None:
        """Transition to shipped and store tracking number."""
        _order_sm.apply(self, "state", "shipped")
        self.tracking_number = tracking_number

    def mark_delivered(self) -> None:
        """Transition to delivered."""
        _order_sm.apply(self, "state", "delivered")

    def apply_coupon(self, code: str, session: Session) -> None:
        """Validate coupon, apply discount, increment used_count atomically."""
        from ecommerce_core.models.coupon import Coupon
        coupon = session.query(Coupon).filter_by(code=code, active=True).first()
        if coupon is None:
            raise ValueError(f"Coupon '{code}' not found.")
        if not coupon.is_valid(self.subtotal):
            raise ValueError(f"Coupon '{code}' is not valid for this order.")
        self.coupon_id = coupon.id
        self.coupon_discount = coupon.compute_discount(self.subtotal)
        coupon.used_count += 1


class SaleOrderLine(Base):
    """Line item on a SaleOrder."""
    __tablename__ = "sale_order_line"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("sale_order.id"), nullable=False)
    variant_id: Mapped[int] = mapped_column(ForeignKey("product_variant.id"), nullable=False)
    qty: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"))
    tax_rate: Mapped[Decimal] = mapped_column(Numeric(5, 4), default=Decimal("0"))

    order: Mapped["SaleOrder"] = relationship("SaleOrder", back_populates="lines")
    variant: Mapped["ProductVariant"] = relationship("ProductVariant")

    @property
    def subtotal(self) -> Decimal:
        return Decimal(str(self.unit_price)) * Decimal(str(self.qty)) - Decimal(str(self.discount_amount))

    @property
    def tax_amount(self) -> Decimal:
        return Decimal(str(self.unit_price)) * Decimal(str(self.qty)) * Decimal(str(self.tax_rate))
