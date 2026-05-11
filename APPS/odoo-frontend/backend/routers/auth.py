from fastapi import APIRouter

router = APIRouter()

@router.get("/health-auth")
def auth_health():
    return {"router": "auth", "status": "ok"}
