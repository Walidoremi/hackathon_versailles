from fastapi import APIRouter
from ..config import settings

router = APIRouter()

@router.get("/health")
async def health():
    return {"status": "ok"}

@router.get("/debug-key", include_in_schema=False)
async def debug_key():
    return {
        "mistral_key_loaded": settings.mistral_api_key is not None,
        "mistral_model": settings.mistral_model,
    }