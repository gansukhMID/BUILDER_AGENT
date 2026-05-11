from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from db import get_db
from ecommerce_core.models.product import ProductTemplate, ProductVariant
from ecommerce_core.models.order import SaleOrder, SaleOrderLine
from ecommerce_core.models.coupon import Coupon, DiscountType
from ecommerce_core.models.category import ProductCategory
from ecommerce_core.models.shipping import ShippingMethod
from ecommerce_core.crud import (
    create_category,
    update_category,
    create_product_template,
    update_product_template,
    create_product_variant,
    update_product_variant,
    create_coupon,
    update_coupon,
    create_shipping_method,
    update_shipping_method,
)
from schemas.ecommerce import (
    ProductTemplateOut,
    ProductDetailOut,
    ProductVariantOut,
    OrderOut,
    OrderDetailOut,
    OrderLineOut,
    CouponOut,
    CategoryOut,
    CategoryIn,
    CategoryUpdate,
    ProductTemplateIn,
    ProductTemplateUpdate,
    ProductVariantIn,
    ProductVariantUpdate,
    CouponIn,
    CouponUpdate,
    ShippingMethodOut,
    ShippingMethodIn,
    ShippingMethodUpdate,
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


# ── Categories ────────────────────────────────────────────────────────────────

@router.get("/categories", response_model=List[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(ProductCategory).order_by(ProductCategory.name).all()


@router.post("/categories", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category_endpoint(body: CategoryIn, db: Session = Depends(get_db)):
    cat = create_category(db, name=body.name, parent_id=body.parent_id)
    db.commit()
    db.refresh(cat)
    return cat


@router.put("/categories/{category_id}", response_model=CategoryOut)
def update_category_endpoint(category_id: int, body: CategoryUpdate, db: Session = Depends(get_db)):
    try:
        cat = update_category(db, category_id, **body.model_dump(exclude_none=True))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    db.commit()
    db.refresh(cat)
    return cat


# ── Products ──────────────────────────────────────────────────────────────────

@router.post("/products", response_model=ProductTemplateOut, status_code=status.HTTP_201_CREATED)
def create_product_endpoint(body: ProductTemplateIn, db: Session = Depends(get_db)):
    tmpl = create_product_template(
        db,
        name=body.name,
        list_price=body.list_price,
        description=body.description,
        category_id=body.category_id,
        image_url=body.image_url,
    )
    db.commit()
    db.refresh(tmpl)
    return ProductTemplateOut(id=tmpl.id, name=tmpl.name, list_price=float(tmpl.list_price), variant_count=0)


@router.put("/products/{product_id}", response_model=ProductTemplateOut)
def update_product_endpoint(product_id: int, body: ProductTemplateUpdate, db: Session = Depends(get_db)):
    try:
        tmpl = update_product_template(db, product_id, **body.model_dump(exclude_none=True))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    db.commit()
    db.refresh(tmpl)
    variant_count = db.query(ProductVariant).filter(ProductVariant.template_id == product_id).count()
    return ProductTemplateOut(id=tmpl.id, name=tmpl.name, list_price=float(tmpl.list_price), variant_count=variant_count)


@router.post("/products/{product_id}/variants", response_model=ProductVariantOut, status_code=status.HTTP_201_CREATED)
def create_variant_endpoint(product_id: int, body: ProductVariantIn, db: Session = Depends(get_db)):
    if not db.get(ProductTemplate, product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    try:
        variant = create_product_variant(
            db,
            template_id=product_id,
            sku=body.sku,
            barcode=body.barcode,
            default_price=body.default_price,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    db.commit()
    db.refresh(variant)
    return ProductVariantOut(id=variant.id, sku=variant.sku, default_price=float(variant.default_price))


@router.put("/variants/{variant_id}", response_model=ProductVariantOut)
def update_variant_endpoint(variant_id: int, body: ProductVariantUpdate, db: Session = Depends(get_db)):
    try:
        variant = update_product_variant(db, variant_id, **body.model_dump(exclude_none=True))
    except ValueError as e:
        raise HTTPException(status_code=404 if "not found" in str(e) else 400, detail=str(e))
    db.commit()
    db.refresh(variant)
    return ProductVariantOut(id=variant.id, sku=variant.sku, default_price=float(variant.default_price))


# ── Coupons ───────────────────────────────────────────────────────────────────

@router.post("/coupons", response_model=CouponOut, status_code=status.HTTP_201_CREATED)
def create_coupon_endpoint(body: CouponIn, db: Session = Depends(get_db)):
    try:
        discount_type = DiscountType(body.discount_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid discount_type: {body.discount_type}")
    coupon = create_coupon(
        db,
        code=body.code,
        discount_type=discount_type,
        discount_value=body.discount_value,
        min_order_amount=body.min_order_amount,
        usage_limit=body.usage_limit,
        expiry_date=body.expiry_date,
    )
    db.commit()
    db.refresh(coupon)
    return CouponOut(
        id=coupon.id,
        code=coupon.code,
        discount_type=coupon.discount_type.value,
        discount_value=float(coupon.discount_value),
    )


@router.put("/coupons/{coupon_id}", response_model=CouponOut)
def update_coupon_endpoint(coupon_id: int, body: CouponUpdate, db: Session = Depends(get_db)):
    try:
        coupon = update_coupon(db, coupon_id, **body.model_dump(exclude_none=True))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    db.commit()
    db.refresh(coupon)
    return CouponOut(
        id=coupon.id,
        code=coupon.code,
        discount_type=coupon.discount_type.value,
        discount_value=float(coupon.discount_value),
    )


# ── Shipping Methods ──────────────────────────────────────────────────────────

@router.get("/shipping-methods", response_model=List[ShippingMethodOut])
def list_shipping_methods(db: Session = Depends(get_db)):
    return [
        ShippingMethodOut(id=m.id, name=m.name, carrier=m.carrier, price=float(m.price), active=m.active)
        for m in db.query(ShippingMethod).all()
    ]


@router.post("/shipping-methods", response_model=ShippingMethodOut, status_code=status.HTTP_201_CREATED)
def create_shipping_method_endpoint(body: ShippingMethodIn, db: Session = Depends(get_db)):
    method = create_shipping_method(db, name=body.name, carrier=body.carrier, price=body.price)
    db.commit()
    db.refresh(method)
    return ShippingMethodOut(id=method.id, name=method.name, carrier=method.carrier, price=float(method.price), active=method.active)


@router.put("/shipping-methods/{method_id}", response_model=ShippingMethodOut)
def update_shipping_method_endpoint(method_id: int, body: ShippingMethodUpdate, db: Session = Depends(get_db)):
    try:
        method = update_shipping_method(db, method_id, **body.model_dump(exclude_none=True))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    db.commit()
    db.refresh(method)
    return ShippingMethodOut(id=method.id, name=method.name, carrier=method.carrier, price=float(method.price), active=method.active)
