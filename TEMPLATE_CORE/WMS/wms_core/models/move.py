from __future__ import annotations
import enum
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import Enum, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from wms_core.db import Base
from wms_core.mixins import TimestampMixin

if TYPE_CHECKING:
    from wms_core.models.picking import Picking


class MoveState(str, enum.Enum):
    draft = "draft"
    confirmed = "confirmed"
    assigned = "assigned"
    done = "done"
    cancelled = "cancelled"


class Move(Base, TimestampMixin):
    """Planned movement of product between locations. Analogous to stock.move in Odoo."""

    __tablename__ = "stock_move"

    id: Mapped[int] = mapped_column(primary_key=True)
    picking_id: Mapped[int | None] = mapped_column(
        ForeignKey("stock_picking.id"), nullable=True
    )
    product_id: Mapped[int] = mapped_column(ForeignKey("product_product.id"), nullable=False)
    lot_id: Mapped[int | None] = mapped_column(ForeignKey("stock_lot.id"), nullable=True)
    location_src_id: Mapped[int] = mapped_column(
        ForeignKey("stock_location.id"), nullable=False
    )
    location_dest_id: Mapped[int] = mapped_column(
        ForeignKey("stock_location.id"), nullable=False
    )
    product_qty: Mapped[Decimal] = mapped_column(
        Numeric(18, 6), default=Decimal("0")
    )
    qty_done: Mapped[Decimal] = mapped_column(Numeric(18, 6), default=Decimal("0"))
    state: Mapped[MoveState] = mapped_column(
        Enum(MoveState, name="move_state"), default=MoveState.draft
    )

    picking: Mapped[Picking | None] = relationship("Picking", back_populates="moves")

    def validate(self) -> None:
        """Apply quant changes. Override or call from Picking.validate() subclass."""
        self.state = MoveState.done
