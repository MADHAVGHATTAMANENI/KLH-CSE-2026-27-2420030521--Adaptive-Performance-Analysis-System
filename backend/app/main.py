from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_v1_router
from app.core.config import settings
from app.core.exceptions import CompilerXException, compilerx_exception_handler
from app.core.logging import configure_logging, logger
from app.db.session import engine
from app.models.base import Base
import app.models  # noqa: F401 - ensure all models are registered on Base.metadata


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application Lifespan Context Manager
    Executes startup and shutdown tasks.
    """
    # 1. Initialize logging
    configure_logging(settings.ENVIRONMENT)
    logger.info(
        "compilerx_starting",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
    )

    # 2. Initialize Database Tables (Auto-create in dev)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("database_initialized", url=settings.DATABASE_URL)

    yield

    # Shutdown: Dispose DB connection pool
    await engine.dispose()
    logger.info("compilerx_shutdown_completed")


def create_application() -> FastAPI:
    """Factory function creating the configured FastAPI application instance."""
    app = FastAPI(
        title=f"{settings.APP_NAME} API",
        version=settings.APP_VERSION,
        description="AI-Powered Adaptive Code Optimization and Performance Analysis System",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Cross-Origin Resource Sharing (CORS)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # Register Exception Handlers
    app.add_exception_handler(CompilerXException, compilerx_exception_handler)

    # Register Core API Router
    app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)

    return app


app = create_application()

