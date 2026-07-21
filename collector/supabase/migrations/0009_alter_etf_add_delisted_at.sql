-- KRX 조회에서 더는 반환되지 않는 종목을 상장폐지로 간주해 최초 감지일을 기록한다.
-- null = 정상 상장, 값이 있으면 그 날짜에 처음 상장폐지가 감지됨(이후 sync에서 덮어쓰지 않음).
alter table public.etf
    add column delisted_at date;

comment on column public.etf.delisted_at is
    'KRX 조회에서 더는 반환되지 않아 상장폐지로 판단된 최초 감지일(null이면 정상 상장)';
