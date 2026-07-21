# ETF 구성종목시세 API로 단일 ETF의 보유종목 목록·비중·평가금액을 조회하는 모듈
from __future__ import annotations

from datetime import date
from typing import Any

from etf_collector.domain.etf.constituent import EtfConstituent
from etf_collector.infra.kis.client import KisApiClient

_PATH = "/uapi/etfetn/v1/quotations/inquire-component-stock-price"
_TR_ID = "FHKST121600C0"
_MARKET_DIV_CODE = "J"
_SCREEN_DIV_CODE = "11216"


async def fetch_constituents(
    client: KisApiClient, token: str, short_code: str
) -> list[dict[str, Any]]:
    """단일 ETF의 구성종목 배열(output2)을 조회한다."""
    result = await client.get(
        _PATH,
        _TR_ID,
        token,
        {
            "fid_cond_mrkt_div_code": _MARKET_DIV_CODE,
            "fid_input_iscd": short_code,
            "fid_cond_scr_div_code": _SCREEN_DIV_CODE,
        },
    )
    output2: list[dict[str, Any]] = result.get("output2") or []
    return output2


def map_to_constituent_rows(
    etf_short_code: str, reference_date: date, output2: list[dict[str, Any]]
) -> list[EtfConstituent]:
    """구성종목시세 응답(output2)을 EtfConstituent 행 목록으로 변환한다.

    이 API 응답에는 보유수량(held_quantity)과 표준코드(constituent_standard_code, ISIN)가
    없어 두 필드는 채우지 않는다 — 종목명/비중/평가금액만 매핑한다. 구성종목
    단축코드(stck_shrn_iscd)가 비어 있는 행은 건너뛴다.
    """
    rows: list[EtfConstituent] = []
    for item in output2:
        constituent_short_code = (item.get("stck_shrn_iscd") or "").strip()
        if not constituent_short_code:
            continue
        rows.append(
            EtfConstituent(
                etf_short_code=etf_short_code,
                constituent_short_code=constituent_short_code,
                constituent_name=item.get("hts_kor_isnm") or None,
                weight_percentage=(
                    float(item["etf_cnfg_issu_rlim"]) if item.get("etf_cnfg_issu_rlim") else None
                ),
                market_value_amount=(
                    float(item["etf_vltn_amt"]) if item.get("etf_vltn_amt") else None
                ),
                reference_date=reference_date,
            )
        )
    return rows
