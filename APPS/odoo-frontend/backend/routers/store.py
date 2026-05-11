from __future__ import annotations

from decimal import Decimal
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from db import get_db
from auth_utils import get_current_user
from models.concrete import User
from ecommerce_core.models.product import ProductTemplate, ProductVariant
from ecommerce_core.models.order import SaleOrder, SaleOrderLine
from ecommerce_core.models.coupon import Coupon
from ecommerce_core.models.partner import Partner, Address, AddressType
from schemas.store import (
    StoreProductOut,
    StoreProductDetailOut,
    StoreVariantOut,
    CouponValidateRequest,
    CouponValidateOut,
    CreateOrderRequest,
    StoreOrderOut,
    StoreOrderDetailOut,
    StoreOrderLineOut,
)

router = APIRouter()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

USER_ID_PREFIX = "user_id:"


def _note_for_user(user_id: int) -> str:
    return f"{USER_ID_PREFIX}{user_id}"


def _get_or_create_default_partner(db: Session, user: User) -> tuple[int, int, int]:
    """
    Return (partner_id, billing_address_id, shipping_address_id) for the given
    user.  Creates a minimal Partner + two addresses if one does not yet exist
    for this user's email.
    """
    partner = db.query(Partner).filter(Partner.email == user.email).first()
    if partner is None:
        partner = Partner(name=user.email, email=user.email)
        db.add(partner)
        db.flush()

        billing = Address(
            partner_id=partner.id,
            address_type=AddressType.billing,
            is_default=True,
        )
        shipping = Address(
            partner_id=partner.id,
            address_type=AddressType.shipping,
            is_default=True,
        )
        db.add_all([billing, shipping])
        db.flush()
    else:
        # Re-use existing addresses (or create if somehow missing)
        billing = (
            db.query(Address)
            .filter(Address.partner_id == partner.id, Address.address_type == AddressType.billing)
            .first()
        )
        shipping = (
            db.query(Address)
            .filter(Address.partner_id == partner.id, Address.address_type == AddressType.shipping)
            .first()
        )
        if billing is None:
            billing = Address(
                partner_id=partner.id,
                address_type=AddressType.billing,
                is_default=True,
            )
            db.add(billing)
            db.flush()
        if shipping is None:
            shipping = Address(
                partner_id=partner.id,
                address_type=AddressType.shipping,
                is_default=True,
            )
            db.add(shipping)
            db.flush()

    return partner.id, billing.id, shipping.id


# ---------------------------------------------------------------------------
# Public endpoints — products
# ---------------------------------------------------------------------------


@router.get("/products", response_model=List[StoreProductOut])
def store_list_products(db: Session = Depends(get_db)):
    """List all active product templates with variant counts (public)."""
    rows = (
        db.query(ProductTemplate, func.count(ProductVariant.id).label("variant_count"))
        .outerjoin(ProductVariant, ProductVariant.template_id == ProductTemplate.id)
        .group_by(ProductTemplate.id)
        .all()
    )
    return [
        StoreProductOut(
            id=template.id,
            name=template.name,
            list_price=float(template.list_price),
            variant_count=variant_count,
        )
        for template, variant_count in rows
    ]


@router.get("/products/{product_id}", response_model=StoreProductDetailOut)
def store_get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a single product template with its variants (public)."""
    template = (
        db.query(ProductTemplate)
        .options(joinedload(ProductTemplate.variants))
        .filter(ProductTemplate.id == product_id)
        .first()
    )
    if template is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return StoreProductDetailOut(
        id=template.id,
        name=template.name,
        list_price=float(template.list_price),
        variants=[
            StoreVariantOut(
                id=v.id,
                sku=v.sku,
                default_price=float(v.default_price),
            )
            for v in template.variants
        ],
    )


# ---------------------------------------------------------------------------
# Public endpoint — coupon validation
# ---------------------------------------------------------------------------


@router.post("/coupons/validate", response_model=CouponValidateOut)
def store_validate_coupon(body: CouponValidateRequest, db: Session = Depends(get_db)):
    """Validate a coupon code (public).  Returns discount info or 404."""
    coupon = db.query(Coupon).filter(Coupon.code == body.code, Coupon.active.is_(True)).first()
    if coupon is None:
        raise HTTPException(status_code=404, detail="Coupon not found or inactive")
    return CouponValidateOut(
        valid=True,
        discount_type=coupon.discount_type.value
        if hasattr(coupon.discount_type, "value")
        else str(coupon.discount_type),
        discount_value=float(coupon.discount_value),
    )


# ---------------------------------------------------------------------------
# Auth-protected endpoints — orders
# ---------------------------------------------------------------------------


@router.post("/orders", response_model=StoreOrderOut, status_code=status.HTTP_201_CREATED)
def store_create_order(
    body: CreateOrderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new order from cart lines (requires JWT auth)."""
    if not body.lines:
        raise HTTPException(status_code=400, detail="Order must have at least one line")

    # Validate all variants exist and gather prices
    resolved_lines: list[tuple[ProductVariant, float]] = []
    for cart_line in body.lines:
        variant = db.query(ProductVariant).filter(ProductVariant.id == cart_line.variant_id).first()
        if variant is None:
            raise HTTPException(
                status_code=404,
                detail=f"Variant {cart_line.variant_id} not found",
            )
        resolved_lines.append((variant, cart_line.qty))

    # Get or create partner/addresses for this user
    partner_id, billing_id, shipping_id = _get_or_create_default_partner(db, current_user)

    # Build SaleOrder
    order = SaleOrder(
        partner_id=partner_id,
        billing_address_id=billing_id,
        shipping_address_id=shipping_id,
        note=_note_for_user(current_user.id),
        coupon_discount=Decimal("0"),
        shipping_amount=Decimal("0"),
    )
    db.add(order)
    db.flush()

    # Add order lines
    for variant, qty in resolved_lines:
        line = SaleOrderLine(
            order_id=order.id,
            variant_id=variant.id,
            qty=Decimal(str(qty)),
            unit_price=variant.default_price,
            discount_amount=Decimal("0"),
            tax_rate=Decimal("0"),
        )
        db.add(line)

    db.flush()

    # Apply coupon if provided
    if body.coupon_code:
        try:
            order.apply_coupon(body.coupon_code, db)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    db.commit()
    db.refresh(order)

    return StoreOrderOut(
        id=order.id,
        reference=f"SO-{order.id}",
        state=order.state.value if hasattr(order.state, "value") else str(order.state),
        total_amount=float(order.total),
    )


@router.get("/orders", response_model=List[StoreOrderOut])
def store_list_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all orders for the current user (requires JWT auth)."""
    note_tag = _note_for_user(current_user.id)
    orders = (
        db.query(SaleOrder)
        .options(joinedload(SaleOrder.lines))
        .filter(SaleOrder.note == note_tag)
        .all()
    )
    return [
        StoreOrderOut(
            id=o.id,
            reference=f"SO-{o.id}",
            state=o.state.value if hasattr(o.state, "value") else str(o.state),
            total_amount=float(o.total),
        )
        for o in orders
    ]


@router.get("/orders/{order_id}", response_model=StoreOrderDetailOut)
def store_get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single order detail.  Returns 403 if order belongs to another user."""
    order = (
        db.query(SaleOrder)
        .options(joinedload(SaleOrder.lines))
        .filter(SaleOrder.id == order_id)
        .first()
    )
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    # Ownership check — note must match current user
    expected_note = _note_for_user(current_user.id)
    if order.note != expected_note:
        raise HTTPException(status_code=403, detail="Not authorized to view this order")

    return StoreOrderDetailOut(
        id=order.id,
        reference=f"SO-{order.id}",
        state=order.state.value if hasattr(order.state, "value") else str(order.state),
        total_amount=float(order.total),
        coupon_discount=float(order.coupon_discount),
        lines=[
            StoreOrderLineOut(
                id=line.id,
                variant_id=line.variant_id,
                qty=float(line.qty),
                unit_price=float(line.unit_price),
                subtotal=float(line.subtotal),
            )
            for line in order.lines
        ],
    )
