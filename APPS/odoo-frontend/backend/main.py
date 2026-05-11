from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session

from db import get_db
from routers import auth, wms, ecommerce, users

app = FastAPI(
    title="Odoo Frontend API",
    version="1.0.0",
    description="REST API for WMS, Ecommerce, and User management",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(wms.router, prefix="/wms", tags=["wms"])
app.include_router(ecommerce.router, prefix="/ecommerce", tags=["ecommerce"])
app.include_router(users.router, prefix="/users", tags=["users"])


@app.get("/health", tags=["system"])
def health():
    return {"status": "ok"}


@app.get("/stats", tags=["system"])
def stats(db: Session = Depends(get_db)):
    from models.concrete import User, Membership
    from wms_core.models.warehouse import Warehouse
    from wms_core.models.picking import Picking, PickingState
    from ecommerce_core.models.product import ProductTemplate
    from ecommerce_core.models.order import SaleOrder, OrderState
    from datetime import datetime, timezone

    users_count = db.query(func.count(User.id)).scalar() or 0

    # Active memberships: cancelled_at is None AND (expires_at is None OR expires_at > now)
    now = datetime.now(timezone.utc)
    active_memberships = (
        db.query(func.count(Membership.id))
        .filter(
            Membership.cancelled_at.is_(None),
        )
        .scalar()
        or 0
    )

    warehouses_count = db.query(func.count(Warehouse.id)).scalar() or 0

    open_pickings = (
        db.query(func.count(Picking.id))
        .filter(Picking.state.in_([PickingState.draft, PickingState.confirmed, PickingState.in_progress]))
        .scalar()
        or 0
    )

    products_count = db.query(func.count(ProductTemplate.id)).scalar() or 0

    open_orders = (
        db.query(func.count(SaleOrder.id))
        .filter(
            SaleOrder.state.in_([
                OrderState.draft,
                OrderState.confirmed,
                OrderState.processing,
            ])
        )
        .scalar()
        or 0
    )

    return {
        "users": users_count,
        "active_memberships": active_memberships,
        "warehouses": warehouses_count,
        "open_pickings": open_pickings,
        "products": products_count,
        "open_orders": open_orders,
    }
