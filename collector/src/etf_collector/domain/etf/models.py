from datetime import UTC, date, datetime

from pydantic import BaseModel, Field


class EtfInfo(BaseModel):
    """Supabase public.etf 테이블과 1:1 대응하는 도메인 타입 (필드명 = 컬럼명)."""

    short_code: str
    standard_code: str
    name: str | None = None
    abbreviated_name: str | None = None
    english_name: str | None = None
    listed_date: date | None = None
    base_index_name: str | None = None
    index_provider: str | None = None
    tracking_multiplier: str | None = None
    replication_method: str | None = None
    base_market_class: str | None = None
    base_asset_class: str | None = None
    listed_shares: int | None = None
    manager: str | None = None
    creation_unit_quantity: int | None = None
    total_fee: float | None = None
    tax_type: str | None = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class EtfQuote(BaseModel):
    """Supabase public.etf_quote 테이블과 1:1 대응하는 도메인 타입 (필드명 = 컬럼명)."""

    short_code: str
    current_price: float | None = None
    price_change: float | None = None
    price_change_sign: str | None = None
    price_change_rate: float | None = None
    volume: int | None = None
    open_price: float | None = None
    high_price: float | None = None
    low_price: float | None = None
    year_high_price: float | None = None
    year_high_date: date | None = None
    year_low_price: float | None = None
    year_low_date: date | None = None
    nav: float | None = None
    nav_change: float | None = None
    nav_change_sign: str | None = None
    nav_change_rate: float | None = None
    tracking_error_rate: float | None = None
    disparity_rate: float | None = None
    net_asset_total: float | None = None
    constituent_count: int | None = None
    circulating_shares: int | None = None
    foreign_holding_qty: int | None = None
    foreign_holding_rate: float | None = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class EtfPrice(BaseModel):
    """Supabase public.etf_price 테이블과 1:1 대응하는 도메인 타입 (필드명 = 컬럼명)."""

    short_code: str
    trade_date: date
    open_price: float | None = None
    high_price: float | None = None
    low_price: float | None = None
    close_price: float | None = None
    volume: int | None = None
    trading_value: float | None = None
    price_change: float | None = None
    price_change_sign: str | None = None
    corporate_action_code: str | None = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
