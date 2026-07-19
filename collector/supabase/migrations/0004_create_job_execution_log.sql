-- 배치 파이프라인 각 단계의 실행 이력을 기록하는 운영 감사 로그.
-- 알림 체계가 없는 현재 상태에서 실패 원인을 추적하는 유일한 수단이다.
create table public.job_execution_log (
    id bigint generated always as identity primary key,
    job_name text not null,
    started_at timestamptz not null,
    finished_at timestamptz,
    execution_status text not null,
    affected_row_count integer,
    error_message text,
    created_at timestamptz not null default now(),
    constraint job_execution_log_status_check
        check (execution_status in ('RUNNING', 'SUCCEEDED', 'FAILED'))
);

comment on table public.job_execution_log is
    '배치 작업(job) 실행 이력과 결과를 기록하는 운영 감사 로그. 알림 체계가 없는 현재 상태에서 실패 원인을 추적하는 유일한 수단이다.';
comment on column public.job_execution_log.job_name is
    '실행된 작업의 이름 (예: sync_etf_info, enrich_etf_info, sync_etf_constituent)';
comment on column public.job_execution_log.started_at is
    '작업 시작 시각';
comment on column public.job_execution_log.finished_at is
    '작업 종료 시각. 실행 상태가 RUNNING인 동안은 널이다.';
comment on column public.job_execution_log.execution_status is
    '작업 실행 상태: RUNNING(진행중) / SUCCEEDED(성공) / FAILED(실패)';
comment on column public.job_execution_log.affected_row_count is
    '작업이 처리(upsert)한 레코드 수';
comment on column public.job_execution_log.error_message is
    '작업 실패 시 원인 메시지. 성공한 경우 널이다.';
comment on column public.job_execution_log.created_at is
    '로그 레코드가 생성된 시각';

alter table public.job_execution_log enable row level security;
-- 정책 없음 = anon/authenticated 역할 완전 차단, service_role 역할(secret key)만 접근 가능 (kis_token_cache와 동일 패턴).

create index ix_job_execution_log_job_name_started_at on public.job_execution_log (job_name, started_at desc);
