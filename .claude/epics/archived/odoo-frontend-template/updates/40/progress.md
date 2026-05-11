# Issue #40: ECOMMERCE API Routers + /stats

**Status:** COMPLETED
**Commit:** d8fb359

## What was done

### Files created/updated

1. **`schemas/ecommerce.py`** (new)
   - `ProductVariantOut`, `ProductTemplateOut` (with `variant_count`), `ProductDetailOut`
   - `OrderLineOut`, `OrderOut`, `OrderDetailOut`
   - `CouponOut`, `StatsOut`
   - Fields mapped to actual model field names (`qty` → `quantity`, `subtotal` → `line_total`, computed `reference`/`currency`/`total_amount`)

2. **`routers/ecommerce.py`** (replaced stub)
   - `GET /ecommerce/products` — list with variant counts via subquery
   - `GET /ecommerce/products/{id}` — detail with joinedload variants, 404 if not found
   - `GET /ecommerce/orders` — list with computed `total` property
   - `GET /ecommerce/orders/{id}` — detail with lines, 404 if not found
   - `GET /ecommerce/coupons` — list all coupons
   - Kept `/health` endpoint

3. **`main.py`** (updated `/stats`)
   - Replaced placeholder with real DB counts using `func.count()`
   - users, active_memberships (cancelled_at IS NULL), warehouses, open_pickings (draft/confirmed/in_progress), products, open_orders (draft/confirmed/processing)

4. **`tests/test_ecommerce.py`** (new)
   - 6 tests: products list, product 404, orders list, order 404, coupons list, stats keys/types

## Test results

```
11 passed in 0.34s — 97% coverage
```

## Key field name decisions

- `SaleOrderLine.qty` → exposed as `quantity`
- `SaleOrderLine.subtotal` (computed property) → exposed as `line_total`
- `SaleOrder.total` (computed property) → exposed as `total_amount`
- `SaleOrder` has no `reference` field → constructed as `"SO-{id}"`
- `SaleOrder` has no `currency` field → hardcoded `"USD"`
