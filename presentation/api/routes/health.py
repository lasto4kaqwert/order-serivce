from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health", include_in_schema=False)
async def liveness() -> dict[str, str]:
    return {"status": "ok"}
