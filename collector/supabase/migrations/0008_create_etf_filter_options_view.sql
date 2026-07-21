-- 프론트엔드 필터 옵션(기초자산/시장/운용사/복제방법/과세유형) 조회용 뷰.
-- etf 테이블 전체를 내려받아 클라이언트에서 distinct를 뽑던 방식 대신,
-- DB에서 미리 집계한 배열 5개만 담긴 행 1개를 내려준다.
create view public.etf_filter_options as
select
    array_agg(distinct base_asset_class order by base_asset_class)
        filter (where base_asset_class is not null) as asset_classes,
    array_agg(distinct base_market_class order by base_market_class)
        filter (where base_market_class is not null) as markets,
    array_agg(distinct manager order by manager)
        filter (where manager is not null) as managers,
    array_agg(distinct replication_method order by replication_method)
        filter (where replication_method is not null) as replication_methods,
    array_agg(distinct tax_type order by tax_type)
        filter (where tax_type is not null) as tax_types
from public.etf;

comment on view public.etf_filter_options is
    'ETF 목록 필터 옵션(기초자산/시장/운용사/복제방법/과세유형)의 distinct 값을 DB에서 미리 집계해 행 1개로 제공하는 뷰.';

-- 프론트엔드는 로그인 없이 publishable key로 직접 SELECT한다 (etf와 동일 패턴).
grant select on public.etf_filter_options to anon, authenticated;
