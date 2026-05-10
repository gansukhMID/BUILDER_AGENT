from __future__ import annotations
from decimal import Decimal
from typing import Optional, TYPE_CHECKING
import enum
from sqlalchemy import ForeignKey, Numeric, Enum as SAEnum, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session
from ecommerce_core.db import Base
from ecommerce_core.mixins import TimestampMixin


class CartStatus(str, enum.Enum):
    active = "active"
    abandoned = "abandoned"
    checked_out = "checked_out"


class Cart(Base, TimestampMixin):
    """Active shopping session. partner_id is nullable for guest checkout."""
    __tablename__ = "cart"

    id: Mapped[int] = mapped_column(primary_key=True)
    partner_id: Mapped[Optional[int]] = mapped_column(ForeignKey("partner.id"), nullable=True)
    session_token: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    pricelist_id: Mapped[Optional[int]] = mapped_column(ForeignKey("pricelist.id"), nullable=True)
    coupon_id: Mapped[Optional[int]] = mapped_column(ForeignKey("coupon.id"), nullable=True)
    shipping_method_id: Mapped[Optional[int]] = mapped_column(ForeignKey("shipping_method.id"), nullable=True)
    status: Mapped[CartStatus] = mapped_column(SAEnum(CartStatus), default=CartStatus.active, nullable=False)

    partner: Mapped[Optional["Partner"]] = relationship("Partner")
    pricelist: Mapped[Optional["Pricelist"]] = relationship("Pricelist")
    coupon: Mapped[Optional["Coupon"]] = relationship("Coupon")
    lines: Mapped[list["CartLine"]] = relationship(
        "CartLine", back_populates="cart", cascade="all, delete-orphan"
    )
    shipping_method: Mapped[Optional["ShippingMethod"]] = relationship("ShippingMethod")

    def add_line(self, variant: "ProductVariant", qty: Decimal) -> "CartLine":
        """Upsert a CartLine — adds qty if line for this variant already exists."""
        for line in self.lines:
            if line.variant_id == variant.id:
                line.qty += qty
                return line
        new_line = CartLine(variant_id=variant.id, qty=qty)
        self.lines.append(new_line)
        return new_line

    def remove_line(self, variant: "ProductVariant") -> None:
        """Remove the CartLine for the given variant. No-op if not present."""
        self.lines = [l for l in self.lines if l.variant_id != variant.id]

    def compute_totals(self) -> dict:
        """Return subtotal, discount, tax_amount, shipping_estimate, total as Decimal."""
        subtotal = sum(
            (Decimal(str(line.variant.default_price)) * Decimal(str(line.qty)))
            for line in self.lines
            if line.variant is not None
        )
        discount = Decimal("0")
        if self.coupon is not None:
            discount = self.coupon.compute_discount(subtotal)
        # Tax is on order lines; cart uses 0 as a stub
        tax_amount = Decimal("0")
        shipping_estimate = Decimal("0")
        if self.shipping_method is not None and self.shipping_method.price is not None:
            shipping_estimate = Decimal(str(self.shipping_method.price))
        total = subtotal - discount + tax_amount + shipping_estimate
        return {
            "subtotal": subtotal,
            "discount": discount,
            "tax_amount": tax_amount,
            "shipping_estimate": shipping_estimate,
            "total": total,
        }

    def checkout(
        self,
        shipping_method_id: Optional[int],
        billing_address_id: int,
        shipping_address_id: int,
    ) -> None:
        """Convert cart to a SaleOrder. Implement after wiring SaleOrder (task #26)."""
        raise NotImplementedError(
            "Cart.checkout() must be implemented by the agent after importing SaleOrder. "
            "Create a SaleOrder from this cart's lines, mark status=checked_out."
        )


class CartLine(Base):
    """A single product variant + qty within a cart."""
    __tablename__ = "cart_line"
    __table_args__ = (UniqueConstraint("cart_id", "variant_id", name="uq_cart_line_cart_variant"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    cart_id: Mapped[int] = mapped_column(ForeignKey("cart.id"), nullable=False)
    variant_id: Mapped[int] = mapped_column(ForeignKey("product_variant.id"), nullable=False)
    qty: Mapped[Decimal] = mapped_column(Numeric(10, 4), default=Decimal("1"))

    cart: Mapped["Cart"] = relationship("Cart", back_populates="lines")
    variant: Mapped[Optional["ProductVariant"]] = relationship("ProductVariant")
