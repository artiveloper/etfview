"""스케줄러와 같은 프로세스에서 잡 수동 트리거 API를 제공하는 FastAPI 앱."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI

from etf_collector.api.jobs_router import router as jobs_router
from etf_collector.config import get_settings
from etf_collector.infra.supabase.client import get_supabase_client
from etf_collector.logging_config import configure_logging
from etf_collector.scheduler.registry import (
    SCHEDULER_TIMEZONE,
    build_job_registry,
    register_cron_jobs,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    supabase = get_supabase_client(settings)
    registry = build_job_registry(settings, supabase)

    scheduler = AsyncIOScheduler(timezone=SCHEDULER_TIMEZONE)
    register_cron_jobs(scheduler, settings, registry)
    scheduler.start()

    app.state.settings = settings
    app.state.job_registry = registry

    yield

    scheduler.shutdown()


app = FastAPI(lifespan=lifespan)
app.include_router(jobs_router)


def run() -> None:
    configure_logging()
    uvicorn.run(app, host="0.0.0.0", port=8000)
