from typing import Literal
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from app.core.config import get_settings
from app.schemas.analysis import EvidenceListResponse
from app.storage.postgres import DatabaseUnavailable, get_subdomain_evidence

router = APIRouter(prefix="/api/v1/subdomains", tags=["subdomains"])


@router.get("/{subdomain_id}/evidence", response_model=EvidenceListResponse)
async def read_subdomain_evidence(
    subdomain_id: UUID,
    evidence_type: Literal["paper", "patent", "news", "market"] | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> EvidenceListResponse:
    settings = get_settings()
    try:
        result = await get_subdomain_evidence(
            database_url=settings.database_url,
            subdomain_id=subdomain_id,
            evidence_type=evidence_type,
            limit=limit,
            offset=offset,
        )
    except DatabaseUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail="PostgreSQL is unavailable.") from exc
    if result is None:
        raise HTTPException(status_code=404, detail="Subdomain not found")
    return result
