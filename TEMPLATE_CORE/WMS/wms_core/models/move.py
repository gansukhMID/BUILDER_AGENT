from __future__ import annotations
import enum
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import Enum, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session
from wms_core.db import Base
from wms_core.mixins import TimestampMixin

if TYPE_CHECKING:
    from wms_core.models.picking import Picking
    from wms_core.models.location import Location
    from wms_core.models.product import Product
    from wms_core.models.lot import Lot


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
    product_qty: Mapped[Decimal] = mapped_column(Numeric(18, 6), default=Decimal("0"))
    qty_done: Mapped[Decimal] = mapped_column(Numeric(18, 6), default=Decimal("0"))
    state: Mapped[MoveState] = mapped_column(
        Enum(MoveState, name="move_state"), default=MoveState.draft
    )

    picking: Mapped[Picking | None] = relationship("Picking", back_populates="moves")
    src_location: Mapped[Location] = relationship(
        "Location", foreign_keys=[location_src_id]
    )
    dest_location: Mapped[Location] = relationship(
        "Location", foreign_keys=[location_dest_id]
    )
    product: Mapped[Product] = relationship("Product")
    lot: Mapped[Lot | None] = relationship("Lot")

    def validate(self, session: Session) -> None:
        """Set state=done and move quants from src to dest."""
        from wms_core.models.quant import Quant
        Quant.add_quantity(session, self.product_id, self.location_src_id, -self.product_qty, self.lot_id)
        Quant.add_quantity(session, self.product_id, self.location_dest_id, self.product_qty, self.lot_id)
        self.state = MoveState.done
        self.qty_done = self.product_qty
