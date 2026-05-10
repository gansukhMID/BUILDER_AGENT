---
name: ecommerce-core-template
description: Reusable SQLAlchemy base models for e-commerce platforms, Odoo-inspired, consumed by AI agents generating custom online store applications
status: backlog
created: 2026-05-10T13:06:31Z
---

# PRD: ecommerce-core-template

## Executive Summary

`TEMPLATE_CORE/ECOMMERCE` is a Python + SQLAlchemy library of reusable base models for e-commerce platforms. Inspired by Odoo's `sale`, `product`, and `account` module architecture, it provides a composable, agent-readable foundation covering product catalog, order management, customer/partner records, pricing & promotions, cart/checkout, and payment — so AI agents can generate fully functional online stores without rebuilding core commerce logic from scratch.

---

## Problem Statement

When an AI agent is tasked with generating a custom e-commerce backend for a client, it currently has no reliable starting point. It must design product, order, customer, pricing, and payment models from scratch each time — leading to inconsistent data models, missing edge cases (variant attributes, coupon stacking, order state rollback), and systems that are hard to maintain or extend.

The core e-commerce domain is well-understood and stable. Rebuilding it repeatedly wastes cycles and introduces variance. A canonical, well-structured template gives agents (and developers) a battle-tested foundation to build on, not fight through.

---

## User Stories

### US-1 — Agent generating a custom online store backend
**As** an AI agent tasked with building an e-commerce backend for a retail client,  
**I want** to inherit from `TEMPLATE_CORE/ECOMMERCE` base models,  
**So that** I can focus on client-specific customizations (storefront theme, carrier integrations, loyalty programs) rather than rebuilding catalog and order fundamentals.

**Acceptance Criteria:**
- Agent can import base models and extend them with additional columns/relationships without modifying template code.
- All core models have documented fields, relationships, and invariants in docstrings.
- Template ships with Alembic migration support so extended models can generate schema diffs cleanly.

### US-2 — Developer reviewing agent-generated store
**As** a developer reviewing AI-generated e-commerce code,  
**I want** to recognize familiar, Odoo-aligned model structure,  
**So that** I can quickly understand the data model and trust its correctness.

**Acceptance Criteria:**
- Model names and field semantics align with Odoo's `sale` / `product` / `account` module conventions (translated to Python/SQLAlchemy idioms).
- Relationships between models (product ↔ variant ↔ attribute, order ↔ order_line ↔ product) are explicit and enforced.
- No circular imports; each model in its own module.

### US-3 — Agent implementing checkout flow
**As** an AI agent adding a cart → checkout → payment flow,  
**I want** `Cart`, `CartLine`, and `PaymentTransaction` base models with full state machines,  
**So that** I can wire up a checkout process without reimplementing order creation and payment capture logic.

**Acceptance Criteria:**
- `Cart` supports adding/removing lines, applying coupons, and computing totals.
- `Cart.checkout()` method stub converts a cart into a confirmed `SaleOrder`.
- `PaymentTransaction` has a state machine (draft → pending → authorized → captured / failed / refunded).

### US-4 — Agent building product catalog with variants
**As** an AI agent generating a product listing page,  
**I want** `ProductTemplate`, `ProductVariant`, and `AttributeValue` base models,  
**So that** I can display a T-shirt with Size × Color combinations without designing the attribute matrix myself.

**Acceptance Criteria:**
- `ProductTemplate` is the merchandising unit; `ProductVariant` is the purchasable SKU.
- `ProductAttribute` + `ProductAttributeValue` model the dimension (Size: S, M, L).
- `ProductVariant` has a unique `(template, attribute_values)` combination constraint helper.
- Each variant has its own `default_price` with optional pricelist override.

### US-5 — Agent applying pricing rules and coupons
**As** an AI agent implementing a promotional campaign,  
**I want** `Pricelist` and `Coupon` base models,  
**So that** I can set up percentage discounts, fixed-amount reductions, and coupon codes without building the discount engine from scratch.

**Acceptance Criteria:**
- `PricelistItem` maps (product / category / all) to a price computation method (fixed / percentage discount / formula).
- `Coupon` has `code`, `discount_type`, `discount_value`, `min_order_amount`, `usage_limit`, and `used_count`.
- `SaleOrder.apply_coupon(code)` validates and records coupon use atomically.

---

## Functional Requirements

### FR-1: Core Model Set

| Model | Odoo Analogue | Purpose |
|---|---|---|
| `ProductCategory` | `product.category` | Hierarchical product classification |
| `ProductTemplate` | `product.template` | Merchandising unit: name, description, category, base price |
| `ProductAttribute` | `product.attribute` | Dimension definition (Size, Color, Material) |
| `ProductAttributeValue` | `product.attribute.value` | Dimension option (S, M, L / Red, Blue) |
| `ProductVariant` | `product.product` | Purchasable SKU: (template + attribute_values) → price, stock ref |
| `Partner` | `res.partner` | Customer / company record with contact info |
| `Address` | `res.partner` (type=delivery/invoice) | Shipping and billing addresses linked to Partner |
| `Pricelist` | `product.pricelist` | Named pricelist with currency |
| `PricelistItem` | `product.pricelist.item` | Rule: product/category scope → price computation |
| `Coupon` | `sale.coupon` | Discount code with usage rules |
| `Cart` | (Odoo website.cart) | Active shopping session linked to Partner |
| `CartLine` | (Odoo website.cart.line) | Product variant + qty in a cart |
| `SaleOrder` | `sale.order` | Confirmed customer order with state machine |
| `SaleOrderLine` | `sale.order.line` | Line item: variant, qty, unit price, discount, tax rate |
| `ShippingMethod` | `delivery.carrier` (stub) | Delivery method stub: name, carrier, price estimate |
| `PaymentTransaction` | `payment.transaction` | Payment attempt with state machine |

### FR-2: Base Mixin Classes
- `TimestampMixin` — `created_at`, `updated_at` auto-managed columns.
- `ActiveMixin` — soft-delete via `active: bool = True`.
- `NameMixin` — `name`, `code` (optional) with unique constraint helpers.
- `CurrencyMixin` — `currency` string field (ISO 4217, default `'USD'`).
- `Base` — declarative base shared across all models, importable as `from ecommerce_core.db import Base`.

### FR-3: Product Hierarchy & Variants
- `ProductCategory` must be self-referential (`parent_id` FK to itself).
- `ProductTemplate` holds the catalog presentation: name, description, `category_id`, `list_price`, `image_url`.
- `ProductVariant` holds the purchasable record: `template_id`, `default_price`, `sku` (unique), `barcode`.
- `ProductVariantAttributeLine` association table links variants to their selected `ProductAttributeValue` records.
- Helper property `ProductVariant.display_name` builds `"T-Shirt — Red / M"` from attribute values.

### FR-4: Pricing Engine
- `Pricelist` has `name`, `currency`, `active`.
- `PricelistItem` fields: `pricelist_id`, `applied_on` (all / category / product / variant), `compute_price` (fixed / percentage / formula), `price_discount`, `fixed_price`, `min_quantity`.
- `Pricelist.get_price(variant, qty)` method — evaluates applicable items in priority order and returns computed unit price.

### FR-5: Coupon
- `Coupon` fields: `code` (unique), `discount_type` (percentage / fixed), `discount_value`, `min_order_amount`, `usage_limit` (nullable = unlimited), `used_count`, `expiry_date`.
- `Coupon.is_valid(order_amount)` — checks expiry, usage limit, and minimum order.
- `SaleOrder.apply_coupon(code)` — validates coupon, stores `coupon_id` on order, increments `used_count` atomically.

### FR-6: Cart & Checkout
- `Cart` fields: `partner_id` (nullable for guest), `session_token` (unique), `pricelist_id`, `coupon_id`, `status` (active / abandoned / checked_out).
- `Cart.add_line(variant, qty)` — upserts `CartLine`.
- `Cart.remove_line(variant)` — removes `CartLine`.
- `Cart.compute_totals()` — returns `subtotal`, `discount`, `tax_amount`, `shipping_estimate`, `total`.
- `Cart.checkout(shipping_method_id, billing_address_id, shipping_address_id)` — creates and returns a `SaleOrder` in `confirmed` state, marks cart as `checked_out`.

### FR-7: SaleOrder State Machine
`SaleOrder.state` transitions:
```
draft → confirmed → processing → shipped → delivered
                ↘                        ↗
                 → cancelled
delivered → refunded  (partial refund via SaleOrderLine)
```
- `confirm()` — validates stock refs exist, transitions to `confirmed`.
- `cancel()` — allowed from `draft` or `confirmed` only.
- `mark_shipped(tracking_number)` — transitions to `shipped`.
- `mark_delivered()` — transitions to `delivered`.

### FR-8: Payment State Machine
`PaymentTransaction.state` transitions:
```
draft → pending → authorized → captured
                ↘            ↗
                 → failed
captured → refunded (partial or full)
```
- `PaymentTransaction` fields: `order_id`, `provider` (string, e.g. `'stripe'`), `provider_ref`, `amount`, `currency`, `state`.
- `authorize()`, `capture()`, `fail()`, `refund(amount)` method stubs.

### FR-9: Tax on Order Lines
- `SaleOrderLine.tax_rate` — decimal field (e.g. `0.10` for 10%).
- `SaleOrderLine.tax_amount` — computed property: `unit_price * qty * tax_rate`.
- No relational `Tax` model in core — agents add `TaxGroup` on top.

### FR-10: ShippingMethod Stub
- `ShippingMethod` fields: `name`, `carrier` (string), `price` (fixed rate), `active`.
- Agents override `estimate_price(order)` to implement dynamic pricing.

### FR-11: Alembic Integration
- `env.py` template pointing to `Base.metadata` from `ecommerce_core.db`.
- `alembic.ini.template` with placeholder DSN.
- Single initial migration generating all core tables.

### FR-12: Module Layout
```
TEMPLATE_CORE/ECOMMERCE/
├── ecommerce_core/
│   ├── __init__.py
│   ├── db.py                    # Base, engine factory, session factory
│   ├── mixins.py                # TimestampMixin, ActiveMixin, NameMixin, CurrencyMixin
│   ├── models/
│   │   ├── __init__.py          # re-exports all models
│   │   ├── category.py          # ProductCategory
│   │   ├── product.py           # ProductTemplate, ProductVariant
│   │   ├── attribute.py         # ProductAttribute, ProductAttributeValue, ProductVariantAttributeLine
│   │   ├── partner.py           # Partner, Address
│   │   ├── pricelist.py         # Pricelist, PricelistItem
│   │   ├── coupon.py            # Coupon
│   │   ├── cart.py              # Cart, CartLine
│   │   ├── order.py             # SaleOrder, SaleOrderLine
│   │   ├── shipping.py          # ShippingMethod (stub)
│   │   └── payment.py           # PaymentTransaction
│   └── utils/
│       ├── state_machine.py     # Generic FSM helper (shared pattern with WMS)
│       └── pricing.py           # Pricelist evaluation helpers
├── alembic/
│   ├── env.py
│   └── versions/
│       └── 0001_initial.py
├── alembic.ini.template
├── pyproject.toml
└── README.md
```

---

## Non-Functional Requirements

- **NFR-1 Extensibility**: All models use SQLAlchemy concrete mapped classes with documented extension points. Agents must be able to add columns and relationships via subclassing without touching template files.
- **NFR-2 Readability**: Every model class and non-obvious method has a one-line docstring. Field comments explain Odoo semantics where naming diverges.
- **NFR-3 DB Agnosticism**: Models must work with PostgreSQL (primary) and SQLite (for agent unit tests). No DB-specific column types in core; use SQLAlchemy-standard types only.
- **NFR-4 No Framework Dependencies**: Template has zero dependencies beyond `sqlalchemy`, `alembic`, and `python-dotenv`. No FastAPI, no Pydantic, no ORM extras — agents add those.
- **NFR-5 Agent Parseable**: File structure and naming conventions are stable and documented so agents can reliably locate and import the right class without semantic search.
- **NFR-6 Test Coverage**: Core model relationships, cart totals, pricing engine, coupon validation, state machines, and payment transitions covered by unit tests using SQLite in-memory DB. Target: ≥85% coverage on `ecommerce_core/`.
- **NFR-7 Consistency with WMS/USER Templates**: Mixin names, `db.py` patterns, `utils/state_machine.py` interface, and pyproject.toml structure must match `TEMPLATE_CORE/WMS` conventions so agents working across templates find a uniform interface.

---

## Success Criteria

1. An AI agent can generate a working custom online store backend (product listing + cart + checkout + order) by importing and extending `ecommerce-core-template` in under 30 minutes of agent runtime, with no changes to template files.
2. Schema generated from `Base.metadata.create_all()` matches Alembic migration output (no drift).
3. `Cart.checkout()` produces a valid `SaleOrder` with correct line totals, coupon discount applied, and `PaymentTransaction` in `draft` state — verified by unit test.
4. `Pricelist.get_price()` returns correct price for all three compute modes (fixed / percentage / formula) — verified by unit test.
5. All models importable from `ecommerce_core.models` without circular import errors.
6. A developer familiar with Odoo sale module can map every core template model to its Odoo analogue within 5 minutes of reading the README.

---

## Constraints & Assumptions

- **Python 3.11+** required.
- **SQLAlchemy 2.x** mapped class style (not legacy 1.x declarative).
- **Alembic 1.13+** for autogenerate support.
- Template does NOT implement multi-company or multi-currency conversion — single currency per pricelist.
- No async SQLAlchemy in core — agents add `AsyncSession` wrappers if needed.
- Guest checkout is supported via nullable `partner_id` on `Cart`; `SaleOrder` always requires a partner (created from guest info at checkout).
- `ProductVariant.stock_qty` is NOT stored in `ecommerce_core` — stock is delegated to `TEMPLATE_CORE/WMS` or an agent-provided inventory model.
- Payment provider integration (Stripe, PayPal, etc.) is out of scope — `PaymentTransaction` provides the model layer only.

---

## Out of Scope

- UI / API layer (no FastAPI routes, no GraphQL, no REST endpoints)
- Multi-currency conversion
- Multi-company / multi-warehouse stock reservation
- Subscription / recurring billing
- Digital product delivery (download links, license keys)
- Affiliate / referral tracking
- Review & rating system
- Email / notification triggers (agents add these)
- Tax group relational model (only `tax_rate` field on order line)
- Dynamic shipping rate API calls (only fixed-price `ShippingMethod` stub)
- Loyalty points / rewards programs

---

## Dependencies

- **Internal**: `TEMPLATE_CORE/WMS` is NOT a dependency — stock management is an optional peer, not a prerequisite.
- **External**:
  - `sqlalchemy>=2.0`
  - `alembic>=1.13`
  - `python-dotenv>=1.0`
  - Dev: `pytest`, `pytest-cov`
