-- ETF의 일별 주가(OHLCV) 시계열. etf_quote(오늘자 스냅샷)와 달리 종목·거래일 조합마다 행을 유지한다.
create table public.etf_price (
    short_code text not null references public.etf(short_code) on delete cascade,
    trade_date date not null,
    open_price numeric,
    high_price numeric,
    low_price numeric,
    close_price numeric,
    volume bigint,
    trading_value numeric,
    price_change numeric,
    price_change_sign text,
    corporate_action_code text,
    updated_at timestamptz not null default now(),
    primary key (short_code, trade_date)
);

comment on table public.etf_price is
    'ETF의 일별 주가(OHLCV) 시계열. 종목·거래일 조합마다 한 행을 유지하며, 같은 조합은 최신 값으로 덮어써진다.';
comment on column public.etf_price.short_code is
    '시세의 대상 ETF 단축코드 (etf.short_code 참조)';
comment on column public.etf_price.trade_date is
    '거래일자';
comment on column public.etf_price.open_price is
    '시가';
comment on column public.etf_price.high_price is
    '최고가';
comment on column public.etf_price.low_price is
    '최저가';
comment on column public.etf_price.close_price is
    '종가';
comment on column public.etf_price.volume is
    '거래량';
comment on column public.etf_price.trading_value is
    '거래대금';
comment on column public.etf_price.price_change is
    '전일 대비 가격';
comment on column public.etf_price.price_change_sign is
    '전일 대비 부호';
comment on column public.etf_price.corporate_action_code is
    '권리락/배당락/분배락 등 구분 코드';
comment on column public.etf_price.updated_at is
    '레코드가 마지막으로 갱신된 시각';

alter table public.etf_price enable row level security;

-- 프론트엔드는 로그인 없이 publishable key로 직접 SELECT한다 (etf와 동일 패턴).
create policy "public_read_etf_price" on public.etf_price
    for select
    to anon, authenticated
    using (true);

-- INSERT/UPDATE/DELETE 정책 없음 — 쓰기는 Python 수집기의 secret key만 (RLS 우회).

create index ix_etf_price_trade_date on public.etf_price (trade_date);
