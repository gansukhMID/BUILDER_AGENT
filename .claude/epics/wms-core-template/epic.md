---
name: wms-core-template
status: backlog
created: 2026-05-08T06:04:54Z
updated: 2026-05-08T06:27:58Z
progress: 0%
prd: .claude/prds/wms-core-template.md
github: https://github.com/gansukhMID/BUILDER_AGENT/issues/1
---

# Epic: wms-core-template

## Overview

Build `TEMPLATE_CORE/WMS` — a Python + SQLAlchemy 2.x library of reusable base models for Warehouse Management Systems. The library is consumed by AI agents that extend it into client-specific WMS applications. Architecture mirrors Odoo's `stock` module, translated into SQLAlchemy mapped classes. Zero framework dependencies beyond `sqlalchemy`, `alembic`, and `python-dotenv`.

Implementation follows a strict dependency chain: each layer builds on the previous so imports never fail mid-construction.

---

## Architecture Decisions

| Decision | Choice | Rationale |
|---|---|---|
| ORM | SQLAlchemy 2.x declarative mapped classes | Typed, modern, autogenerate-friendly |
| Shared Base | Single `Base` in `db.py`, imported everywhere | Prevents metadata split; Alembic sees all tables |
| Abstract mixins | Mixin classes (not `__abstract__ = True` models) | Agents subclass concrete models, not abstract ones |
| Quant as materialized view | `Quant` table updated on move validation | Query speed; avoids reconstructing inventory from history |
| State machine | Generic FSM helper in `utils/state_machine.py` | Reusable; keeps `Picking` model clean |
| Location hierarchy | Self-referential FK + `complete_name` property | Mirrors Odoo; enables routing logic |
| DB agnosticism | SQLAlchemy standard types only | Works on PostgreSQL (prod) and SQLite (tests) |
| Lot tracking | Per-product flag (`tracking`: `lot`/`serial`/`none`) | Optional complexity; agents enable per product |

---

## Technical Approach

### Backend Models (all layers)

**Layer 0 — Foundation** (`db.py`, `mixins.py`)
- `db.py`: declarative `Base`, `engine_factory(dsn)`, `SessionFactory`, `get_session()` context manager.
- `mixins.py`: `TimestampMixin` (`created_at`, `updated_at`), `ActiveMixin` (`active: bool`), `NameMixin` (`name`, `code`).

**Layer 1 — Topology** (`location.py`, `warehouse.py`)
- `Location`: self-referential via `parent_id`; `location_type` enum; `complete_name` computed property; `is_ancestor_of()`.
- `Warehouse`: top-level facility; FKs to `Location` for `lot_stock_id`, `wh_input_stock_loc_id`, `wh_output_stock_loc_id`.
- `utils/hierarchy.py`: `build_full_path(location)`, `get_all_children(location_id, session)`.

**Layer 2 — Items** (`product.py`, `lot.py`)
- `Product`: `uom` as string enum; `tracking` enum (`none`/`lot`/`serial`); `can_be_sold`, `can_be_purchased` flags.
- `Lot`: FK to `Product`; `ref` (internal reference); unique constraint on `(name, product_id)`.

**Layer 3 — Inventory State** (`quant.py`)
- `Quant`: composite unique on `(product_id, location_id, lot_id)`; `quantity`, `reserved_quantity`.
- Class methods: `add_quantity()` (upsert with row-level locking hint), `get_available()`.

**Layer 4 — Operations** (`picking_type.py`, `picking.py`, `move.py`)
- `PickingType`: `code` enum (`incoming`/`outgoing`/`internal`); default source/destination location FKs.
- `Picking`: state machine via FSM helper; `validate()` stub; `cancel()` guard.
- `Move`: `product_id`, `location_src_id`, `location_dest_id`, `product_qty`, `qty_done`; `validate()` calls `Quant.add_quantity()`.
- `utils/state_machine.py`: `StateMachine(transitions)` — declarative transition table, `can(state, action)`, `apply(obj, action)`.

**Layer 5 — Rules + Stubs** (`stock_rule.py`, `package.py`)
- `StockRule`: procurement/replenishment rule; FKs to `PickingType`, `Location` (src/dest), `Warehouse`.
- `Package`: stub — `id`, `name`, `location_id` only; agents extend.

### Infrastructure (`alembic/`)
- `env.py` imports `Base` from `wms_core.db`, reads DSN from `DATABASE_URL` env var.
- `alembic.ini.template`: placeholder DSN, migration path wired.
- `0001_initial.py`: auto-generated migration covering all tables.

### Testing (`tests/`)
- SQLite in-memory DB fixture via `pytest` + `get_session()`.
- Tests: model instantiation, location hierarchy, quant round-trip (receipt → delivery), state machine transitions.
- Target: ≥80% coverage on `wms_core/`.

---

## Implementation Strategy

Strict bottom-up build matching the dependency chain. Each task is independently testable before the next begins. No circular imports by construction — each module only imports from modules completed in earlier tasks.

```
Task 1: db.py + project scaffold
Task 2: mixins.py
  ↓
Task 3: location.py + utils/hierarchy.py    Task 5: product.py  ← parallel after Task 2
Task 4: warehouse.py (needs location)
  ↓
Task 6: lot.py (needs product)
  ↓
Task 7: quant.py (needs location + product + lot)
Task 8: picking_type.py (needs warehouse)   ← parallel with Task 7
  ↓
Task 9: picking.py + utils/state_machine.py (needs picking_type)
  ↓
Task 10: move.py + stock_rule.py + package.py + models/__init__ + alembic + tests
```

---

## Task Breakdown Preview

| # | Task | Depends On | Parallel? |
|---|---|---|---|
| 1 | Project scaffold + `db.py` | — | No (foundation) |
| 2 | `mixins.py` | 1 | No |
| 3 | `location.py` + `utils/hierarchy.py` | 1, 2 | With 5 |
| 4 | `warehouse.py` | 1, 2, 3 | No |
| 5 | `product.py` | 1, 2 | With 3 |
| 6 | `lot.py` | 5 | No |
| 7 | `quant.py` | 3, 5, 6 | With 8 |
| 8 | `picking_type.py` | 4 | With 7 |
| 9 | `picking.py` + `utils/state_machine.py` | 8 | No |
| 10 | `move.py` + `stock_rule.py` + `package.py` + `models/__init__` + Alembic + tests | 7, 9 | No |

Parallel windows:
- **Window A**: Tasks 3 + 5 (location and product share no files)
- **Window B**: Tasks 7 + 8 (quant and picking_type share no files)

---

## Dependencies

- `sqlalchemy>=2.0`
- `alembic>=1.13`
- `python-dotenv>=1.0`
- Dev: `pytest`, `pytest-cov`

---

## Success Criteria (Technical)

1. `python -c "from wms_core.models import Warehouse, Location, Product, Lot, Quant, PickingType, Picking, Move, StockRule"` exits 0 with no import errors.
2. `Base.metadata.create_all()` on SQLite produces the same table set as running `alembic upgrade head`.
3. Unit test: receipt `Move` validated → `Quant` quantity increases; delivery `Move` validated → `Quant` quantity decreases.
4. `Location.complete_name` returns `"WH/Stock/Shelf-A"` for a 3-level hierarchy.
5. `Picking.validate()` raises `InvalidTransition` if state is not `in_progress`.
6. `pytest --cov=wms_core` reports ≥80% coverage.

---

## Estimated Effort

| Task | Effort |
|---|---|
| Tasks 1–2 (db + mixins) | 1–2 hrs |
| Tasks 3–4 (location + warehouse) | 2–3 hrs |
| Tasks 5–6 (product + lot) | 1–2 hrs |
| Task 7 (quant) | 2–3 hrs |
| Tasks 8–9 (picking_type + picking + FSM) | 3–4 hrs |
| Task 10 (move + stock_rule + alembic + tests) | 4–5 hrs |
| **Total** | **13–19 hrs** |

---

## Tasks Created

- [ ] #4 - Project Scaffold + db.py (parallel: false)
- [ ] #8 - Core Mixins (parallel: false)
- [ ] #10 - Location Model + Hierarchy Utilities (parallel: true)
- [ ] #11 - Warehouse Model (parallel: false)
- [ ] #2 - Product Model (parallel: true)
- [ ] #5 - Lot Model (parallel: false)
- [ ] #7 - Quant Model (parallel: true)
- [ ] #3 - PickingType Model (parallel: true)
- [ ] #6 - Picking Model + StateMachine Utility (parallel: false)
- [ ] #9 - Move, StockRule, Package + Alembic Integration + Test Suite (parallel: false)

Total tasks: 10
Parallel tasks: 4 (#10, #2, #7, #3)
Sequential tasks: 6 (#4, #8, #11, #5, #6, #9)
Estimated total effort: 13–19 hours
