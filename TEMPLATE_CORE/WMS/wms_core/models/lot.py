from __future__ import annotations
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from wms_core.db import Base
from wms_core.mixins import TimestampMixin, NameMixin


class Lot(Base, TimestampMixin, NameMixin):
    """Lot / serial number tied to a product. Analogous to stock.lot in Odoo."""

    __tablename__ = "lot"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("product_product.id"), nullable=False)
    ref: Mapped[str | None] = mapped_column(nullable=True)
