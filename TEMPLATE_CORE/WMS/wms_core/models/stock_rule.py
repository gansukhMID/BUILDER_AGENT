from __future__ import annotations
import enum
from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from wms_core.db import Base
from wms_core.mixins import TimestampMixin, ActiveMixin, NameMixin


class RuleAction(str, enum.Enum):
    pull = "pull"
    push = "push"
    pull_push = "pull_push"


class StockRule(Base, TimestampMixin, ActiveMixin, NameMixin):
    """Procurement / replenishment rule. Analogous to stock.rule in Odoo."""

    __tablename__ = "stock_rule"

    id: Mapped[int] = mapped_column(primary_key=True)
    action: Mapped[RuleAction] = mapped_column(
        Enum(RuleAction, name="rule_action"), nullable=False
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
    delay: Mapped[int] = mapped_column(default=0)
