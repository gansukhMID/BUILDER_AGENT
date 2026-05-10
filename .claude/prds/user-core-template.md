---
name: user-core-template
description: Abstract SQLAlchemy 2.x base models for unified user management — auth, profiles, memberships, orders, purchases, reviews, and activity tracking — consumed by AI agents generating custom user systems
status: backlog
created: 2026-05-08T05:43:00Z
---

# PRD: user-core-template

## Executive Summary

`TEMPLATE_CORE/USER` is a Python + SQLAlchemy 2.x library of **abstract** base models for unified user management systems. Using SQLAlchemy's `__abstract__ = True` pattern, every model is a true base class — agents generate concrete subclasses with client-specific table names and columns, never touching the template. The library covers the full user lifecycle: registration, authentication (email/password + OAuth), profile management, membership tiers, order history, purchase history, review history, and basic activity tracking.

---

## Problem Statement

Every custom application that serves end users needs a user system. When an AI agent builds such an application, it currently has to design and implement user authentication, profile management, membership logic, and history tables from scratch. Each iteration re-solves the same domain problems (password hashing hooks, OAuth provider linking, tier expiry, review polymorphism) differently, producing inconsistent and hard-to-maintain data models.

`TEMPLATE_CORE/USER` makes user domain logic a one-time investment: agents extend the abstract base classes, add application-specific columns, and skip the foundational design work entirely.

---

## User Stories

### US-1 — Agent generating a SaaS application
**As** an AI agent building a SaaS platform with Free/Pro/VIP tiers,  
**I want** to subclass `AbstractUser`, `AbstractMembership`, and `AbstractOAuthAccount`,  
**So that** I can focus on billing logic and feature gating rather than reimplementing auth and membership tracking.

**Acceptance Criteria:**
- Agent subclasses `AbstractUser` with `__tablename__ = "user"` and a custom `company_id` FK column — no template modification required.
- `AbstractMembership.tier` enum maps to Free, Pro, VIP with an expiry date for paid tiers.
- `AbstractOAuthAccount` supports linking multiple providers per user (Google, GitHub, etc.).

### US-2 — Agent building an e-commerce storefront
**As** an AI agent generating an online store,  
**I want** `AbstractOrder`, `AbstractOrderLine`, and `AbstractPurchase` base classes,  
**So that** I can track what users bought, the line-item detail, and payment outcomes without building those tables from scratch.

**Acceptance Criteria:**
- `AbstractOrder` has a state machine: `draft → placed → confirmed → shipped → delivered / cancelled`.
- `AbstractOrderLine` stores product reference (string/UUID, not a FK — agents wire the FK in the subclass), quantity, and unit price.
- `AbstractPurchase` records payment outcome (status, amount, currency, payment method) and links to an `AbstractOrder`.

### US-3 — Agent building a marketplace with user-generated content
**As** an AI agent generating a marketplace,  
**I want** `AbstractReview` with polymorphic target support,  
**So that** user reviews can target products, sellers, or services with a single base model.

**Acceptance Criteria:**
- `AbstractReview` uses `target_type: str` + `target_id: int` (polymorphic ref) so agents don't need a separate review table per entity type.
- Rating is 1–5 integer with a database check constraint.
- Review has `status: draft | published | flagged | removed`.

### US-4 — Agent adding compliance / audit features
**As** an AI agent tasked with adding GDPR-compliant activity logging,  
**I want** `AbstractActivityEvent` with event type, timestamp, IP, user agent, and JSON metadata,  
**So that** I can log login events, profile updates, and consent changes without designing the schema myself.

**Acceptance Criteria:**
- `AbstractActivityEvent.event_type` is a string (agents define their own enum values).
- `metadata_` column is `JSON` type for arbitrary structured payload.
- Activity events are append-only (no update methods exposed).
- Events link to the user via `user_id` FK (set in subclass).

---

## Functional Requirements

### FR-1: Abstract Model Set

All base classes use `__abstract__ = True`. Agents subclass them and define `__tablename__`.

| Model | Purpose |
|---|---|
| `AbstractUser` | Core user entity: credentials, verification, soft-delete |
| `AbstractOAuthAccount` | Linked OAuth provider account (one user, many providers) |
| `AbstractUserProfile` | Extended user profile: avatar, bio, preferences |
| `AbstractMembership` | Membership tier record per user |
| `AbstractOrder` | Order header with state machine |
| `AbstractOrderLine` | Line item within an order |
| `AbstractPurchase` | Payment / purchase record tied to an order |
| `AbstractReview` | User-written review with polymorphic target |
| `AbstractActivityEvent` | Append-only activity / audit log entry |

### FR-2: AbstractUser
- `id: int` — primary key (defined in subclass via mixin)
- `email: str` — unique, indexed, lowercase-normalized
- `password_hash: str | None` — nullable (OAuth-only users have no password)
- `is_active: bool` — default `True`; `False` = soft-deactivated
- `is_verified: bool` — default `False`; email verification status
- `is_superuser: bool` — default `False`
- `last_login_at: datetime | None`
- Inherits `TimestampMixin` (created_at, updated_at)
- `set_password(raw: str) -> None` — stub; subclass wires in bcrypt/argon2
- `check_password(raw: str) -> bool` — stub returning `False`; override in subclass

### FR-3: AbstractOAuthAccount
- `id: int` — PK
- `user_id: int` — FK to user table (defined in subclass)
- `provider: str` — e.g., `"google"`, `"github"`, `"facebook"`
- `provider_uid: str` — the provider's user identifier
- `access_token: str | None` — stored token (agents handle encryption)
- `refresh_token: str | None`
- `token_expires_at: datetime | None`
- Unique constraint: `(provider, provider_uid)`
- Inherits `TimestampMixin`

### FR-4: AbstractUserProfile
- `id: int` — PK
- `user_id: int` — FK to user (one-to-one enforced via unique constraint in subclass)
- `display_name: str | None`
- `avatar_url: str | None`
- `bio: str | None`
- `phone: str | None`
- `timezone: str` — default `"UTC"`
- `locale: str` — default `"en"`
- `preferences: dict | None` — `JSON` column for arbitrary agent-defined prefs
- Inherits `TimestampMixin`

### FR-5: AbstractMembership
- `id: int` — PK
- `user_id: int` — FK to user
- `tier: MembershipTier` — Enum: `free | pro | vip`
- `started_at: datetime` — when this tier began
- `expires_at: datetime | None` — `None` = non-expiring (Free tier)
- `is_active: bool` — computed helper; subclass may override with a hybrid property
- `cancelled_at: datetime | None`
- Inherits `TimestampMixin`

### FR-6: AbstractOrder + AbstractOrderLine
**AbstractOrder:**
- `id: int` — PK
- `user_id: int` — FK to user
- `reference: str` — human-readable order number (e.g., `ORD-20260508-001`)
- `state: OrderState` — Enum: `draft | placed | confirmed | shipped | delivered | cancelled`
- `currency: str` — ISO 4217, default `"USD"`
- `total_amount: Decimal` — `Numeric(18, 4)`
- `placed_at: datetime | None`
- `notes: str | None`
- Inherits `TimestampMixin`
- `cancel() -> None` — state machine stub
- `confirm() -> None` — state machine stub

**AbstractOrderLine:**
- `id: int` — PK
- `order_id: int` — FK to order
- `product_ref: str` — external product identifier (string; agents add FK in subclass)
- `product_name: str` — snapshot of name at time of order
- `quantity: Decimal` — `Numeric(18, 4)`
- `unit_price: Decimal` — `Numeric(18, 4)`
- `line_total: Decimal` — `Numeric(18, 4)` (computed: qty × price; stored for auditability)
- Inherits `TimestampMixin`

### FR-7: AbstractPurchase
- `id: int` — PK
- `user_id: int` — FK to user
- `order_id: int | None` — FK to order (nullable: standalone purchases without orders)
- `amount: Decimal` — `Numeric(18, 4)`
- `currency: str` — ISO 4217
- `status: PurchaseStatus` — Enum: `pending | completed | failed | refunded`
- `payment_method: str | None` — e.g., `"card"`, `"paypal"`, `"crypto"`
- `external_ref: str | None` — payment gateway transaction ID
- `purchased_at: datetime | None`
- Inherits `TimestampMixin`

### FR-8: AbstractReview
- `id: int` — PK
- `user_id: int` — FK to user
- `target_type: str` — entity type string (e.g., `"product"`, `"seller"`)
- `target_id: int` — entity PK
- `rating: int` — 1–5; enforced via `CheckConstraint("rating BETWEEN 1 AND 5")`
- `title: str | None`
- `body: str | None`
- `status: ReviewStatus` — Enum: `draft | published | flagged | removed`
- Index: `(target_type, target_id)` for efficient listing
- Inherits `TimestampMixin`

### FR-9: AbstractActivityEvent
- `id: int` — PK
- `user_id: int | None` — FK to user (nullable: pre-auth events)
- `event_type: str` — free-form string; agents define their event taxonomy
- `ip_address: str | None`
- `user_agent: str | None`
- `metadata_: dict | None` — `JSON` column (trailing underscore avoids Python keyword conflict)
- `occurred_at: datetime` — `server_default=func.now()`, not mutable after insert
- No `updated_at` — append-only semantics
- Index: `(user_id, occurred_at)` for chronological user feed

### FR-10: Shared Mixins
- `TimestampMixin` — `created_at`, `updated_at` auto-managed
- `SoftDeleteMixin` — `deleted_at: datetime | None`; `is_deleted` property; `soft_delete()` method
- `PrimaryKeyMixin` — `id: Mapped[int] = mapped_column(primary_key=True)` — included in abstract bases; agents inherit automatically

### FR-11: Module Layout
```
TEMPLATE_CORE/USER/
├── user_core/
│   ├── __init__.py
│   ├── db.py                     # Base, engine_from_url, session_factory
│   ├── mixins.py                 # TimestampMixin, SoftDeleteMixin, PrimaryKeyMixin
│   ├── enums.py                  # MembershipTier, OrderState, PurchaseStatus, ReviewStatus
│   └── models/
│       ├── __init__.py           # re-exports all abstract models
│       ├── user.py               # AbstractUser
│       ├── oauth_account.py      # AbstractOAuthAccount
│       ├── user_profile.py       # AbstractUserProfile
│       ├── membership.py         # AbstractMembership
│       ├── order.py              # AbstractOrder, AbstractOrderLine
│       ├── purchase.py           # AbstractPurchase
│       ├── review.py             # AbstractReview
│       └── activity_event.py    # AbstractActivityEvent
├── alembic/
│   ├── env.py
│   └── versions/                 # empty — agents generate their own migrations
├── alembic.ini.template
├── pyproject.toml
└── README.md
```

**Note on migrations**: Because all models are abstract, the template ships no initial migration. Agents run `alembic revision --autogenerate` against their concrete subclass models.

---

## Non-Functional Requirements

- **NFR-1 Abstract-only**: `__abstract__ = True` on every model class. No tables are created by the template itself. `Base.metadata` contains zero tables.
- **NFR-2 Zero extra dependencies**: Only `sqlalchemy>=2.0`, `alembic>=1.13`, `python-dotenv>=1.0`. No `passlib`, `pyjwt`, `cryptography`, `httpx`. Agents add auth libraries of their choice.
- **NFR-3 Docstrings on every class**: Each abstract model and every non-obvious method/property has a docstring explaining its purpose and extension points.
- **NFR-4 No circular imports**: Each model file imports only from `user_core.db`, `user_core.mixins`, and `user_core.enums`. No model imports another model.
- **NFR-5 DB agnosticism**: Column types limited to SQLAlchemy-standard types (`String`, `Integer`, `Boolean`, `Numeric`, `DateTime`, `JSON`). No `ARRAY`, no `TSVECTOR`, no PostgreSQL-specific extensions in the core.
- **NFR-6 SQLAlchemy 2.x style**: All annotations use `Mapped[T]` + `mapped_column()`. No legacy `Column()` style.
- **NFR-7 Testability**: A reference concrete implementation in `tests/concrete_models.py` instantiates all abstract classes with minimal configuration. Test suite uses SQLite in-memory. Target ≥ 80% coverage on `user_core/`.

---

## Success Criteria

1. `python -c "from user_core.models import *"` produces no errors and no tables in `Base.metadata`.
2. A concrete subclass of all 9 abstract models can be defined in < 50 lines, with `Base.metadata.create_all()` generating a valid schema.
3. An AI agent can produce a working user registration + OAuth login flow by extending `AbstractUser` and `AbstractOAuthAccount` without modifying any template file.
4. All 9 models have docstrings; `pydoc user_core.models` is readable without opening source.
5. `pytest tests/ --cov=user_core` passes with ≥ 80% coverage on Python 3.11+ and SQLite.

---

## Constraints & Assumptions

- **Python 3.11+** (`Self` type hint, `match` in utils).
- **SQLAlchemy 2.x** declarative mapped class style throughout.
- **Single-file enums**: All domain enums in `user_core/enums.py` — no enum defined inline in model files.
- Password hashing is **not** in scope — `set_password()` and `check_password()` are stubs with documented override points.
- Token storage (OAuth `access_token`) is plain string — agents add field-level encryption.
- Soft delete is opt-in via `SoftDeleteMixin` — not mandatory on every model.
- `preferences` and `metadata_` JSON columns use Python `dict`; serialization is SQLAlchemy's responsibility.
- No async SQLAlchemy in core — agents add `AsyncSession` wrappers.

---

## Out of Scope

- Password hashing implementation (no bcrypt/argon2 in template)
- JWT / session token generation and validation
- OAuth provider HTTP clients (no httpx/requests)
- Email verification sending (no SMTP)
- Rate limiting / brute-force protection
- Two-factor authentication
- Role-based access control (RBAC) beyond `is_superuser` flag
- Multi-tenancy / organization models
- Billing / subscription management (agents add Stripe integration on top)
- Full-text search on reviews
- Real-time notifications

---

## Dependencies

- **Internal**: None — foundational template, no upstream `TEMPLATE_CORE` deps.
- **External**:
  - `sqlalchemy>=2.0`
  - `alembic>=1.13`
  - `python-dotenv>=1.0`
  - Dev: `pytest>=7.0`, `pytest-cov>=4.0`
