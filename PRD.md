# PRD — etfy (국내 상장 ETF 조회 서비스)

이 문서는 etfy 제품이 **무엇을 하고, 어떤 데이터·기능·한계를 갖는지**를 한눈에 파악하기 위한 제품 명세다.
"코드를 어떻게 다루는가"(작업 지침·검증 커맨드·아키텍처 리뷰 라우팅)는 [`CLAUDE.md`](./CLAUDE.md)에 있다 — 역할이 겹치면 이 문서는 제품/기능을, CLAUDE.md는 작업 방식을 맡는다.

> **살아있는 문서.** 기능·스키마·스케줄을 바꾸는 작업을 하면, 같은 맥락에서 이 문서의 관련 섹션과 맨 아래 [변경 이력](#9-변경-이력)을 함께 갱신한다.

---

## 1. 제품 개요

국내 상장 ETF의 기본정보·시세·구성종목을 **조회 전용**으로 제공하는 웹 서비스다. 투자 판단에 필요한 ETF 정보(총보수·순자산·추적오차·괴리율·구성종목 비중 등)를 한 화면에서 빠르게 훑어보는 것을 목표로 한다. 매매·주문·로그인 같은 사용자 인증 기능은 없다.

두 배포 단위로 구성된다.
- **`web/`** — 사용자가 보는 Next.js 조회 사이트 (읽기 전용).
- **`collector/`** — 한국투자증권(KIS)·KRX에서 ETF 데이터를 수집해 Supabase에 적재하는 Python 배치 수집기 (쓰기 전용).

둘은 **`etf` Supabase 스키마로만 결합**된다 — 코드 의존성이 없고, DB 테이블을 계약으로 공유한다.

---

## 2. 시스템 구성 (한눈에)

```
  사용자
    │  (조회)
    ▼
┌─────────────┐   publishable key    ┌──────────────┐   secret key   ┌─────────────┐
│   web/      │ ───── 읽기 전용 ────▶ │  Supabase    │ ◀──── 쓰기 ──── │ collector/  │
│ Next.js     │                       │  Postgres    │                 │ Python 배치 │
│ (조회 사이트)│                       │ (etf 스키마) │                 │ (수집기)    │
└─────────────┘                       └──────────────┘                 └──────┬──────┘
                                                                              │ 수집
                                                                    ┌─────────┴─────────┐
                                                                    │  KRX 데이터포털   │
                                                                    │  KIS Open API     │
                                                                    └───────────────────┘
```

| 배포 단위 | 역할 | DB 접근 |
|----------|------|---------|
| `web/` | ETF 목록·상세 조회 UI | publishable key (읽기) |
| `collector/` | KRX/KIS → Supabase 적재 배치 | secret key (쓰기, RLS 우회) |

스키마 변경 시 항상 양쪽 모두 확인한다 — `collector/src/etf_collector/domain/etf/models.py` ↔ `web/domain/etf/parser/etf.parser.ts`.

---

## 3. 데이터 모델

Supabase(Postgres) 테이블. 마이그레이션은 `collector/supabase/migrations/`에서 관리한다. 모든 결합은 ETF **단축코드(`short_code`)**로 이뤄진다(ISIN 아님).

| 테이블 / 뷰 | 담는 데이터 | 키 | 이력 |
|------------|-----------|-----|------|
| `etf` | ETF 기본정보(종목명·운용사·기초지수·총보수·자산/시장분류·상장일·상장폐지 감지일 등) | PK `short_code` | 최신 (upsert) |
| `etf_quote` | 일 1회 시세 스냅샷(현재가·등락·NAV·괴리율·추적오차·순자산총액·구성종목수·외국인비중 등) | PK/FK `short_code` | **미보존** (덮어쓰기) |
| `etf_price` | 일별 OHLCV 시계열(시/고/저/종가·거래량·거래대금·권리락코드) | PK `(short_code, trade_date)` | 보존 (일자별 누적) |
| `etf_constituent` | 구성종목 스냅샷(종목명·비중·평가금액 + 구성종목 시세) — **비중 상위 30종목만** | PK `(etf_short_code, constituent_short_code)` | **미보존** (덮어쓰기) |
| `kis_token_cache` | KIS 접근토큰 싱글턴 캐시 + 분산 락 | PK `id=1` (CHECK) | 최신 |
| `job_execution_log` | 배치 실행 이력(잡명·시작/종료·상태·처리행수·에러) | PK `id` (identity) | 보존 |
| `etf_filter_options` (뷰) | `etf`에서 필터 옵션 5종을 미리 distinct 집계(자산/시장/운용사/복제방법/과세유형) | — | — |

---

## 4. 데이터 수집 (collector)

APScheduler로 평일에 3개 파이프라인이 돈다(진입점: `collector/src/etf_collector/scheduler/main.py`, 단계 정의: `jobs/pipeline.py`). 각 단계는 `job_execution_log`에 개별 기록되고, 한 단계 실패 시 해당 파이프라인은 중단된다.

| 파이프라인 | 스케줄 (평일) | 하는 일 | 적재 대상 |
|-----------|--------------|--------|----------|
| `run_daily_open` | 08:30 (1회) | `sync_etf_info` — KRX 마스터파일로 ETF 유니버스 동기화 + 사라진 종목 상장폐지 표시 | `etf` |
| `run_intraday_price` | 09:00~15:30 (30분 간격) | `sync_etf_price`(window=0) — 오늘 미완성 봉만 갱신 | `etf_price` |
| `run_daily_close` | 15:40 (1회) | `enrich_etf_info`(현재가 스냅샷) → `sync_etf_price`(window=7, 봉 확정) → `sync_etf_constituent`(구성종목) 순차 | `etf_quote`·`etf_price`·`etf_constituent` |

- **온디맨드**: `--backfill-price --backfill-days=N` — 최근 N일 주가 소급 수집(90일 단위 윈도우 분할).
- **CLI 플래그**: `--once`(open 1회), `--intraday-once`(intraday 1회), `--revoke`(종료 시 KIS 토큰 폐기).

**데이터 출처**
- **KRX 데이터포털** `MDCSTAT04601` — ETF 전종목 기본정보(마스터파일).
- **KIS Open API** — 현재가 상세(`FHPST02400000`) / 일별 OHLCV(`FHKST03010100`) / 구성종목시세(`FHKST121600C0`).

수집 안정성: 동시요청 세마포어 + 최소 디스패치 간격(페이싱)으로 KIS 유량 한도를 지키고, 토큰은 `kis_token_cache`에 캐싱하며 다중 인스턴스 대비 행 기반 리스 락으로 동시 재발급을 막는다.

> 검증 커맨드(uv sync / ruff / mypy / pytest / `--once`)는 [CLAUDE.md의 collector 섹션](./CLAUDE.md) 참조.

---

## 5. 사용자 기능 (web)

라우트: 목록 `web/app/page.tsx`, 상세 `web/app/etf/[shortCode]/page.tsx`. 두 페이지 모두 서버에서 프리페치 후 `HydrationBoundary`로 넘겨 초기 로딩을 최적화한다.

### 목록 페이지
- ✅ **검색** — ETF 이름으로 검색(`etf.name` 부분일치 ILIKE). *구성종목명 검색은 미지원 → [8. 로드맵](#8-로드맵--보류-항목) 참고.*
- ✅ **필터 6종** (누적 적용, 초기화 버튼) — 기초자산 · 시장 · 유형(일반/레버리지/인버스) · 운용사 · 복제방법 · 과세유형.
- ✅ **정렬** — 순자산총액 내림차순 → 단축코드 순 (서버 고정, UI 선택기 없음).
- ✅ **무한스크롤** — IntersectionObserver로 18개씩 로드.
- ✅ **ETF 카드** — 약칭·총보수·현재가·등락률·운용사·기초자산·시장·추적배수·순자산·상장일. 카드 클릭 시 상세로 이동.

### 상세 페이지
- ✅ **헤더** — ETF명·종목코드·현재가·등락금액/률.
- ✅ **핵심지표 4** — 총보수 · 순자산총액 · 추적오차율 · 괴리율.
- ✅ **개요** — 운용사·기초지수·지수산출기관·NAV·1년 최고/최저·구성종목수·외국인 보유비중·상장일.
- ✅ **구성비중 파이차트** — 비중 상위 10종목 + 기타 합산 (recharts).
- ✅ **구성종목 TOP30 테이블** — 종목명·현재가·등락률·비중 (모바일 카드 ↔ 데스크톱 테이블 전환). *전체 보유내역 아님 — [7. 한계](#7-제약--알려진-한계) 참고.*
- ✅ **개념 설명 팝오버** — NAV·괴리율.

### 공통
- ✅ 반응형(모바일 1열 → 태블릿 2열 → 데스크톱 3열, 44px 터치타겟) · ✅ 다크/라이트 모드 · ✅ URL 상태 저장(검색·필터를 쿼리스트링으로, 뒤로가기 복원).

데이터 레이어는 `web/domain/etf/`의 7계층(types·apis·parser·query-keys·query-options·hooks·prefetch)으로 구성된다.

> 검증 커맨드(pnpm typecheck / lint / dev / build)는 [CLAUDE.md의 web 섹션](./CLAUDE.md) 참조.

---

## 6. 기술 스택

| 영역 | 스택 |
|-----|------|
| `web/` | Next.js 16 (App Router) · React 19 · TanStack React Query(useSuspenseQuery 기본) · nuqs(URL 상태) · Tailwind v4 + shadcn/ui · recharts · pnpm |
| `collector/` | Python 3.12 · httpx(async) · APScheduler · pydantic / pydantic-settings · supabase-py · uv · ruff/mypy strict/pytest |
| 공유 | Supabase (Postgres) |

---

## 7. 제약 · 알려진 한계

- **구성종목은 비중 상위 30종목만.** KIS 구성종목시세 API(`FHKST121600C0`)가 실제 구성종목 수와 무관하게 서버 안정성 목적으로 최대 30건만 반환한다(KIS 공식 확인). 따라서 `etf_constituent`와 상세페이지 구성종목은 **전체 보유내역이 아니다**.
- **`etf_quote`·`etf_constituent`는 이력을 보존하지 않는다** — 매 수집마다 최신 스냅샷으로 덮어쓴다. 시계열이 필요한 시세는 `etf_price`만 일자별로 누적한다.
- **web에 자동화 테스트가 없다** — UI/데이터 변경은 `pnpm dev` 실제 화면 확인이 사실상 유일한 검증 수단이다.
- **알림 체계가 없다** — 배치 실패는 `job_execution_log`가 유일한 사후 추적 수단이다.

---

## 8. 로드맵 / 보류 항목

| 항목 | 상태 | 비고 |
|-----|------|------|
| **구성종목명 검색 → 포함 ETF 노출** | **보류** | 기술적으로 가능(web/만 수정)하나, 구성종목이 비중 상위 30종목만 적재돼 "포함 ETF 전체"로 오해할 위험이 큼. KIS가 전체 구성종목을 제공하기 시작하는 **2026년 하반기** 이후 재검토. |

---

## 9. 변경 이력

| 날짜 | 변경 내용 | 사유 |
|------|----------|------|
| 2026-07-24 | PRD.md 초기 작성 (제품 개요·데이터 모델·수집 파이프라인·사용자 기능·제약·로드맵) | 전체 구조·기능을 한눈에 파악할 제품 문서 부재 → 살아있는 문서로 신설 |
| 2026-07-28 | 제품명 etfview → etfy로 리브랜딩, 문서 전반 반영 | 사용자 리브랜딩 결정 |
