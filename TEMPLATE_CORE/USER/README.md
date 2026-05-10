# User Core Template

Abstract SQLAlchemy 2.x base models for unified user management. Part of `TEMPLATE_CORE` — a library of reusable bases for AI agent-generated applications.

All 9 models use `__abstract__ = True`. The template creates **zero database tables**. Agents subclass each model, set `__tablename__`, and add FK columns.

---

## Model Reference

| Template Model | Purpose | Key Fields |
|---|---|---|
| `AbstractUser` | Core identity and credentials | `email`, `password_hash`, `is_active`, `is_verified`, `is_superuser` |
| `AbstractOAuthAccount` | Linked OAuth provider | `provider`, `provider_uid`, `access_token`, `token_expires_at` |
| `AbstractUserProfile` | Extended profile data | `display_name`, `avatar_url`, `bio`, `timezone`, `preferences` (JSON) |
| `AbstractMembership` | Subscription tier | `tier` (free/pro/vip), `started_at`, `expires_at`, `is_active` |
| `AbstractOrder` | Order header | `reference`, `state`, `total_amount`, `currency` |
| `AbstractOrderLine` | Line item | `product_ref`, `product_name`, `quantity`, `unit_price`, `line_total` |
| `AbstractPurchase` | Payment record | `amount`, `currency`, `status`, `external_ref`, `payment_method` |
| `AbstractReview` | Polymorphic user review | `target_type`, `target_id`, `rating` (1–5), `status` |
| `AbstractActivityEvent` | Append-only audit log | `event_type`, `user_id` (nullable), `metadata_` (JSON) |

---

## Quick Start

```python
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from user_core.db import Base, engine_from_url, session_factory
from user_core.models.user import AbstractUser
from user_core.models.oauth_account import AbstractOAuthAccount

class User(AbstractUser):
    __tablename__ = "user"
    # Add any application-specific columns:
    company_id: Mapped[int | None] = mapped_column(nullable=True)

class OAuthAccount(AbstractOAuthAccount):
    __tablename__ = "oauth_account"
    # Add the FK that the template leaves to you:
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

engine = engine_from_url("postgresql+psycopg2://user:pass@localhost/mydb")
Base.metadata.create_all(engine)
```

---

## Extension Patterns

### Merging `__table_args__`

For models that define `__table_args__` (Review, ActivityEvent, OAuthAccount),
merge instead of overriding:

```python
class Review(AbstractReview):
    __tablename__ = "review"
    __table_args__ = AbstractReview.__table_args__ + (
        UniqueConstraint("user_id", "target_type", "target_id"),
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
```

### Password Hashing

`set_password` and `check_password` are stubs. Override in your concrete class:

```python
from passlib.hash import argon2

class User(AbstractUser):
    __tablename__ = "user"

    def set_password(self, raw: str) -> None:
        self.password_hash = argon2.hash(raw)

    def check_password(self, raw: str) -> bool:
        if not self.password_hash:
            return False
        return argon2.verify(raw, self.password_hash)
```

### Alembic Setup

1. Copy `alembic.ini.template` → `alembic.ini` and set `DATABASE_URL`.
2. In `alembic/env.py`, import your concrete model module so `Base.metadata` is populated:

```python
import myapp.models  # noqa: F401
target_metadata = Base.metadata
```

3. Generate the initial migration:

```bash
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```

---

## Running Tests

```bash
pip install -e ".[dev]"
pytest tests/ -v --cov=user_core
```

---

## Dependencies

- `sqlalchemy>=2.0`
- `alembic>=1.13`
- `python-dotenv>=1.0`
