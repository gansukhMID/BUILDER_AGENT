status: completed

## Stream B: Frontend Scaffold

Commit: a195d88
Branch: epic/odoo-frontend-template

### Files created (12)
- APPS/odoo-frontend/frontend/package.json — Next.js 15.3.1, React 19, Tailwind 4, TypeScript 5
- APPS/odoo-frontend/frontend/tsconfig.json — strict mode, bundler moduleResolution, @/* path alias
- APPS/odoo-frontend/frontend/next.config.ts
- APPS/odoo-frontend/frontend/postcss.config.mjs — @tailwindcss/postcss plugin
- APPS/odoo-frontend/frontend/app/globals.css — @import "tailwindcss"
- APPS/odoo-frontend/frontend/app/layout.tsx — RootLayout with metadata
- APPS/odoo-frontend/frontend/app/page.tsx — redirects to /dashboard
- APPS/odoo-frontend/frontend/middleware.ts — cookie-based auth guard (access_token)
- APPS/odoo-frontend/frontend/lib/api.ts — typed fetch wrapper with Bearer token injection
- APPS/odoo-frontend/frontend/components/.gitkeep
- APPS/odoo-frontend/frontend/components/ui/.gitkeep
- APPS/odoo-frontend/frontend/components/layout/.gitkeep
