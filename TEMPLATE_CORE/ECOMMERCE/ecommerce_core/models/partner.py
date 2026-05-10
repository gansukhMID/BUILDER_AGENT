from __future__ import annotations
from typing import Optional
import enum
from sqlalchemy import ForeignKey, Enum as SAEnum, Index, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ecommerce_core.db import Base
from ecommerce_core.mixins import TimestampMixin, ActiveMixin


class AddressType(str, enum.Enum):
    shipping = "shipping"
    billing = "billing"


class Partner(Base, TimestampMixin, ActiveMixin):
    """Customer or company contact record."""
    __tablename__ = "partner"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[Optional[str]] = mapped_column(nullable=True, unique=True, index=True)
    phone: Mapped[Optional[str]] = mapped_column(nullable=True)
    company_name: Mapped[Optional[str]] = mapped_column(nullable=True)
    is_company: Mapped[bool] = mapped_column(Boolean, default=False)

    addresses: Mapped[list["Address"]] = relationship(
        "Address", back_populates="partner", cascade="all, delete-orphan"
    )

    @property
    def default_shipping(self) -> Optional["Address"]:
        """Return first shipping address or None."""
        for addr in self.addresses:
            if addr.address_type == AddressType.shipping:
                return addr
        return None

    @property
    def default_billing(self) -> Optional["Address"]:
        """Return first billing address or None."""
        for addr in self.addresses:
            if addr.address_type == AddressType.billing:
                return addr
        return None


class Address(Base, TimestampMixin):
    """Shipping or billing address linked to a Partner."""
    __tablename__ = "address"

    id: Mapped[int] = mapped_column(primary_key=True)
    partner_id: Mapped[int] = mapped_column(ForeignKey("partner.id"), nullable=False)
    address_type: Mapped[AddressType] = mapped_column(SAEnum(AddressType), nullable=False)
    street: Mapped[Optional[str]] = mapped_column(nullable=True)
    street2: Mapped[Optional[str]] = mapped_column(nullable=True)
    city: Mapped[Optional[str]] = mapped_column(nullable=True)
    state: Mapped[Optional[str]] = mapped_column(nullable=True)
    country: Mapped[Optional[str]] = mapped_column(nullable=True)
    zip_code: Mapped[Optional[str]] = mapped_column(nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    partner: Mapped["Partner"] = relationship("Partner", back_populates="addresses")
