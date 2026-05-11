---
name: odoo-frontend-template
description: Next.js + FastAPI web application that exposes all 3 TEMPLATE_CORE libraries (USER, WMS, ECOMMERCE) through REST API and an Odoo-style admin dashboard UI
status: backlog
created: 2026-05-11T01:36:59Z
---

# PRD: odoo-frontend-template

## Executive Summary

BUILDER_AGENT contains three production-ready SQLAlchemy template libraries (USER, WMS, ECOMMERCE) that define 35 domain models inspired by Odoo. These templates are backend-only — no API, no UI exists. This PRD specifies a reference web application (`APPS/odoo-frontend/`) that wires those templates together into a deployable, Odoo-style admin dashboard: a **FastAPI REST backend** serving concrete implementations of all three template libraries, and a **Next.js frontend** that presents Warehouse, E-commerce, and User Management modules in a cohesive sidebar-driven UI.

The result is a demonstration and starter application that any developer can fork, extend, and deploy.

---

## Problem Statement

The three TEMPLATE_CORE libraries are useful as building blocks, but there is no runnable application that shows how they fit together, how to subclass the abstract USER models, how to wire FastAPI routes to SQLAlchemy sessions, or how to render Odoo-style views on top of them. Developers consuming these templates must figure out the integration layer from scratch.

Without a reference frontend + backend, the templates are underutilised — they prove correctness (via tests) but not usability.

---

## User Stories

### US-1 — Warehouse Operator
> As a warehouse operator, I want to view all warehouses and their locations, browse current inventory (quants), and see a list of pending stock pickings, so that I can manage daily operations without touching the database directly.

**Acceptance Criteria:**
- Dashboard shows count of warehouses, total SKUs, and open pickings
- `/wms/warehouses` lists all warehouses with location count
- `/wms/locations` renders an indented tree matching the `complete_name` hierarchy
- `/wms/inventory` shows a filterable table of (product, location, lot, qty)
- `/wms/pickings` lists pickings with state badge (draft / confirmed / in_progress / done)

### US-2 — E-commerce Manager
> As an e-commerce manager, I want to browse the product catalog (templates + variants), view and filter sale orders, and inspect order detail including lines, status, and payment state.

**Acceptance Criteria:**
- `/ecommerce/products` lists ProductTemplates with variant count and list price
- `/ecommerce/orders` shows SaleOrders with state badge; filterable by state
- `/ecommerce/orders/:id` shows order header, line items, totals, and linked PaymentTransaction state
- Coupon list at `/ecommerce/coupons` shows code, discount, and usage stats

### US-3 — Admin / User Manager
> As an admin, I want to list all users, view their profile, membership tier, and recent activity events, so that I can monitor usage and support requests.

**Acceptance Criteria:**
- `/users` lists users with email, membership tier badge, and last login
- `/users/:id` shows profile fields, current membership dates, and last 20 activity events
- `/users/:id/orders` shows order history for that user

### US-4 — Developer (API Consumer)
> As a developer integrating this system, I want fully documented REST endpoints for all three domains, so that I can build custom UIs or scripts without reading source code.

**Acceptance Criteria:**
- FastAPI auto-generates Swagger UI at `/docs` and ReDoc at `/redoc`
- Every endpoint has description, request schema, and response schema
- All 200, 404, and 422 response shapes are documented

### US-5 — Authenticated User
> As any user of the system, I want to log in with email + password and have my session authenticated via JWT, so that API and UI access is protected.

**Acceptance Criteria:**
- `POST /auth/register` creates a user; returns JWT
- `POST /auth/login` validates credentials; returns JWT (access token, 24 h expiry)
- `GET /auth/me` returns current user from token
- Frontend redirects unauthenticated visitors to `/login`
- JWT stored in httpOnly cookie (Next.js middleware validates on every route)

### US-6 — Dashboard Overview
> As any authenticated user, I want a summary dashboard showing key metrics across all three modules so I can orient quickly.

**Acceptance Criteria:**
- `/dashboard` shows stat cards: total users, active memberships, warehouses, open pickings, total products, open orders
- Cards link to the relevant module list page
- Data fetched from a single `GET /stats` API endpoint

---

## Functional Requirements

### Backend (FastAPI)

**FR-1**: Concrete model layer — subclass all abstract USER models with `__tablename__` definitions; extend WMS and ECOMMERCE models as-is or with minor concrete aliases.

**FR-2**: Single SQLite database for development (`odoo_frontend.db`); database URL configurable via `DATABASE_URL` environment variable.

**FR-3**: Alembic migration — one `0001_initial` migration that creates all tables for USER + WMS + ECOMMERCE concrete models.

**FR-4**: Auth endpoints:
- `POST /auth/register` — create user, return JWT
- `POST /auth/login` — validate password hash, return JWT
- `GET /auth/me` — return current user (requires valid JWT)

**FR-5**: WMS API (`/wms/*`):
- `GET /wms/warehouses` — list all warehouses
- `GET /wms/locations` — hierarchical location list (with `complete_name`)
- `GET /wms/products` — list products (id, name, tracking_type, active)
- `GET /wms/inventory` — list quants (product_name, location_name, lot, quantity)
- `GET /wms/pickings` — list pickings (reference, state, picking_type, scheduled_date)
- `GET /wms/pickings/:id` — picking detail with move lines

**FR-6**: ECOMMERCE API (`/ecommerce/*`):
- `GET /ecommerce/products` — list ProductTemplates with variant count
- `GET /ecommerce/products/:id` — template detail with variants and attribute values
- `GET /ecommerce/orders` — list SaleOrders (reference, partner, state, total)
- `GET /ecommerce/orders/:id` — order detail with lines and PaymentTransaction
- `GET /ecommerce/coupons` — list coupons with usage count

**FR-7**: USER API (`/users/*`):
- `GET /users` — list users (id, email, membership tier, last_login_at)
- `GET /users/:id` — user detail with profile and membership
- `GET /users/:id/activity` — last 50 activity events
- `GET /users/:id/orders` — user's order history

**FR-8**: Stats endpoint:
- `GET /stats` — returns `{ users, active_memberships, warehouses, open_pickings, products, open_orders }`

**FR-9**: Seed script — `backend/seed.py` populates the database with realistic sample data (2 warehouses, 10 locations, 20 products, 5 pickings, 3 users, 10 sale orders, 5 coupons).

### Frontend (Next.js)

**FR-10**: Odoo-style shell layout — collapsible sidebar with module icons (WMS, Ecommerce, Users), top navbar with user avatar + logout, breadcrumb.

**FR-11**: WMS module pages: Warehouse list, Location tree, Inventory table (filterable by location), Picking list with state badges, Picking detail.

**FR-12**: Ecommerce module pages: Product catalog grid/list toggle, Order list with state filter, Order detail.

**FR-13**: User Management pages: User table with tier badges, User profile page, Activity log timeline.

**FR-14**: Login page (`/login`) with email + password form; redirects to `/dashboard` on success.

**FR-15**: Dashboard overview with 6 stat cards (FR-8 data).

**FR-16**: API client module (`lib/api.ts`) — typed fetch wrapper with JWT injection and base URL from `NEXT_PUBLIC_API_URL`.

---

## Non-Functional Requirements

- **NFR-1 Type safety**: TypeScript strict mode (`"strict": true`) in frontend; Pydantic v2 schemas for all FastAPI request/response models.
- **NFR-2 Test coverage**: Backend API routes ≥80% coverage via pytest; at minimum one integration test per router module.
- **NFR-3 Responsive UI**: All pages usable on 1280 px desktop and 768 px tablet (no mobile-first requirement).
- **NFR-4 Dev startup**: `uvicorn main:app --reload` and `npm run dev` each start in under 10 seconds on a modern laptop.
- **NFR-5 No external services**: No Redis, no Celery, no email service — SQLite only for dev. External service hooks are stubs only.
- **NFR-6 Auth security**: Passwords stored as bcrypt hashes (passlib); JWT signed with HS256 using `SECRET_KEY` env var; tokens expire in 24 h.
- **NFR-7 Error handling**: 404 and 422 from API must surface as user-friendly messages in the UI (toast or inline).

---

## Success Criteria

1. `cd APPS/odoo-frontend/backend && uvicorn main:app --reload` starts without errors and Swagger UI loads at `http://localhost:8000/docs`.
2. `cd APPS/odoo-frontend/frontend && npm run dev` starts without errors and the dashboard loads at `http://localhost:3000`.
3. A developer can register a user, log in, and browse WMS → Ecommerce → Users pages without a 500 error.
4. Backend test suite passes with ≥80% coverage: `pytest tests/ --cov=. --cov-report=term-missing`.
5. `npm run build` in the frontend directory exits 0 (no TypeScript errors, no missing imports).

---

## Constraints & Assumptions

- **Template immutability**: `TEMPLATE_CORE/` files are never modified — only consumed as Python packages.
- **Database**: SQLite for dev; PostgreSQL-compatible SQL only (no SQLite-specific functions).
- **Auth scope**: Single-role system (all authenticated users see everything); no RBAC in this iteration.
- **Python version**: 3.11+ (required by TEMPLATE_CORE's `Self` type hints).
- **Node version**: 20 LTS.
- **Package manager**: `pip` + `pyproject.toml` for backend; `npm` for frontend.

---

## Out of Scope

- Real payment gateway integration (PaymentTransaction state is set manually via seed data)
- Email verification or password reset flows
- Multi-tenant / multi-company support
- Mobile-responsive design below 768 px
- Production deployment configuration (Docker, CI/CD, nginx)
- Real-time updates (WebSockets, SSE)
- RBAC / permissions system
- GraphQL API
- Dark mode

---

## Dependencies

- `TEMPLATE_CORE/USER` — provides AbstractUser and 8 other abstract models (must be installed as editable package: `pip install -e TEMPLATE_CORE/USER`)
- `TEMPLATE_CORE/WMS` — provides 10 concrete WMS models
- `TEMPLATE_CORE/ECOMMERCE` — provides 16 concrete ecommerce models
- `fastapi>=0.110`, `uvicorn[standard]`, `python-jose[cryptography]`, `passlib[bcrypt]`, `pydantic>=2.0`, `alembic>=1.13`
- `next@15`, `react@19`, `tailwindcss@4`, `typescript@5`
