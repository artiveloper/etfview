from datetime import UTC, date, datetime

from pydantic import BaseModel, Field


class EtfInfo(BaseModel):
    """Supabase public.etf_info 테이블과 1:1 대응하는 도메인 타입 (필드명 = 컬럼명)."""

    short_code: str
    standard_code: str
    name: str | None = None
    abbr_name: str | None = None
    eng_name: str | None = None
    listed_date: date | None = None
    base_index_name: str | None = None
    index_provider: str | None = None
    tracking_multiplier: str | None = None
    replication_method: str | None = None
    base_market_class: str | None = None
    base_asset_class: str | None = None
    listed_shares: int | None = None
    manager: str | None = None
    cu_quantity: int | None = None
    total_fee: float | None = None
    tax_type: str | None = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
