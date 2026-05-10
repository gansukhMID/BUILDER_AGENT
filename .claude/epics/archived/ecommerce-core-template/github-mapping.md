# GitHub Issue Mapping — ecommerce-core-template

Epic: #23 - https://github.com/gansukhMID/BUILDER_AGENT/issues/23

## Tasks

| Local File | Issue | Title |
|---|---|---|
| 24.md | #24 | Package Scaffold |
| 27.md | #27 | Product Catalog Models |
| 29.md | #29 | Partner & Address Models |
| 31.md | #31 | Pricing Models & Engine |
| 33.md | #33 | Coupon Model |
| 25.md | #25 | Cart & Checkout |
| 26.md | #26 | SaleOrder & SaleOrderLine |
| 28.md | #28 | ShippingMethod Stub & PaymentTransaction |
| 30.md | #30 | Model Re-exports & Alembic Migration |
| 32.md | #32 | Test Suite & README |

## Dependency Graph (real issue numbers)

```
#24 (Scaffold)
    ├── #27 (Product Catalog)  ┐
    ├── #29 (Partner/Address)  ├── parallel
    ├── #31 (Pricing Engine)   │
    └── #33 (Coupon)           ┘
              ↓
         #25 (Cart)      ← depends on #27, #29, #31, #33 / conflicts #26
         #26 (SaleOrder) ← depends on #27, #29, #33        / conflicts #25
              ↓
         #28 (Shipping + Payment) ← depends on #26
              ↓
         #30 (Migration + Re-exports) ← depends on #27,#29,#31,#33,#25,#26,#28
              ↓
         #32 (Tests + README) ← depends on #30
```

Synced: 2026-05-10T13:11:38Z
Worktree: ../epic-ecommerce-core-template
Branch: epic/ecommerce-core-template
