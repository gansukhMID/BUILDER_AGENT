from __future__ import annotations
import enum
from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from wms_core.db import Base
from wms_core.mixins import TimestampMixin, ActiveMixin, NameMixin


class OperationType(str, enum.Enum):
    incoming = "incoming"
    outgoing = "outgoing"
    internal = "internal"


class PickingType(Base, TimestampMixin, ActiveMixin, NameMixin):
    """Operation type definition. Analogous to stock.picking.type in Odoo."""

    __tablename__ = "picking_type"

    id: Mapped[int] = mapped_column(primary_key=True)
    operation_type: Mapped[OperationType] = mapped_column(
        Enum(OperationType, name="operation_type"), nullable=False
    )
    warehouse_id: Mapped[int | None] = mapped_column(
        ForeignKey("warehouse.id"), nullable=True
    )
    default_location_src_id: Mapped[int | None] = mapped_column(
        ForeignKey("stock_location.id"), nullable=True
    )
    default_location_dest_id: Mapped[int | None] = mapped_column(
        ForeignKey("stock_location.id"), nullable=True
    )
