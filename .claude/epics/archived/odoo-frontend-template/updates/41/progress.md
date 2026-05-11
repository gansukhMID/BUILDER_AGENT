# Issue #41: USER API Routers — Progress

## Status: COMPLETE

## Date: 2026-05-11

## What was done

Created the USER API routers for the odoo-frontend backend, replacing the stub health endpoint with full CRUD-style endpoints.

### Files created/modified

- `APPS/odoo-frontend/backend/schemas/users.py` — new file with Pydantic schemas:
  - `UserOut` — id, email, is_active, is_verified, last_login_at
  - `ProfileOut` — display_name, avatar_url, bio, phone, timezone, locale
  - `MembershipOut` — tier (str), started_at, expires_at; handles MembershipTier enum via `from_orm_obj` classmethod
  - `UserDetailOut` — composite: user fields + nested profile + membership
  - `ActivityEventOut` — id, event_type, occurred_at, ip_address
  - `UserOrderOut` — id, state, total_amount (Decimal), created_at

- `APPS/odoo-frontend/backend/routers/users.py` — replaced stub with 4 endpoints:
  - `GET /users` — list all users ordered by id
  - `GET /users/{user_id}` — user detail with profile and most-recent membership
  - `GET /users/{user_id}/activity` — last 50 activity events ordered by occurred_at desc
  - `GET /users/{user_id}/orders` — all orders for user

- `APPS/odoo-frontend/backend/tests/test_users.py` — 5 tests covering all endpoints

## Test results

```
5 passed in 0.48s
routers/users.py — 100% coverage
schemas/users.py — 98% coverage
```

## Key implementation notes

- `MembershipTier` is a Python enum; serialized to string via `.value` in `MembershipOut.from_orm_obj()`
- `Order.total_amount` is `Decimal` (Numeric 18,4) — exposed as `Optional[Decimal]` in schema
- `ActivityEvent.occurred_at` confirmed as the correct field name (set server-side on insert)
- `Order.created_at` comes from `TimestampMixin`
- No auth required on any read endpoint (public)

## Commit

`f5084ff` — "Issue #41: USER API routers — list, detail, activity, orders"
