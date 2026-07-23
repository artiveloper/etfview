-- ETF 구성종목시세 API(output2)에 있었지만 미매핑이던 구성종목별 시세 필드를 etf_constituent에 추가한다.
alter table public.etf_constituent
    add column current_price numeric,
    add column price_change numeric,
    add column price_change_sign text,
    add column price_change_rate numeric,
    add column volume bigint,
    add column trade_amount bigint,
    add column today_change_rate numeric,
    add column volume_vs_prev_day bigint,
    add column trade_turnover_rate numeric,
    add column market_cap bigint,
    add column constituent_market_cap bigint;

comment on column public.etf_constituent.current_price is
    '구성종목의 주식 현재가(원)';
comment on column public.etf_constituent.price_change is
    '구성종목의 전일 대비(원)';
comment on column public.etf_constituent.price_change_sign is
    '구성종목의 전일 대비 부호';
comment on column public.etf_constituent.price_change_rate is
    '구성종목의 전일 대비율(퍼센트)';
comment on column public.etf_constituent.volume is
    '구성종목의 누적 거래량(주)';
comment on column public.etf_constituent.trade_amount is
    '구성종목의 누적 거래 대금(원)';
comment on column public.etf_constituent.today_change_rate is
    '구성종목의 당일 등락 비율(퍼센트)';
comment on column public.etf_constituent.volume_vs_prev_day is
    '구성종목의 전일 대비 거래량(주)';
comment on column public.etf_constituent.trade_turnover_rate is
    '구성종목의 거래대금 회전율(퍼센트)';
comment on column public.etf_constituent.market_cap is
    '구성종목의 HTS 시가총액';
comment on column public.etf_constituent.constituent_market_cap is
    'ETF 구성종목 시가총액';
