"""LeadForge AI – FastAPI application entrypoint."""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.core.config import get_settings
from app.core.logger import configure_logging

settings = get_settings()
configure_logging(settings)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage startup / shutdown resources."""
    # Future: initialise connection pools, warm caches, etc.
    yield
    # Future: close external connections gracefully


def create_app() -> FastAPI:
    """Application factory — keeps test setup clean."""
    app = FastAPI(
        title=settings.app_name,
        description="Business discovery & opportunity analysis platform",
        version="0.1.0",
        docs_url="/docs" if settings.app_debug else None,
        redoc_url="/redoc" if settings.app_debug else None,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Tighten per environment via config
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)

    return app


app = create_app()
