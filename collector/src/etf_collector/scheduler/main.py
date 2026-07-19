"""스케줄러 진입점. 비즈니스 로직 없음 — APScheduler 등록과 CLI만 담당한다."""

import argparse
import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from etf_collector.config import Settings, get_settings
from etf_collector.infra.supabase.client import get_supabase_client
from etf_collector.infra.supabase.etf_repository import EtfInfoRepository
from etf_collector.jobs.sync_etf_info import sync_etf_info
from etf_collector.logging_config import configure_logging

logger = logging.getLogger(__name__)


def _build_repository(settings: Settings) -> EtfInfoRepository:
    supabase = get_supabase_client(settings)
    return EtfInfoRepository(supabase)


async def _run_once() -> None:
    settings = get_settings()
    repository = _build_repository(settings)
    await sync_etf_info(repository)


def _run_scheduler() -> None:
    settings = get_settings()
    repository = _build_repository(settings)

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        sync_etf_info,
        trigger="cron",
        day_of_week=settings.sync_cron_day_of_week,
        hour=settings.sync_cron_hour,
        minute=settings.sync_cron_minute,
        args=[repository],
    )
    scheduler.start()
    logger.info(
        "스케줄 등록 완료: day_of_week=%s hour=%d minute=%d",
        settings.sync_cron_day_of_week,
        settings.sync_cron_hour,
        settings.sync_cron_minute,
    )
    asyncio.get_event_loop().run_forever()


def run() -> None:
    configure_logging()
    parser = argparse.ArgumentParser(description="ETF 정보 수집 스케줄러")
    parser.add_argument(
        "--once", action="store_true", help="스케줄을 기다리지 않고 즉시 1회 실행 후 종료"
    )
    args = parser.parse_args()

    if args.once:
        asyncio.run(_run_once())
    else:
        _run_scheduler()


if __name__ == "__main__":
    run()
