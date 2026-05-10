from __future__ import annotations
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ecommerce_core.db import Base
from ecommerce_core.mixins import TimestampMixin, ActiveMixin


class ProductCategory(Base, ActiveMixin):
    """Hierarchical product classification."""
    __tablename__ = "product_category"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("product_category.id"), nullable=True)

    parent: Mapped[Optional["ProductCategory"]] = relationship(
        "ProductCategory", remote_side="ProductCategory.id", back_populates="children"
    )
    children: Mapped[list["ProductCategory"]] = relationship(
        "ProductCategory", back_populates="parent"
    )

    @property
    def complete_name(self) -> str:
        """Return full path e.g. 'Electronics / Phones / Accessories'."""
        parts = [self.name]
        node = self.parent
        while node is not None:
            parts.insert(0, node.name)
            node = node.parent
        return " / ".join(parts)
