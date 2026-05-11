from __future__ import annotations
from decimal import Decimal
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
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
    PickingTypeOut,
    LotOut,
    WarehouseIn,
    WarehouseUpdate,
    LocationIn,
    LocationUpdate,
    WmsProductIn,
    WmsProductUpdate,
    LotIn,
    LotUpdate,
    PickingTypeIn,
    PickingTypeUpdate,
    PickingIn,
    PickingUpdate,
    MoveIn,
    MoveUpdate,
)

from wms_core.models.warehouse import Warehouse
from wms_core.models.location import Location, LocationType
from wms_core.models.product import Product, TrackingType
from wms_core.models.lot import Lot
from wms_core.models.quant import Quant
from wms_core.models.picking_type import PickingType, OperationType
from wms_core.models.picking import Picking
from wms_core.models.move import Move
from wms_core.crud import (
    create_warehouse,
    update_warehouse,
    create_location,
    update_location,
    create_product,
    update_product,
    create_lot,
    update_lot,
    create_picking_type,
    update_picking_type,
    create_picking,
    update_picking,
    create_move,
    update_move,
)

router = APIRouter()


@router.get("/health")
def wms_health():
    return {"router": "wms", "status": "ok"}


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


# ── Warehouses ────────────────────────────────────────────────────────────────

@router.post("/warehouses", response_model=WarehouseOut, status_code=status.HTTP_201_CREATED)
def create_warehouse_endpoint(body: WarehouseIn, db: Session = Depends(get_db)):
    wh = create_warehouse(
        db,
        name=body.name,
        code=body.code,
        reception_steps=body.reception_steps,
        delivery_steps=body.delivery_steps,
    )
    db.commit()
    db.refresh(wh)
    return WarehouseOut(id=wh.id, name=wh.name, code=wh.code)


@router.put("/warehouses/{warehouse_id}", response_model=WarehouseOut)
def update_warehouse_endpoint(warehouse_id: int, body: WarehouseUpdate, db: Session = Depends(get_db)):
    try:
        wh = update_warehouse(db, warehouse_id, **body.model_dump(exclude_none=True))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    db.commit()
    db.refresh(wh)
    return WarehouseOut(id=wh.id, name=wh.name, code=wh.code)


# ── Locations ─────────────────────────────────────────────────────────────────

@router.post("/locations", response_model=LocationOut, status_code=status.HTTP_201_CREATED)
def create_location_endpoint(body: LocationIn, db: Session = Depends(get_db)):
    try:
        loc_type = LocationType(body.location_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid location_type: {body.location_type}")
    loc = create_location(db, name=body.name, location_type=loc_type, parent_id=body.parent_id, code=body.code)
    db.commit()
    db.refresh(loc)
    return LocationOut(
        id=loc.id,
        name=loc.name,
        complete_name=loc.complete_name,
        location_type=loc.location_type.value,
        parent_id=loc.parent_id,
    )


@router.put("/locations/{location_id}", response_model=LocationOut)
def update_location_endpoint(location_id: int, body: LocationUpdate, db: Session = Depends(get_db)):
    kwargs = body.model_dump(exclude_none=True)
    if "location_type" in kwargs:
        try:
            kwargs["location_type"] = LocationType(kwargs["location_type"])
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid location_type: {kwargs['location_type']}")
    try:
        loc = update_location(db, location_id, **kwargs)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    db.commit()
    db.refresh(loc)
    return LocationOut(
        id=loc.id,
        name=loc.name,
        complete_name=loc.complete_name,
        location_type=loc.location_type.value,
        parent_id=loc.parent_id,
    )


# ── WMS Products ──────────────────────────────────────────────────────────────

@router.post("/products", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_wms_product_endpoint(body: WmsProductIn, db: Session = Depends(get_db)):
    try:
        tracking = TrackingType(body.tracking)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid tracking: {body.tracking}")
    product = create_product(
        db,
        name=body.name,
        tracking=tracking,
        uom=body.uom,
        sale_price=body.sale_price,
        cost_price=body.cost_price,
        code=body.code,
    )
    db.commit()
    db.refresh(product)
    return ProductOut(id=product.id, name=product.name, tracking=product.tracking.value, active=product.active)


@router.put("/products/{product_id}", response_model=ProductOut)
def update_wms_product_endpoint(product_id: int, body: WmsProductUpdate, db: Session = Depends(get_db)):
    kwargs = body.model_dump(exclude_none=True)
    if "tracking" in kwargs:
        try:
            kwargs["tracking"] = TrackingType(kwargs["tracking"])
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid tracking: {kwargs['tracking']}")
    try:
        product = update_product(db, product_id, **kwargs)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    db.commit()
    db.refresh(product)
    return ProductOut(id=product.id, name=product.name, tracking=product.tracking.value, active=product.active)


# ── Lots ──────────────────────────────────────────────────────────────────────

@router.get("/lots", response_model=List[LotOut])
def list_lots(db: Session = Depends(get_db)):
    return db.query(Lot).all()


@router.post("/lots", response_model=LotOut, status_code=status.HTTP_201_CREATED)
def create_lot_endpoint(body: LotIn, db: Session = Depends(get_db)):
    lot = create_lot(db, name=body.name, product_id=body.product_id, ref=body.ref, expiration_date=body.expiration_date)
    db.commit()
    db.refresh(lot)
    return LotOut(id=lot.id, name=lot.name, product_id=lot.product_id)


@router.put("/lots/{lot_id}", response_model=LotOut)
def update_lot_endpoint(lot_id: int, body: LotUpdate, db: Session = Depends(get_db)):
    try:
        lot = update_lot(db, lot_id, **body.model_dump(exclude_none=True))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    db.commit()
    db.refresh(lot)
    return LotOut(id=lot.id, name=lot.name, product_id=lot.product_id)


# ── PickingTypes ──────────────────────────────────────────────────────────────

@router.get("/picking-types", response_model=List[PickingTypeOut])
def list_picking_types(db: Session = Depends(get_db)):
    pts = db.query(PickingType).all()
    return [
        PickingTypeOut(
            id=pt.id,
            name=pt.name,
            operation_type=pt.operation_type.value,
            warehouse_id=pt.warehouse_id,
            sequence_prefix=pt.sequence_prefix,
            active=pt.active,
        )
        for pt in pts
    ]


@router.post("/picking-types", response_model=PickingTypeOut, status_code=status.HTTP_201_CREATED)
def create_picking_type_endpoint(body: PickingTypeIn, db: Session = Depends(get_db)):
    try:
        op_type = OperationType(body.operation_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid operation_type: {body.operation_type}")
    pt = create_picking_type(
        db,
        name=body.name,
        operation_type=op_type,
        warehouse_id=body.warehouse_id,
        default_location_src_id=body.default_location_src_id,
        default_location_dest_id=body.default_location_dest_id,
        sequence_prefix=body.sequence_prefix,
    )
    db.commit()
    db.refresh(pt)
    return PickingTypeOut(
        id=pt.id, name=pt.name, operation_type=pt.operation_type.value,
        warehouse_id=pt.warehouse_id, sequence_prefix=pt.sequence_prefix, active=pt.active,
    )


@router.put("/picking-types/{picking_type_id}", response_model=PickingTypeOut)
def update_picking_type_endpoint(picking_type_id: int, body: PickingTypeUpdate, db: Session = Depends(get_db)):
    try:
        pt = update_picking_type(db, picking_type_id, **body.model_dump(exclude_none=True))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    db.commit()
    db.refresh(pt)
    return PickingTypeOut(
        id=pt.id, name=pt.name, operation_type=pt.operation_type.value,
        warehouse_id=pt.warehouse_id, sequence_prefix=pt.sequence_prefix, active=pt.active,
    )


# ── Pickings ──────────────────────────────────────────────────────────────────

@router.post("/pickings", response_model=PickingOut, status_code=status.HTTP_201_CREATED)
def create_picking_endpoint(body: PickingIn, db: Session = Depends(get_db)):
    picking = create_picking(
        db,
        name=body.name,
        picking_type_id=body.picking_type_id,
        location_src_id=body.location_src_id,
        location_dest_id=body.location_dest_id,
        origin=body.origin,
        scheduled_date=body.scheduled_date,
    )
    db.commit()
    db.refresh(picking)
    return PickingOut(
        id=picking.id,
        name=picking.name,
        state=picking.state.value,
        picking_type_id=picking.picking_type_id,
        scheduled_date=picking.scheduled_date.isoformat() if picking.scheduled_date else None,
        origin=picking.origin,
    )


@router.put("/pickings/{picking_id}", response_model=PickingOut)
def update_picking_endpoint(picking_id: int, body: PickingUpdate, db: Session = Depends(get_db)):
    try:
        picking = update_picking(db, picking_id, **body.model_dump(exclude_none=True))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    db.commit()
    db.refresh(picking)
    return PickingOut(
        id=picking.id,
        name=picking.name,
        state=picking.state.value,
        picking_type_id=picking.picking_type_id,
        scheduled_date=picking.scheduled_date.isoformat() if picking.scheduled_date else None,
        origin=picking.origin,
    )


@router.post("/pickings/{picking_id}/confirm", response_model=PickingOut)
def confirm_picking(picking_id: int, db: Session = Depends(get_db)):
    picking = db.get(Picking, picking_id)
    if not picking:
        raise HTTPException(status_code=404, detail="Picking not found")
    picking.confirm()
    db.commit()
    return PickingOut(id=picking.id, name=picking.name, state=picking.state.value, picking_type_id=picking.picking_type_id, scheduled_date=None, origin=picking.origin)


@router.post("/pickings/{picking_id}/start", response_model=PickingOut)
def start_picking(picking_id: int, db: Session = Depends(get_db)):
    picking = db.get(Picking, picking_id)
    if not picking:
        raise HTTPException(status_code=404, detail="Picking not found")
    picking.start()
    db.commit()
    return PickingOut(id=picking.id, name=picking.name, state=picking.state.value, picking_type_id=picking.picking_type_id, scheduled_date=None, origin=picking.origin)


@router.post("/pickings/{picking_id}/validate", response_model=PickingOut)
def validate_picking(picking_id: int, db: Session = Depends(get_db)):
    picking = db.get(Picking, picking_id)
    if not picking:
        raise HTTPException(status_code=404, detail="Picking not found")
    picking.validate()
    db.commit()
    return PickingOut(id=picking.id, name=picking.name, state=picking.state.value, picking_type_id=picking.picking_type_id, scheduled_date=None, origin=picking.origin)


@router.post("/pickings/{picking_id}/cancel", response_model=PickingOut)
def cancel_picking(picking_id: int, db: Session = Depends(get_db)):
    picking = db.get(Picking, picking_id)
    if not picking:
        raise HTTPException(status_code=404, detail="Picking not found")
    picking.cancel()
    db.commit()
    return PickingOut(id=picking.id, name=picking.name, state=picking.state.value, picking_type_id=picking.picking_type_id, scheduled_date=None, origin=picking.origin)


# ── Moves ─────────────────────────────────────────────────────────────────────

@router.post("/pickings/{picking_id}/moves", response_model=MoveOut, status_code=status.HTTP_201_CREATED)
def create_move_endpoint(picking_id: int, body: MoveIn, db: Session = Depends(get_db)):
    if not db.get(Picking, picking_id):
        raise HTTPException(status_code=404, detail="Picking not found")
    move = create_move(
        db,
        picking_id=picking_id,
        product_id=body.product_id,
        location_src_id=body.location_src_id,
        location_dest_id=body.location_dest_id,
        product_qty=body.product_qty,
    )
    db.commit()
    db.refresh(move)
    return MoveOut(
        id=move.id, picking_id=move.picking_id, product_id=move.product_id,
        product_qty=float(move.product_qty), qty_done=float(move.qty_done), state=move.state.value,
    )


@router.put("/moves/{move_id}", response_model=MoveOut)
def update_move_endpoint(move_id: int, body: MoveUpdate, db: Session = Depends(get_db)):
    try:
        move = update_move(db, move_id, **body.model_dump(exclude_none=True))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    db.commit()
    db.refresh(move)
    return MoveOut(
        id=move.id, picking_id=move.picking_id, product_id=move.product_id,
        product_qty=float(move.product_qty), qty_done=float(move.qty_done), state=move.state.value,
    )
