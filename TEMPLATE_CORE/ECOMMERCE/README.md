# ecommerce-core-template

`TEMPLATE_CORE/ECOMMERCE` is a Python + SQLAlchemy library of reusable base models for e-commerce platforms. Inspired by Odoo's `sale`, `product`, and `account` module architecture, it provides a composable, agent-readable foundation so AI agents can generate fully functional online store backends without rebuilding core commerce logic from scratch.

---

## Model Reference

| Model | Odoo Analogue | Purpose |
|---|---|---|
| `ProductCategory` | `product.category` | Hierarchical product classification (self-referential) |
| `ProductTemplate` | `product.template` | Merchandising unit: name, description, base price |
| `ProductVariant` | `product.product` | Purchasable SKU: template + attribute combination |
| `ProductAttribute` | `product.attribute` | Dimension definition (Size, Color, Material) |
| `ProductAttributeValue` | `product.attribute.value` | Dimension option (S, M, L / Red, Blue) |
| `ProductVariantAttributeLine` | *(association table)* | Links variants to their selected attribute values |
| `Partner` | `res.partner` | Customer / company contact record |
| `Address` | `res.partner` (type) | Shipping or billing address linked to a Partner |
| `Pricelist` | `product.pricelist` | Named pricelist with currency and pricing rules |
| `PricelistItem` | `product.pricelist.item` | Rule: scope → price computation (fixed/percentage/formula) |
| `Coupon` | `sale.coupon` | Discount code with usage limit, expiry, and min order |
| `ShippingMethod` | `delivery.carrier` | Delivery method stub with fixed price and extension hook |
| `Cart` | `website.cart` | Active shopping session (nullable partner = guest checkout) |
| `CartLine` | `website.cart.line` | Product variant + qty in a cart |
| `SaleOrder` | `sale.order` | Confirmed customer order with full state machine |
| `SaleOrderLine` | `sale.order.line` | Line item: variant, qty, unit price, discount, tax rate |
| `PaymentTransaction` | `payment.transaction` | Payment attempt with state machine |

---

## Module Layout

```
TEMPLATE_CORE/ECOMMERCE/
├── ecommerce_core/
│   ├── __init__.py
│   ├── db.py                    # Base, engine_factory, session_factory, get_session
│   ├── mixins.py                # TimestampMixin, ActiveMixin, NameMixin, CurrencyMixin
│   ├── models/
│   │   ├── __init__.py          # re-exports all models
│   │   ├── category.py          # ProductCategory
│   │   ├── product.py           # ProductTemplate, ProductVariant
│   │   ├── attribute.py         # ProductAttribute, ProductAttributeValue, assoc table
│   │   ├── partner.py           # Partner, Address
│   │   ├── pricelist.py         # Pricelist, PricelistItem
│   │   ├── coupon.py            # Coupon
│   │   ├── cart.py              # Cart, CartLine
│   │   ├── order.py             # SaleOrder, SaleOrderLine
│   │   ├── shipping.py          # ShippingMethod (stub)
│   │   └── payment.py           # PaymentTransaction
│   └── utils/
│       ├── state_machine.py     # Generic FSM (same API as TEMPLATE_CORE/WMS)
│       └── pricing.py           # evaluate_pricelist() engine
├── alembic/
│   ├── env.py
│   └── versions/
│       └── 0001_initial.py      # Creates all 17 tables
├── alembic.ini.template
├── pyproject.toml
└── README.md
```

---

## Quickstart — Subclassing a Model

Extend `ProductVariant` to add a `weight_kg` field without touching any template file:

```python
from sqlalchemy import Numeric
from sqlalchemy.orm import Mapped, mapped_column
from ecommerce_core.models import ProductVariant

class WeightedVariant(ProductVariant):
    """ProductVariant extended with physical weight for shipping calculation."""
    __tablename__ = "weighted_variant"

    id: Mapped[int] = mapped_column(primary_key=True)  # own PK for joined-table inheritance
    weight_kg: Mapped[float] = mapped_column(Numeric(6, 3), default=0.0)
```

Or add a `loyalty_points` field to `SaleOrder`:

```python
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column
from ecommerce_core.models import SaleOrder

class LoyaltyOrder(SaleOrder):
    __tablename__ = "loyalty_order"
    id: Mapped[int] = mapped_column(primary_key=True)
    loyalty_points_earned: Mapped[int] = mapped_column(Integer, default=0)
```

---

## Extension Points

These stubs raise `NotImplementedError` and are designed to be overridden by agents:

| Method | Where | What to implement |
|---|---|---|
| `Cart.checkout()` | `cart.py` | Create `SaleOrder` from cart lines, mark cart `checked_out` |
| `ShippingMethod.estimate_price(order)` | `shipping.py` | Dynamic carrier rate (Fedex, DHL API calls) |
| `PricelistItem` `formula` mode | `utils/pricing.py` | Custom price formula (e.g. cost × margin) |

---

## Running Tests

```bash
cd TEMPLATE_CORE/ECOMMERCE
pip install -e ".[dev]"
pytest tests/ --cov=ecommerce_core --cov-report=term-missing
```

Expected: ≥85% coverage across all `ecommerce_core/` modules.
