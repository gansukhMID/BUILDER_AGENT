# Issue #36 Progress: Concrete Models + Alembic Migration

**Status**: COMPLETED
**Commit**: 3f42b04

## What Was Done

### Task 1: db.py
Updated `APPS/odoo-frontend/backend/db.py` with sqlite-aware `_connect_args` (only sets `check_same_thread: False` for SQLite URLs).

### Task 2: models/concrete.py
Created `APPS/odoo-frontend/backend/models/concrete.py` with concrete subclasses for all 9 AbstractUser models:
- `User`, `OAuthAccount`, `UserProfile`, `Membership`, `Order`, `OrderLine`, `Purchase`, `Review`, `ActivityEvent`
- WMS and ECOMMERCE models imported to register with their Base objects.

### Task 3: alembic/env.py
Replaced stub with full implementation:
- `sys.path.insert` to make backend importable
- Loads all 3 metadata objects (`UserBase`, `WMSBase`, `ECBase`)
- Passes `target_metadata` as a list to Alembic context

### Task 4: alembic/versions/0001_initial.py
Created initial migration using `create_all`/`drop_all` on each Base's metadata.

### Task 5: Verification
- Fixed `pyproject.toml` build-backend from `setuptools.backends.legacy:build` (not available in setuptools 82.0.1) to `setuptools.build_meta`
- Created Python 3.12 venv at `APPS/odoo-frontend/backend/.venv`
- `alembic upgrade head` ran successfully

## Tables Created: 36 (+ alembic_version = 37 total)

**USER (9)**: `user`, `oauth_account`, `user_profile`, `membership`, `order`, `order_line`, `purchase`, `review`, `activity_event`

**WMS (10)**: `stock_warehouse`, `stock_location`, `stock_picking_type`, `stock_picking`, `stock_move`, `stock_quant`, `stock_quant_package`, `stock_lot`, `stock_rule`, `product_product`

**ECOMMERCE (17)**: `product_template`, `product_variant`, `product_attribute`, `product_attribute_value`, `product_variant_attribute_line`, `product_category`, `sale_order`, `sale_order_line`, `cart`, `cart_line`, `payment_transaction`, `pricelist`, `pricelist_item`, `coupon`, `shipping_method`, `partner`, `address`
