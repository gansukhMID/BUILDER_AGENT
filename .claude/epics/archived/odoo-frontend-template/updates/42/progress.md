# Issue #42: Next.js Frontend Scaffold + Odoo Shell Layout

**Status:** DONE
**Commit:** 0d0b065

## Files Created

### Route Groups
- `app/(auth)/login/page.tsx` — Login form with JWT cookie auth
- `app/(app)/layout.tsx` — App shell (Sidebar + Navbar wrapping `{children}`)
- `app/(app)/dashboard/page.tsx` — Dashboard with stat cards (server component, fetches `/stats`)
- `app/(app)/wms/page.tsx` — WMS stub (placeholder for issue #43)
- `app/(app)/ecommerce/page.tsx` — Ecommerce stub (placeholder for issue #44)
- `app/(app)/users/page.tsx` — Users stub (placeholder for issue #44)

### Layout Components
- `components/layout/Sidebar.tsx` — Dark sidebar with module nav (Dashboard, WMS, Ecommerce, Users) and active-link highlighting
- `components/layout/Navbar.tsx` — Top bar with Sign out button (clears JWT cookie → /login)

### UI Components
- `components/ui/StatCard.tsx` — Metric card with optional href link
- `components/ui/Badge.tsx` — Status badge with color map for 15 states
- `components/ui/Spinner.tsx` — Loading spinner (animated border)
- `components/ui/DataTable.tsx` — Generic typed data table with column renderers

## Build Result
`npm run build` passed with 0 TypeScript errors. 9 routes compiled (7 app routes + 2 Next.js internals).

## Notes
- `app/page.tsx` already had `redirect("/dashboard")` from issue #35 — not modified
- `middleware.ts` and `lib/api.ts` from issue #35 — not modified
- Dashboard gracefully degrades when backend is offline (shows yellow warning banner)
