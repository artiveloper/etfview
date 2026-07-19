# ETF_ETN 현재가 API로 ETF 종목의 세부 필드(운용사/CU수량/추적배수 등)를 보강하는 모듈
from __future__ import annotations

from typing import Any

from etf_collector.infra.kis.client import KisApiClient

_PATH = "/uapi/etfetn/v1/quotations/inquire-price"
_TR_ID = "FHPST02400000"
_MARKET_DIV_CODE = "J"


async def fetch_etf_quote(client: KisApiClient, token: str, short_code: str) -> dict[str, Any]:
    """단일 ETF 종목의 현재가 상세 정보(output)를 조회한다."""
    result = await client.get(
        _PATH,
        _TR_ID,
        token,
        {"fid_cond_mrkt_div_code": _MARKET_DIV_CODE, "fid_input_iscd": short_code},
    )
    output: dict[str, Any] = result["output"]
    return output


def map_to_etf_info_fields(quote: dict[str, Any]) -> dict[str, Any]:
    """현재가 API 응답에서 EtfInfo 미채움 필드로 매핑 가능한 값만 추출한다.

    index_provider/total_fee/tax_type/base_market_class/base_asset_class/
    base_index_name은 이 API 응답에 없어 매핑하지 않는다 — 별도 API 확보가 필요하다.
    replication_method는 etf_div_name(수익증권형/투자회사형 등)을 잠정 매핑한 것으로,
    엄밀한 복제방법 개념과 다를 수 있어 검증이 필요하다.
    """
    fields: dict[str, Any] = {}
    if quote.get("mbcr_name"):
        fields["manager"] = quote["mbcr_name"]
    if quote.get("etf_cu_unit_scrt_cnt"):
        fields["creation_unit_quantity"] = int(quote["etf_cu_unit_scrt_cnt"])
    if quote.get("etf_trc_ert_mltp"):
        fields["tracking_multiplier"] = quote["etf_trc_ert_mltp"]
    if quote.get("etf_div_name"):
        fields["replication_method"] = quote["etf_div_name"]
    return fields
