"""
Bangladeshi-ai — FastAPI Application Entry Point
=================================================
Runs the multi-model AI backend that powers the platform.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import chat, code_helper, grammar, study_helper, user
from app.utils.config import settings


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    """Startup and shutdown events."""
    # Startup: initialise connections, warm-up caches, etc.
    yield
    # Shutdown: clean up resources if needed.


# ── Application factory ───────────────────────────────────────────────────────

def create_app() -> FastAPI:
    application = FastAPI(
        title=settings.app_name,
        description=(
            "World-class, FREE AI platform for Bengali students and communities. "
            "Powered by Gemini, DeepSeek, Grok and more."
        ),
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ── CORS ──────────────────────────────────────────────────
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers ───────────────────────────────────────────────
    application.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])
    application.include_router(study_helper.router, prefix="/api/v1/study", tags=["Study Helper"])
    application.include_router(grammar.router, prefix="/api/v1/grammar", tags=["Grammar"])
    application.include_router(code_helper.router, prefix="/api/v1/code", tags=["Code Assistant"])
    application.include_router(user.router, prefix="/api/v1/users", tags=["Users"])

    return application


app = create_app()


# ── Root health-check ─────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
async def root():
    return {
        "message": "বাংলাদেশী AI — Welcome! The platform is running. 🇧🇩",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}
