from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from wms_core.db import Base
from wms_core.mixins import TimestampMixin, ActiveMixin, NameMixin

if TYPE_CHECKING:
    from wms_core.models.product import Product


class Lot(Base, TimestampMixin, ActiveMixin, NameMixin):
    """Lot / serial number tied to a product. Analogous to stock.lot in Odoo."""

    __tablename__ = "stock_lot"
    __table_args__ = (
        UniqueConstraint("name", "product_id", name="uq_lot_name_product"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("product_product.id"), nullable=False)
    ref: Mapped[str | None] = mapped_column(nullable=True)
    expiration_date: Mapped[datetime | None] = mapped_column(nullable=True)

    product: Mapped[Product] = relationship("Product", back_populates="lots")
