-- KIS 접근토큰 캐시. 재발급 빈도 제한 때문에 컨테이너 재시작에도 살아남도록
-- Supabase에 저장한다 (단일 행만 존재하는 싱글턴 테이블).
--
-- lock_owner_identifier/lock_expiration_time은 토큰 재발급 동시성을 제어하는
-- 행 기반 리스(lease) 락이다. Supabase는 PostgREST 경유이고 흔히 pgbouncer
-- transaction-mode 풀링을 쓰기 때문에 세션 단위인 pg_advisory_lock은 호출마다
-- 다른 커넥션에 걸릴 수 있어 안전하지 않다 — 그래서 조건부 UPDATE 기반 행 잠금
-- 패턴을 쓴다.
create table public.kis_token_cache (
    id smallint primary key default 1,
    access_token text not null,
    expires_at timestamptz not null,
    lock_owner_identifier text,
    lock_expiration_time timestamptz,
    updated_at timestamptz not null default now(),
    constraint kis_token_cache_singleton check (id = 1)
);

comment on table public.kis_token_cache is
    'KIS 접근토큰 캐시(싱글턴). 재발급 빈도 제한을 지키기 위해 만료 임박 시점에만 재발급한다.';
comment on column public.kis_token_cache.id is
    '항상 1인 싱글턴 행 식별자';
comment on column public.kis_token_cache.access_token is
    'KIS가 발급한 접근토큰(access_token)';
comment on column public.kis_token_cache.expires_at is
    '접근토큰의 만료 시각';
comment on column public.kis_token_cache.lock_owner_identifier is
    '토큰 재발급 분산 락을 보유한 프로세스의 식별자(호스트명:프로세스ID:실행UUID 조합). 널이면 락이 해제된 상태를 의미한다.';
comment on column public.kis_token_cache.lock_expiration_time is
    '분산 락 임차 만료 시각. 이 시각이 지나면 락 소유자가 비정상 종료됐다고 간주해 다른 프로세스가 락을 재획득할 수 있다.';
comment on column public.kis_token_cache.updated_at is
    '레코드가 마지막으로 갱신된 시각';

alter table public.kis_token_cache enable row level security;
-- 정책 없음 = anon/authenticated 역할 완전 차단, service_role 역할(secret key)만 접근 가능 (안전한 기본값).
