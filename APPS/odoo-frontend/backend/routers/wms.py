from __future__ import annotations
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from db import get_db
from schemas.wms import (
    WarehouseOut,
    LocationOut,
    ProductOut,
    QuantDetailOut,
    PickingOut,
    PickingDetailOut,
    MoveOut,
)

from wms_core.models.warehouse import Warehouse
from wms_core.models.location import Location
from wms_core.models.product import Product
from wms_core.models.quant import Quant
from wms_core.models.picking import Picking
from wms_core.models.move import Move

router = APIRouter()


@router.get("/warehouses", response_model=List[WarehouseOut])
def list_warehouses(db: Session = Depends(get_db)):
    warehouses = db.query(Warehouse).all()
    return warehouses


@router.get("/locations", response_model=List[LocationOut])
def list_locations(db: Session = Depends(get_db)):
    locations = (
        db.query(Location)
        .options(joinedload(Location.parent))
        .all()
    )
    # Sort by complete_name
    locations.sort(key=lambda loc: loc.complete_name)
    return [
        LocationOut(
            id=loc.id,
            name=loc.name,
            complete_name=loc.complete_name,
            location_type=loc.location_type.value if hasattr(loc.location_type, "value") else str(loc.location_type),
            parent_id=loc.parent_id,
        )
        for loc in locations
    ]


@router.get("/products", response_model=List[ProductOut])
def list_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return [
        ProductOut(
            id=p.id,
            name=p.name,
            tracking=p.tracking.value if hasattr(p.tracking, "value") else str(p.tracking),
            active=p.active,
        )
        for p in products
    ]


@router.get("/inventory", response_model=List[QuantDetailOut])
def list_inventory(db: Session = Depends(get_db)):
    quants = (
        db.query(Quant)
        .options(
            joinedload(Quant.product),
            joinedload(Quant.location).joinedload(Location.parent),
            joinedload(Quant.lot),
        )
        .all()
    )
    result = []
    for q in quants:
        result.append(
            QuantDetailOut(
                product_name=q.product.name,
                location_name=q.location.complete_name,
                lot_name=q.lot.name if q.lot else None,
                quantity=float(q.quantity),
            )
        )
    return result


@router.get("/pickings", response_model=List[PickingOut])
def list_pickings(db: Session = Depends(get_db)):
    pickings = db.query(Picking).all()
    return [
        PickingOut(
            id=p.id,
            name=p.name,
            state=p.state.value if hasattr(p.state, "value") else str(p.state),
            picking_type_id=p.picking_type_id,
            scheduled_date=p.scheduled_date.isoformat() if p.scheduled_date else None,
            origin=p.origin,
        )
        for p in pickings
    ]


@router.get("/pickings/{picking_id}", response_model=PickingDetailOut)
def get_picking(picking_id: int, db: Session = Depends(get_db)):
    picking = (
        db.query(Picking)
        .options(joinedload(Picking.moves))
        .filter(Picking.id == picking_id)
        .first()
    )
    if picking is None:
        raise HTTPException(status_code=404, detail="Picking not found")

    moves = [
        MoveOut(
            id=m.id,
            picking_id=m.picking_id,
            product_id=m.product_id,
            product_qty=float(m.product_qty),
            qty_done=float(m.qty_done),
            state=m.state.value if hasattr(m.state, "value") else str(m.state),
        )
        for m in picking.moves
    ]

    return PickingDetailOut(
        id=picking.id,
        name=picking.name,
        state=picking.state.value if hasattr(picking.state, "value") else str(picking.state),
        picking_type_id=picking.picking_type_id,
        scheduled_date=picking.scheduled_date.isoformat() if picking.scheduled_date else None,
        origin=picking.origin,
        moves=moves,
    )
