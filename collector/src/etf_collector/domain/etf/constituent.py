# ETF 구성종목(보유종목) 정보를 담는 순수 타입
from datetime import UTC, date, datetime

from pydantic import BaseModel, Field


class EtfConstituent(BaseModel):
    """Supabase public.etf_constituent 테이블과 1:1 대응하는 도메인 타입 (필드명 = 컬럼명)."""

    etf_short_code: str
    constituent_short_code: str
    constituent_standard_code: str | None = None
    constituent_name: str | None = None
    held_quantity: int | None = None
    weight_percentage: float | None = None
    market_value_amount: float | None = None
    current_price: float | None = None
    price_change: float | None = None
    price_change_sign: str | None = None
    price_change_rate: float | None = None
    volume: int | None = None
    trade_amount: int | None = None
    today_change_rate: float | None = None
    volume_vs_prev_day: int | None = None
    trade_turnover_rate: float | None = None
    market_cap: int | None = None
    constituent_market_cap: int | None = None
    reference_date: date
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
