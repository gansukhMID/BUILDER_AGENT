from __future__ import annotations
import enum
from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from wms_core.db import Base
from wms_core.mixins import TimestampMixin, ActiveMixin, NameMixin


class LocationType(str, enum.Enum):
    internal = "internal"
    view = "view"
    customer = "customer"
    supplier = "supplier"
    transit = "transit"
    inventory = "inventory"
    production = "production"


class Location(Base, TimestampMixin, ActiveMixin, NameMixin):
    """Hierarchical storage location. Analogous to stock.location in Odoo."""

    __tablename__ = "stock_location"

    id: Mapped[int] = mapped_column(primary_key=True)
    location_type: Mapped[LocationType] = mapped_column(
        Enum(LocationType, name="location_type"), default=LocationType.internal
    )
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("stock_location.id"), nullable=True
    )

    parent: Mapped[Location | None] = relationship(
        "Location", remote_side="Location.id", back_populates="children"
    )
    children: Mapped[list[Location]] = relationship(
        "Location", back_populates="parent"
    )

    @property
    def complete_name(self) -> str:
        """Full path, e.g. WH/Stock/Shelf-A/Bin-01."""
        parts = [self.name]
        node = self.parent
        while node is not None:
            parts.append(node.name)
            node = node.parent
        return "/".join(reversed(parts))

    def is_ancestor_of(self, location: Location) -> bool:
        """Return True if self is an ancestor of location."""
        node = location.parent
        while node is not None:
            if node.id == self.id:
                return True
            node = node.parent
        return False
