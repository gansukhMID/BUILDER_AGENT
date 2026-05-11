---
issue: 46
stream: backend-implementation
started: 2026-05-11T05:37:01Z
status: completed
---
## Scope
Create schemas/store.py, routers/store.py, edit main.py

## Progress
- Read all model files (SaleOrder, ProductTemplate, Coupon, Partner, concrete.py)
- Discovered SaleOrder has no user_id; uses note field to store "user_id:<id>" tag
- Created schemas/store.py with full Pydantic schema set
- Created routers/store.py with all 6 endpoints:
  - GET /store/products (public) — product listing with variant counts
  - GET /store/products/{id} (public) — product detail with variants
  - POST /store/coupons/validate (public) — coupon validation
  - POST /store/orders (auth) — create order from cart lines, optional coupon
  - GET /store/orders (auth) — list current user's orders
  - GET /store/orders/{id} (auth) — order detail, 403 for wrong user
- Edited main.py to register store router at /store prefix
- Added tests/test_store.py with 15 tests covering all acceptance criteria
- All 43 tests pass; overall coverage 86%, routers/store.py at 88%
- Committed: Issue #46: /store router — products, coupons, orders endpoints
