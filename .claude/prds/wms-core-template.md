---
name: wms-core-template
description: Reusable SQLAlchemy base models for warehouse management systems, Odoo-inspired, consumed by AI agents generating custom WMS applications
status: backlog
created: 2026-05-08T04:06:48Z
---

# PRD: wms-core-template

## Executive Summary

`TEMPLATE_CORE/WMS` is a Python + SQLAlchemy library of reusable base models for Warehouse Management Systems. Inspired by Odoo's proven stock module architecture, it provides a composable, agent-readable foundation that AI agents can extend into fully functional, domain-specific WMS applications without rebuilding core inventory logic from scratch.

---

## Problem Statement

When an AI agent is tasked with generating a custom WMS for a client, it currently has no reliable starting point. It must design warehouse, location, inventory, and movement models from scratch each time — leading to inconsistent data models, missing edge cases (lot tracking, multi-step transfers, location hierarchies), and systems that are hard to maintain or extend.

The core WMS domain is well-understood and stable. Rebuilding it repeatedly wastes cycles and introduces variance. A canonical, well-structured template gives agents (and developers) a battle-tested foundation to build on, not fight through.

---

## User Stories

### US-1 — Agent generating a custom WMS
**As** an AI agent tasked with building a WMS for a logistics client,  
**I want** to inherit from `TEMPLATE_CORE/WMS` base models,  
**So that** I can focus on client-specific customizations (carrier integrations, billing rules, UI) rather than rebuilding inventory fundamentals.

**Acceptance Criteria:**
- Agent can import base models and extend them with additional columns/relationships without modifying template code.
- All core models have documented fields, relationships, and invariants in docstrings.
- Template ships with Alembic migration support so extended models can generate schema diffs cleanly.

### US-2 — Developer reviewing agent-generated WMS
**As** a developer reviewing AI-generated WMS code,  
**I want** to recognize familiar, Odoo-aligned model structure,  
**So that** I can quickly understand the data model and trust its correctness.

**Acceptance Criteria:**
- Model names and field semantics align with Odoo's stock module conventions (translated to Python/SQLAlchemy idioms).
- Relationships between models (quant ↔ location ↔ product, picking ↔ moves ↔ move lines) are explicit and enforced.
- No circular imports; each model in its own module.

### US-3 — Agent extending picking workflows
**As** an AI agent adding a multi-step "pick → pack → ship" workflow,  
**I want** `PickingType` and `Picking` base models that support chaining and operation types,  
**So that** I can wire up custom routing rules without reimplementing transfer state machines.

**Acceptance Criteria:**
- `PickingType` supports at minimum: receipt, delivery, internal transfer.
- `Picking` has a state machine (draft → confirmed → in_progress → done / cancelled).
- `Move` and `MoveLine` link to `Picking` and carry quantity, lot, and location data.

### US-4 — Agent building inventory reporting
**As** an AI agent generating inventory dashboards,  
**I want** a `Quant` model that is the single source of truth for on-hand stock,  
**So that** I can query current inventory by location, product, and lot without reconstructing it from move history.

**Acceptance Criteria:**
- `Quant` stores (product, location, lot) → quantity as the materialized inventory view.
- Quants are updated atomically when moves are validated.
- Quants support negative quantities (for transit/expected scenarios) as a config option.

---

## Functional Requirements

### FR-1: Core Model Set
The template must include the following SQLAlchemy model base classes:

| Model | Odoo Analogue | Purpose |
|---|---|---|
| `Warehouse` | `stock.warehouse` | Top-level facility with input/output/stock locations |
| `Location` | `stock.location` | Hierarchical storage location (internal, view, customer, supplier, transit, inventory) |
| `Product` | `product.product` | Storable item with UoM reference |
| `Lot` | `stock.lot` | Lot / serial number tied to a product |
| `Quant` | `stock.quant` | Materialized on-hand quantity: (product, location, lot) → qty |
| `PickingType` | `stock.picking.type` | Operation type definition (receive / deliver / internal) |
| `Picking` | `stock.picking` | Transfer operation header with state machine |
| `Move` | `stock.move` | Planned movement: product from location_src to location_dest |
| `StockRule` | `stock.rule` | Procurement / replenishment rule |

### FR-2: Base Mixin Classes
- `TimestampMixin` — `created_at`, `updated_at` auto-managed columns.
- `ActiveMixin` — soft-delete via `active: bool = True`.
- `NameMixin` — `name`, `code` (optional) with unique constraint helpers.
- `Base` — declarative base shared across all models, importable as `from wms_core.db import Base`.

### FR-3: Location Hierarchy
- `Location` must be self-referential (parent_id FK to itself).
- Location types: `internal`, `view`, `customer`, `supplier`, `transit`, `inventory`, `production`.
- Helper `complete_name` property that builds the full path (e.g., `WH/Stock/Shelf-A/Bin-01`).
- `is_ancestor_of(location)` method for routing logic.

### FR-4: State Machine on Picking
`Picking.state` transitions:
```
draft → confirmed → in_progress → done
                 ↘               ↗
                  → cancelled
```
Provide a `validate()` method stub that subclasses override to move quants.

### FR-5: Quant Management
- `Quant.add_quantity(product, location, qty, lot=None)` class method — creates or updates quant atomically.
- `Quant.get_available(product, location)` — returns available quantity.
- Quant updates triggered from `Move.validate()`.

### FR-6: Package Support (Optional Extension Point)
- Define `Package` model stub (empty beyond `id`, `name`, `location_id`) so agents can enable it without schema conflicts.

### FR-7: Alembic Integration
- `env.py` template pointing to `Base.metadata` from `wms_core.db`.
- `alembic.ini.template` with placeholder DSN.
- Single initial migration generating all core tables.

### FR-8: Module Layout
```
TEMPLATE_CORE/WMS/
├── wms_core/
│   ├── __init__.py
│   ├── db.py                  # Base, engine factory, session factory
│   ├── mixins.py              # TimestampMixin, ActiveMixin, NameMixin
│   ├── models/
│   │   ├── __init__.py        # re-exports all models
│   │   ├── warehouse.py
│   │   ├── location.py
│   │   ├── product.py
│   │   ├── lot.py
│   │   ├── quant.py
│   │   ├── picking_type.py
│   │   ├── picking.py
│   │   ├── move.py
│   │   ├── stock_rule.py
│   │   └── package.py         # stub
│   └── utils/
│       ├── state_machine.py   # generic FSM helper
│       └── hierarchy.py       # location tree helpers
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

- **NFR-1 Extensibility**: All models use SQLAlchemy's `__abstract__ = True` or concrete mapped classes with documented extension points. Agents must be able to add columns and relationships via subclassing without touching template files.
- **NFR-2 Readability**: Every model class and non-obvious method has a one-line docstring. Field comments explain Odoo semantics where naming diverges.
- **NFR-3 DB Agnosticism**: Models must work with PostgreSQL (primary) and SQLite (for agent unit tests). No DB-specific column types in the core; use SQLAlchemy-standard types only.
- **NFR-4 No Framework Dependencies**: Template has zero dependencies beyond `sqlalchemy`, `alembic`, and `python-dotenv`. No FastAPI, no Pydantic, no ORM extras — agents add those.
- **NFR-5 Agent Parseable**: File structure and naming conventions are stable and documented so agents can reliably locate and import the right class without semantic search.
- **NFR-6 Test Coverage**: Core model relationships and quant logic covered by unit tests using SQLite in-memory DB. Target: ≥80% coverage on `wms_core/`.

---

## Success Criteria

1. An AI agent can generate a working custom WMS (with receipt + delivery workflows) by importing and extending `wms-core-template` in under 30 minutes of agent runtime, with no changes to template files.
2. Schema generated from `Base.metadata.create_all()` matches Alembic migration output (no drift).
3. `Quant.get_available()` returns correct on-hand quantities after a round-trip receipt → delivery cycle in the unit test suite.
4. All models importable from `wms_core.models` without circular import errors.
5. A developer familiar with Odoo stock module can map every core template model to its Odoo analogue within 5 minutes of reading the README.

---

## Constraints & Assumptions

- **Python 3.11+** required (uses `match` statements in state machine helper, `Self` type hint).
- **SQLAlchemy 2.x** mapped class style (not legacy 1.x declarative).
- **Alembic 1.13+** for autogenerate support.
- Template does NOT implement a full Odoo multi-company structure — single-company model only.
- Lot tracking is per-product optional (enabled via `Product.tracking = 'lot' | 'serial' | 'none'`).
- No async SQLAlchemy in core — agents add `AsyncSession` wrappers if needed.
- UoM (Unit of Measure) is stored as a string enum, not a relational model, to keep the template lean.

---

## Out of Scope

- UI / API layer (no FastAPI routes, no GraphQL, no REST endpoints)
- Multi-company / multi-currency support
- Barcode scanning integration
- Carrier / shipping label generation
- Batch picking / wave picking (agents add these on top)
- Purchase orders / sales orders (only stock movements, not procurement source documents)
- Landed costs / valuation accounting
- MRP / manufacturing integration
- Real-time inventory reservation locking (optimistic concurrency only in core)

---

## Dependencies

- **Internal**: None — this is a foundational template with no upstream TEMPLATE_CORE deps.
- **External**:
  - `sqlalchemy>=2.0`
  - `alembic>=1.13`
  - `python-dotenv>=1.0` (for `alembic/env.py` DSN loading)
  - Dev: `pytest`, `pytest-cov`
