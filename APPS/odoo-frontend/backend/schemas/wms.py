from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from typing import Optional, List


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
