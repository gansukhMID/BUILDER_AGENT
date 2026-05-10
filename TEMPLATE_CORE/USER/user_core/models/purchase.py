"""AbstractPurchase — payment record tied to an order or standalone."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Enum, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from user_core.db import Base
from user_core.enums import PurchaseStatus
from user_core.mixins import PrimaryKeyMixin, TimestampMixin


class AbstractPurchase(PrimaryKeyMixin, TimestampMixin, Base):
    """Abstract base for a purchase / payment record.

    Links a payment outcome to a user and optionally to an order. Supports
    standalone purchases (``order_id`` is nullable) for one-click buys,
    subscriptions, or tip payments that exist outside the order flow.

    ``external_ref`` stores the payment gateway transaction ID (Stripe charge
    ID, PayPal transaction ID, etc.) for reconciliation.

    Concrete subclass must:
    1. Set ``__tablename__``.
    2. Add FKs::

           user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
           order_id: Mapped[int | None] = mapped_column(
               ForeignKey("order.id"), nullable=True
           )
    """

    __abstract__ = True

    # Agents must add ForeignKey("user.id") in their concrete subclass
    user_id: Mapped[int] = mapped_column(nullable=False)
    # Agents must add ForeignKey("<order_table>.id") in their concrete subclass
    order_id: Mapped[int | None] = mapped_column(nullable=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    currency: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[PurchaseStatus] = mapped_column(
        Enum(PurchaseStatus, name="purchase_status"),
        default=PurchaseStatus.pending,
        nullable=False,
    )
    payment_method: Mapped[str | None] = mapped_column(nullable=True)
    external_ref: Mapped[str | None] = mapped_column(nullable=True)
    purchased_at: Mapped[datetime | None] = mapped_column(nullable=True)
