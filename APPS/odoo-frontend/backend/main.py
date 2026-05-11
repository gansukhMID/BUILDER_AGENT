from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import auth, wms, ecommerce, users

app = FastAPI(
    title="Odoo Frontend API",
    version="1.0.0",
    description="REST API for WMS, Ecommerce, and User management",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(wms.router, prefix="/wms", tags=["wms"])
app.include_router(ecommerce.router, prefix="/ecommerce", tags=["ecommerce"])
app.include_router(users.router, prefix="/users", tags=["users"])


@app.get("/health", tags=["system"])
def health():
    return {"status": "ok"}


@app.get("/stats", tags=["system"])
def stats_placeholder():
    return {
        "users": 0,
        "active_memberships": 0,
        "warehouses": 0,
        "open_pickings": 0,
        "products": 0,
        "open_orders": 0,
    }
