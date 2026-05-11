from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel


class StoreVariantOut(BaseModel):
    id: int
    sku: Optional[str] = None
    default_price: float


class StoreProductOut(BaseModel):
    id: int
    name: str
    list_price: float
    variant_count: int = 0


class StoreProductDetailOut(BaseModel):
    id: int
    name: str
    list_price: float
    variants: List[StoreVariantOut]


class CouponValidateRequest(BaseModel):
    code: str


class CouponValidateOut(BaseModel):
    valid: bool
    discount_type: str
    discount_value: float


class CartLineIn(BaseModel):
    variant_id: int
    qty: float


class CreateOrderRequest(BaseModel):
    lines: List[CartLineIn]
    coupon_code: Optional[str] = None


class StoreOrderLineOut(BaseModel):
    id: int
    variant_id: Optional[int] = None
    qty: float
    unit_price: float
    subtotal: float


class StoreOrderOut(BaseModel):
    id: int
    reference: str
    state: str
    total_amount: float


class StoreOrderDetailOut(BaseModel):
    id: int
    reference: str
    state: str
    total_amount: float
    coupon_discount: float
    lines: List[StoreOrderLineOut]
