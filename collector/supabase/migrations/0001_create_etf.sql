-- KOSPI에 상장된 ETF(상장지수펀드)의 기본정보. KIS 마스터파일과 종목별 상세 API로 채워진다.
-- 프론트엔드의 web/domain/etf/parser/etf.parser.ts RawEtfRow와 1:1 대응.
create table public.etf (
    short_code text primary key,
    standard_code text not null unique,
    name text,
    abbreviated_name text,
    english_name text,
    listed_date date,
    base_index_name text,
    index_provider text,
    tracking_multiplier text,
    replication_method text,
    base_market_class text,
    base_asset_class text,
    listed_shares bigint,
    manager text,
    creation_unit_quantity bigint,
    total_fee numeric,
    tax_type text,
    updated_at timestamptz not null default now()
);

comment on table public.etf is
    'KOSPI에 상장된 ETF(상장지수펀드)의 기본정보. KIS 마스터파일과 종목별 상세 API로 채워진다.';
comment on column public.etf.short_code is
    'ETF의 단축코드(거래소 매매 시 사용하는 코드)';
comment on column public.etf.standard_code is
    'ETF의 표준코드(ISIN)';
comment on column public.etf.name is
    'ETF 종목명(정식 명칭)';
comment on column public.etf.abbreviated_name is
    'ETF 종목의 축약명';
comment on column public.etf.english_name is
    'ETF 종목의 영문명';
comment on column public.etf.listed_date is
    'ETF가 거래소에 최초 상장된 일자';
comment on column public.etf.base_index_name is
    'ETF가 추종하는 기초지수명';
comment on column public.etf.index_provider is
    '기초지수를 산출·공표하는 지수산출기관';
comment on column public.etf.tracking_multiplier is
    '기초지수 대비 추적 배수(예: 레버리지 2배, 인버스 -1배)';
comment on column public.etf.replication_method is
    '기초지수 복제 방법(실물복제/합성복제 등)';
comment on column public.etf.base_market_class is
    '기초 시장 분류(국내/해외 등)';
comment on column public.etf.base_asset_class is
    '기초 자산 분류(주식/채권/원자재 등)';
comment on column public.etf.listed_shares is
    '상장 좌수(주식 수)';
comment on column public.etf.manager is
    'ETF를 운용하는 자산운용사명';
comment on column public.etf.creation_unit_quantity is
    '창설단위(Creation Unit)를 구성하는 좌수';
comment on column public.etf.total_fee is
    '총보수(연간, 퍼센트)';
comment on column public.etf.tax_type is
    '분배금 등에 적용되는 과세 유형';
comment on column public.etf.updated_at is
    '레코드가 마지막으로 갱신된 시각';

alter table public.etf enable row level security;

-- 프론트엔드는 로그인 없이 publishable key로 직접 SELECT한다 (PostgREST는 이를 anon 역할로 매핑한다).
create policy "public_read_etf" on public.etf
    for select
    to anon, authenticated
    using (true);

-- INSERT/UPDATE/DELETE 정책 없음 — 쓰기는 Python 수집기의 secret key만 (RLS 우회).

create index ix_etf_base_asset_class on public.etf (base_asset_class);
create index ix_etf_base_market_class on public.etf (base_market_class);
