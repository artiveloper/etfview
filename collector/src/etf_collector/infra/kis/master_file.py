"""코스피 종목 마스터파일(kospi_code.mst) 다운로드 및 ETF 필터링.

`docs/kospi-example.py`의 파싱 로직(cp949 인코딩, 고정폭 필드)을 이식했다.
ETF/ETN/주식 등 모든 유가증권시장 상품이 이 마스터파일 하나에 섞여 있으므로,
`group_code == 'EF'`로 ETF만 골라낸다.
"""

from __future__ import annotations

import zipfile
from datetime import date
from io import BytesIO

import httpx

from etf_collector.domain.etf.models import EtfInfo

KOSPI_MASTER_URL = "https://new.real.download.dws.co.kr/common/master/kospi_code.mst.zip"
MASTER_FILENAME = "kospi_code.mst"
ETF_GROUP_CODE = "EF"

_PART1_SHORT_CODE_LEN = 9
_PART1_STANDARD_CODE_LEN = 12
_PART2_LEN = 228

# kospi_code.mst 뒤쪽 228바이트 고정폭 블록의 필드 순서/길이.
# 전체 구조는 docs/kospi-header.txt(ST_KSP_CODE)를 따르되, 실제 파일을 다운로드해
# 오프셋을 검증해보면 문서화된 필드 앞에 1바이트 예약 필드가 존재한다
# (합계가 227이 아닌 228이 되어야 정확히 슬라이싱됨 — group_code가 실제로는
# part2[1:3]에 위치, part2[0:2]가 아님. reserved0을 넣지 않으면 이후 모든
# 필드 오프셋이 1바이트씩 밀려 listed_date/listed_shares가 깨진다).
_PART2_FIELD_SPECS: list[tuple[str, int]] = [
    ("reserved0", 1),
    ("group_code", 2),
    ("mkt_cap_scale", 1),
    ("idx_large_div", 4),
    ("idx_medium_div", 4),
    ("idx_small_div", 4),
    ("manufacturing", 1),
    ("low_liquidity", 1),
    ("governance_idx", 1),
    ("kospi200_sector", 1),
    ("kospi100", 1),
    ("kospi50", 1),
    ("krx", 1),
    ("etp_type", 1),
    ("elw_issued", 1),
    ("krx100", 1),
    ("krx_auto", 1),
    ("krx_semicon", 1),
    ("krx_bio", 1),
    ("krx_bank", 1),
    ("spac", 1),
    ("krx_energy_chem", 1),
    ("krx_steel", 1),
    ("short_term_overheated", 1),
    ("krx_media_telecom", 1),
    ("krx_construction", 1),
    ("non1", 1),
    ("krx_securities", 1),
    ("krx_ship", 1),
    ("krx_insurance", 1),
    ("krx_transport", 1),
    ("sri", 1),
    ("base_price", 9),
    ("trading_unit", 5),
    ("after_hours_unit", 5),
    ("trading_halt", 1),
    ("settlement_trading", 1),
    ("administrative_issue", 1),
    ("market_alert", 2),
    ("market_alert_risk_notice", 1),
    ("unfaithful_disclosure", 1),
    ("bypass_listing", 1),
    ("dividend_type", 2),
    ("face_value_change", 2),
    ("capital_increase_type", 2),
    ("margin_rate", 3),
    ("credit_available", 1),
    ("credit_period", 3),
    ("prev_volume", 12),
    ("face_value", 12),
    ("listed_date", 8),
    ("listed_shares", 15),
    ("capital", 21),
    ("settlement_month", 2),
    ("public_offering_price", 7),
    ("preferred_stock_type", 1),
    ("short_selling_hot", 1),
    ("sudden_surge", 1),
    ("krx300", 1),
    ("kospi", 1),
    ("sales", 9),
    ("operating_profit", 9),
    ("ordinary_profit", 9),
    ("net_income", 5),
    ("roe", 9),
    ("base_yyyymm", 8),
    ("market_cap", 9),
    ("group_company_code", 3),
    ("credit_limit_exceeded", 1),
    ("secured_loan_available", 1),
    ("short_selling_available", 1),
]


def _build_offsets(specs: list[tuple[str, int]]) -> dict[str, tuple[int, int]]:
    offsets: dict[str, tuple[int, int]] = {}
    cursor = 0
    for field_name, width in specs:
        offsets[field_name] = (cursor, cursor + width)
        cursor += width
    return offsets


_PART2_OFFSETS = _build_offsets(_PART2_FIELD_SPECS)


def _parse_listed_date(raw: str) -> date | None:
    raw = raw.strip()
    if len(raw) != 8 or not raw.isdigit():
        return None
    return date(int(raw[0:4]), int(raw[4:6]), int(raw[6:8]))


def _parse_listed_shares(raw: str) -> int | None:
    raw = raw.strip()
    if not raw or not raw.lstrip("-").isdigit():
        return None
    return int(raw)


def _parse_line(line: str) -> EtfInfo | None:
    part1 = line[: len(line) - _PART2_LEN]
    part2 = line[-_PART2_LEN:]

    group_start, group_end = _PART2_OFFSETS["group_code"]
    if part2[group_start:group_end] != ETF_GROUP_CODE:
        return None

    standard_code_end = _PART1_SHORT_CODE_LEN + _PART1_STANDARD_CODE_LEN
    short_code = part1[:_PART1_SHORT_CODE_LEN].strip()
    standard_code = part1[_PART1_SHORT_CODE_LEN:standard_code_end].strip()
    name = part1[standard_code_end:].strip()

    listed_date_start, listed_date_end = _PART2_OFFSETS["listed_date"]
    listed_shares_start, listed_shares_end = _PART2_OFFSETS["listed_shares"]

    return EtfInfo(
        short_code=short_code,
        standard_code=standard_code,
        name=name or None,
        listed_date=_parse_listed_date(part2[listed_date_start:listed_date_end]),
        listed_shares=_parse_listed_shares(part2[listed_shares_start:listed_shares_end]),
    )


def parse_master_file(content: bytes) -> list[EtfInfo]:
    """kospi_code.mst 원본 바이트를 받아 ETF(group_code == 'EF') 행만 EtfInfo로 변환한다."""
    text = content.decode("cp949")
    rows: list[EtfInfo] = []
    for line in text.splitlines():
        if not line.strip():
            continue
        etf = _parse_line(line)
        if etf is not None:
            rows.append(etf)
    return rows


async def download_master_file(client: httpx.AsyncClient) -> bytes:
    """kospi_code.mst.zip을 내려받아 압축 해제한 원본 바이트를 반환한다."""
    response = await client.get(KOSPI_MASTER_URL)
    response.raise_for_status()
    with zipfile.ZipFile(BytesIO(response.content)) as zf:
        return zf.read(MASTER_FILENAME)


async def fetch_etf_universe() -> list[EtfInfo]:
    """코스피 마스터파일을 다운로드해 ETF 유니버스(부분 필드만 채워진 EtfInfo 목록)를 반환한다."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        content = await download_master_file(client)
    return parse_master_file(content)
