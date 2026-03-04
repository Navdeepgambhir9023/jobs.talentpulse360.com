"""Jobs Service — FastAPI application factory.

Creates the FastAPI app with lifespan management for database pool,
Redis connection, and event emitter. Registers middleware, exception
handlers, and the v1 router.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import redis.asyncio as aioredis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from tp360_shared.db.pool import close_pool, create_pool
from tp360_shared.errors.handlers import register_exception_handlers
from tp360_shared.events.emitter import EventEmitter
from tp360_shared.logging.config import configure_logging
from tp360_shared.middleware.request_id import RequestIdMiddleware

from app.api.v1.router import v1_router
from app.core.config import get_settings
from app.core.exception_handlers import setup_exception_handlers
from app.events.emitter import JobsEventEmitter

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application lifecycle resources."""
    settings = get_settings()
    configure_logging(settings.SERVICE_NAME, settings.LOG_LEVEL)
    logger.info("Starting %s", settings.SERVICE_NAME)

    app.state.db_pool = await create_pool(settings.DATABASE_URL)
    app.state.redis = aioredis.from_url(
        settings.REDIS_URL, decode_responses=True,
    )
    shared_emitter = EventEmitter(app.state.db_pool, app.state.redis)
    app.state.event_emitter = JobsEventEmitter(shared_emitter)

    logger.info("Resources initialized")
    yield

    await close_pool(app.state.db_pool)
    await app.state.redis.close()
    logger.info("Resources released")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    app = FastAPI(
        title="TalentPulse360 Jobs Service",
        description="Job lifecycle, analysis, and qualification management",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    setup_exception_handlers(app)

    app.include_router(v1_router)

    return app


app = create_app()
