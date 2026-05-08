import enum
from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column
from wms_core.db import Base
from wms_core.mixins import TimestampMixin, ActiveMixin, NameMixin


class TrackingType(str, enum.Enum):
    none = "none"
    lot = "lot"
    serial = "serial"


class Product(Base, TimestampMixin, ActiveMixin, NameMixin):
    """Storable item. Analogous to product.product in Odoo."""

    __tablename__ = "product_product"

    id: Mapped[int] = mapped_column(primary_key=True)
    tracking: Mapped[TrackingType] = mapped_column(
        Enum(TrackingType, name="tracking_type"), default=TrackingType.none
    )
    uom: Mapped[str] = mapped_column(nullable=False, default="unit")
    can_be_sold: Mapped[bool] = mapped_column(default=True)
    can_be_purchased: Mapped[bool] = mapped_column(default=True)
    sale_price: Mapped[float | None] = mapped_column(nullable=True)
    cost_price: Mapped[float | None] = mapped_column(nullable=True)
