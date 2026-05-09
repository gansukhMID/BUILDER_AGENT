from __future__ import annotations
import enum
from typing import TYPE_CHECKING
from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from wms_core.db import Base
from wms_core.mixins import TimestampMixin, ActiveMixin, NameMixin

if TYPE_CHECKING:
    from wms_core.models.location import Location
    from wms_core.models.warehouse import Warehouse


class OperationType(str, enum.Enum):
    incoming = "incoming"
    outgoing = "outgoing"
    internal = "internal"


class PickingType(Base, TimestampMixin, ActiveMixin, NameMixin):
    """Operation type definition. Analogous to stock.picking.type in Odoo."""

    __tablename__ = "stock_picking_type"

    id: Mapped[int] = mapped_column(primary_key=True)
    # `code` in Odoo maps to operation_type here; validated at app level via OperationType enum
    operation_type: Mapped[OperationType] = mapped_column(
        Enum(OperationType, name="operation_type"), nullable=False
    )
    warehouse_id: Mapped[int | None] = mapped_column(
        ForeignKey("stock_warehouse.id"), nullable=True
    )
    default_location_src_id: Mapped[int | None] = mapped_column(
        ForeignKey("stock_location.id"), nullable=True
    )
    default_location_dest_id: Mapped[int | None] = mapped_column(
        ForeignKey("stock_location.id"), nullable=True
    )
    sequence_prefix: Mapped[str | None] = mapped_column(nullable=True)
    count_picking_ready: Mapped[int] = mapped_column(default=0)

    warehouse: Mapped[Warehouse | None] = relationship(
        "Warehouse", foreign_keys=[warehouse_id]
    )
    default_src_location: Mapped[Location | None] = relationship(
        "Location", foreign_keys=[default_location_src_id]
    )
    default_dest_location: Mapped[Location | None] = relationship(
        "Location", foreign_keys=[default_location_dest_id]
    )
