"""
FastAPI application entry point for the Bangladeshi Education AI platform.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.endpoints import chat as chat_router
from app.api.v1.endpoints import study as study_router
from app.api.v1.endpoints import admission as admission_router
from app.middleware.nctb_middleware import NCTBMiddleware
from app.middleware.data_saver import DataSaverMiddleware
from app.middleware.rate_limit import RateLimitMiddleware

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "A high-performance educational AI platform for Bangladeshi students. "
        "Supports NCTB curriculum (SSC/HSC) and admission preparation for "
        "BUET, DU, Medical, and BCS examinations. Responses delivered in Bengali."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# Middleware (order matters – added in reverse execution order)
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(DataSaverMiddleware)
app.add_middleware(NCTBMiddleware)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(chat_router.router, prefix="/api/v1")
app.include_router(study_router.router, prefix="/api/v1")
app.include_router(admission_router.router, prefix="/api/v1")


# ---------------------------------------------------------------------------
# Root endpoint
# ---------------------------------------------------------------------------
@app.get("/", tags=["root"])
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "message": "বাংলাদেশী শিক্ষার্থীদের জন্য AI শিক্ষা প্ল্যাটফর্মে স্বাগতম! 🎓",
        "docs": "/docs",
        "endpoints": {
            "chat_stream": "/api/v1/chat/stream",
            "chat": "/api/v1/chat",
            "study_stream": "/api/v1/study/stream",
            "admission_stream": "/api/v1/admission/stream",
            "health": "/api/v1/health",
            "subjects": "/api/v1/subjects",
            "classes": "/api/v1/classes",
        },
    }
