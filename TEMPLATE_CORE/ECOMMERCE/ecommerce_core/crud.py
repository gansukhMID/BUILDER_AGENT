from __future__ import annotations
from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from ecommerce_core.models.category import ProductCategory
from ecommerce_core.models.product import ProductTemplate, ProductVariant
from ecommerce_core.models.coupon import Coupon, DiscountType
from ecommerce_core.models.shipping import ShippingMethod


# ── ProductCategory ───────────────────────────────────────────────────────────

def create_category(
    session: Session,
    *,
    name: str,
    parent_id: Optional[int] = None,
) -> ProductCategory:
    cat = ProductCategory(name=name, parent_id=parent_id)
    session.add(cat)
    session.flush()
    return cat


def update_category(
    session: Session,
    category_id: int,
    *,
    name: Optional[str] = None,
    parent_id: Optional[int] = None,
) -> ProductCategory:
    cat = session.get(ProductCategory, category_id)
    if cat is None:
        raise ValueError(f"ProductCategory {category_id} not found")
    if name is not None:
        cat.name = name
    if parent_id is not None:
        cat.parent_id = parent_id
    session.flush()
    return cat


# ── ProductTemplate ───────────────────────────────────────────────────────────

def create_product_template(
    session: Session,
    *,
    name: str,
    list_price: Decimal = Decimal("0"),
    description: Optional[str] = None,
    category_id: Optional[int] = None,
    image_url: Optional[str] = None,
) -> ProductTemplate:
    tmpl = ProductTemplate(
        name=name,
        list_price=list_price,
        description=description,
        category_id=category_id,
        image_url=image_url,
    )
    session.add(tmpl)
    session.flush()
    return tmpl


def update_product_template(
    session: Session,
    template_id: int,
    *,
    name: Optional[str] = None,
    list_price: Optional[Decimal] = None,
    description: Optional[str] = None,
    category_id: Optional[int] = None,
    image_url: Optional[str] = None,
    active: Optional[bool] = None,
) -> ProductTemplate:
    tmpl = session.get(ProductTemplate, template_id)
    if tmpl is None:
        raise ValueError(f"ProductTemplate {template_id} not found")
    if name is not None:
        tmpl.name = name
    if list_price is not None:
        tmpl.list_price = list_price
    if description is not None:
        tmpl.description = description
    if category_id is not None:
        tmpl.category_id = category_id
    if image_url is not None:
        tmpl.image_url = image_url
    if active is not None:
        tmpl.active = active
    session.flush()
    return tmpl


# ── ProductVariant ────────────────────────────────────────────────────────────

def create_product_variant(
    session: Session,
    *,
    template_id: int,
    sku: Optional[str] = None,
    barcode: Optional[str] = None,
    default_price: Decimal = Decimal("0"),
) -> ProductVariant:
    if sku is not None:
        existing = session.query(ProductVariant).filter_by(sku=sku).first()
        if existing:
            raise ValueError(f"SKU '{sku}' already exists")
    variant = ProductVariant(
        template_id=template_id,
        sku=sku,
        barcode=barcode,
        default_price=default_price,
    )
    session.add(variant)
    session.flush()
    return variant


def update_product_variant(
    session: Session,
    variant_id: int,
    *,
    sku: Optional[str] = None,
    barcode: Optional[str] = None,
    default_price: Optional[Decimal] = None,
    active: Optional[bool] = None,
) -> ProductVariant:
    variant = session.get(ProductVariant, variant_id)
    if variant is None:
        raise ValueError(f"ProductVariant {variant_id} not found")
    if sku is not None:
        existing = session.query(ProductVariant).filter(
            ProductVariant.sku == sku, ProductVariant.id != variant_id
        ).first()
        if existing:
            raise ValueError(f"SKU '{sku}' already exists")
        variant.sku = sku
    if barcode is not None:
        variant.barcode = barcode
    if default_price is not None:
        variant.default_price = default_price
    if active is not None:
        variant.active = active
    session.flush()
    return variant


# ── Coupon ────────────────────────────────────────────────────────────────────

def create_coupon(
    session: Session,
    *,
    code: str,
    discount_type: DiscountType,
    discount_value: Decimal,
    min_order_amount: Decimal = Decimal("0"),
    usage_limit: Optional[int] = None,
    expiry_date: Optional[date] = None,
) -> Coupon:
    coupon = Coupon(
        code=code,
        discount_type=discount_type,
        discount_value=discount_value,
        min_order_amount=min_order_amount,
        usage_limit=usage_limit,
        expiry_date=expiry_date,
    )
    session.add(coupon)
    session.flush()
    return coupon


def update_coupon(
    session: Session,
    coupon_id: int,
    *,
    discount_value: Optional[Decimal] = None,
    min_order_amount: Optional[Decimal] = None,
    usage_limit: Optional[int] = None,
    expiry_date: Optional[date] = None,
    active: Optional[bool] = None,
) -> Coupon:
    coupon = session.get(Coupon, coupon_id)
    if coupon is None:
        raise ValueError(f"Coupon {coupon_id} not found")
    if discount_value is not None:
        coupon.discount_value = discount_value
    if min_order_amount is not None:
        coupon.min_order_amount = min_order_amount
    if usage_limit is not None:
        coupon.usage_limit = usage_limit
    if expiry_date is not None:
        coupon.expiry_date = expiry_date
    if active is not None:
        coupon.active = active
    session.flush()
    return coupon


# ── ShippingMethod ────────────────────────────────────────────────────────────

def create_shipping_method(
    session: Session,
    *,
    name: str,
    carrier: Optional[str] = None,
    price: Decimal = Decimal("0"),
) -> ShippingMethod:
    method = ShippingMethod(name=name, carrier=carrier, price=price)
    session.add(method)
    session.flush()
    return method


def update_shipping_method(
    session: Session,
    method_id: int,
    *,
    name: Optional[str] = None,
    carrier: Optional[str] = None,
    price: Optional[Decimal] = None,
    active: Optional[bool] = None,
) -> ShippingMethod:
    method = session.get(ShippingMethod, method_id)
    if method is None:
        raise ValueError(f"ShippingMethod {method_id} not found")
    if name is not None:
        method.name = name
    if carrier is not None:
        method.carrier = carrier
    if price is not None:
        method.price = price
    if active is not None:
        method.active = active
    session.flush()
    return method
