-- ETF가 보유한 구성종목(창설단위 바스켓) 최신 스냅샷 테이블.
create table public.etf_constituent (
    etf_short_code text not null references public.etf(short_code) on delete cascade,
    constituent_short_code text not null,
    constituent_standard_code text,
    constituent_name text,
    held_quantity bigint,
    weight_percentage numeric,
    market_value_amount numeric,
    reference_date date not null,
    updated_at timestamptz not null default now(),
    primary key (etf_short_code, constituent_short_code)
);

comment on table public.etf_constituent is
    'ETF가 보유한 구성종목(창설단위 바스켓)의 최신 스냅샷. 종목별 이력이 아닌 현재 상태만 유지하며, 이력 조회가 필요해지면 reference_date를 포함한 별도 이력 테이블로 분리한다.';
comment on column public.etf_constituent.etf_short_code is
    '구성종목을 보유한 ETF의 단축코드 (etf.short_code 참조)';
comment on column public.etf_constituent.constituent_short_code is
    '구성(보유)종목의 단축코드';
comment on column public.etf_constituent.constituent_standard_code is
    '구성(보유)종목의 표준코드(ISIN)';
comment on column public.etf_constituent.constituent_name is
    '구성(보유)종목명';
comment on column public.etf_constituent.held_quantity is
    'ETF가 보유한 구성종목 수량(주)';
comment on column public.etf_constituent.weight_percentage is
    'ETF 순자산 대비 구성종목 비중(퍼센트)';
comment on column public.etf_constituent.market_value_amount is
    '구성종목 평가금액(원)';
comment on column public.etf_constituent.reference_date is
    '구성종목 현황의 기준일자(공시 또는 조회 기준일)';
comment on column public.etf_constituent.updated_at is
    '레코드가 마지막으로 갱신된 시각';

alter table public.etf_constituent enable row level security;

-- 프론트엔드는 로그인 없이 publishable key로 직접 SELECT한다 (etf와 동일 패턴).
create policy "public_read_etf_constituent" on public.etf_constituent
    for select
    to anon, authenticated
    using (true);

-- INSERT/UPDATE/DELETE 정책 없음 — 쓰기는 Python 수집기의 secret key만 (RLS 우회).

create index ix_etf_constituent_reference_date on public.etf_constituent (reference_date);
