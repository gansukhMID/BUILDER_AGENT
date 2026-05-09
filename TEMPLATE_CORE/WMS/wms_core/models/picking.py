from __future__ import annotations
import enum
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from wms_core.db import Base
from wms_core.mixins import TimestampMixin, ActiveMixin
from wms_core.utils.state_machine import transition

if TYPE_CHECKING:
    from wms_core.models.move import Move


class PickingState(str, enum.Enum):
    draft = "draft"
    confirmed = "confirmed"
    in_progress = "in_progress"
    done = "done"
    cancelled = "cancelled"


class Picking(Base, TimestampMixin, ActiveMixin):
    """Transfer operation header. Analogous to stock.picking in Odoo."""

    __tablename__ = "picking"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    state: Mapped[PickingState] = mapped_column(
        Enum(PickingState, name="picking_state"), default=PickingState.draft
    )
    picking_type_id: Mapped[int | None] = mapped_column(
        ForeignKey("stock_picking_type.id"), nullable=True
    )
    location_src_id: Mapped[int | None] = mapped_column(
        ForeignKey("stock_location.id"), nullable=True
    )
    location_dest_id: Mapped[int | None] = mapped_column(
        ForeignKey("stock_location.id"), nullable=True
    )
    scheduled_date: Mapped[datetime | None] = mapped_column(nullable=True)

    moves: Mapped[list[Move]] = relationship("Move", back_populates="picking")

    def confirm(self) -> None:
        self.state = PickingState(transition(self.state.value, "confirmed"))

    def validate(self) -> None:
        """Move quants and mark done. Override in subclasses to add quant logic."""
        self.state = PickingState(transition(self.state.value, "done"))

    def cancel(self) -> None:
        self.state = PickingState(transition(self.state.value, "cancelled"))
