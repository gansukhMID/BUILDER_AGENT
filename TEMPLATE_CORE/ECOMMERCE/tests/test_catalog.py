from decimal import Decimal
import pytest
from sqlalchemy.exc import IntegrityError
from ecommerce_core.models import (
    ProductCategory, ProductTemplate, ProductVariant,
    ProductAttribute, ProductAttributeValue,
)


def test_category_complete_name(session):
    root = ProductCategory(name="Electronics")
    child = ProductCategory(name="Phones", parent=root)
    grand = ProductCategory(name="Accessories", parent=child)
    session.add_all([root, child, grand])
    session.flush()
    assert root.complete_name == "Electronics"
    assert child.complete_name == "Electronics / Phones"
    assert grand.complete_name == "Electronics / Phones / Accessories"


def test_category_no_parent(session):
    cat = ProductCategory(name="Standalone")
    session.add(cat)
    session.flush()
    assert cat.complete_name == "Standalone"
    assert cat.parent is None


def test_product_variant_display_name_with_attributes(session):
    cat = ProductCategory(name="Clothing")
    tmpl = ProductTemplate(name="T-Shirt", list_price=Decimal("29.99"), category=cat)
    variant = ProductVariant(template=tmpl, sku="TS-RED-M", default_price=Decimal("29.99"))
    attr = ProductAttribute(name="Color")
    val = ProductAttributeValue(attribute=attr, name="Red")
    session.add_all([cat, tmpl, variant, attr, val])
    session.flush()
    variant.attribute_values.append(val)
    session.flush()
    assert "T-Shirt" in variant.display_name
    assert "Red" in variant.display_name


def test_product_variant_display_name_no_attributes(session):
    tmpl = ProductTemplate(name="Widget", list_price=Decimal("9.99"))
    variant = ProductVariant(template=tmpl, sku="WDG-001", default_price=Decimal("9.99"))
    session.add_all([tmpl, variant])
    session.flush()
    assert variant.display_name == "Widget"


def test_variant_sku_unique(session):
    tmpl = ProductTemplate(name="Prod", list_price=Decimal("1"))
    v1 = ProductVariant(template=tmpl, sku="DUP-SKU-A", default_price=Decimal("1"))
    v2 = ProductVariant(template=tmpl, sku="DUP-SKU-A", default_price=Decimal("1"))
    session.add_all([tmpl, v1, v2])
    with pytest.raises(IntegrityError):
        session.flush()
    session.rollback()


def test_template_category_relationship(session):
    cat = ProductCategory(name="Tools")
    tmpl = ProductTemplate(name="Hammer", list_price=Decimal("15.00"), category=cat)
    session.add_all([cat, tmpl])
    session.flush()
    assert tmpl.category.name == "Tools"


def test_attribute_values_relationship(session):
    attr = ProductAttribute(name="Size")
    v_s = ProductAttributeValue(attribute=attr, name="S")
    v_m = ProductAttributeValue(attribute=attr, name="M")
    session.add_all([attr, v_s, v_m])
    session.flush()
    assert len(attr.values) == 2
