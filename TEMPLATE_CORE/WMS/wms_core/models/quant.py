from __future__ import annotations
from decimal import Decimal
from sqlalchemy import ForeignKey, Numeric, UniqueConstraint, select
from sqlalchemy.orm import Mapped, mapped_column, Session
from wms_core.db import Base
from wms_core.mixins import TimestampMixin


class Quant(Base, TimestampMixin):
    """Materialized on-hand inventory. Analogous to stock.quant in Odoo.

    Single source of truth: (product, location, lot) → quantity.
    """

    __tablename__ = "quant"
    __table_args__ = (
        UniqueConstraint("product_id", "location_id", "lot_id", name="uq_quant_key"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("product_product.id"), nullable=False)
    location_id: Mapped[int] = mapped_column(ForeignKey("stock_location.id"), nullable=False)
    lot_id: Mapped[int | None] = mapped_column(ForeignKey("stock_lot.id"), nullable=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 6), default=Decimal("0"))
    reserved_quantity: Mapped[Decimal] = mapped_column(
        Numeric(18, 6), default=Decimal("0")
    )

    @classmethod
    def add_quantity(
        cls,
        session: Session,
        product_id: int,
        location_id: int,
        qty: Decimal,
        lot_id: int | None = None,
    ) -> Quant:
        """Atomically add qty to the matching quant, creating it if absent."""
        quant = session.execute(
            select(cls).where(
                cls.product_id == product_id,
                cls.location_id == location_id,
                cls.lot_id == lot_id,
            ).with_for_update()
        ).scalar_one_or_none()

        if quant is None:
            quant = cls(
                product_id=product_id,
                location_id=location_id,
                lot_id=lot_id,
                quantity=qty,
            )
            session.add(quant)
        else:
            quant.quantity += qty
        return quant

    @classmethod
    def get_available(
        cls,
        session: Session,
        product_id: int,
        location_id: int,
    ) -> Decimal:
        """Sum of (quantity - reserved_quantity) across all lots at this location."""
        rows = session.execute(
            select(cls).where(
                cls.product_id == product_id,
                cls.location_id == location_id,
            )
        ).scalars().all()
        return sum(
            (q.quantity - q.reserved_quantity for q in rows), Decimal("0")
        )
