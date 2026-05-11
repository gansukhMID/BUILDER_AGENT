from __future__ import annotations
from typing import Optional, List
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
