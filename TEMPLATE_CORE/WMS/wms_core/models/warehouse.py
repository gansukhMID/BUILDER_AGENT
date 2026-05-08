from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from wms_core.db import Base
from wms_core.mixins import TimestampMixin, ActiveMixin, NameMixin

if TYPE_CHECKING:
    from wms_core.models.location import Location


class Warehouse(Base, TimestampMixin, ActiveMixin, NameMixin):
    """Top-level facility. Analogous to stock.warehouse in Odoo."""

    __tablename__ = "warehouse"

    id: Mapped[int] = mapped_column(primary_key=True)
    short_name: Mapped[str] = mapped_column(nullable=False)
    # Nullable — set after location records for this warehouse are created
    lot_stock_id: Mapped[int | None] = mapped_column(
        ForeignKey("stock_location.id"), nullable=True
    )

    lot_stock_location: Mapped[Location | None] = relationship(
        "Location", foreign_keys=[lot_stock_id]
    )
