from decimal import Decimal
import pytest
from ecommerce_core.models import (
    ProductCategory, ProductTemplate, ProductVariant,
    Pricelist, PricelistItem, AppliedOn, ComputePrice,
)


def _variant(session, name, list_price="10.00", default_price="10.00", sku=None):
    tmpl = ProductTemplate(name=name, list_price=Decimal(list_price))
    v = ProductVariant(template=tmpl, sku=sku or f"SKU-{name}", default_price=Decimal(default_price))
    session.add_all([tmpl, v])
    session.flush()
    return v


def test_get_price_no_items_falls_back_to_default(session):
    pl = Pricelist(name="Empty PL")
    session.add(pl)
    session.flush()
    v = _variant(session, "NoRule", default_price="19.99", sku="NR-001")
    assert pl.get_price(v, Decimal("1")) == Decimal("19.99")


def test_get_price_fixed(session):
    pl = Pricelist(name="Fixed PL")
    item = PricelistItem(
        pricelist=pl, applied_on=AppliedOn.all,
        compute_price=ComputePrice.fixed, fixed_price=Decimal("5.00"),
    )
    session.add_all([pl, item])
    session.flush()
    v = _variant(session, "FixedItem", default_price="10.00", sku="FX-001")
    assert pl.get_price(v, Decimal("1")) == Decimal("5.00")


def test_get_price_percentage(session):
    pl = Pricelist(name="Pct PL")
    item = PricelistItem(
        pricelist=pl, applied_on=AppliedOn.all,
        compute_price=ComputePrice.percentage, price_discount=Decimal("20"),
    )
    session.add_all([pl, item])
    session.flush()
    v = _variant(session, "PctItem", list_price="100.00", default_price="100.00", sku="PCT-001")
    price = pl.get_price(v, Decimal("1"))
    assert price == Decimal("80.00")


def test_get_price_formula_raises(session):
    pl = Pricelist(name="Formula PL")
    item = PricelistItem(
        pricelist=pl, applied_on=AppliedOn.all,
        compute_price=ComputePrice.formula,
    )
    session.add_all([pl, item])
    session.flush()
    v = _variant(session, "FormulaItem", sku="FM-001")
    with pytest.raises(NotImplementedError):
        pl.get_price(v, Decimal("1"))


def test_get_price_variant_scope_wins_over_all(session):
    pl = Pricelist(name="Spec PL")
    v = _variant(session, "SpecItem", list_price="100.00", default_price="100.00", sku="SP-001")
    item_all = PricelistItem(
        pricelist=pl, applied_on=AppliedOn.all,
        compute_price=ComputePrice.fixed, fixed_price=Decimal("50.00"),
    )
    item_variant = PricelistItem(
        pricelist=pl, applied_on=AppliedOn.variant,
        product_variant_id=v.id,
        compute_price=ComputePrice.fixed, fixed_price=Decimal("30.00"),
    )
    session.add_all([pl, item_all, item_variant])
    session.flush()
    assert pl.get_price(v, Decimal("1")) == Decimal("30.00")


def test_get_price_min_quantity_not_met_falls_back(session):
    pl = Pricelist(name="MinQty PL")
    item = PricelistItem(
        pricelist=pl, applied_on=AppliedOn.all,
        compute_price=ComputePrice.fixed, fixed_price=Decimal("2.00"),
        min_quantity=Decimal("10"),
    )
    session.add_all([pl, item])
    session.flush()
    v = _variant(session, "MinItem", default_price="9.00", sku="MQ-001")
    # qty=1 doesn't meet min_quantity=10, falls back to default_price
    assert pl.get_price(v, Decimal("1")) == Decimal("9.00")
