# KRX 데이터포털에서 ETF 전종목 기본정보(기초지수/운용사/총보수 등)를 조회하는 모듈
from __future__ import annotations

from datetime import date
from typing import Any

import httpx

from etf_collector.domain.etf.models import EtfInfo
from etf_collector.infra.krx.auth import _USER_AGENT

_MENU_URL = "https://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201030104"
_DATA_URL = "https://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd"
_BLD = "dbms/MDC/STAT/standard/MDCSTAT04601"


def _parse_date(raw: str) -> date | None:
    raw = raw.strip()
    if not raw:
        return None
    return date.fromisoformat(raw.replace("/", "-"))


def _parse_int(raw: str) -> int | None:
    raw = raw.strip().replace(",", "")
    if not raw or not raw.lstrip("-").isdigit():
        return None
    return int(raw)


def map_to_etf_info(row: dict[str, Any]) -> EtfInfo:
    """MDCSTAT04601 응답 행 하나를 EtfInfo로 변환한다.

    IDX_CALC_INST_NM2는 필드명과 달리 실제로는 추적배수(일반/2X 레버리지/1X 인버스 등)
    값을 담고 있다 — KRX 다운로드 CSV의 "추적배수" 컬럼과 위치가 일치함을 확인했다.
    """
    return EtfInfo(
        short_code=row["ISU_SRT_CD"],
        standard_code=row["ISU_CD"],
        name=row.get("ISU_NM") or None,
        abbreviated_name=row.get("ISU_ABBRV") or None,
        english_name=row.get("ISU_ENG_NM") or None,
        listed_date=_parse_date(row.get("LIST_DD", "")),
        base_index_name=row.get("ETF_OBJ_IDX_NM") or None,
        index_provider=row.get("IDX_CALC_INST_NM1") or None,
        tracking_multiplier=row.get("IDX_CALC_INST_NM2") or None,
        replication_method=row.get("ETF_REPLICA_METHD_TP_CD") or None,
        base_market_class=row.get("IDX_MKT_CLSS_NM") or None,
        base_asset_class=row.get("IDX_ASST_CLSS_NM") or None,
        listed_shares=_parse_int(row.get("LIST_SHRS", "")),
        manager=row.get("COM_ABBRV") or None,
        creation_unit_quantity=_parse_int(row.get("CU_QTY", "")),
        total_fee=float(row["ETF_TOT_FEE"]) if row.get("ETF_TOT_FEE") else None,
        tax_type=row.get("TAX_TP_CD") or None,
    )


def parse_etf_universe(rows: list[dict[str, Any]]) -> list[EtfInfo]:
    return [map_to_etf_info(row) for row in rows]


async def fetch_etf_universe(client: httpx.AsyncClient) -> list[EtfInfo]:
    """로그인된 세션으로 ETF 전종목 기본정보를 조회해 EtfInfo 목록으로 변환한다.

    trdDd는 응답 내용에 영향을 주지 않는 것으로 확인됐다(임의 날짜로도 동일 결과) —
    당일 날짜를 형식만 맞춰 채워 넣는다.
    """
    response = await client.post(
        _DATA_URL,
        data={
            "bld": _BLD,
            "locale": "ko_KR",
            "trdDd": date.today().strftime("%Y%m%d"),
            "share": "1",
            "csvxls_isNo": "false",
        },
        headers={
            "X-Requested-With": "XMLHttpRequest",
            "Referer": _MENU_URL,
            "User-Agent": _USER_AGENT,
        },
    )
    response.raise_for_status()
    rows: list[dict[str, Any]] = response.json()["output"]
    return parse_etf_universe(rows)
