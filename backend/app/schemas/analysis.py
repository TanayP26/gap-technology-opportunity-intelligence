from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

EngineName = Literal["google_scholar", "google_patents", "google_trends", "google_news", "google"]
AnalysisStatus = Literal["draft", "planned", "running", "complete", "failed"]
ScoreStatus = Literal["scored", "insufficient_evidence"]
EvidenceType = Literal["paper", "patent", "news", "market"]


class AnalysisPreviewRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "technology": "Neuromorphic Computing",
                "subdomains": [
                    "Spiking Neural Networks",
                    "Memristive Computing",
                    "Event-Based Vision",
                    "Neuromorphic Processors",
                    "Neuromorphic Sensors",
                    "On-Device Learning",
                ],
                "geography": "Worldwide",
            }
        }
    )

    technology: str = Field(min_length=2, max_length=120)
    subdomains: list[str] = Field(min_length=2, max_length=8)
    geography: str = Field(default="Worldwide", min_length=2, max_length=120)

    @field_validator("technology", "geography")
    @classmethod
    def clean_text(cls, value: str) -> str:
        return " ".join(value.split())

    @field_validator("subdomains")
    @classmethod
    def clean_subdomains(cls, values: list[str]) -> list[str]:
        cleaned = [" ".join(value.split()) for value in values]
        if any(len(value) < 2 or len(value) > 120 for value in cleaned):
            raise ValueError("each subdomain must contain between 2 and 120 characters")
        if len(set(item.casefold() for item in cleaned)) != len(cleaned):
            raise ValueError("subdomains must be unique")
        return cleaned


class AnalysisCreateRequest(AnalysisPreviewRequest):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "technology": "Neuromorphic Computing",
                "subdomains": [
                    "Spiking Neural Networks",
                    "Memristive Computing",
                    "Event-Based Vision",
                    "Neuromorphic Processors",
                    "Neuromorphic Sensors",
                    "On-Device Learning",
                ],
                "geography": "Worldwide",
                "confirm_live_search": True,
            }
        }
    )

    confirm_live_search: bool = False


class PlannedSearch(BaseModel):
    engine: EngineName
    purpose: str
    query: str
    params: dict[str, str | int | bool]
    target_subdomains: list[str] = Field(default_factory=list)


class AnalysisPreviewResponse(BaseModel):
    technology: str
    subdomains: list[str]
    planned_searches: list[PlannedSearch]
    estimated_serpapi_calls: int


class SignalVector(BaseModel):
    research: float | None = Field(default=None, ge=0, le=1)
    patents: float | None = Field(default=None, ge=0, le=1)
    attention: float | None = Field(default=None, ge=0, le=1)
    events: float | None = Field(default=None, ge=0, le=1)
    market: float | None = Field(default=None, ge=0, le=1)
    confidence: float = Field(ge=0, le=1)


class GapScoreResponse(BaseModel):
    signals: SignalVector
    status: ScoreStatus = "scored"
    missing_signals: list[str] = Field(default_factory=list)
    technical_momentum: float | None = None
    demand_momentum: float | None = None
    whitespace: float | None = None
    gap_score: float | None = None


class LiveProbeRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "technology": "Neuromorphic Computing",
                "subdomain": "Event-Based Vision",
                "geography": "Worldwide",
                "confirm_live_search": True,
            }
        }
    )

    technology: str = Field(min_length=2, max_length=120)
    subdomain: str = Field(min_length=2, max_length=120)
    geography: str = Field(default="Worldwide", min_length=2, max_length=120)
    confirm_live_search: bool = False

    @field_validator("technology", "subdomain", "geography")
    @classmethod
    def clean_probe_text(cls, value: str) -> str:
        return " ".join(value.split())


class SourceRunSummary(BaseModel):
    engine: EngineName
    purpose: str
    status: Literal["success", "error"]
    cached: bool
    result_count: int
    estimated_total_results: int | None = None
    search_id: str | None = None
    error: str | None = None


class EvidencePreview(BaseModel):
    evidence_type: EvidenceType
    title: str
    url: str | None = None
    source_name: str | None = None
    published_at: str | None = None
    snippet: str | None = None


class LiveProbeResponse(BaseModel):
    technology: str
    subdomain: str
    source_runs: list[SourceRunSummary]
    signals: SignalVector
    score: GapScoreResponse
    evidence_count: int
    trend_point_count: int
    evidence_preview: list[EvidencePreview]


class SubdomainAnalysis(BaseModel):
    id: UUID
    name: str
    position: int
    signals: SignalVector
    score: GapScoreResponse
    evidence_count: int
    source_error_count: int


class AnalysisResponse(BaseModel):
    id: UUID
    technology: str
    geography: str
    status: AnalysisStatus
    created_at: str
    started_at: str | None = None
    completed_at: str | None = None
    failure_reason: str | None = None
    subdomains: list[SubdomainAnalysis]


class LandscapeEntry(BaseModel):
    subdomain_id: UUID
    name: str
    position: int
    signals: SignalVector
    score_status: ScoreStatus = "scored"
    missing_signals: list[str] = Field(default_factory=list)
    technical_momentum: float | None = None
    demand_momentum: float | None = None
    whitespace: float | None = None
    gap_score: float | None = None
    evidence_count: int
    source_error_count: int


class LandscapeResponse(BaseModel):
    analysis_id: UUID
    technology: str
    status: AnalysisStatus
    entries: list[LandscapeEntry]


class EvidenceItemResponse(BaseModel):
    id: UUID
    evidence_type: EvidenceType
    title: str
    url: str | None = None
    source_name: str | None = None
    published_at: str | None = None
    snippet: str | None = None
    external_id: str | None = None
    metadata: dict = Field(default_factory=dict)


class EvidenceListResponse(BaseModel):
    subdomain_id: UUID
    total: int
    limit: int
    offset: int
    items: list[EvidenceItemResponse]
