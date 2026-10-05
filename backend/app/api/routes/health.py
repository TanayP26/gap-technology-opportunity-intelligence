from fastapi import APIRouter

from app.core.config import get_settings
from app.storage.postgres import DatabaseUnavailable, database_ready

router = APIRouter(tags=["system"])


@router.get("/health")
async def health() -> dict[str, str | bool]:
    settings = get_settings()
    try:
        postgres_ready = await database_ready(settings.database_url)
    except DatabaseUnavailable:
        postgres_ready = False
    return {
        "status": "ok",
        "service": "gap-api",
        "serpapi_configured": bool(settings.serpapi_api_key),
        "postgres_ready": postgres_ready,
    }
