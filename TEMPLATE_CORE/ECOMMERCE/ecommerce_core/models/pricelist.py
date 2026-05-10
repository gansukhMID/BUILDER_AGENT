from __future__ import annotations
from decimal import Decimal
from typing import Optional, TYPE_CHECKING
import enum
from sqlalchemy import ForeignKey, Numeric, Enum as SAEnum, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ecommerce_core.db import Base
from ecommerce_core.mixins import TimestampMixin, ActiveMixin, CurrencyMixin

if TYPE_CHECKING:
    from ecommerce_core.models.product import ProductVariant


class AppliedOn(str, enum.Enum):
    all = "all"
    category = "category"
    product = "product"
    variant = "variant"


class ComputePrice(str, enum.Enum):
    fixed = "fixed"
    percentage = "percentage"
    formula = "formula"


# Specificity order for matching (higher = more specific)
_SPECIFICITY = {
    AppliedOn.all: 0,
    AppliedOn.category: 1,
    AppliedOn.product: 2,
    AppliedOn.variant: 3,
}


class Pricelist(Base, TimestampMixin, ActiveMixin, CurrencyMixin):
    """Named pricelist with currency and ordered pricing rules."""
    __tablename__ = "pricelist"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)

    items: Mapped[list["PricelistItem"]] = relationship(
        "PricelistItem", back_populates="pricelist", cascade="all, delete-orphan",
        order_by="PricelistItem.priority.desc()"
    )

    def get_price(self, variant: "ProductVariant", qty: Decimal) -> Decimal:
        """Return effective unit price for variant at qty. Falls back to variant.default_price."""
        from ecommerce_core.utils.pricing import evaluate_pricelist
        return evaluate_pricelist(self, variant, qty)


class PricelistItem(Base):
    """A single pricing rule within a pricelist."""
    __tablename__ = "pricelist_item"

    id: Mapped[int] = mapped_column(primary_key=True)
    pricelist_id: Mapped[int] = mapped_column(ForeignKey("pricelist.id"), nullable=False)
    applied_on: Mapped[AppliedOn] = mapped_column(SAEnum(AppliedOn), nullable=False, default=AppliedOn.all)
    product_variant_id: Mapped[Optional[int]] = mapped_column(ForeignKey("product_variant.id"), nullable=True)
    product_template_id: Mapped[Optional[int]] = mapped_column(ForeignKey("product_template.id"), nullable=True)
    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("product_category.id"), nullable=True)
    compute_price: Mapped[ComputePrice] = mapped_column(SAEnum(ComputePrice), nullable=False, default=ComputePrice.fixed)
    fixed_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)
    price_discount: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    min_quantity: Mapped[Decimal] = mapped_column(Numeric(10, 4), default=Decimal("0"))
    priority: Mapped[int] = mapped_column(Integer, default=0)

    pricelist: Mapped["Pricelist"] = relationship("Pricelist", back_populates="items")

    @property
    def specificity(self) -> int:
        return _SPECIFICITY.get(self.applied_on, 0)
