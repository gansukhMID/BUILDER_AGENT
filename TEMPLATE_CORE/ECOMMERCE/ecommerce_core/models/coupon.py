from __future__ import annotations
from datetime import date
from decimal import Decimal
from typing import Optional
import enum
from sqlalchemy import Enum as SAEnum, Numeric, Integer, Date, Boolean, Index
from sqlalchemy.orm import Mapped, mapped_column
from ecommerce_core.db import Base
from ecommerce_core.mixins import TimestampMixin, ActiveMixin


class DiscountType(str, enum.Enum):
    percentage = "percentage"
    fixed = "fixed"


class Coupon(Base, TimestampMixin, ActiveMixin):
    """Discount code with usage rules and expiry."""
    __tablename__ = "coupon"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    discount_type: Mapped[DiscountType] = mapped_column(SAEnum(DiscountType), nullable=False)
    discount_value: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    min_order_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"))
    usage_limit: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # None = unlimited
    used_count: Mapped[int] = mapped_column(Integer, default=0)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    def is_valid(self, order_amount: Decimal) -> bool:
        """Return True if coupon can be applied to an order of given amount."""
        if not self.active:
            return False
        if self.expiry_date is not None and self.expiry_date < date.today():
            return False
        if self.usage_limit is not None and self.used_count >= self.usage_limit:
            return False
        if order_amount < self.min_order_amount:
            return False
        return True

    def compute_discount(self, subtotal: Decimal) -> Decimal:
        """Return discount amount to subtract from subtotal."""
        if self.discount_type == DiscountType.percentage:
            return subtotal * (self.discount_value / Decimal("100"))
        # fixed — cap at subtotal
        return min(self.discount_value, subtotal)
