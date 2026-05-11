---
name: storefront
description: Customer-facing ecommerce storefront on top of the existing odoo-frontend app — product browsing, cart, checkout, and order history
status: backlog
created: 2026-05-11T04:51:14Z
---

# PRD: storefront

## Executive Summary

The `odoo-frontend` app currently has a fully functional admin dashboard (WMS, Ecommerce, User Management modules). There is no customer-facing surface — customers have no way to browse products, add items to a cart, or place orders through a UI. This PRD specifies a public storefront route group (`/store`) built on top of the existing FastAPI backend and Next.js frontend. It shares the same auth system, product catalog, and order models, but presents a consumer-grade shopping experience rather than an admin interface.

---

## Problem Statement

The admin dashboard exposes all ecommerce data to operators, but the customer side is completely absent. A developer forking this template must build the storefront from scratch. Without a reference storefront, the ECOMMERCE template library is only half-demonstrated — order creation, coupon application, and payment flows are exercised only in tests, not in a running UI.

---

## User Stories

### US-1 — Guest Shopper
> As a visitor, I want to browse all available products and see their prices and variants, so that I can decide what to buy before creating an account.

**Acceptance Criteria:**
- `/store` shows a product grid with name, price, and variant count — no login required
- `/store/products/[id]` shows product detail: name, price, available variants (sku + price), and an "Add to Cart" button per variant
- Cart item count is visible in the navbar at all times

### US-2 — Cart Management
> As a shopper, I want to add items to a cart, adjust quantities, and remove items, without being forced to log in first.

**Acceptance Criteria:**
- Cart state persisted in localStorage (survives page refresh)
- Cart page (`/store/cart`) shows line items: variant name, quantity, unit price, subtotal
- Quantity can be incremented/decremented inline; item removable
- Cart total displayed at bottom; "Proceed to Checkout" button links to `/store/checkout`
- Empty cart shows a friendly message with a link back to the store

### US-3 — Checkout & Coupon
> As a shopper, I want to apply a discount coupon and place my order, so that I can complete a purchase.

**Acceptance Criteria:**
- `/store/checkout` requires authentication — unauthenticated users are redirected to `/store/login`
- Coupon code field: calls `POST /store/coupons/validate`; shows discount amount or error inline
- Order summary shows items, subtotal, discount (if coupon applied), and final total
- "Place Order" calls `POST /store/orders`; on success redirects to `/store/orders/[id]`
- Validation errors (empty cart, invalid coupon) shown inline without page reload

### US-4 — Order History
> As a logged-in customer, I want to view my past orders and their status, so that I can track and review what I've purchased.

**Acceptance Criteria:**
- `/store/orders` lists the current user's orders: reference, date, total, state badge
- `/store/orders/[id]` shows order lines, totals, coupon discount (if any), and state
- Both pages redirect unauthenticated visitors to `/store/login`
- Orders are scoped to the current user — customers cannot see other users' orders

### US-5 — Store Authentication
> As a customer, I want to register and log in from the storefront without being exposed to the admin interface.

**Acceptance Criteria:**
- `/store/login` and `/store/register` pages with the same backend auth endpoints (`/auth/login`, `/auth/register`)
- Successful login redirects to the page the user originally tried to access (or `/store`)
- Store layout navbar shows "Login" when unauthenticated, and user email + "Logout" when authenticated
- Logout clears the cookie and redirects to `/store`

---

## Functional Requirements

### Backend — new `/store` router

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/store/products` | None | List all product templates (id, name, list_price, variant_count) |
| GET | `/store/products/{id}` | None | Product detail with variants (sku, default_price) |
| POST | `/store/coupons/validate` | None | Validate coupon code; return discount info or 404 |
| POST | `/store/orders` | Required | Create sale order from cart lines; returns created order |
| GET | `/store/orders` | Required | List current user's orders |
| GET | `/store/orders/{id}` | Required | Order detail (own orders only) |

### Frontend — new `(store)` route group

| Route | Auth | Description |
|-------|------|-------------|
| `/store` | None | Product grid homepage |
| `/store/products/[id]` | None | Product detail + variant selector + add to cart |
| `/store/cart` | None | Cart contents + proceed to checkout |
| `/store/checkout` | Required | Coupon + order summary + place order |
| `/store/orders` | Required | Customer's order list |
| `/store/orders/[id]` | Required | Order detail |
| `/store/login` | None | Customer login form |
| `/store/register` | None | Customer registration form |

### Storefront Layout
- Separate `(store)/layout.tsx` — no admin sidebar
- Top navbar: logo/brand name, "Products" link, cart icon with item count badge, auth state (Login or user email + Logout)
- Clean, consumer-friendly design (Tailwind CSS) — distinct from the admin dark theme

### Cart (Client-Side)
- State managed via React Context + localStorage
- Shape: `{ items: [{ variantId, variantSku, productName, unitPrice, qty }] }`
- Cart count badge on navbar updates reactively

---

## Non-Functional Requirements

- Public product endpoints must work without auth (no 401 for browsing)
- Order creation endpoint must reject requests from users viewing other users' orders (403)
- Store routes do not appear in the admin sidebar
- Admin routes remain completely unaffected by this change
- TypeScript strict mode for all new frontend files
- `npm run build` must pass with no type errors after changes

---

## Success Criteria

1. A visitor can browse products and add items to cart without logging in
2. A logged-in customer can apply a coupon, place an order, and see it in order history
3. Unauthenticated access to `/store/checkout`, `/store/orders` redirects to `/store/login`
4. Admin dashboard routes and sidebar are unmodified
5. `npm run build` passes; backend tests pass (≥80% coverage maintained)

---

## Constraints & Assumptions

- Cart is client-side only (localStorage) — no server-side cart/session
- Payment processing is out of scope; orders are created in `draft` state
- Product images are out of scope — text/price only
- The storefront shares the same SQLite database and FastAPI backend as the admin
- No separate customer role — any registered user can shop and access the admin (this is a demo/template app)
- Coupon validation is stateless (no usage tracking per user in this scope)

---

## Out of Scope

- Payment gateway integration (Stripe, PayPal, etc.)
- Product search / filtering / sorting
- Product images or media uploads
- Inventory reservation (stock check before order)
- Address / shipping management
- Email notifications (order confirmation)
- Customer role vs. admin role separation
- Mobile app / PWA

---

## Dependencies

- Existing: `GET /ecommerce/products` and `GET /ecommerce/products/{id}` (storefront router will replicate these publicly rather than reuse, to keep admin/store concerns separate)
- Existing: `POST /auth/login`, `POST /auth/register`, `GET /auth/me`
- Existing: `ecommerce_core.models.order.SaleOrder`, `SaleOrderLine`, `Coupon`
- Existing: `auth_utils.get_current_user` FastAPI dependency
- Frontend: Cart context wraps the `(store)` layout only
