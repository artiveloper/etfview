-- etfview.kr 프론트엔드의 domain/etf/parser/etf.parser.ts RawEtfRow와 1:1 대응.
create table public.etf_info (
    short_code text primary key,
    standard_code text not null unique,
    name text,
    abbr_name text,
    eng_name text,
    listed_date date,
    base_index_name text,
    index_provider text,
    tracking_multiplier text,
    replication_method text,
    base_market_class text,
    base_asset_class text,
    listed_shares bigint,
    manager text,
    cu_quantity bigint,
    total_fee numeric,
    tax_type text,
    updated_at timestamptz not null default now()
);

alter table public.etf_info enable row level security;

-- 프론트엔드는 로그인 없이 anon(publishable) 키로 직접 SELECT한다.
create policy "public_read_etf_info" on public.etf_info
    for select
    to anon, authenticated
    using (true);

-- INSERT/UPDATE/DELETE 정책 없음 — 쓰기는 Python 수집기의 service_role 키만 (RLS 우회).

create index ix_etf_info_base_asset_class on public.etf_info (base_asset_class);
create index ix_etf_info_base_market_class on public.etf_info (base_market_class);
