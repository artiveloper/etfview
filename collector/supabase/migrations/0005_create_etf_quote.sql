-- ETF의 일 1회 배치 시세 스냅샷. enrich_etf_info 단계에서 KIS 현재가 API 응답으로 매일 덮어써진다.
create table public.etf_quote (
    short_code text primary key references public.etf(short_code) on delete cascade,
    current_price numeric,
    price_change numeric,
    price_change_sign text,
    price_change_rate numeric,
    volume bigint,
    open_price numeric,
    high_price numeric,
    low_price numeric,
    year_high_price numeric,
    year_high_date date,
    year_low_price numeric,
    year_low_date date,
    nav numeric,
    nav_change numeric,
    nav_change_rate numeric,
    tracking_error_rate numeric,
    disparity_rate numeric,
    net_asset_total numeric,
    constituent_count bigint,
    updated_at timestamptz not null default now()
);

comment on table public.etf_quote is
    'ETF의 일 1회 배치 시세 스냅샷. etf 테이블(고정 정보)과 달리 매일 최신 값으로 덮어써지며, 이력은 유지하지 않는다.';
comment on column public.etf_quote.short_code is
    '시세의 대상 ETF 단축코드 (etf.short_code 참조)';
comment on column public.etf_quote.current_price is
    '현재가';
comment on column public.etf_quote.price_change is
    '전일 대비 가격';
comment on column public.etf_quote.price_change_sign is
    '전일 대비 부호';
comment on column public.etf_quote.price_change_rate is
    '전일 대비율(퍼센트)';
comment on column public.etf_quote.volume is
    '누적 거래량';
comment on column public.etf_quote.open_price is
    '시가';
comment on column public.etf_quote.high_price is
    '당일 최고가';
comment on column public.etf_quote.low_price is
    '당일 최저가';
comment on column public.etf_quote.year_high_price is
    '연중 최고가';
comment on column public.etf_quote.year_high_date is
    '연중 최고가 달성 일자';
comment on column public.etf_quote.year_low_price is
    '연중 최저가';
comment on column public.etf_quote.year_low_date is
    '연중 최저가 달성 일자';
comment on column public.etf_quote.nav is
    '순자산가치(NAV)';
comment on column public.etf_quote.nav_change is
    'NAV 전일 대비';
comment on column public.etf_quote.nav_change_rate is
    'NAV 전일 대비율(퍼센트)';
comment on column public.etf_quote.tracking_error_rate is
    '기초지수 대비 추적 오차율(퍼센트)';
comment on column public.etf_quote.disparity_rate is
    '시장가격과 NAV 간 괴리율(퍼센트)';
comment on column public.etf_quote.net_asset_total is
    '순자산총액(AUM)';
comment on column public.etf_quote.constituent_count is
    'ETF 구성종목 수';
comment on column public.etf_quote.updated_at is
    '레코드가 마지막으로 갱신된 시각';

alter table public.etf_quote enable row level security;

-- 프론트엔드는 로그인 없이 publishable key로 직접 SELECT한다 (etf와 동일 패턴).
create policy "public_read_etf_quote" on public.etf_quote
    for select
    to anon, authenticated
    using (true);

-- INSERT/UPDATE/DELETE 정책 없음 — 쓰기는 Python 수집기의 secret key만 (RLS 우회).
