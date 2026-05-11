from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from wms_core.models.warehouse import Warehouse
from wms_core.models.location import Location, LocationType
from wms_core.models.product import Product, TrackingType
from wms_core.models.lot import Lot
from wms_core.models.picking_type import PickingType, OperationType
from wms_core.models.picking import Picking
from wms_core.models.move import Move


# ── Warehouse ────────────────────────────────────────────────────────────────

def create_warehouse(
    session: Session,
    *,
    name: str,
    code: Optional[str] = None,
    reception_steps: str = "one_step",
    delivery_steps: str = "one_step",
) -> Warehouse:
    wh = Warehouse(
        name=name,
        code=code,
        reception_steps=reception_steps,
        delivery_steps=delivery_steps,
    )
    session.add(wh)
    session.flush()
    return wh


def update_warehouse(
    session: Session,
    warehouse_id: int,
    *,
    name: Optional[str] = None,
    code: Optional[str] = None,
    reception_steps: Optional[str] = None,
    delivery_steps: Optional[str] = None,
    active: Optional[bool] = None,
) -> Warehouse:
    wh = session.get(Warehouse, warehouse_id)
    if wh is None:
        raise ValueError(f"Warehouse {warehouse_id} not found")
    if name is not None:
        wh.name = name
    if code is not None:
        wh.code = code
    if reception_steps is not None:
        wh.reception_steps = reception_steps
    if delivery_steps is not None:
        wh.delivery_steps = delivery_steps
    if active is not None:
        wh.active = active
    session.flush()
    return wh


# ── Location ─────────────────────────────────────────────────────────────────

def create_location(
    session: Session,
    *,
    name: str,
    location_type: LocationType = LocationType.internal,
    parent_id: Optional[int] = None,
    code: Optional[str] = None,
) -> Location:
    loc = Location(
        name=name,
        location_type=location_type,
        parent_id=parent_id,
        code=code,
    )
    session.add(loc)
    session.flush()
    return loc


def update_location(
    session: Session,
    location_id: int,
    *,
    name: Optional[str] = None,
    location_type: Optional[LocationType] = None,
    parent_id: Optional[int] = None,
    active: Optional[bool] = None,
) -> Location:
    loc = session.get(Location, location_id)
    if loc is None:
        raise ValueError(f"Location {location_id} not found")
    if name is not None:
        loc.name = name
    if location_type is not None:
        loc.location_type = location_type
    if parent_id is not None:
        loc.parent_id = parent_id
    if active is not None:
        loc.active = active
    session.flush()
    return loc


# ── Product ───────────────────────────────────────────────────────────────────

def create_product(
    session: Session,
    *,
    name: str,
    tracking: TrackingType = TrackingType.none,
    uom: str = "unit",
    sale_price: Optional[float] = None,
    cost_price: Optional[float] = None,
    code: Optional[str] = None,
) -> Product:
    product = Product(
        name=name,
        tracking=tracking,
        uom=uom,
        sale_price=sale_price,
        cost_price=cost_price,
        code=code,
    )
    session.add(product)
    session.flush()
    return product


def update_product(
    session: Session,
    product_id: int,
    *,
    name: Optional[str] = None,
    tracking: Optional[TrackingType] = None,
    uom: Optional[str] = None,
    sale_price: Optional[float] = None,
    cost_price: Optional[float] = None,
    active: Optional[bool] = None,
) -> Product:
    product = session.get(Product, product_id)
    if product is None:
        raise ValueError(f"Product {product_id} not found")
    if name is not None:
        product.name = name
    if tracking is not None:
        product.tracking = tracking
    if uom is not None:
        product.uom = uom
    if sale_price is not None:
        product.sale_price = sale_price
    if cost_price is not None:
        product.cost_price = cost_price
    if active is not None:
        product.active = active
    session.flush()
    return product


# ── Lot ───────────────────────────────────────────────────────────────────────

def create_lot(
    session: Session,
    *,
    name: str,
    product_id: int,
    ref: Optional[str] = None,
    expiration_date: Optional[datetime] = None,
) -> Lot:
    lot = Lot(
        name=name,
        product_id=product_id,
        ref=ref,
        expiration_date=expiration_date,
    )
    session.add(lot)
    session.flush()
    return lot


def update_lot(
    session: Session,
    lot_id: int,
    *,
    ref: Optional[str] = None,
    expiration_date: Optional[datetime] = None,
    active: Optional[bool] = None,
) -> Lot:
    lot = session.get(Lot, lot_id)
    if lot is None:
        raise ValueError(f"Lot {lot_id} not found")
    if ref is not None:
        lot.ref = ref
    if expiration_date is not None:
        lot.expiration_date = expiration_date
    if active is not None:
        lot.active = active
    session.flush()
    return lot


# ── PickingType ───────────────────────────────────────────────────────────────

def create_picking_type(
    session: Session,
    *,
    name: str,
    operation_type: OperationType,
    warehouse_id: Optional[int] = None,
    default_location_src_id: Optional[int] = None,
    default_location_dest_id: Optional[int] = None,
    sequence_prefix: Optional[str] = None,
) -> PickingType:
    pt = PickingType(
        name=name,
        operation_type=operation_type,
        warehouse_id=warehouse_id,
        default_location_src_id=default_location_src_id,
        default_location_dest_id=default_location_dest_id,
        sequence_prefix=sequence_prefix,
    )
    session.add(pt)
    session.flush()
    return pt


def update_picking_type(
    session: Session,
    picking_type_id: int,
    *,
    name: Optional[str] = None,
    default_location_src_id: Optional[int] = None,
    default_location_dest_id: Optional[int] = None,
    active: Optional[bool] = None,
) -> PickingType:
    pt = session.get(PickingType, picking_type_id)
    if pt is None:
        raise ValueError(f"PickingType {picking_type_id} not found")
    if name is not None:
        pt.name = name
    if default_location_src_id is not None:
        pt.default_location_src_id = default_location_src_id
    if default_location_dest_id is not None:
        pt.default_location_dest_id = default_location_dest_id
    if active is not None:
        pt.active = active
    session.flush()
    return pt


# ── Picking ───────────────────────────────────────────────────────────────────

def create_picking(
    session: Session,
    *,
    name: str,
    picking_type_id: Optional[int] = None,
    location_src_id: Optional[int] = None,
    location_dest_id: Optional[int] = None,
    origin: Optional[str] = None,
    scheduled_date: Optional[datetime] = None,
) -> Picking:
    picking = Picking(
        name=name,
        picking_type_id=picking_type_id,
        location_src_id=location_src_id,
        location_dest_id=location_dest_id,
        origin=origin,
        scheduled_date=scheduled_date,
    )
    session.add(picking)
    session.flush()
    return picking


def update_picking(
    session: Session,
    picking_id: int,
    *,
    origin: Optional[str] = None,
    scheduled_date: Optional[datetime] = None,
) -> Picking:
    picking = session.get(Picking, picking_id)
    if picking is None:
        raise ValueError(f"Picking {picking_id} not found")
    if origin is not None:
        picking.origin = origin
    if scheduled_date is not None:
        picking.scheduled_date = scheduled_date
    session.flush()
    return picking


# ── Move ──────────────────────────────────────────────────────────────────────

def create_move(
    session: Session,
    *,
    picking_id: Optional[int] = None,
    product_id: int,
    location_src_id: int,
    location_dest_id: int,
    product_qty: Decimal,
) -> Move:
    move = Move(
        picking_id=picking_id,
        product_id=product_id,
        location_src_id=location_src_id,
        location_dest_id=location_dest_id,
        product_qty=product_qty,
    )
    session.add(move)
    session.flush()
    return move


def update_move(
    session: Session,
    move_id: int,
    *,
    product_qty: Optional[Decimal] = None,
) -> Move:
    move = session.get(Move, move_id)
    if move is None:
        raise ValueError(f"Move {move_id} not found")
    if product_qty is not None:
        move.product_qty = product_qty
    session.flush()
    return move
