from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def wms_health():
    return {"router": "wms", "status": "ok"}
