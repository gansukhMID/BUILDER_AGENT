from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def ecommerce_health():
    return {"router": "ecommerce", "status": "ok"}
