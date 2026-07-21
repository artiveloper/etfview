-- ETF_ETN 현재가 API 응답에 있었지만 미매핑이던 필드(NAV 부호, 유통좌수, 외국인 보유)를 etf_quote에 추가한다.
alter table public.etf_quote
    add column nav_change_sign text,
    add column circulating_shares bigint,
    add column foreign_holding_qty bigint,
    add column foreign_holding_rate numeric;

comment on column public.etf_quote.nav_change_sign is
    'NAV 전일 대비 부호';
comment on column public.etf_quote.circulating_shares is
    'ETF 유통좌수';
comment on column public.etf_quote.foreign_holding_qty is
    '외국인 보유 수량';
comment on column public.etf_quote.foreign_holding_rate is
    '외국인 보유 비중(퍼센트)';
