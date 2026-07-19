"""ETF 수집 파이프라인: universe sync → enrichment → 구성종목 수집을 순차 실행한다.

enrichment/구성종목 수집은 etf 유니버스가 먼저 채워져 있어야 하므로,
독립된 cron 3개로 스태거링하지 않고 단일 cron이 이 파이프라인 하나를 순차
호출하는 구조로 의존관계를 안전하게 표현한다. 각 단계는 job_execution_log에
개별 기록되어, 알림 체계가 없는 현재 상태에서도 사후 디버깅이 가능하다.
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable

import httpx

from etf_collector.config import Settings
from etf_collector.infra.kis.auth import KisAuthManager
from etf_collector.infra.kis.client import KisApiClient
from etf_collector.infra.supabase.etf_constituent_repository import EtfConstituentRepository
from etf_collector.infra.supabase.etf_quote_repository import EtfQuoteRepository
from etf_collector.infra.supabase.etf_repository import EtfInfoRepository
from etf_collector.infra.supabase.job_log_repository import JobExecutionLogRepository
from etf_collector.jobs.enrich_etf_info import enrich_etf_info
from etf_collector.jobs.sync_etf_constituent import sync_etf_constituent
from etf_collector.jobs.sync_etf_info import sync_etf_info
from supabase import Client

logger = logging.getLogger(__name__)


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


async def run_pipeline(
    settings: Settings,
    supabase: Client,
    etf_repository: EtfInfoRepository,
    quote_repository: EtfQuoteRepository,
    constituent_repository: EtfConstituentRepository,
    job_log_repository: JobExecutionLogRepository,
) -> None:
    async with httpx.AsyncClient(timeout=30.0) as http_client:
        auth_manager = KisAuthManager(settings, supabase, http_client)
        api_client = KisApiClient(settings, http_client)

        await _run_stage(job_log_repository, "sync_etf_info", lambda: sync_etf_info(etf_repository))
        await _run_stage(
            job_log_repository,
            "enrich_etf_info",
            lambda: enrich_etf_info(etf_repository, quote_repository, auth_manager, api_client),
        )
        await _run_stage(
            job_log_repository,
            "sync_etf_constituent",
            lambda: sync_etf_constituent(constituent_repository),
        )
