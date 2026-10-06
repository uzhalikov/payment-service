from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from app.config import settings
from app.database import async_session

api_key_header = APIKeyHeader(name="X-API-Key")


async def verify_api_key(x_api_key: str = Depends(api_key_header)):
    if x_api_key != settings.api_key:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid API key")


async def get_session():
    async with async_session() as session:
        yield session
