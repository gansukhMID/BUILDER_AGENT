from __future__ import annotations
from typing import Optional, List
from datetime import date
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class ProductVariantOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    sku: Optional[str]
    default_price: Optional[float]


class ProductTemplateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    list_price: float
    variant_count: int = 0


class ProductDetailOut(BaseModel):
    id: int
    name: str
    list_price: float
    variants: List[ProductVariantOut]


class OrderLineOut(BaseModel):
    id: int
    quantity: float      # mapped from SaleOrderLine.qty
    unit_price: float
    line_total: float    # mapped from SaleOrderLine.subtotal property


class OrderOut(BaseModel):
    id: int
    reference: str       # constructed as "SO-{id}"
    state: str
    total_amount: float  # from SaleOrder.total property
    currency: str        # default "USD"


class OrderDetailOut(BaseModel):
    id: int
    reference: str
    state: str
    total_amount: float
    lines: List[OrderLineOut]


class CouponOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    code: str
    discount_type: str
    discount_value: float


class StatsOut(BaseModel):
    users: int
    active_memberships: int
    warehouses: int
    open_pickings: int
    products: int
    open_orders: int


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    parent_id: Optional[int]


class ShippingMethodOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    carrier: Optional[str]
    price: float
    active: bool


# ── Input schemas ─────────────────────────────────────────────────────────────

class CategoryIn(BaseModel):
    name: str
    parent_id: Optional[int] = None


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[int] = None


class ProductTemplateIn(BaseModel):
    name: str
    list_price: Decimal = Decimal("0")
    description: Optional[str] = None
    category_id: Optional[int] = None
    image_url: Optional[str] = None


class ProductTemplateUpdate(BaseModel):
    name: Optional[str] = None
    list_price: Optional[Decimal] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    image_url: Optional[str] = None
    active: Optional[bool] = None


class ProductVariantIn(BaseModel):
    sku: Optional[str] = None
    barcode: Optional[str] = None
    default_price: Decimal = Decimal("0")


class ProductVariantUpdate(BaseModel):
    sku: Optional[str] = None
    barcode: Optional[str] = None
    default_price: Optional[Decimal] = None
    active: Optional[bool] = None


class CouponIn(BaseModel):
    code: str
    discount_type: str
    discount_value: Decimal
    min_order_amount: Decimal = Decimal("0")
    usage_limit: Optional[int] = None
    expiry_date: Optional[date] = None


class CouponUpdate(BaseModel):
    discount_value: Optional[Decimal] = None
    min_order_amount: Optional[Decimal] = None
    usage_limit: Optional[int] = None
    expiry_date: Optional[date] = None
    active: Optional[bool] = None


class ShippingMethodIn(BaseModel):
    name: str
    carrier: Optional[str] = None
    price: Decimal = Decimal("0")


class ShippingMethodUpdate(BaseModel):
    name: Optional[str] = None
    carrier: Optional[str] = None
    price: Optional[Decimal] = None
    active: Optional[bool] = None
