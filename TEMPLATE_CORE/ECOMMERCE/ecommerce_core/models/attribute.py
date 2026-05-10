from __future__ import annotations
from sqlalchemy import ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ecommerce_core.db import Base
from ecommerce_core.mixins import ActiveMixin


# Association table: ProductVariant ↔ ProductAttributeValue
ProductVariantAttributeLine = Table(
    "product_variant_attribute_line",
    Base.metadata,
    Column("variant_id", ForeignKey("product_variant.id", ondelete="CASCADE"), primary_key=True),
    Column("attribute_value_id", ForeignKey("product_attribute_value.id", ondelete="CASCADE"), primary_key=True),
)


class ProductAttribute(Base, ActiveMixin):
    """Dimension definition e.g. Size, Color."""
    __tablename__ = "product_attribute"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)

    values: Mapped[list["ProductAttributeValue"]] = relationship(
        "ProductAttributeValue", back_populates="attribute", cascade="all, delete-orphan"
    )


class ProductAttributeValue(Base, ActiveMixin):
    """Dimension option e.g. Red, XL."""
    __tablename__ = "product_attribute_value"

    id: Mapped[int] = mapped_column(primary_key=True)
    attribute_id: Mapped[int] = mapped_column(ForeignKey("product_attribute.id"), nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)

    attribute: Mapped["ProductAttribute"] = relationship("ProductAttribute", back_populates="values")
