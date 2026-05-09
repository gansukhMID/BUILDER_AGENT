from __future__ import annotations
import enum
from typing import TYPE_CHECKING
from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from wms_core.db import Base
from wms_core.mixins import TimestampMixin, ActiveMixin, NameMixin

if TYPE_CHECKING:
    from wms_core.models.location import Location
    from wms_core.models.picking_type import PickingType
    from wms_core.models.warehouse import Warehouse


class RuleAction(str, enum.Enum):
    pull = "pull"
    push = "push"
    pull_push = "pull_push"


class ProcureMethod(str, enum.Enum):
    make_to_stock = "make_to_stock"
    make_to_order = "make_to_order"


class RuleAuto(str, enum.Enum):
    manual = "manual"
    transparent = "transparent"


class StockRule(Base, TimestampMixin, ActiveMixin, NameMixin):
    """Procurement / replenishment rule. Analogous to stock.rule in Odoo."""

    __tablename__ = "stock_rule"

    id: Mapped[int] = mapped_column(primary_key=True)
    action: Mapped[RuleAction] = mapped_column(
        Enum(RuleAction, name="rule_action"), nullable=False
    )
    procure_method: Mapped[ProcureMethod] = mapped_column(
        Enum(ProcureMethod, name="procure_method"), default=ProcureMethod.make_to_stock
    )
    auto: Mapped[RuleAuto] = mapped_column(
        Enum(RuleAuto, name="rule_auto"), default=RuleAuto.manual
    )
    location_src_id: Mapped[int | None] = mapped_column(
        ForeignKey("stock_location.id"), nullable=True
    )
    location_dest_id: Mapped[int] = mapped_column(
        ForeignKey("stock_location.id"), nullable=False
    )
    picking_type_id: Mapped[int | None] = mapped_column(
        ForeignKey("stock_picking_type.id"), nullable=True
    )
    warehouse_id: Mapped[int | None] = mapped_column(
        ForeignKey("stock_warehouse.id"), nullable=True
    )
    delay: Mapped[int] = mapped_column(default=0)

    src_location: Mapped[Location | None] = relationship(
        "Location", foreign_keys=[location_src_id]
    )
    dest_location: Mapped[Location] = relationship(
        "Location", foreign_keys=[location_dest_id]
    )
    picking_type: Mapped[PickingType | None] = relationship(
        "PickingType", foreign_keys=[picking_type_id]
    )
    warehouse: Mapped[Warehouse | None] = relationship(
        "Warehouse", foreign_keys=[warehouse_id]
    )
