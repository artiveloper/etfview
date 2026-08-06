"""스케줄 잡 등록과 동시 실행 방지 락을 관리하는 모듈 — CLI 스케줄러와 API가 공유한다."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Literal
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from etf_collector.config import Settings
from etf_collector.infra.supabase.etf_constituent_repository import EtfConstituentRepository
from etf_collector.infra.supabase.etf_price_repository import EtfPriceRepository
from etf_collector.infra.supabase.etf_quote_repository import EtfQuoteRepository
from etf_collector.infra.supabase.etf_repository import EtfInfoRepository
from etf_collector.infra.supabase.job_log_repository import JobExecutionLogRepository
from etf_collector.jobs.pipeline import run_daily_close, run_daily_open, run_intraday_price
from supabase import Client

logger = logging.getLogger(__name__)

JobId = Literal["open", "intraday", "close", "close_nxt"]

# 장중 실행이 KIS 지연 등으로 30분 창을 넘기면 다음 실행과 겹칠 수 있어 단일 인스턴스로
# 제한하고, 지연 실행은 grace 안에서만 따라잡게 한다(누적 misfire 폭주 방지).
_MAX_INSTANCES = 1
_MISFIRE_GRACE_SECONDS = 300
SCHEDULER_TIMEZONE = ZoneInfo("Asia/Seoul")


@dataclass
class RegisteredJob:
    name: str
    lock: asyncio.Lock
    run: Callable[[], Awaitable[None]]


class JobRegistry:
    """잡별 락을 두어 cron 실행과 API 수동 트리거가 겹치지 않게 한다."""

    def __init__(self, jobs: dict[JobId, RegisteredJob]) -> None:
        self._jobs = jobs

    def is_running(self, job_id: JobId) -> bool:
        return self._jobs[job_id].lock.locked()

    async def run_locked(self, job_id: JobId) -> bool:
        """이미 실행 중이면 대기하지 않고 건너뛴다. 실행했으면 True를 반환한다."""
        job = self._jobs[job_id]
        if job.lock.locked():
            logger.warning("%s 잡이 이미 실행 중이라 건너뜀", job.name)
            return False
        async with job.lock:
            logger.info("%s 잡 시작", job.name)
            try:
                await job.run()
            except Exception:
                logger.exception("%s 잡 실패", job.name)
                raise
            logger.info("%s 잡 종료", job.name)
        return True


def build_job_registry(settings: Settings, supabase: Client) -> JobRegistry:
    etf_repository = EtfInfoRepository(supabase)
    quote_repository = EtfQuoteRepository(supabase)
    price_repository = EtfPriceRepository(supabase)
    constituent_repository = EtfConstituentRepository(supabase)
    job_log_repository = JobExecutionLogRepository(supabase)

    jobs: dict[JobId, RegisteredJob] = {
        "open": RegisteredJob(
            name="open",
            lock=asyncio.Lock(),
            run=lambda: run_daily_open(settings, supabase, etf_repository, job_log_repository),
        ),
        "intraday": RegisteredJob(
            name="intraday",
            lock=asyncio.Lock(),
            run=lambda: run_intraday_price(
                settings, supabase, etf_repository, price_repository, job_log_repository
            ),
        ),
        "close": RegisteredJob(
            name="close",
            lock=asyncio.Lock(),
            run=lambda: run_daily_close(
                settings,
                supabase,
                etf_repository,
                quote_repository,
                price_repository,
                constituent_repository,
                job_log_repository,
            ),
        ),
        "close_nxt": RegisteredJob(
            name="close_nxt",
            lock=asyncio.Lock(),
            run=lambda: run_daily_close(
                settings,
                supabase,
                etf_repository,
                quote_repository,
                price_repository,
                constituent_repository,
                job_log_repository,
            ),
        ),
    }
    return JobRegistry(jobs)


def register_cron_jobs(
    scheduler: AsyncIOScheduler, settings: Settings, registry: JobRegistry
) -> None:
    scheduler.add_job(
        registry.run_locked,
        trigger="cron",
        day_of_week=settings.open_cron_day_of_week,
        hour=settings.open_cron_hour,
        minute=settings.open_cron_minute,
        max_instances=_MAX_INSTANCES,
        misfire_grace_time=_MISFIRE_GRACE_SECONDS,
        args=["open"],
        id="open",
    )
    scheduler.add_job(
        registry.run_locked,
        trigger="cron",
        day_of_week=settings.intraday_cron_day_of_week,
        hour=settings.intraday_cron_hour,
        minute=settings.intraday_cron_minute,
        max_instances=_MAX_INSTANCES,
        misfire_grace_time=_MISFIRE_GRACE_SECONDS,
        args=["intraday"],
        id="intraday",
    )
    scheduler.add_job(
        registry.run_locked,
        trigger="cron",
        day_of_week=settings.close_cron_day_of_week,
        hour=settings.close_cron_hour,
        minute=settings.close_cron_minute,
        max_instances=_MAX_INSTANCES,
        misfire_grace_time=_MISFIRE_GRACE_SECONDS,
        args=["close"],
        id="close",
    )
    scheduler.add_job(
        registry.run_locked,
        trigger="cron",
        day_of_week=settings.close_nxt_cron_day_of_week,
        hour=settings.close_nxt_cron_hour,
        minute=settings.close_nxt_cron_minute,
        max_instances=_MAX_INSTANCES,
        misfire_grace_time=_MISFIRE_GRACE_SECONDS,
        args=["close_nxt"],
        id="close_nxt",
    )
    logger.info(
        "스케줄 등록 완료: open=%s %s:%s / intraday=%s %s:%s / close=%s %s:%s / close_nxt=%s %s:%s",
        settings.open_cron_day_of_week,
        settings.open_cron_hour,
        settings.open_cron_minute,
        settings.intraday_cron_day_of_week,
        settings.intraday_cron_hour,
        settings.intraday_cron_minute,
        settings.close_cron_day_of_week,
        settings.close_cron_hour,
        settings.close_cron_minute,
        settings.close_nxt_cron_day_of_week,
        settings.close_nxt_cron_hour,
        settings.close_nxt_cron_minute,
    )
