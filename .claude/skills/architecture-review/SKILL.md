---
name: architecture-review
description: >
  이 모노레포(web/ Next.js 프론트엔드 + collector/ Python 수집기)의 아키텍처/설계/코드
  리뷰 요청을 적절한 전문 에이전트(architect, frontend-architect, qa-frontend,
  design-system, backend-architect, dba-advisor, qa-backend)로 라우팅하는 디스패처.
  "이 컴포넌트/코드 구조 어때", "설계 리뷰해줘", "상태관리 이렇게 해도 될까", "디자인
  시스템/일관성 확인해줘", "테스트 전략/커버리지 봐줘", "DB 스키마/마이그레이션 검토해줘",
  "잡/스케줄러 구조 리뷰", "Supabase RLS 확인해줘", "이 페이지/코드 구조적으로 문제
  없어?" 같은 요청 시 사용. 후속 요청("다시 검토해줘", "방금 지적한 부분만 다시 봐줘",
  "이전 리뷰 기반으로 업데이트")에도 반드시 사용한다.
  Next.js/React Query/shadcn/Python/Supabase의 구체적 구현 방법 질문("query key는
  어떻게 써", "prefetch 어떻게 해", "토큰 캐싱 어떻게 해")은 nextjs-guide/react-query-guide/
  shadcn-ui/python-guide/supabase-guide 스킬을 직접 참고하면 되므로 이 스킬을 거치지
  않아도 된다 — 이 스킬은 "구조가 맞는지 리뷰/설계"해달라는 요청에만 반응한다.
---

# Architecture Review Dispatcher (모노레포 루트)

## 실행 모드: 서브 에이전트 (전문가 풀)

이 모노레포의 8개 에이전트(`architect`, `frontend-architect`, `qa-frontend`, `design-system`, `backend-architect`, `dba-advisor`, `qa-backend`)는 **서로 통신하지 않고 독립적으로 호출**된다 — 원본 ai-docs 하네스의 설계 그대로다. 한 요청이 여러 관점을 필요로 하면 이 스킬이 관련 에이전트를 **병렬로 서브 에이전트 호출**하고 결과를 종합한다. `TeamCreate`/`SendMessage` 기반 팀 조율은 쓰지 않는다 — 각 에이전트가 서로의 중간 결과에 실시간으로 반응할 이유가 없는 독립 리뷰 작업이기 때문이다.

## Phase 0: 컨텍스트 확인

라우팅 전에 먼저 판단한다:
- 대화 맥락에 이 스킬로 방금 수행한 리뷰 결과가 있고, 사용자가 "그 중 일부만 다시" 또는 "지적한 부분 반영했는지 확인"을 요청하면 → **후속 리뷰**: 해당 부분을 다뤘던 에이전트만 재호출하고, 이전 지적사항을 프롬프트에 포함해 "개선됐는지"를 판단하게 한다.
- 새로운 리뷰 요청이면 → **신규 리뷰**: 아래 라우팅 표로 진행. 먼저 요청이 `web/`(프론트) 대상인지 `collector/`(백엔드) 대상인지, 아니면 둘 다에 걸친 상위 구조 질문인지부터 구분한다.

## 라우팅 표

### web/ (Next.js 프론트엔드)

| 요청 성격 | 호출 에이전트 |
|-----------|---------------|
| 컴포넌트 경계, 상태관리, `domain/{feature}` 계층 위반, 데이터 fetching | `frontend-architect` |
| 디자인 토큰, 컴포넌트 중복, 접근성, 모바일 퍼스트/터치 타겟 위반 | `design-system` |
| 테스트 전략, 컴포넌트/E2E 테스트 갭 | `qa-frontend` |

### collector/ (Python 수집기)

| 요청 성격 | 호출 에이전트 |
|-----------|---------------|
| 계층 분리, 잡 오케스트레이션, 에러 처리, KIS/Supabase 경계 계약 | `backend-architect` |
| Supabase 스키마, 마이그레이션, 인덱스, RLS | `dba-advisor` |
| 테스트 전략, 커버리지 갭, mock 경계 | `qa-backend` |

### 공통 / 상위 구조

| 요청 성격 | 호출 에이전트 |
|-----------|---------------|
| 요구사항/기술스택/`web/`↔`collector/` 경계/전체 구조 | `architect` |
| "전체 리뷰해줘" / "이 PR/변경사항 종합 검토" 같은 광범위 요청 (특정 서브프로젝트 대상) | 해당 서브프로젝트의 관련 에이전트 전원(보통 architect + 2개), 상위 구조 변경이면 `architect` 포함 |
| 두 서브프로젝트 모두에 걸친 변경(예: `etf` 스키마 변경) | `architect` + 영향받는 양쪽의 관련 에이전트(`backend-architect`/`dba-advisor` + `frontend-architect`) |

애매하면 요청 문구에 언급된 경로로 판단한다: `web/domain/` 언급 → frontend-architect, `web/components/` 스타일·색상·접근성 → design-system, `collector/src/etf_collector/infra|jobs|scheduler` 언급 → backend-architect, `collector/supabase/migrations/` 언급 → dba-advisor, `tests/` 언급(양쪽 모두 존재하므로 경로로 구분) → 해당 서브프로젝트의 qa 에이전트.

**Next.js App Router 메커니즘, React Query query-key/prefetch, nuqs, shadcn 구현 패턴, Python/Supabase 구현 패턴 자체에 대한 질문은 이 스킬이 아니라 해당 기술 스킬(`nextjs-guide`/`react-query-guide`/`shadcn-ui`/`python-guide`/`supabase-guide`)을 직접 참고한다** — 그 컨벤션들은 이미 그 스킬들이 SSoT이므로 에이전트를 거치지 않고 바로 답할 수 있다. 이 디스패처는 "그 컨벤션이 지켜지고 있는가/구조가 맞는가"를 판단하는 리뷰 요청에만 반응한다.

## 실행 방법

각 대상 에이전트를 `Agent` 도구로 직접 호출한다. **`model: "opus"`를 반드시 명시**하고, `subagent_type`에 에이전트 정의 파일의 이름을 지정한다. 프롬프트에는 리뷰 대상 범위(`web/`/`collector/` 중 어느 쪽인지 포함한 파일 경로, 또는 최근 변경 diff)와 사용자의 원래 질문을 그대로 전달한다 — 에이전트 정의 내용을 요약해서 다시 적지 않는다(에이전트가 자신의 `.md`와 스킬을 직접 읽는다).

- 단일 에이전트로 충분한 요청 → 포그라운드로 1회 호출.
- 복수 에이전트가 필요한 광범위 요청 → 여러 `Agent` 호출을 **한 메시지에 병렬로** 보내고(`run_in_background: true`), 모두 완료되면 결과를 종합한다. 종합 시 에이전트별 소제목으로 구분하고, 서로 다른 에이전트가 상충하는 의견을 내면 삭제하지 말고 둘 다 남기며 출처를 표기한다.

## 데이터 전달

반환값 기반(각 `Agent` 호출의 반환 메시지를 이 스킬이 직접 수집). 대용량 산출물이 없는 작업이므로 파일 기반 전달은 쓰지 않는다.

## 에러 핸들링

- 특정 에이전트 호출이 실패하거나 타임아웃되면 1회 재시도한다. 재실패 시 해당 관점 없이 나머지 결과로 진행하고, 최종 응답에 "OO 관점은 확인하지 못함"을 명시한다 — 조용히 누락하지 않는다.
- 리뷰 대상 코드/파일이 존재하지 않으면 해당 사실을 사용자에게 먼저 확인한다.

## 테스트 시나리오

**정상 흐름 (단일 서브프로젝트)**: "web/domain/etf 상태관리 구조 리뷰해줘" → `web/domain/` 언급으로 `frontend-architect` 1개만 호출 → 구조 진단 반환.

**정상 흐름 (다른 서브프로젝트)**: "collector/src/etf_collector/infra/kis/auth.py 토큰 캐싱 구조 리뷰해줘" → `collector/.../infra/` 언급으로 `backend-architect` 1개만 호출.

**광범위 흐름**: "collector에 enrichment job 추가했는데 전체적으로 검토해줘" → `backend-architect`(계층/에러처리) + `dba-advisor`(새 컬럼/인덱스) + `qa-backend`(테스트 갭) 병렬 호출 → 3개 결과를 소제목으로 종합.

**모노레포 경계 흐름**: "etf에 컬럼 추가하려는데 양쪽 다 봐줘" → `architect`(경계 정합성) + `dba-advisor`(마이그레이션) + `backend-architect`(모델 동기화) + `frontend-architect`(파서 타입 동기화) 병렬 호출 → 4개 결과 종합.

**에러 흐름**: `design-system` 호출이 타임아웃 → 1회 재시도 후에도 실패 → 나머지 결과만으로 응답하고 "디자인 시스템 관점은 이번에 확인하지 못했다"고 명시.
