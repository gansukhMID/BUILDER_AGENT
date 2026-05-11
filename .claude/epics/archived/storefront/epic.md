---
name: storefront
status: completed
created: 2026-05-11T05:07:07Z
updated: 2026-05-11T06:59:52Z
progress: 100%
prd: .claude/prds/storefront.md
github: https://github.com/gansukhMID/BUILDER_AGENT/issues/45
---

# Epic: storefront

## Overview

Add a customer-facing ecommerce storefront to the existing `APPS/odoo-frontend` app. The app already has a Next.js + FastAPI admin dashboard. This epic layers a public `/store` route group (Next.js) and a `/store` FastAPI router on top of the existing codebase — sharing the same auth, database, and models — without touching any existing admin code.

## Architecture Decisions

1. **Separate route group**: `app/(store)/` with its own `layout.tsx` (navbar, no sidebar). Admin `app/(app)/` layout is untouched.
2. **Client-side cart**: React Context + localStorage. No backend cart session needed. Cart shape: `{ items: [{ variantId, variantSku, productName, unitPrice, qty }] }`.
3. **New `/store` backend router**: Duplicates product read endpoints from `/ecommerce` as public (no auth). Order creation and history are authenticated. Keeps admin and store concerns cleanly separated.
4. **Same auth system**: Reuses `/auth/login` and `/auth/register`. Store pages handle their own redirect-to-login flow via Next.js middleware (existing `middleware.ts` already protects `/dashboard/*` — extend to protect `/store/checkout` and `/store/orders/*`).
5. **SaleOrder creation**: `POST /store/orders` creates a `SaleOrder` + `SaleOrderLine` rows linked to the authenticated user. Coupon discount is recorded on the order.

## Technical Approach

### Backend Services

**New file: `routers/store.py`**
- `GET /store/products` — public, list ProductTemplates
- `GET /store/products/{id}` — public, ProductTemplate + variants
- `POST /store/coupons/validate` — public, validates coupon code, returns `{valid, discount_type, discount_value}`
- `POST /store/orders` — auth required, body: `{lines: [{variant_id, qty}], coupon_code?}`, creates SaleOrder + lines, returns order id
- `GET /store/orders` — auth required, current user's SaleOrders
- `GET /store/orders/{id}` — auth required, own order only (403 if not owner)

**New file: `schemas/store.py`**
- `StoreProductOut`, `StoreProductDetailOut`, `StoreVariantOut`
- `CouponValidateRequest`, `CouponValidateOut`
- `CartLineIn`, `CreateOrderRequest`, `StoreOrderOut`, `StoreOrderDetailOut`, `StoreOrderLineOut`

**Edit: `main.py`** — register `store.router` with prefix `/store`

### Frontend Components

**New: `app/(store)/layout.tsx`** — navbar with logo, Products link, cart badge, auth state

**New: `lib/cart.tsx`** — `CartContext`, `useCart()` hook, localStorage persistence

**New pages:**
- `app/(store)/store/page.tsx` — product grid
- `app/(store)/store/products/[id]/page.tsx` — product detail + variant selector + add to cart
- `app/(store)/store/cart/page.tsx` — cart line items, quantities, proceed to checkout
- `app/(store)/store/checkout/page.tsx` — coupon field, order summary, place order
- `app/(store)/store/orders/page.tsx` — my orders list
- `app/(store)/store/orders/[id]/page.tsx` — order detail
- `app/(store)/store/login/page.tsx` — login form (calls `/auth/login`)
- `app/(store)/store/register/page.tsx` — register form (calls `/auth/register`)

**Edit: `middleware.ts`** — protect `/store/checkout` and `/store/orders/*` routes

**Edit: `lib/api.ts`** — add store API functions (or new `lib/store-api.ts`)

### Infrastructure

No new infrastructure. Same SQLite DB, same FastAPI server, same Next.js dev server.

## Implementation Strategy

Tasks are ordered to minimize blocking:
1. Backend store router + schemas (unblocks all frontend work)
2. Cart context (unblocks product detail and cart pages)
3. Store layout + auth pages (unblocks authenticated routes)
4. Product pages (depends on 1 + 2)
5. Cart + checkout pages (depends on 1 + 2 + 3)
6. Order history pages (depends on 1 + 3)

Tasks 2 and 3 can run in parallel with each other after task 1.

## Task Breakdown Preview

| # | Task | Depends On | Parallel |
|---|------|-----------|---------|
| 001 | Backend: `/store` router, schemas, register in main.py | — | No (foundation) |
| 002 | Frontend: Cart context (CartContext + useCart + localStorage) | — | Yes (with 003) |
| 003 | Frontend: Store layout + navbar + auth pages (login, register) | — | Yes (with 002) |
| 004 | Frontend: Product grid (`/store`) + product detail (`/store/products/[id]`) | 001, 002 | Yes (with 005, 006) |
| 005 | Frontend: Cart page + checkout page | 001, 002, 003 | Yes (with 004, 006) |
| 006 | Frontend: Order history pages (`/store/orders`, `/store/orders/[id]`) | 001, 003 | Yes (with 004, 005) |
| 007 | Middleware update + integration smoke test (`npm run build` passing) | 004, 005, 006 | No (final gate) |

## Dependencies

- `ecommerce_core.models.product.ProductTemplate`, `ProductVariant`
- `ecommerce_core.models.order.SaleOrder`, `SaleOrderLine`
- `ecommerce_core.models.coupon.Coupon`
- `auth_utils.get_current_user`
- Existing `middleware.ts` (extend, not replace)

## Success Criteria (Technical)

- `GET /store/products` returns 200 with no auth header
- `POST /store/orders` returns 401 without token, 201 with valid token + cart lines
- `GET /store/orders/{id}` returns 403 when requesting another user's order
- `npm run build` exits 0 with no TypeScript errors
- All existing backend tests still pass

## Estimated Effort

7 tasks — estimated 1–2 days of parallel agent execution.

## Tasks Created

- [ ] 001.md — Backend: /store router, schemas, register in main.py (parallel: false)
- [ ] 002.md — Frontend: Cart context (CartContext + useCart + localStorage) (parallel: true)
- [ ] 003.md — Frontend: Store layout + navbar + auth pages (parallel: true)
- [ ] 004.md — Frontend: Product grid + product detail pages (parallel: true)
- [ ] 005.md — Frontend: Cart page + checkout page (parallel: true)
- [ ] 006.md — Frontend: Order history pages (parallel: true)
- [ ] 007.md — Middleware update + npm run build passing (parallel: false)

Total tasks: 7
Parallel tasks: 5
Sequential tasks: 2
Estimated total effort: 19 hours
