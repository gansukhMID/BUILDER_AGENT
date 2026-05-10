from __future__ import annotations
from decimal import Decimal
from typing import Optional, TYPE_CHECKING
from sqlalchemy import Numeric
from sqlalchemy.orm import Mapped, mapped_column
from ecommerce_core.db import Base
from ecommerce_core.mixins import TimestampMixin, ActiveMixin

if TYPE_CHECKING:
    from ecommerce_core.models.order import SaleOrder


class ShippingMethod(Base, TimestampMixin, ActiveMixin):
    """Delivery method stub. Override estimate_price() for dynamic carrier rates."""
    __tablename__ = "shipping_method"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    carrier: Mapped[Optional[str]] = mapped_column(nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0"))

    def estimate_price(self, order: "SaleOrder") -> Decimal:
        """Return dynamic shipping price for order. Override in subclass; defaults to self.price."""
        raise NotImplementedError(
            "Override estimate_price(order) to implement carrier-based dynamic pricing."
        )
