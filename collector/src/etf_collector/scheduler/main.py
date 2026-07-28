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
from etf_collector.jobs.pipeline import run_daily_close, run_daily_open, run_intraday_price
from etf_collector.logging_config import configure_logging
from etf_collector.scheduler.registry import (
    SCHEDULER_TIMEZONE,
    build_job_registry,
    register_cron_jobs,
)
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


async def _run_daily_once() -> None:
    """개장(유니버스) → 마감(확정 시세·스냅샷·구성종목)을 한 번에 실행한다(e2e 검증용)."""
    settings = get_settings()
    supabase = get_supabase_client(settings)
    (
        etf_repository,
        quote_repository,
        price_repository,
        constituent_repository,
        job_log_repository,
    ) = _build_repositories(supabase)
    await run_daily_open(settings, supabase, etf_repository, job_log_repository)
    await run_daily_close(
        settings,
        supabase,
        etf_repository,
        quote_repository,
        price_repository,
        constituent_repository,
        job_log_repository,
    )


async def _run_open_once() -> None:
    """개장 전 유니버스 동기화(run_daily_open)만 1회 실행한다."""
    settings = get_settings()
    supabase = get_supabase_client(settings)
    etf_repository, _, _, _, job_log_repository = _build_repositories(supabase)
    await run_daily_open(settings, supabase, etf_repository, job_log_repository)


async def _run_close_once() -> None:
    """장 마감 후 확정 동기화(run_daily_close)만 1회 실행한다."""
    settings = get_settings()
    supabase = get_supabase_client(settings)
    (
        etf_repository,
        quote_repository,
        price_repository,
        constituent_repository,
        job_log_repository,
    ) = _build_repositories(supabase)
    await run_daily_close(
        settings,
        supabase,
        etf_repository,
        quote_repository,
        price_repository,
        constituent_repository,
        job_log_repository,
    )


async def _run_intraday_once() -> None:
    """장중 일별 시세 갱신을 1회 실행한다(오늘 미완성 봉 확인용)."""
    settings = get_settings()
    supabase = get_supabase_client(settings)
    etf_repository, _, price_repository, _, job_log_repository = _build_repositories(supabase)
    await run_intraday_price(
        settings, supabase, etf_repository, price_repository, job_log_repository
    )


async def _run_backfill_price(days_back: int) -> None:
    settings = get_settings()
    supabase = get_supabase_client(settings)
    etf_repository = EtfInfoRepository(supabase)
    price_repository = EtfPriceRepository(supabase)
    async with httpx.AsyncClient(timeout=30.0) as http_client:
        api_client = KisApiClient(settings, http_client)
        auth_manager = KisAuthManager(settings, supabase, api_client)
        await backfill_etf_price(
            price_repository, etf_repository, auth_manager, api_client, days_back
        )


async def _run_revoke() -> None:
    settings = get_settings()
    supabase = get_supabase_client(settings)
    async with httpx.AsyncClient(timeout=30.0) as http_client:
        api_client = KisApiClient(settings, http_client)
        auth_manager = KisAuthManager(settings, supabase, api_client)
        await auth_manager.revoke_token()
    logger.info("KIS 접근토큰 폐기 완료")


async def _run_scheduler() -> None:
    settings = get_settings()
    supabase = get_supabase_client(settings)
    registry = build_job_registry(settings, supabase)

    scheduler = AsyncIOScheduler(timezone=SCHEDULER_TIMEZONE)
    register_cron_jobs(scheduler, settings, registry)
    scheduler.start()
    await asyncio.Event().wait()


def run() -> None:
    configure_logging()
    parser = argparse.ArgumentParser(description="ETF 정보 수집 스케줄러")
    parser.add_argument(
        "--once",
        action="store_true",
        help="개장→마감 일일 사이클을 즉시 1회 실행 후 종료(장중 시세 제외)",
    )
    parser.add_argument(
        "--open-once",
        action="store_true",
        help="개장 전 유니버스 동기화(run_daily_open)만 즉시 1회 실행 후 종료",
    )
    parser.add_argument(
        "--close-once",
        action="store_true",
        help="장 마감 후 확정 동기화(run_daily_close)만 즉시 1회 실행 후 종료",
    )
    parser.add_argument(
        "--intraday-once",
        action="store_true",
        help="장중 일별 시세 갱신을 즉시 1회 실행 후 종료",
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
    elif args.intraday_once:
        asyncio.run(_run_intraday_once())
    elif args.open_once:
        asyncio.run(_run_open_once())
    elif args.close_once:
        asyncio.run(_run_close_once())
    elif args.once:
        asyncio.run(_run_daily_once())
    else:
        asyncio.run(_run_scheduler())


if __name__ == "__main__":
    run()
