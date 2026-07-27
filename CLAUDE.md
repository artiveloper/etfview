# CLAUDE.md — etf 모노레포 작업 지침

이 문서는 이 저장소(`web/` Next.js 프론트엔드 + `collector/` Python 배치 수집기)에서 코드를 다룰 때 지켜야 할 행동 지침이다.
속도보다 신중함을 우선한다. 불필요한 diff가 줄고, 재작성이 줄고, 질문이 앞당겨지면 잘 지켜지고 있는 것이다.

---

## 1. 코딩 전에 생각한다

가정하지 말고, 혼란을 숨기지 말고, 트레이드오프를 드러낸다.

- 가정은 명시한다. 불확실하면 묻는다.
- 해석이 여럿이면 조용히 하나를 고르지 말고 제시한다.
- 더 단순한 방법이 있으면 말한다. 필요하면 반대 의견도 낸다.
- 불명확하면 멈추고, 무엇이 헷갈리는지 이름 붙여 묻는다.

## 2. 단순함 우선

문제를 푸는 최소 코드만 쓴다. 추측성 구현은 없다.

- 요청받지 않은 기능·추상화·"유연성"은 넣지 않는다.
- 일어날 수 없는 시나리오에 대한 에러 처리는 넣지 않는다.
- 200줄인데 50줄로 될 것 같으면 다시 쓴다. "시니어가 과설계라 할까?" 자문한다.

## 3. 외과적 변경

건드려야 하는 것만 건드리고, 내가 만든 것만 치운다.

- 인접 코드·주석·서식을 "개선"하지 않는다. 안 깨진 걸 리팩터링하지 않는다.
- 내가 좋아하는 방식이라도 기존 스타일에 맞춘다(→ `web/`은 `nextjs-guide` 4절 4-space, `collector/`는 `python-guide`의 ruff 설정 참고).
- 무관한 죽은 코드는 발견하면 언급만 하고 지우지 않는다.
- 단, 내 변경이 만든 미사용 import·변수·함수는 내가 제거한다.
- `web/`과 `collector/`는 별개 배포 단위다 — 한쪽 작업 중 다른 쪽 파일을 건드릴 이유가 없으면 건드리지 않는다(예외: `etf` 스키마처럼 둘 다에 영향을 주는 변경).

## 4. 목표 기반 실행

성공 기준을 정의하고 검증될 때까지 반복한다.

- "검증 추가"는 "잘못된 입력에 대한 테스트를 쓰고 통과시킨다"로 바꾼다.
- "버그 수정"은 "재현 시나리오를 확인하고 고친 뒤 다시 재현해 실패하지 않음을 확인한다"로 바꾼다.
- 다단계 작업은 먼저 짧게 적는다. 단계별 **계획**, 완료를 표시할 **체크리스트**, 결정·전제를 남기는 **컨텍스트 노트**를 두고, 각 단계마다 검증 방법을 명시한다.

## 5. 한국어 출력 시 문장 끝은 마침표

한국어 문장을 콜론(:)으로 끝내지 않는다.

- 다음 줄이 목록·예시여도 문장 종결은 `.` `?` `!` 로 한다.
- 영어 문서로 학습된 콜론 습관이 한국어에 새어 나온다. 잡아낸다.
- 코드·키값 쌍·라벨 안의 콜론은 괜찮다. 문장 종결로만 쓰지 않는다.

## 6. 새 파일 첫 줄은 한국어 역할 주석

새 소스 파일을 만들면 첫 줄에 역할을 한 줄 한국어로 적는다.

- `collector/`(Python)는 `# KIS 마스터파일을 다운로드해 ETF 종목만 골라내는 모듈` 처럼 쓴다.
- `web/`(TypeScript)는 `// ETF 목록 검색·필터 상태를 URL과 동기화하는 컴포넌트` 처럼 쓴다.
- 필수 지시자(`from __future__`, `'use client'`/`'use server'` 등) 바로 아래 둔다.
- 설정 파일(`*.toml`, `*.json`, `*.mjs` 설정 등)은 예외다.
- 이유는 에이전트가 파일을 선택적으로 읽기 때문이다. 한 줄 헤더가 다음 세션에 즉시 맥락을 준다.

## 7. 오류는 읽고, 추측하지 않는다

실패하면 실제 에러·로그 줄을 읽는다.

- 전체 에러 메시지와 스택 트레이스를 읽는다. 가정한 로그가 아니라 실제 출력을 본다.
- 원인 확인 전에 "흔한 수정"을 적용하지 않는다. 불명확하면 로그/콘솔을 찍어 상태를 확인한 뒤 고친다.
- `web/`은 Supabase(publishable key, 읽기 전용)에 의존한다 — 실패 시 Supabase 쿼리 / React Query / 렌더링 중 어느 경계인지 먼저 특정한다.
- `collector/`는 KIS Open API·Supabase(secret key)에 의존한다 — 실패 시 KIS 마스터파일 파싱 / KIS 인증 / Supabase upsert / 스케줄러 중 어느 경계인지 먼저 특정한다.

## 8. 완료 전에 실행해서 확인한다

코드를 건드렸으면 "다 됐다"고 하기 전에 검증한다.

- `web/` 변경: 타입 체크·린트를 통과시키고, UI를 바꿨으면 `pnpm dev`로 실제 화면에서 확인한다.
- `collector/` 변경: 테스트·린트·타입체크를 통과시키고, 실제 KIS/Supabase 경로를 건드렸으면 `--once` 플래그로 단발 실행해 로그를 확인한다.
- 사용자가 "끝", "완료"라고 하기 전에 선제적으로 검증한다. 구체 명령은 아래 [프로젝트 컨텍스트](#프로젝트-컨텍스트--검증) 참고.

## 9. 커밋은 원자적·의미 단위로

되돌릴 수 있게, 한 번에 하나의 논리적 변경만 커밋한다.

- 무관한 변경을 한 커밋에 섞지 않는다. 리팩터링과 기능 추가를 분리한다. `web/`과 `collector/`에 걸친 변경(`etf` 스키마 등)은 예외적으로 한 커밋에 묶을 수 있다 — 원자성의 단위는 "논리적 변경" 하나이지 "디렉토리 하나"가 아니다.
- 커밋 메시지는 "무엇을 왜"가 드러나게 쓴다.
- 커밋·푸시는 사용자가 요청할 때 한다. 이 저장소는 `main` 브랜치에서 직접 작업한다 — 별도 feature 브랜치를 만들지 않고 `main`에 바로 커밋·푸시한다(사용자 지침, 2026-07-27).

---

## 프로젝트 컨텍스트 & 검증

이 저장소는 국내 상장 ETF 정보를 다루는 두 서브프로젝트로 구성된다. **`web/`**은 조회 전용 Next.js 사이트, **`collector/`**는 한국투자증권(KIS) Open API로 ETF 정보를 수집해 Supabase에 적재하는 Python 배치 수집기다. 둘은 **`etf` Supabase 테이블 스키마로만 결합**된다 — `collector/`가 secret key로 유일하게 쓰고, `web/`은 publishable key로 읽기만 한다. 스키마를 바꾸면 항상 양쪽 모두(`collector/src/etf_collector/domain/etf/models.py` ↔ `web/domain/etf/parser/etf.parser.ts`) 확인한다.

### web/ — Next.js 프론트엔드

```
web/app/                진입점 (App Router) — page.tsx, layout.tsx, providers.tsx
web/domain/etf/          유일한 도메인 — types/apis/parser/query-keys/query-options/hooks/prefetch 7계층
web/components/etf/      ETF 목록/카드/필터/검색/스켈레톤 (기능 콜로케이션)
web/components/ui/        shadcn 프리미티브 (Card, Badge, Button, ToggleGroup 등)
web/lib/supabase/         Supabase 클라이언트 (publishable key)
web/lib/react-query/      QueryClient, runPrefetch
```

스택: Next.js App Router(TypeScript strict) · TanStack React Query(`useSuspenseQuery` 기본) · `nuqs`(URL 상태) · Tailwind + shadcn/ui · 패키지 매니저 `pnpm`.

```bash
cd web
pnpm typecheck                 # tsc --noEmit
pnpm lint                      # eslint
pnpm format                    # prettier --write
pnpm dev                       # 실제 화면 확인 (테스트 스위트 없음 — 이게 사실상의 검증 수단)
pnpm build                     # 프로덕션 빌드 통과 확인
```

> 자동화된 테스트가 아직 없다. UI/데이터 관련 변경은 `pnpm dev`로 직접 화면을 띄워 확인하는 것이 유일한 실질적 검증 수단이다.

### collector/ — Python 배치 수집기

```
collector/src/etf_collector/domain/etf/    순수 타입 (EtfInfo pydantic 모델)
collector/src/etf_collector/infra/kis/     KIS 마스터파일 다운로드·파싱, OAuth 토큰 캐싱, httpx 래퍼
collector/src/etf_collector/infra/supabase/ Supabase 클라이언트, EtfInfoRepository
collector/src/etf_collector/jobs/          domain+infra 오케스트레이션 (sync_etf_info)
collector/src/etf_collector/scheduler/     APScheduler 등록 + CLI 진입점 (--once 플래그)
collector/supabase/migrations/             etf, kis_token_cache, etf_constituent, job_execution_log 스키마
collector/tests/{unit,integration}/
```

스택: Python 3.12 · `uv` + `pyproject.toml` · httpx(비동기) · APScheduler · pydantic-settings · supabase-py · ruff/mypy strict/pytest.

```bash
cd collector
uv sync                                             # 의존성 설치
uv run ruff check . && uv run ruff format --check . # 린트·포맷
uv run mypy src                                     # 타입 체크
uv run pytest                                       # 테스트
uv run etf-collector --once                         # 단발 실행 (.env 필요)
```

> KIS **ETF 구성종목시세 API**(국내주식-073, TR `FHKST121600C0`)는 `output2`에 구성종목을 **구성비중(`etf_cnfg_issu_rlim`) 내림차순 상위 30개까지만** 반환한다(장중 실측 확인 — KODEX 200은 구성종목 201개 중 비중 상위 30개만 내려옴). 그래서 `etf_constituent`에 적재되는 값은 비중 상위 30종목일 뿐 전체 보유내역이 아니다 — 구성종목 커버리지를 다룰 때는 이 한계를 전제로 삼는다. 또한 `output2`는 구성종목별 실시간 시세 배열이라 **장 개장 전에는 비어서 돌아온다** — 수집 단계를 마감 후(15:40)에 두는 이유다.

---

## 하네스: 아키텍처 리뷰

**목표:** `web/`(프론트엔드 구조·상태관리·디자인 시스템·테스트)과 `collector/`(백엔드 구조·DB 스키마·테스트)에 걸친 아키텍처/설계 리뷰 요청을 전문 에이전트(architect, frontend-architect, qa-frontend, design-system, backend-architect, dba-advisor, qa-backend)로 라우팅한다. 에이전트는 독립 호출되며 팀 통신은 없다.

**트리거:** 아키텍처/설계/컴포넌트·코드 구조/디자인 시스템/DB 스키마/테스트 전략 리뷰 요청 시 `architecture-review` 스킬(오케스트레이터)을 사용하라. Next.js/React Query/shadcn/Python/Supabase의 구체적 구현 방법 자체는 `nextjs-guide`/`react-query-guide`/`shadcn-ui`/`python-guide`/`supabase-guide` 스킬로 직접 답해도 된다 — 하네스를 거치지 않아도 된다. 단순 질문(코드 설명 등)은 직접 응답 가능.

**변경 이력:**
| 날짜 | 변경 내용 | 대상 | 사유 |
|------|----------|------|------|
| 2026-07-18 | etfview.kr 하네스 초기 구성 (에이전트 4, 스킬 4 — ai-docs common/front 기반) | web | eft-collector/ai-docs를 프로젝트에 이식 |
| 2026-07-18 | eft-collector 하네스 초기 구성 (에이전트 4, 스킬 6 — ai-docs common/back 기반) | collector | 동일 |
| 2026-07-19 | nextjs-guide·react-query-guide·shadcn-ui 스킬 3종 신규 | web | GamePot 원본을 실제 코드 기준으로 재작성 |
| 2026-07-19 | 두 저장소를 `web/`+`collector/` 모노레포로 통합, `.claude`·`CLAUDE.md`를 루트 하나로 병합 (에이전트 7, 스킬 13) | 전체 | `etf_info` 스키마로만 결합된 두 프로젝트를 한 저장소에서 관리하기로 결정 — `architect`/`system-architecture`/`architecture-review` 3개는 양쪽 내용을 병합, 나머지는 대상 서브프로젝트를 스코프 노트로 명시하고 그대로 이동 |
