# Odoo Frontend Template

Reference web application combining all three TEMPLATE_CORE libraries (USER, WMS, ECOMMERCE) into an Odoo-style admin dashboard.

## Stack

- **Backend**: FastAPI + SQLAlchemy 2.x + Alembic (Python 3.11+)
- **Frontend**: Next.js 15 + Tailwind CSS 4 + TypeScript (Node 20 LTS)
- **Database**: SQLite (dev) / PostgreSQL-compatible

## Quick Start

### Backend
```bash
cd backend
pip install -e .
pip install -e ../../TEMPLATE_CORE/USER
pip install -e ../../TEMPLATE_CORE/WMS
pip install -e ../../TEMPLATE_CORE/ECOMMERCE
cp ../.env.example .env
alembic upgrade head
python seed.py
uvicorn main:app --reload
# → http://localhost:8000/docs
```

### Frontend
```bash
cd frontend
npm install
cp ../.env.example .env.local
npm run dev
# → http://localhost:3000
```

## Modules

| Module | Routes | Description |
|---|---|---|
| WMS | `/wms/*` | Warehouses, locations, inventory, pickings |
| Ecommerce | `/ecommerce/*` | Products, orders, coupons |
| Users | `/users/*` | User management, profiles, memberships |
