from __future__ import annotations
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from wms_core.db import Base
from wms_core.mixins import TimestampMixin, NameMixin


class Package(Base, TimestampMixin, NameMixin):
    """Packaging unit stub. Extend to add barcode, weight, package type."""

    __tablename__ = "package"

    id: Mapped[int] = mapped_column(primary_key=True)
    location_id: Mapped[int | None] = mapped_column(
        ForeignKey("stock_location.id"), nullable=True
    )
