---
name: ecommerce-core-template
status: merged
created: 2026-05-10T13:09:48Z
updated: 2026-05-10T16:00:00Z
progress: 100%
prd: .claude/prds/ecommerce-core-template.md
github: https://github.com/gansukhMID/BUILDER_AGENT/issues/23
---

# Epic: ecommerce-core-template

## Overview

Build `TEMPLATE_CORE/ECOMMERCE` — a Python + SQLAlchemy library of reusable base models for e-commerce platforms. Follows the same conventions as `TEMPLATE_CORE/WMS` (mixins, `db.py`, `utils/state_machine.py`, pyproject.toml structure) so agents working across templates find a uniform interface.

Covers 16 models across 6 domains: product catalog, partner/address, pricing & promotions, cart/checkout, order management, and payment.

---

## Architecture Decisions

1. **No `TEMPLATE_CORE/WMS` dependency** — stock management is a peer template. `ProductVariant` stores a `sku` but no `stock_qty`; agents wire in WMS separately.
2. **Concrete mapped classes, not `__abstract__`** — same choice as WMS; agents subclass and add columns without touching template files.
3. **Shared `utils/state_machine.py` interface** — copy the FSM helper pattern from WMS verbatim (same API) so the two templates are drop-in consistent.
4. **Tax as a field, not a model** — `SaleOrderLine.tax_rate` (Decimal) keeps the template lean; agents add `TaxGroup` on top.
5. **`ShippingMethod` is a stub** — fixed `price` field only; agents override `estimate_price(order)` for dynamic rates.
6. **Guest checkout** — `Cart.partner_id` nullable; `Cart.checkout()` requires a partner (caller creates one from guest info first).
7. **SQLite-compatible** — no PostgreSQL-specific types; enables lightweight in-memory unit tests identical to WMS pattern.

---

## Technical Approach

### Package layout
```
TEMPLATE_CORE/ECOMMERCE/
├── ecommerce_core/
│   ├── __init__.py
│   ├── db.py                  # Base, engine_factory, session_factory
│   ├── mixins.py              # TimestampMixin, ActiveMixin, NameMixin, CurrencyMixin
│   ├── models/
│   │   ├── __init__.py        # re-exports all 16 models
│   │   ├── category.py        # ProductCategory (self-referential)
│   │   ├── product.py         # ProductTemplate, ProductVariant
│   │   ├── attribute.py       # ProductAttribute, ProductAttributeValue, assoc table
│   │   ├── partner.py         # Partner, Address
│   │   ├── pricelist.py       # Pricelist, PricelistItem
│   │   ├── coupon.py          # Coupon
│   │   ├── cart.py            # Cart, CartLine
│   │   ├── order.py           # SaleOrder, SaleOrderLine
│   │   ├── shipping.py        # ShippingMethod stub
│   │   └── payment.py         # PaymentTransaction
│   └── utils/
│       ├── state_machine.py   # Generic FSM (same interface as WMS)
│       └── pricing.py         # Pricelist evaluation helpers
├── alembic/
│   ├── env.py
│   └── versions/
│       └── 0001_initial.py
├── alembic.ini.template
├── pyproject.toml
└── README.md
```

### Backend Services
- **`db.py`** — `Base`, `engine_factory(dsn)`, `session_factory()` — mirrors WMS exactly.
- **`mixins.py`** — `TimestampMixin`, `ActiveMixin`, `NameMixin`, `CurrencyMixin`.
- **`utils/state_machine.py`** — generic FSM: same class API as WMS so agents reuse the same extension pattern.
- **`utils/pricing.py`** — `evaluate_pricelist(pricelist, variant, qty)` pure function; called by `Pricelist.get_price()`.

### Key Relationships
```
ProductTemplate ──< ProductVariant >── ProductVariantAttributeLine ──> ProductAttributeValue
                                                                              │
                                                                     ProductAttribute

Partner ──< Address

Cart ──< CartLine >── ProductVariant
Cart ──> Pricelist
Cart ──> Coupon

SaleOrder ──> Partner
SaleOrder ──< SaleOrderLine >── ProductVariant
SaleOrder ──> Coupon
SaleOrder ──> ShippingMethod
SaleOrder ──< PaymentTransaction
```

### Infrastructure
- **Alembic** — `env.py` reads `DATABASE_URL` from `.env`; `0001_initial.py` creates all tables.
- **pyproject.toml** — `[project]` with `sqlalchemy>=2.0`, `alembic>=1.13`, `python-dotenv>=1.0`; dev extras for `pytest`, `pytest-cov`.

---

## Implementation Strategy

Work in three parallel streams after scaffolding is done:

1. **Scaffolding** (must finish first) — package skeleton, `db.py`, `mixins.py`, `state_machine.py`, `pyproject.toml`.
2. **Catalog stream** (parallelizable after scaffolding) — category, product, attribute models.
3. **Commerce stream** (parallelizable after scaffolding) — partner/address, pricelist/coupon, cart, order, shipping, payment.
4. **Integration** (depends on both streams) — `models/__init__.py` re-exports, Alembic migration, test suite, README.

---

## Task Breakdown Preview

| # | Task | Depends on | Parallel? |
|---|---|---|---|
| 001 | Package scaffold: `db.py`, `mixins.py`, `utils/state_machine.py`, `pyproject.toml`, `alembic.ini.template` | — | No (foundation) |
| 002 | Product catalog models: `ProductCategory`, `ProductTemplate`, `ProductVariant`, `ProductAttribute`, `ProductAttributeValue`, association table | 001 | Yes |
| 003 | Partner & Address models | 001 | Yes |
| 004 | Pricing models: `Pricelist`, `PricelistItem`, `utils/pricing.py`, `Pricelist.get_price()` | 001 | Yes |
| 005 | Coupon model + `Coupon.is_valid()` | 004 | Yes |
| 006 | Cart & CartLine models: `add_line()`, `remove_line()`, `compute_totals()`, `checkout()` stub | 002, 003, 004, 005 | No |
| 007 | SaleOrder & SaleOrderLine: state machine, `confirm()`, `cancel()`, `mark_shipped()`, `mark_delivered()`, `apply_coupon()` | 002, 003, 005 | No |
| 008 | ShippingMethod stub + PaymentTransaction state machine | 007 | Yes |
| 009 | `models/__init__.py` re-exports + Alembic initial migration (`0001_initial.py`) | 002–008 | No |
| 010 | Full test suite (≥85% coverage) + README | 009 | No |

---

## Dependencies

- **Internal**: None — foundational template.
- **External**: `sqlalchemy>=2.0`, `alembic>=1.13`, `python-dotenv>=1.0`, dev: `pytest`, `pytest-cov`.

---

## Success Criteria (Technical)

1. `python -c "from ecommerce_core.models import *"` exits cleanly — no circular imports.
2. `Base.metadata.create_all()` output matches `alembic upgrade head` schema — zero drift.
3. Unit test: `Cart.checkout()` → valid `SaleOrder` with correct line totals, coupon discount, and `PaymentTransaction(state='draft')`.
4. Unit test: `Pricelist.get_price()` returns correct price for `fixed`, `percentage`, and `formula` compute modes.
5. Unit test: `SaleOrder` state machine rejects invalid transitions (e.g., `cancel()` from `shipped`).
6. Unit test: `PaymentTransaction` state machine covers happy path (draft → captured) and failure path.
7. `pytest --cov=ecommerce_core` reports ≥85% coverage.

---

## Estimated Effort

| Task | Estimate |
|---|---|
| 001 Scaffold | 30 min |
| 002 Product catalog | 45 min |
| 003 Partner/Address | 20 min |
| 004 Pricing engine | 40 min |
| 005 Coupon | 20 min |
| 006 Cart + checkout | 45 min |
| 007 SaleOrder | 45 min |
| 008 Shipping + Payment | 30 min |
| 009 Migration + re-exports | 30 min |
| 010 Tests + README | 60 min |
| **Total** | **~6 hours** |

---

## Tasks Created
- [ ] 001.md - Package Scaffold (parallel: false)
- [ ] 002.md - Product Catalog Models (parallel: true)
- [ ] 003.md - Partner & Address Models (parallel: true)
- [ ] 004.md - Pricing Models & Engine (parallel: true)
- [ ] 005.md - Coupon Model (parallel: true)
- [ ] 006.md - Cart & Checkout (parallel: false)
- [ ] 007.md - SaleOrder & SaleOrderLine (parallel: false)
- [ ] 008.md - ShippingMethod Stub & PaymentTransaction (parallel: true)
- [ ] 009.md - Model Re-exports & Alembic Migration (parallel: false)
- [ ] 010.md - Test Suite & README (parallel: false)

Total tasks: 10
Parallel tasks: 4 (002, 003, 004, 005 run concurrently after 001)
Sequential tasks: 6
Estimated total effort: ~6 hours
