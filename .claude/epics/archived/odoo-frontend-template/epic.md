---
name: odoo-frontend-template
status: backlog
created: 2026-05-11T01:36:59Z
updated: 2026-05-11T01:58:56Z
progress: 90%
prd: .claude/prds/odoo-frontend-template.md
github: https://github.com/gansukhMID/BUILDER_AGENT/issues/34
---

# Epic: odoo-frontend-template

## Overview

Wire the three TEMPLATE_CORE libraries (USER, WMS, ECOMMERCE) into a runnable reference application: a **FastAPI REST backend** with concrete model implementations and typed Pydantic responses, plus a **Next.js 15 frontend** with an Odoo-style sidebar dashboard. The app lives at `APPS/odoo-frontend/`.

Target: developer can `uvicorn main:app` + `npm run dev` and browse all three modules within 5 minutes of cloning.

---

## Architecture Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Backend framework | FastAPI | Pydantic v2 native, auto Swagger, async-capable |
| Frontend framework | Next.js 15 (App Router) | SSR + API routes, TypeScript, Vercel-deployable |
| CSS | Tailwind CSS 4 | Utility-first, no build step for CSS, Odoo-like spacing |
| Auth | JWT (HS256, python-jose) + bcrypt | Stateless, template-compatible, no Redis needed |
| Database (dev) | SQLite via SQLAlchemy 2.x | Zero-config, same as template tests |
| Migrations | Alembic (single `0001_initial`) | Consistent with template pattern |
| API client | Typed `fetch` wrapper (`lib/api.ts`) | No extra dep, tree-shakeable |

---

## Technical Approach

### Backend Layout
```
APPS/odoo-frontend/backend/
├── main.py              # FastAPI app factory, CORS, routers
├── db.py                # engine + session (reuses TEMPLATE_CORE pattern)
├── models/
│   └── concrete.py      # Subclass AbstractUser→User, etc.
├── schemas/
│   ├── auth.py          # LoginRequest, TokenResponse, MeResponse
│   ├── wms.py           # WarehouseOut, LocationOut, QuantOut, PickingOut
│   ├── ecommerce.py     # ProductTemplateOut, OrderOut, CouponOut
│   └── users.py         # UserOut, ProfileOut, ActivityOut
├── routers/
│   ├── auth.py          # /auth/*
│   ├── wms.py           # /wms/*
│   ├── ecommerce.py     # /ecommerce/*
│   └── users.py         # /users/* + /stats
├── seed.py              # Populate realistic sample data
├── alembic/
│   └── versions/0001_initial.py
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_wms.py
│   ├── test_ecommerce.py
│   └── test_users.py
└── pyproject.toml
```

### Frontend Layout
```
APPS/odoo-frontend/frontend/
├── app/
│   ├── layout.tsx           # Root layout (OdooShell)
│   ├── (auth)/login/page.tsx
│   ├── dashboard/page.tsx
│   ├── wms/
│   │   ├── page.tsx          # Warehouse list
│   │   ├── locations/page.tsx
│   │   ├── inventory/page.tsx
│   │   └── pickings/
│   │       ├── page.tsx
│   │       └── [id]/page.tsx
│   ├── ecommerce/
│   │   ├── page.tsx          # Product catalog
│   │   ├── orders/page.tsx
│   │   └── orders/[id]/page.tsx
│   └── users/
│       ├── page.tsx
│       └── [id]/page.tsx
├── components/
│   ├── layout/
│   │   ├── Sidebar.tsx
│   │   ├── Navbar.tsx
│   │   └── Breadcrumb.tsx
│   └── ui/
│       ├── DataTable.tsx
│       ├── StatCard.tsx
│       ├── Badge.tsx
│       └── Spinner.tsx
├── lib/
│   └── api.ts               # Typed fetch wrapper with JWT
├── middleware.ts             # JWT validation, redirect unauthenticated
└── package.json
```

### Template Consumption Pattern
- `user_core` abstract models → subclassed in `backend/models/concrete.py` (pattern from `TEMPLATE_CORE/USER/tests/concrete_models.py`)
- `wms_core` and `ecommerce_core` concrete models → used directly (no subclassing needed)
- All three packages installed as editable: `pip install -e ../../TEMPLATE_CORE/{USER,WMS,ECOMMERCE}`

---

## Implementation Strategy

**Two parallel tracks after scaffold:**
- **Track A (Backend)**: concrete models → FastAPI foundation → all four routers + auth
- **Track B (Frontend)**: Next.js scaffold with layout → module pages (unblocked once API contract known)

Both tracks join at integration testing.

---

## Task Breakdown Preview

| # | Title | Track | Parallel? |
|---|---|---|---|
| 001 | Project scaffold (dirs, pyproject.toml, package.json, .env.example) | Both | — |
| 002 | Concrete models + Alembic 0001_initial | A | After 001 |
| 003 | FastAPI foundation (main.py, db, CORS, health, Swagger) | A | After 002 |
| 004 | Auth API (register, login, me, JWT, bcrypt) | A | After 003 |
| 005 | WMS API routers (6 endpoints) | A | After 003, ∥ 004/006/007 |
| 006 | ECOMMERCE API routers (5 endpoints + /stats) | A | After 003, ∥ 004/005/007 |
| 007 | USER API routers (4 endpoints) | A | After 004, ∥ 005/006 |
| 008 | Next.js frontend scaffold + Odoo shell layout | B | After 001, ∥ 003–007 |
| 009 | WMS dashboard pages | B | After 005 + 008 |
| 010 | Ecommerce + User pages + seed script + backend tests | B+A | After 006/007 + 008 |

---

## Dependencies

- Python 3.11+, Node 20 LTS
- `TEMPLATE_CORE/USER`, `TEMPLATE_CORE/WMS`, `TEMPLATE_CORE/ECOMMERCE` (installed editable)
- External: `fastapi`, `uvicorn`, `python-jose`, `passlib[bcrypt]`, `pydantic>=2`, `alembic`
- External: `next@15`, `react@19`, `tailwindcss@4`, `typescript@5`

---

## Success Criteria (Technical)

1. `uvicorn main:app --reload` → Swagger at `localhost:8000/docs` with all routes listed
2. `npm run dev` → Dashboard at `localhost:3000`, all module pages render without console errors
3. `pytest tests/ --cov --cov-report=term-missing` → ≥80% backend coverage
4. `npm run build` → exit 0, zero TypeScript errors
5. End-to-end manual smoke: register → login → dashboard stats load → WMS inventory table shows seeded data → Ecommerce order detail renders

---

## Estimated Effort

10 tasks, executable in 2 parallel tracks. Estimated wall-clock: 2–3 hours with parallel agents.

---

## Tasks Created
- [ ] 001.md - Project Scaffold (parallel: false)
- [ ] 002.md - Concrete Models + Alembic Migration (parallel: false)
- [ ] 003.md - FastAPI Foundation (parallel: false)
- [ ] 004.md - Auth API (register, login, JWT) (parallel: true)
- [ ] 005.md - WMS API Routers (parallel: true)
- [ ] 006.md - ECOMMERCE API Routers + /stats (parallel: true)
- [ ] 007.md - USER API Routers (parallel: true)
- [ ] 008.md - Next.js Frontend Scaffold + Odoo Shell Layout (parallel: true)
- [ ] 009.md - WMS Dashboard Pages (parallel: true)
- [ ] 010.md - Ecommerce + User Pages + Seed Script + Backend Tests (parallel: true)

Total tasks: 10
Parallel tasks: 8
Sequential tasks: 2 (001, 002, 003 are sequential chain)
Estimated total effort: 20 hours (wall-clock ~3 hours with parallelism)
