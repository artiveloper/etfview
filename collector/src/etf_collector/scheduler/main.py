"""스케줄러 진입점. 비즈니스 로직 없음 — APScheduler 등록과 CLI만 담당한다."""

import argparse
import asyncio
import logging

import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from etf_collector.config import get_settings
from etf_collector.infra.kis.auth import KisAuthManager
from etf_collector.infra.kis.client import KisApiClient
from etf_collector.infra.supabase.client import get_supabase_client
from etf_collector.infra.supabase.etf_constituent_repository import EtfConstituentRepository
from etf_collector.infra.supabase.etf_price_repository import EtfPriceRepository
from etf_collector.infra.supabase.etf_quote_repository import EtfQuoteRepository
from etf_collector.infra.supabase.etf_repository import EtfInfoRepository
from etf_collector.infra.supabase.job_log_repository import JobExecutionLogRepository
from etf_collector.jobs.backfill_etf_price import backfill_etf_price
from etf_collector.jobs.pipeline import run_pipeline
from etf_collector.logging_config import configure_logging
from supabase import Client

logger = logging.getLogger(__name__)


def _build_repositories(
    supabase: Client,
) -> tuple[
    EtfInfoRepository,
    EtfQuoteRepository,
    EtfPriceRepository,
    EtfConstituentRepository,
    JobExecutionLogRepository,
]:
    return (
        EtfInfoRepository(supabase),
        EtfQuoteRepository(supabase),
        EtfPriceRepository(supabase),
        EtfConstituentRepository(supabase),
        JobExecutionLogRepository(supabase),
    )


async def _run_once() -> None:
    settings = get_settings()
    supabase = get_supabase_client(settings)
    (
        etf_repository,
        quote_repository,
        price_repository,
        constituent_repository,
        job_log_repository,
    ) = _build_repositories(supabase)
    await run_pipeline(
        settings,
        supabase,
        etf_repository,
        quote_repository,
        price_repository,
        constituent_repository,
        job_log_repository,
    )


async def _run_backfill_price(days_back: int) -> None:
    settings = get_settings()
    supabase = get_supabase_client(settings)
    etf_repository = EtfInfoRepository(supabase)
    price_repository = EtfPriceRepository(supabase)
    async with httpx.AsyncClient(timeout=30.0) as http_client:
        auth_manager = KisAuthManager(settings, supabase, http_client)
        api_client = KisApiClient(settings, http_client)
        await backfill_etf_price(
            price_repository, etf_repository, auth_manager, api_client, days_back
        )


async def _run_revoke() -> None:
    settings = get_settings()
    supabase = get_supabase_client(settings)
    async with httpx.AsyncClient(timeout=30.0) as http_client:
        auth_manager = KisAuthManager(settings, supabase, http_client)
        await auth_manager.revoke_token()
    logger.info("KIS 접근토큰 폐기 완료")


def _run_scheduler() -> None:
    settings = get_settings()
    supabase = get_supabase_client(settings)
    (
        etf_repository,
        quote_repository,
        price_repository,
        constituent_repository,
        job_log_repository,
    ) = _build_repositories(supabase)

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        run_pipeline,
        trigger="cron",
        day_of_week=settings.sync_cron_day_of_week,
        hour=settings.sync_cron_hour,
        minute=settings.sync_cron_minute,
        args=[
            settings,
            supabase,
            etf_repository,
            quote_repository,
            price_repository,
            constituent_repository,
            job_log_repository,
        ],
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
    parser.add_argument("--revoke", action="store_true", help="캐시된 KIS 접근토큰을 폐기하고 종료")
    parser.add_argument(
        "--backfill-price",
        action="store_true",
        help="최근 N일치 일별 주가(OHLCV)를 1회 소급 수집하고 종료 (--backfill-days로 기간 조절)",
    )
    parser.add_argument(
        "--backfill-days",
        type=int,
        default=365,
        help="--backfill-price와 함께 사용, 오늘로부터 며칠 전까지 백필할지 (기본 365)",
    )
    args = parser.parse_args()

    if args.revoke:
        asyncio.run(_run_revoke())
    elif args.backfill_price:
        asyncio.run(_run_backfill_price(args.backfill_days))
    elif args.once:
        asyncio.run(_run_once())
    else:
        _run_scheduler()


if __name__ == "__main__":
    run()
