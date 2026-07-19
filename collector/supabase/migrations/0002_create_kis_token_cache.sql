-- KIS 접근토큰 캐시. 재발급 빈도 제한 때문에 컨테이너 재시작에도 살아남도록
-- Supabase에 저장한다 (단일 행만 존재하는 싱글턴 테이블).
create table public.kis_token_cache (
    id smallint primary key default 1,
    access_token text not null,
    expires_at timestamptz not null,
    updated_at timestamptz not null default now(),
    constraint kis_token_cache_singleton check (id = 1)
);

alter table public.kis_token_cache enable row level security;
-- 정책 없음 = anon/authenticated 완전 차단, service_role만 접근 가능 (안전한 기본값).
