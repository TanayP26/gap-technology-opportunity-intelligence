from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.analysis import router as analysis_router
from app.api.routes.health import router as health_router
from app.api.routes.subdomains import router as subdomains_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="GAP API",
    version="0.2.1",
    description="Technology opportunity intelligence backed by traceable search evidence.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(analysis_router)
app.include_router(subdomains_router)
