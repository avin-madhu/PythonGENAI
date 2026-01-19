from fastapi import APIRouter

# tags make a docs more organised
router = APIRouter(tags=["health"])


@router.get("/health")
async def get_health():
    return {"status": "up",
            "service": "AI"}
