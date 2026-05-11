# Issue #43: WMS Dashboard Pages — Progress

**Status:** COMPLETE
**Date:** 2026-05-11
**Commit:** 84daa2c

## Files Created / Modified

| File | Action |
|------|--------|
| `app/(app)/wms/page.tsx` | Replaced stub — Warehouse list via DataTable |
| `app/(app)/wms/locations/page.tsx` | Created — Location tree with depth-indented list |
| `app/(app)/wms/inventory/page.tsx` | Created — Inventory quant table |
| `app/(app)/wms/pickings/page.tsx` | Created — Picking list with Badge + View link |
| `app/(app)/wms/pickings/[id]/page.tsx` | Created — Picking detail with moves table |

## Implementation Notes

- All pages are Next.js 15 async Server Components using direct `fetch()` (not `api.get`) to avoid the `document.cookie` client-side dependency in `lib/api.ts`.
- Base URL: `process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"` with `cache: "no-store"` for fresh data.
- `params` in `[id]/page.tsx` typed as `Promise<{id: string}>` and `await`-ed per Next.js 15 convention.
- TypeScript cast `(data as unknown) as Record<string, unknown>[]` used for DataTable compatibility since typed interfaces lack an index signature.
- `npm run build` passes cleanly — 5 WMS routes compiled: `/wms`, `/wms/inventory`, `/wms/locations`, `/wms/pickings`, `/wms/pickings/[id]`.

## Build Output (routes)

```
ƒ /wms                     — Warehouse list
ƒ /wms/inventory           — Inventory quants
ƒ /wms/locations           — Location tree
ƒ /wms/pickings            — Picking list
ƒ /wms/pickings/[id]       — Picking detail
```
