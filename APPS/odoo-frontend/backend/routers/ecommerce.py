from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from db import get_db
from ecommerce_core.models.product import ProductTemplate, ProductVariant
from ecommerce_core.models.order import SaleOrder, SaleOrderLine
from ecommerce_core.models.coupon import Coupon
from schemas.ecommerce import (
    ProductTemplateOut,
    ProductDetailOut,
    ProductVariantOut,
    OrderOut,
    OrderDetailOut,
    OrderLineOut,
    CouponOut,
)

router = APIRouter()


@router.get("/health")
def ecommerce_health():
    return {"router": "ecommerce", "status": "ok"}


@router.get("/products", response_model=List[ProductTemplateOut])
def list_products(db: Session = Depends(get_db)):
    """List all product templates with variant counts."""
    rows = (
        db.query(ProductTemplate, func.count(ProductVariant.id).label("variant_count"))
        .outerjoin(ProductVariant, ProductVariant.template_id == ProductTemplate.id)
        .group_by(ProductTemplate.id)
        .all()
    )
    result = []
    for template, variant_count in rows:
        result.append(
            ProductTemplateOut(
                id=template.id,
                name=template.name,
                list_price=float(template.list_price),
                variant_count=variant_count,
            )
        )
    return result


@router.get("/products/{product_id}", response_model=ProductDetailOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a single product template with its variants."""
    template = (
        db.query(ProductTemplate)
        .options(joinedload(ProductTemplate.variants))
        .filter(ProductTemplate.id == product_id)
        .first()
    )
    if template is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductDetailOut(
        id=template.id,
        name=template.name,
        list_price=float(template.list_price),
        variants=[
            ProductVariantOut(
                id=v.id,
                sku=v.sku,
                default_price=float(v.default_price),
            )
            for v in template.variants
        ],
    )


@router.get("/orders", response_model=List[OrderOut])
def list_orders(db: Session = Depends(get_db)):
    """List all sale orders."""
    orders = db.query(SaleOrder).options(joinedload(SaleOrder.lines)).all()
    result = []
    for order in orders:
        result.append(
            OrderOut(
                id=order.id,
                reference=f"SO-{order.id}",
                state=order.state.value if hasattr(order.state, "value") else str(order.state),
                total_amount=float(order.total),
                currency="USD",
            )
        )
    return result


@router.get("/orders/{order_id}", response_model=OrderDetailOut)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """Get a single sale order with its lines."""
    order = (
        db.query(SaleOrder)
        .options(joinedload(SaleOrder.lines))
        .filter(SaleOrder.id == order_id)
        .first()
    )
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return OrderDetailOut(
        id=order.id,
        reference=f"SO-{order.id}",
        state=order.state.value if hasattr(order.state, "value") else str(order.state),
        total_amount=float(order.total),
        lines=[
            OrderLineOut(
                id=line.id,
                quantity=float(line.qty),
                unit_price=float(line.unit_price),
                line_total=float(line.subtotal),
            )
            for line in order.lines
        ],
    )


@router.get("/coupons", response_model=List[CouponOut])
def list_coupons(db: Session = Depends(get_db)):
    """List all coupons."""
    coupons = db.query(Coupon).all()
    return [
        CouponOut(
            id=c.id,
            code=c.code,
            discount_type=c.discount_type.value if hasattr(c.discount_type, "value") else str(c.discount_type),
            discount_value=float(c.discount_value),
        )
        for c in coupons
    ]
