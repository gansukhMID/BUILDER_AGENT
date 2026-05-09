from __future__ import annotations
import enum
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from wms_core.db import Base
from wms_core.mixins import TimestampMixin, ActiveMixin, NameMixin
from wms_core.utils.state_machine import StateMachine, InvalidTransition, PICKING_TRANSITIONS

if TYPE_CHECKING:
    from wms_core.models.move import Move
    from wms_core.models.location import Location
    from wms_core.models.picking_type import PickingType


class PickingState(str, enum.Enum):
    draft = "draft"
    confirmed = "confirmed"
    in_progress = "in_progress"
    done = "done"
    cancelled = "cancelled"


_fsm = StateMachine(PICKING_TRANSITIONS)


class Picking(Base, TimestampMixin, ActiveMixin, NameMixin):
    """Transfer operation header. Analogous to stock.picking in Odoo."""

    __tablename__ = "stock_picking"

    id: Mapped[int] = mapped_column(primary_key=True)
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
    partner_id: Mapped[int | None] = mapped_column(nullable=True)
    origin: Mapped[str | None] = mapped_column(nullable=True)
    scheduled_date: Mapped[datetime | None] = mapped_column(nullable=True)

    moves: Mapped[list[Move]] = relationship("Move", back_populates="picking")
    picking_type: Mapped[PickingType | None] = relationship(
        "PickingType", foreign_keys=[picking_type_id]
    )
    src_location: Mapped[Location | None] = relationship(
        "Location", foreign_keys=[location_src_id]
    )
    dest_location: Mapped[Location | None] = relationship(
        "Location", foreign_keys=[location_dest_id]
    )

    def confirm(self) -> None:
        _fsm.apply(self, "state", PickingState.confirmed)

    def start(self) -> None:
        _fsm.apply(self, "state", PickingState.in_progress)

    def validate(self) -> None:
        """Move quants and mark done. Override in subclasses to add quant logic."""
        _fsm.apply(self, "state", PickingState.done)

    def cancel(self) -> None:
        _fsm.apply(self, "state", PickingState.cancelled)
