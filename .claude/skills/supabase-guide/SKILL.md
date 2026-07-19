---
name: supabase-guide
description: >
  eft-collector Python + Supabase 실무 가이드.
  supabase-py 클라이언트, service_role 키, RLS, 마이그레이션, 싱글턴 캐시 테이블 관련
  작업 시 참조. 이 프로젝트는 사용자 인증이 없는 서버 전용 배치 수집기이므로,
  브라우저/SSR 클라이언트나 유저 인증 패턴(GamePot 원본 supabase-guide의 대상)은 다루지 않는다.
---

# collector Supabase 가이드

> 대상: `collector/` 서브프로젝트. 경로 언급은 `collector/` 기준 상대경로다.
> 원칙: DB는 항상 RLS로 보호한다. service_role 키는 RLS를 우회하므로 서버 프로세스 밖으로 절대 나가지 않는다.

이 프로젝트는 사용자 로그인이 없는 **서버 전용 배치 수집기**다 — 원본(GamePot) `supabase-guide`가 다루는 브라우저/SSR 클라이언트, `getUser()`/`getSession()` 인증 패턴, JWT `app_metadata` 롤 체크, 미들웨어 토큰 갱신은 이 프로젝트에 존재하지 않는다. 대신 **단일 service_role 클라이언트로 모든 쓰기를 수행**하는 훨씬 단순한 모델을 쓴다.

---

## 1. 클라이언트 설정

### 패키지

```bash
uv add supabase
```

### Service 클라이언트 (유일한 클라이언트)

```python
# src/etf_collector/infra/supabase/client.py
from supabase import Client, create_client

from etf_collector.config import Settings


def get_supabase_client(settings: Settings) -> Client:
    """service_role 키로 생성하는 서버 전용 클라이언트 — RLS를 우회한다."""
    return create_client(settings.supabase_url, settings.supabase_service_role_key)
```

- `SUPABASE_SERVICE_ROLE_KEY`는 `.env`(컨테이너 환경변수)로만 주입하고, 로그·에러 메시지에 절대 노출하지 않는다.
- 이 프로젝트에는 anon/publishable 키를 쓰는 클라이언트가 없다 — 만약 익명 키 클라이언트가 코드에 등장하면(예: 읽기 검증용) 왜 필요한지부터 의심한다. 읽기는 `etfview.kr`(별도 프로젝트)의 책임이다.

---

## 2. 인증

이 프로젝트에는 사용자 인증이 없다. `KisAuthManager`가 다루는 것은 **KIS Open API 접근토큰**이지 Supabase Auth가 아니다 — 이름이 비슷해 혼동하기 쉬우니 리뷰 시 구분한다 (`infra/kis/auth.py` vs Supabase Auth는 무관).

---

## 3. 키 관리

| 키 | 용도 | 노출 |
|----|------|------|
| `SUPABASE_SERVICE_ROLE_KEY` | 유일한 클라이언트, RLS 우회 | 절대 노출 금지 — `.env`/컨테이너 시크릿으로만 |
| `KIS_APP_KEY` / `KIS_APP_SECRET` | KIS Open API 인증 (Supabase와 무관) | 절대 노출 금지 |

```bash
# .env (git 제외)
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=sb_secret_xxx
```

---

## 4. RLS (Row Level Security)

> public 스키마의 모든 테이블에 RLS를 활성화한다. 예외 없음 — service_role 키는 RLS를 우회하므로 이 프로젝트의 쓰기 경로는 영향받지 않지만, RLS가 꺼진 테이블은 anon/authenticated 키를 가진 누구나 접근 가능해진다는 뜻이다.

### 기본 설정

```sql
alter table public.etf_info enable row level security;
-- RLS 활성화 + 정책 없음 = 완전 차단 (안전한 기본값)
```

### 이 프로젝트의 두 가지 RLS 패턴

**공개 읽기 테이블 (`etf_info`)** — 프론트엔드(`etfview.kr`)가 anon 키로 직접 SELECT:

```sql
create policy "public_read_etf_info" on public.etf_info
    for select
    to anon, authenticated
    using (true);

-- INSERT/UPDATE/DELETE 정책 없음 — 쓰기는 이 프로젝트의 service_role 키만
```

**완전 비공개 테이블 (`kis_token_cache`)** — service_role만 접근, 정책 자체를 만들지 않는다:

```sql
alter table public.kis_token_cache enable row level security;
-- 정책 없음 = anon/authenticated 완전 차단, service_role만 접근 가능
```

판단 기준: 이 테이블 데이터를 브라우저에서 봐도 되는가? Yes → `public_read_*` 정책 추가. No(내부 캐시·시크릿성 데이터) → 정책을 아예 만들지 않는다(가장 안전한 기본값).

### 정책 컬럼 인덱싱

```sql
-- 정책 조건에 쓰이는 컬럼, 또는 프론트가 자주 필터링하는 컬럼은 인덱싱
create index ix_etf_info_base_asset_class on public.etf_info (base_asset_class);
create index ix_etf_info_base_market_class on public.etf_info (base_market_class);
```

---

## 5. 스키마 변경 시 동기화

이 프로젝트에는 TypeScript 타입 생성(`supabase gen types`)이 없다 — 대신 **`domain/etf/models.py`의 pydantic 모델이 스키마의 Python 쪽 SSoT**다. 마이그레이션으로 컬럼을 추가/변경하면 반드시 같은 커밋에서 `EtfInfo` 모델과 `EtfInfoRepository`를 함께 갱신한다. 하나만 바뀌면 upsert 시 조용히 필드가 누락되거나 타입 불일치가 런타임에야 드러난다.

프론트엔드(`etfview.kr`)의 `RawEtfRow`/파서도 같은 테이블을 읽으므로, `etf_info` 스키마를 바꾸면 그쪽 타입도 갱신이 필요하다는 것을 PR/커밋 설명에 남긴다(레포가 분리되어 있어 자동 동기화 수단이 없다).

---

## 6. 마이그레이션

```bash
supabase init          # 최초 1회
supabase link --project-ref <ref>

supabase migration new add-etf-enrichment-fields
supabase db push        # 원격 적용 — 실행 전 항상 diff 확인
```

- `supabase/migrations/`는 git 커밋 대상이다.
- 이 프로젝트는 CLI가 로컬에 아직 설치되어 있지 않다(`0001_create_etf_info.sql`, `0002_create_kis_token_cache.sql`은 CLI 없이 작성됨) — CLI 설치 전까지는 Supabase Studio SQL Editor에 마이그레이션 SQL을 그대로 붙여넣어 적용하고, 적용한 파일은 그대로 `supabase/migrations/`에 남겨 이력을 유지한다.
- 프로덕션 마이그레이션은 가능하면 staging에서 먼저 검증한다 — 이 프로젝트는 아직 단일 환경이므로, 최소한 `db push` 전에 SQL을 직접 다시 읽고 `enable row level security` 누락이 없는지 확인한다.

---

## 7. 체크리스트

### 보안
- [ ] public 스키마 모든 테이블 RLS 활성화
- [ ] 공개 읽기 테이블은 `to anon, authenticated` + `using (true)`로 SELECT만 허용, 쓰기 정책은 만들지 않음(service_role 전용)
- [ ] 비공개 테이블(캐시 등)은 정책 자체를 만들지 않음(완전 차단이 기본값)
- [ ] `SUPABASE_SERVICE_ROLE_KEY`는 서버 전용, git/로그 노출 없음

### 성능
- [ ] 프론트 필터 쿼리가 쓰는 컬럼에 인덱스 존재
- [ ] upsert가 배치(리스트 전체 1회 호출)로 이루어지는가, 종목별 N+1 호출로 퇴행하지 않는가

### 개발
- [ ] `etf_info` 스키마 변경 시 `domain/etf/models.py` + `EtfInfoRepository` 동시 갱신
- [ ] `etfview.kr` 쪽 타입도 갱신이 필요함을 커밋/PR에 명시
- [ ] 마이그레이션 파일은 CLI 유무와 무관하게 `supabase/migrations/`에 보존
