from __future__ import annotations
from decimal import Decimal
from typing import Optional
from sqlalchemy import ForeignKey, Numeric, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ecommerce_core.db import Base
from ecommerce_core.mixins import TimestampMixin, ActiveMixin
from ecommerce_core.models.attribute import ProductVariantAttributeLine, ProductAttributeValue


class ProductTemplate(Base, TimestampMixin, ActiveMixin):
    """Merchandising unit — the item as shown in the catalog."""
    __tablename__ = "product_template"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[Optional[str]] = mapped_column(nullable=True)
    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("product_category.id"), nullable=True)
    list_price: Mapped[Decimal] = mapped_column(Numeric(12, 4), default=Decimal("0"))
    image_url: Mapped[Optional[str]] = mapped_column(nullable=True)

    category: Mapped[Optional["ProductCategory"]] = relationship("ProductCategory")
    variants: Mapped[list["ProductVariant"]] = relationship(
        "ProductVariant", back_populates="template", cascade="all, delete-orphan"
    )


class ProductVariant(Base, TimestampMixin, ActiveMixin):
    """Purchasable SKU — a specific combination of template + attribute values."""
    __tablename__ = "product_variant"
    __table_args__ = (UniqueConstraint("sku", name="uq_product_variant_sku"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    template_id: Mapped[int] = mapped_column(ForeignKey("product_template.id"), nullable=False)
    sku: Mapped[Optional[str]] = mapped_column(nullable=True, index=True)
    barcode: Mapped[Optional[str]] = mapped_column(nullable=True)
    default_price: Mapped[Decimal] = mapped_column(Numeric(12, 4), default=Decimal("0"))

    template: Mapped["ProductTemplate"] = relationship("ProductTemplate", back_populates="variants")
    attribute_values: Mapped[list["ProductAttributeValue"]] = relationship(
        "ProductAttributeValue",
        secondary=ProductVariantAttributeLine,
    )

    @property
    def display_name(self) -> str:
        """Return 'Template Name — Val1 / Val2' from linked attribute values."""
        vals = " / ".join(av.name for av in self.attribute_values)
        return f"{self.template.name} — {vals}" if vals else self.template.name
