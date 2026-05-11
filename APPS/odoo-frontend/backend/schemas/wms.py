from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class WarehouseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    code: Optional[str]


class LocationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    complete_name: str
    location_type: str
    parent_id: Optional[int]


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    tracking: str
    active: bool


class LotOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    product_id: int


class QuantOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    product_id: int
    location_id: int
    lot_id: Optional[int]
    quantity: float


class QuantDetailOut(BaseModel):
    product_name: str
    location_name: str
    lot_name: Optional[str]
    quantity: float


class MoveOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    picking_id: Optional[int]
    product_id: int
    product_qty: float
    qty_done: float
    state: str


class PickingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    state: str
    picking_type_id: Optional[int]
    scheduled_date: Optional[str]
    origin: Optional[str]


class PickingDetailOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    state: str
    picking_type_id: Optional[int]
    scheduled_date: Optional[str]
    origin: Optional[str]
    moves: List[MoveOut]


class PickingTypeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    operation_type: str
    warehouse_id: Optional[int]
    sequence_prefix: Optional[str]
    active: bool


# ── Input schemas ─────────────────────────────────────────────────────────────

class WarehouseIn(BaseModel):
    name: str
    code: Optional[str] = None
    reception_steps: str = "one_step"
    delivery_steps: str = "one_step"


class WarehouseUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    reception_steps: Optional[str] = None
    delivery_steps: Optional[str] = None
    active: Optional[bool] = None


class LocationIn(BaseModel):
    name: str
    location_type: str = "internal"
    parent_id: Optional[int] = None
    code: Optional[str] = None


class LocationUpdate(BaseModel):
    name: Optional[str] = None
    location_type: Optional[str] = None
    parent_id: Optional[int] = None
    active: Optional[bool] = None


class WmsProductIn(BaseModel):
    name: str
    tracking: str = "none"
    uom: str = "unit"
    sale_price: Optional[float] = None
    cost_price: Optional[float] = None
    code: Optional[str] = None


class WmsProductUpdate(BaseModel):
    name: Optional[str] = None
    tracking: Optional[str] = None
    uom: Optional[str] = None
    sale_price: Optional[float] = None
    cost_price: Optional[float] = None
    active: Optional[bool] = None


class LotIn(BaseModel):
    name: str
    product_id: int
    ref: Optional[str] = None
    expiration_date: Optional[datetime] = None


class LotUpdate(BaseModel):
    ref: Optional[str] = None
    expiration_date: Optional[datetime] = None
    active: Optional[bool] = None


class PickingTypeIn(BaseModel):
    name: str
    operation_type: str
    warehouse_id: Optional[int] = None
    default_location_src_id: Optional[int] = None
    default_location_dest_id: Optional[int] = None
    sequence_prefix: Optional[str] = None


class PickingTypeUpdate(BaseModel):
    name: Optional[str] = None
    default_location_src_id: Optional[int] = None
    default_location_dest_id: Optional[int] = None
    active: Optional[bool] = None


class PickingIn(BaseModel):
    name: str
    picking_type_id: Optional[int] = None
    location_src_id: Optional[int] = None
    location_dest_id: Optional[int] = None
    origin: Optional[str] = None
    scheduled_date: Optional[datetime] = None


class PickingUpdate(BaseModel):
    origin: Optional[str] = None
    scheduled_date: Optional[datetime] = None


class MoveIn(BaseModel):
    product_id: int
    location_src_id: int
    location_dest_id: int
    product_qty: Decimal
    picking_id: Optional[int] = None


class MoveUpdate(BaseModel):
    product_qty: Optional[Decimal] = None
