# ETF 구성종목(보유종목) 수집 뼈대 — 데이터 소스 미확정
"""master_file.py와 동일한 "다운로드 → 파서 → 도메인 매핑" 3단 구조로 뼈대만 둔다.

정확한 다운로드 URL과 필드 레이아웃은 아직 확정되지 않았다(collector/docs에
대응 API 문서 없음). 실제 스펙이 확보되면 이 파일의 구현부만 채우면
jobs/sync_etf_constituent.py 이후 파이프라인은 그대로 동작한다.
"""

from __future__ import annotations

from typing import Any

import httpx

from etf_collector.domain.etf.constituent import EtfConstituent


async def download_constituent_master(client: httpx.AsyncClient) -> bytes:
    """구성종목 마스터파일(또는 API 응답)을 원본 바이트로 내려받는다."""
    raise NotImplementedError("구성종목 데이터 소스가 아직 확정되지 않았다")


def parse_constituent_master(content: bytes) -> list[dict[str, Any]]:
    """원본 바이트를 파싱해 종목별 원시 행(raw row) 목록으로 변환한다."""
    raise NotImplementedError("구성종목 필드 레이아웃이 아직 확정되지 않았다")


def map_to_domain(rows: list[dict[str, Any]]) -> list[EtfConstituent]:
    """원시 행 목록을 EtfConstituent 도메인 타입으로 매핑한다."""
    raise NotImplementedError("구성종목 필드 매핑이 아직 확정되지 않았다")


async def fetch_etf_constituents() -> list[EtfConstituent]:
    """구성종목 전체를 조회해 도메인 타입 목록으로 반환한다."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        content = await download_constituent_master(client)
    rows = parse_constituent_master(content)
    return map_to_domain(rows)
