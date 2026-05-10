"""AbstractOrder and AbstractOrderLine — order header and line-item models."""
from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Enum, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from user_core.db import Base
from user_core.enums import OrderState
from user_core.mixins import PrimaryKeyMixin, TimestampMixin

import datetime as _dt


class AbstractOrder(PrimaryKeyMixin, TimestampMixin, Base):
    """Abstract base for an order placed by a user.

    Carries a state machine covering the full fulfilment lifecycle.
    ``cancel()`` and ``confirm()`` are stubs — override them to add
    business rules (stock reservation, email triggers, etc.).

    Concrete subclass must:
    1. Set ``__tablename__``.
    2. Add FK: ``user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))``.

    ``total_amount`` stores the order total as a high-precision decimal.
    ``product_ref`` on lines is a plain string — agents add the FK to their
    product table in the ``AbstractOrderLine`` subclass.
    """

    __abstract__ = True

    # Agents must add ForeignKey("user.id") in their concrete subclass
    user_id: Mapped[int] = mapped_column(nullable=False)
    reference: Mapped[str] = mapped_column(nullable=False)
    state: Mapped[OrderState] = mapped_column(
        Enum(OrderState, name="order_state"), default=OrderState.draft, nullable=False
    )
    currency: Mapped[str] = mapped_column(default="USD", nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 4), default=Decimal("0.0000")
    )
    placed_at: Mapped[_dt.datetime | None] = mapped_column(nullable=True)
    notes: Mapped[str | None] = mapped_column(nullable=True)

    def confirm(self) -> None:
        """Transition the order from ``placed`` to ``confirmed``.

        **Stub** — override to add inventory reservation, notification, etc.
        """
        self.state = OrderState.confirmed

    def cancel(self) -> None:
        """Transition the order to ``cancelled``.

        **Stub** — override to release reservations, trigger refunds, etc.
        """
        self.state = OrderState.cancelled


class AbstractOrderLine(PrimaryKeyMixin, TimestampMixin, Base):
    """Abstract base for a line item within an order.

    ``product_ref`` is a plain string (SKU, UUID, or external ID). Agents who
    have a local products table should override it with a FK column::

        product_ref: Mapped[str] = mapped_column(ForeignKey("product.sku"))

    ``line_total`` is stored (not computed at query time) so historical totals
    survive price changes.

    Concrete subclass must:
    1. Set ``__tablename__``.
    2. Add FK: ``order_id: Mapped[int] = mapped_column(ForeignKey("order.id"))``.
    """

    __abstract__ = True

    # Agents must add ForeignKey("<order_table>.id") in their concrete subclass
    order_id: Mapped[int] = mapped_column(nullable=False)
    product_ref: Mapped[str] = mapped_column(nullable=False)
    product_name: Mapped[str] = mapped_column(nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    # Stored snapshot: qty × unit_price at time of order
    line_total: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
