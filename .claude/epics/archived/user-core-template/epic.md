---
name: user-core-template
status: completed
created: 2026-05-08T05:47:53Z
updated: 2026-05-10T05:33:51Z
progress: 100%
prd: .claude/prds/user-core-template.md
github: https://github.com/gansukhMID/BUILDER_AGENT/issues/12
---

# Epic: user-core-template

## Overview

Build `TEMPLATE_CORE/USER` — a Python + SQLAlchemy 2.x library of **abstract** base models for unified user management. Unlike `wms-core-template` (which uses concrete tables), every model here uses `__abstract__ = True`, so the template creates zero database tables itself. Agents subclass each abstract model, set `__tablename__`, and run `alembic revision --autogenerate` to produce their schema.

The library covers: registration + auth (email/password + OAuth), user profiles, membership tiers (Free/Pro/VIP), order + line-item history, purchase records, user reviews (polymorphic), and append-only activity logging.

---

## Architecture Decisions

### AD-1: Pure Abstract Base Classes
All 9 domain models use `__abstract__ = True`. `Base.metadata` remains empty in the template. Agents do:
```python
from user_core.models.user import AbstractUser
class User(AbstractUser):
    __tablename__ = "user"
    company_id: Mapped[int] = mapped_column(ForeignKey("company.id"))
```
This guarantees zero template modification — a core constraint.

### AD-2: Enums Isolated in `enums.py`
All domain enums (`MembershipTier`, `OrderState`, `PurchaseStatus`, `ReviewStatus`) live in `user_core/enums.py`. Model files import from `enums.py` only. This eliminates the only credible source of circular imports in this package.

### AD-3: No Cross-Model Python Imports
Model files import only from `user_core.db`, `user_core.mixins`, and `user_core.enums`. FK columns are typed as `Mapped[int]` (bare integer) — not `Mapped[User]`. Relationships are defined in the subclass by the agent, not in the abstract base. This enforces the no-circular-imports constraint structurally.

### AD-4: Password Stubs as Extension Points
`AbstractUser.set_password()` and `.check_password()` are documented stubs that return `None`/`False`. Subclasses override them with their chosen hashing library (bcrypt, argon2-cffi, etc.). This keeps the template dependency-free while making the extension point obvious.

### AD-5: No Initial Migration
Because abstract models create no tables, the template ships no Alembic migration. `alembic/versions/` is empty. The `env.py` template is wired to `Base.metadata` — agents import their concrete models into `env.py` to populate it.

### AD-6: `PrimaryKeyMixin` Included in All Abstract Bases
Every abstract model includes `PrimaryKeyMixin` which declares `id: Mapped[int] = mapped_column(primary_key=True)`. This means agents get PK without redeclaring it. Agents needing UUID PKs override by redefining `id` in their subclass.

---

## Technical Approach

### Package Structure
```
TEMPLATE_CORE/USER/
├── user_core/
│   ├── __init__.py          # __version__ = "0.1.0"
│   ├── db.py                # Base (DeclarativeBase), engine_from_url, session_factory
│   ├── mixins.py            # TimestampMixin, SoftDeleteMixin, PrimaryKeyMixin
│   ├── enums.py             # MembershipTier, OrderState, PurchaseStatus, ReviewStatus
│   └── models/
│       ├── __init__.py      # re-exports all 9 abstract models
│       ├── user.py          # AbstractUser
│       ├── oauth_account.py # AbstractOAuthAccount
│       ├── user_profile.py  # AbstractUserProfile
│       ├── membership.py    # AbstractMembership
│       ├── order.py         # AbstractOrder, AbstractOrderLine
│       ├── purchase.py      # AbstractPurchase
│       ├── review.py        # AbstractReview
│       └── activity_event.py # AbstractActivityEvent
├── alembic/
│   ├── env.py
│   └── versions/            # empty — agents generate their own
├── alembic.ini.template
├── pyproject.toml
└── README.md
tests/
├── conftest.py              # SQLite in-memory engine, session fixture
├── concrete_models.py       # Minimal concrete subclasses of all 9 abstracts
└── test_core.py             # 8+ tests covering all success criteria
```

### SQLAlchemy 2.x Patterns
- `Mapped[T]` + `mapped_column()` throughout — no legacy `Column()`.
- `from __future__ import annotations` in every model file.
- `TYPE_CHECKING` guards for any cross-model type hints (none expected given AD-3).
- Enums: `sqlalchemy.Enum(PythonEnum, name="enum_name")` — named to avoid DB conflicts.

### Key Column Specifications
| Model | Notable Columns |
|---|---|
| AbstractUser | `email` unique+indexed, `password_hash` nullable, `last_login_at`, `is_active`, `is_verified`, `is_superuser` |
| AbstractOAuthAccount | `UniqueConstraint("provider", "provider_uid")`, `token_expires_at` |
| AbstractUserProfile | `preferences: JSON`, `timezone` default "UTC", `locale` default "en" |
| AbstractMembership | `tier: MembershipTier` enum, `expires_at` nullable (None = non-expiring) |
| AbstractOrder | `state: OrderState` enum, `total_amount: Numeric(18,4)`, `reference` |
| AbstractOrderLine | `product_ref: str` (no FK — agent adds), `line_total: Numeric(18,4)` stored |
| AbstractPurchase | `status: PurchaseStatus`, `external_ref` for gateway ID, nullable `order_id` |
| AbstractReview | `(target_type, target_id)` polymorphic, `CheckConstraint("rating BETWEEN 1 AND 5")`, `Index("(target_type, target_id)")` |
| AbstractActivityEvent | `event_type: str`, `metadata_: JSON` (trailing `_` avoids keyword), `occurred_at` server-default only |

---

## Implementation Strategy

Build in dependency order within each task. No task depends on another task's model files (AD-3 guarantees this), so Tasks 2–6 are fully parallelizable after Task 1.

---

## Task Breakdown Preview

| # | Task | Parallel? | Depends On |
|---|---|---|---|
| 1 | Foundation: `db.py`, `mixins.py`, `enums.py` | — | — |
| 2 | `AbstractUser` + `AbstractOAuthAccount` | ✓ | Task 1 |
| 3 | `AbstractUserProfile` + `AbstractMembership` | ✓ | Task 1 |
| 4 | `AbstractOrder` + `AbstractOrderLine` | ✓ | Task 1 |
| 5 | `AbstractPurchase` | ✓ | Task 1 |
| 6 | `AbstractReview` + `AbstractActivityEvent` | ✓ | Task 1 |
| 7 | `models/__init__.py`, `wms_core/__init__.py`, package `__init__` files | — | Tasks 2–6 |
| 8 | Alembic `env.py` + `alembic.ini.template` | ✓ | Task 1 |
| 9 | `pyproject.toml` + `README.md` | ✓ | — |
| 10 | Tests: `conftest.py`, `concrete_models.py`, `test_core.py` | — | Tasks 7, 8 |

---

## Dependencies

- `sqlalchemy>=2.0`
- `alembic>=1.13`
- `python-dotenv>=1.0`
- Dev: `pytest>=7.0`, `pytest-cov>=4.0`
- Internal: None

---

## Success Criteria (Technical)

1. `python -c "from user_core.models import *; from user_core.db import Base; assert len(Base.metadata.tables) == 0"` — zero tables registered.
2. All 9 concrete subclasses in `tests/concrete_models.py` + `Base.metadata.create_all()` produces a valid SQLite schema with no errors.
3. `pytest tests/ -v --cov=user_core` passes with ≥ 80% coverage.
4. `python -c "import user_core.models"` — no `ImportError` or `CircularImportError`.
5. Every abstract class passes `inspect.getdoc(cls)` — non-None docstring.

---

## Estimated Effort

- Tasks 1, 7, 10: ~1 hour each (foundation + wiring + tests)
- Tasks 2–6: ~30 min each (well-specified, parallel-safe)
- Tasks 8–9: ~20 min each (boilerplate)
- **Total**: ~5–6 hours (or ~2 hours with 5 parallel agents on Tasks 2–6 + 8–9 simultaneously)

## Tasks Created
- [ ] 001.md - Foundation: db.py, mixins.py, enums.py (parallel: false)
- [ ] 002.md - AbstractUser + AbstractOAuthAccount (parallel: true)
- [ ] 003.md - AbstractUserProfile + AbstractMembership (parallel: true)
- [ ] 004.md - AbstractOrder + AbstractOrderLine (parallel: true)
- [ ] 005.md - AbstractPurchase (parallel: true)
- [ ] 006.md - AbstractReview + AbstractActivityEvent (parallel: true)
- [ ] 007.md - Package wiring: models/__init__.py + __init__.py files (parallel: false)
- [ ] 008.md - Alembic env.py + alembic.ini.template (parallel: true)
- [ ] 009.md - pyproject.toml + README.md (parallel: true)
- [ ] 010.md - Tests: conftest.py, concrete_models.py, test_core.py (parallel: false)

Total tasks: 10
Parallel tasks: 7 (002-006, 008, 009)
Sequential tasks: 3 (001, 007, 010)
Estimated total effort: 5-6 hours
