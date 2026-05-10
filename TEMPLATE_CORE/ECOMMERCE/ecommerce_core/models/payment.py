from __future__ import annotations
from decimal import Decimal
from typing import Optional
import enum
from sqlalchemy import ForeignKey, Numeric, Enum as SAEnum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ecommerce_core.db import Base
from ecommerce_core.mixins import TimestampMixin
from ecommerce_core.utils.state_machine import StateMachine, InvalidTransition

PAYMENT_TRANSITIONS: dict[str, list[str]] = {
    "draft":      ["pending"],
    "pending":    ["authorized", "failed"],
    "authorized": ["captured", "failed"],
    "captured":   ["refunded"],
    "failed":     [],
    "refunded":   [],
}

_payment_sm = StateMachine(PAYMENT_TRANSITIONS)


class PaymentState(str, enum.Enum):
    draft      = "draft"
    pending    = "pending"
    authorized = "authorized"
    captured   = "captured"
    failed     = "failed"
    refunded   = "refunded"


class PaymentTransaction(Base, TimestampMixin):
    """Payment attempt linked to a SaleOrder."""
    __tablename__ = "payment_transaction"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("sale_order.id"), nullable=False)
    provider: Mapped[str] = mapped_column(nullable=False)
    provider_ref: Mapped[Optional[str]] = mapped_column(nullable=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(default="USD")
    state: Mapped[PaymentState] = mapped_column(SAEnum(PaymentState), default=PaymentState.draft, nullable=False)
    refunded_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"))
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    order: Mapped["SaleOrder"] = relationship("SaleOrder", back_populates="payment_transactions")

    def authorize(self, provider_ref: Optional[str] = None) -> None:
        """Transition draft→pending→authorized and record provider reference."""
        try:
            _payment_sm.apply(self, "state", "authorized")
        except InvalidTransition:
            _payment_sm.apply(self, "state", "pending")
            _payment_sm.apply(self, "state", "authorized")
        if provider_ref:
            self.provider_ref = provider_ref

    def capture(self) -> None:
        """Transition authorized→captured."""
        try:
            _payment_sm.apply(self, "state", "captured")
        except InvalidTransition as e:
            raise ValueError(str(e)) from e

    def fail(self, error_message: Optional[str] = None) -> None:
        """Transition to failed and record error."""
        try:
            _payment_sm.apply(self, "state", "failed")
        except InvalidTransition as e:
            raise ValueError(str(e)) from e
        if error_message:
            self.error_message = error_message

    def refund(self, amount: Decimal) -> None:
        """Transition captured→refunded. Validates amount <= self.amount."""
        if amount > self.amount:
            raise ValueError(
                f"Refund amount {amount} exceeds transaction amount {self.amount}."
            )
        try:
            _payment_sm.apply(self, "state", "refunded")
        except InvalidTransition as e:
            raise ValueError(str(e)) from e
        self.refunded_amount = amount
