# ETF_ETN 현재가 API로 ETF 종목의 세부 필드(운용사/CU수량/추적배수 등)를 보강하는 모듈
from __future__ import annotations

from datetime import date
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


def _parse_yyyymmdd(raw: str) -> date | None:
    raw = raw.strip()
    if len(raw) != 8 or not raw.isdigit():
        return None
    return date(int(raw[0:4]), int(raw[4:6]), int(raw[6:8]))


def map_to_etf_quote_fields(quote: dict[str, Any]) -> dict[str, Any]:
    """현재가 API 응답에서 EtfQuote(일 1회 배치 시세 스냅샷) 필드로 매핑 가능한 값만 추출한다."""
    fields: dict[str, Any] = {}
    if quote.get("stck_prpr"):
        fields["current_price"] = float(quote["stck_prpr"])
    if quote.get("prdy_vrss"):
        fields["price_change"] = float(quote["prdy_vrss"])
    if quote.get("prdy_vrss_sign"):
        fields["price_change_sign"] = quote["prdy_vrss_sign"]
    if quote.get("prdy_ctrt"):
        fields["price_change_rate"] = float(quote["prdy_ctrt"])
    if quote.get("acml_vol"):
        fields["volume"] = int(quote["acml_vol"])
    if quote.get("stck_oprc"):
        fields["open_price"] = float(quote["stck_oprc"])
    if quote.get("stck_hgpr"):
        fields["high_price"] = float(quote["stck_hgpr"])
    if quote.get("stck_lwpr"):
        fields["low_price"] = float(quote["stck_lwpr"])
    if quote.get("stck_dryy_hgpr"):
        fields["year_high_price"] = float(quote["stck_dryy_hgpr"])
    if quote.get("dryy_hgpr_date"):
        fields["year_high_date"] = _parse_yyyymmdd(quote["dryy_hgpr_date"])
    if quote.get("stck_dryy_lwpr"):
        fields["year_low_price"] = float(quote["stck_dryy_lwpr"])
    if quote.get("dryy_lwpr_date"):
        fields["year_low_date"] = _parse_yyyymmdd(quote["dryy_lwpr_date"])
    if quote.get("nav"):
        fields["nav"] = float(quote["nav"])
    if quote.get("nav_prdy_vrss"):
        fields["nav_change"] = float(quote["nav_prdy_vrss"])
    if quote.get("nav_prdy_ctrt"):
        fields["nav_change_rate"] = float(quote["nav_prdy_ctrt"])
    if quote.get("trc_errt"):
        fields["tracking_error_rate"] = float(quote["trc_errt"])
    if quote.get("dprt"):
        fields["disparity_rate"] = float(quote["dprt"])
    if quote.get("etf_ntas_ttam"):
        fields["net_asset_total"] = float(quote["etf_ntas_ttam"])
    if quote.get("etf_cnfg_issu_cnt"):
        fields["constituent_count"] = int(quote["etf_cnfg_issu_cnt"])
    return fields


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
