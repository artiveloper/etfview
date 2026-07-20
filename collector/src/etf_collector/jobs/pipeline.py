"""ETF 수집 파이프라인 — 데이터 성격에 맞춰 3개 진입점으로 분리한다.

- run_daily_open: 장 시작 전 1회. 마스터파일로 ETF 유니버스를 채운다. 장중/마감
  단계가 모두 etf 테이블 존재를 전제하므로 반드시 먼저 실행돼야 한다.
- run_intraday_price: 장중 30분 주기. 일별 시세를 오늘 하루만 좁혀 갱신해 상세
  페이지의 오늘 캔들이 실시간으로 자라게 한다(가벼운 단일 단계).
- run_daily_close: 장 마감 후 1회. 오늘 봉 확정 + EOD 시세 스냅샷(enrich) +
  구성종목 바스켓을 함께 적재한다.

각 단계는 _run_stage로 감싸 job_execution_log에 개별 기록되어, 알림 체계가 없는
현재 상태에서도 사후 디버깅이 가능하다. 한 단계가 실패하면 로그에 fail을 남기고
해당 진입점 실행을 중단한다.
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable

import httpx

from etf_collector.config import Settings
from etf_collector.infra.kis.auth import KisAuthManager
from etf_collector.infra.kis.client import KisApiClient
from etf_collector.infra.supabase.etf_constituent_repository import EtfConstituentRepository
from etf_collector.infra.supabase.etf_price_repository import EtfPriceRepository
from etf_collector.infra.supabase.etf_quote_repository import EtfQuoteRepository
from etf_collector.infra.supabase.etf_repository import EtfInfoRepository
from etf_collector.infra.supabase.job_log_repository import JobExecutionLogRepository
from etf_collector.jobs.enrich_etf_info import enrich_etf_info
from etf_collector.jobs.sync_etf_constituent import sync_etf_constituent
from etf_collector.jobs.sync_etf_info import sync_etf_info
from etf_collector.jobs.sync_etf_price import sync_etf_price
from supabase import Client

logger = logging.getLogger(__name__)

# 장중 시세 갱신은 오늘 하루만 좁혀 미완성 봉만 재조회한다.
_INTRADAY_WINDOW_DAYS = 0


async def _run_stage(
    job_log_repository: JobExecutionLogRepository,
    job_name: str,
    stage: Callable[[], Awaitable[int]],
) -> None:
    log_id = job_log_repository.start(job_name)
    try:
        count = await stage()
    except Exception as exc:
        logger.exception("%s 단계 실패", job_name)
        job_log_repository.fail(log_id, str(exc))
        raise
    job_log_repository.succeed(log_id, count)


async def run_daily_open(
    settings: Settings,
    supabase: Client,
    etf_repository: EtfInfoRepository,
    job_log_repository: JobExecutionLogRepository,
) -> None:
    """장 시작 전 1회: ETF 유니버스 동기화."""
    await _run_stage(job_log_repository, "sync_etf_info", lambda: sync_etf_info(etf_repository))


async def run_intraday_price(
    settings: Settings,
    supabase: Client,
    etf_repository: EtfInfoRepository,
    price_repository: EtfPriceRepository,
    job_log_repository: JobExecutionLogRepository,
) -> None:
    """장중 30분 주기: 오늘 일별 시세(미완성 봉)만 갱신."""
    async with httpx.AsyncClient(timeout=30.0) as http_client:
        auth_manager = KisAuthManager(settings, supabase, http_client)
        api_client = KisApiClient(settings, http_client)
        await _run_stage(
            job_log_repository,
            "sync_etf_price_intraday",
            lambda: sync_etf_price(
                price_repository,
                etf_repository,
                auth_manager,
                api_client,
                window_days=_INTRADAY_WINDOW_DAYS,
            ),
        )


async def run_daily_close(
    settings: Settings,
    supabase: Client,
    etf_repository: EtfInfoRepository,
    quote_repository: EtfQuoteRepository,
    price_repository: EtfPriceRepository,
    constituent_repository: EtfConstituentRepository,
    job_log_repository: JobExecutionLogRepository,
) -> None:
    """장 마감 후 1회: 오늘 봉 확정 + EOD 시세 스냅샷(enrich) + 구성종목 바스켓."""
    async with httpx.AsyncClient(timeout=30.0) as http_client:
        auth_manager = KisAuthManager(settings, supabase, http_client)
        api_client = KisApiClient(settings, http_client)

        await _run_stage(
            job_log_repository,
            "enrich_etf_info",
            lambda: enrich_etf_info(etf_repository, quote_repository, auth_manager, api_client),
        )
        await _run_stage(
            job_log_repository,
            "sync_etf_price",
            lambda: sync_etf_price(price_repository, etf_repository, auth_manager, api_client),
        )
        await _run_stage(
            job_log_repository,
            "sync_etf_constituent",
            lambda: sync_etf_constituent(
                constituent_repository, etf_repository, auth_manager, api_client
            ),
        )
