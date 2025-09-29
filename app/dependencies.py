from fastapi import Header, HTTPException, status
from .config import settings

async def enforce_api_key(x_api_key: str | None = Header(default=None)):
    if settings.api_key is None:
        return
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
