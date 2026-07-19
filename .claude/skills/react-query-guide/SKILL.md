---
name: react-query-guide
description: >
  etfview.kr React Query 데이터 레이어 SSoT.
  도메인 디렉토리 구조(types/apis/parser/query-keys/query-options/hooks/prefetch),
  query key 안정성 규칙, queryOptions 팩토리, useQuery vs useSuspenseQuery, prefetch/
  HydrationBoundary, 캐시 레이어, nuqs URL 상태, 페이지네이션, mutation/invalidation 규칙.
  React Query, query key, query options, prefetch, useSuspenseQuery, useInfiniteQuery,
  nuqs, mutation, invalidate, 신규 도메인/feature 데이터 레이어 추가 시 반드시 참조.
---

# React Query — 데이터 레이어 패턴

> 대상: `web/` 서브프로젝트. 경로 언급은 `web/` 기준 상대경로다.
> UI/컴포넌트/Tailwind·shadcn 구현 → `shadcn-ui` 스킬 참조
> Next.js Server/Client 경계·Suspense → `nextjs-guide` 스킬 참조
> Supabase 클라이언트 → 현재 `lib/supabase/client.ts` (anon 키, 읽기 전용 — 이 프로젝트는 DB 스키마를 소유하지 않는다. 쓰기는 별도 저장소 `eft-collector`가 담당)

---

## 1. 도메인 디렉토리 구조 (필수)

```
domain/{feature}/
├── index.ts                     — 클라이언트 안전 public API
├── server.ts                    — 서버 전용 public API (import "server-only")
├── types/
│   └── index.ts                 — 도메인 타입 (엔티티, request/response shape)
├── apis/
│   └── {domain}.api.ts          — 외부 API(Supabase 등) fetch 호출
├── parser/
│   └── {domain}.parser.ts       — API 응답 → 도메인 타입 변환
├── query-keys/
│   └── {domain}.query-keys.ts   — Query key 팩토리
├── query-options/
│   └── {domain}.query-options.ts — queryOptions 팩토리 (hooks·prefetch가 공유)
├── hooks/
│   └── {domain}.hooks.ts        — 클라이언트 React Query 훅
└── prefetch/
    └── {domain}.prefetch.ts     — 서버 전용 prefetch (import "server-only")
```

실제 구현 예시(`domain/etf/`): `types` → `EtfInfo`/`EtfListParams` 등, `apis/etf.api.ts` → Supabase 쿼리, `parser/etf.parser.ts` → snake_case DB row를 camelCase 도메인 타입으로 변환, `query-keys`/`query-options`/`hooks`/`prefetch`가 아래 절의 패턴을 그대로 따른다.

### 레이어 책임

| 레이어 | 역할 | 의존성 |
|-------|------|--------|
| **types** | 타입 정의 | 없음 |
| **apis** | 외부 API 호출 (fetch) | types |
| **parser** | API 응답 → 도메인 타입 변환 | types |
| **query-keys** | Query Key 팩토리 | types |
| **query-options** | queryOptions 팩토리 | query-keys, apis, parser |
| **hooks** | Client-side React Query hooks | query-options, query-keys |
| **prefetch** | SSR prefetch (server-only) | query-options |

### 진입점 규칙

`server.ts`와 `prefetch/`는 반드시 `import "server-only"`를 최상단에 선언한다(`domain/etf/server.ts`, `domain/etf/prefetch/etf.prefetch.ts` 참고).

| 디렉토리 | index.ts | 이유 |
|----------|----------|------|
| 루트 | ✅ 필수 | 클라이언트 public API |
| types | ✅ 필수 | 외부에서 타입 import |
| hooks / query-keys / query-options | ❌ 불필요 | 루트에서 직접 export |
| apis / parser | ❌ 불필요 | 내부에서만 사용 |
| prefetch | ❌ 불필요 | server.ts에서 export |

```ts
// ❌ deep import
import { etfPrefetch } from "@/domain/etf/prefetch/etf.prefetch"

// ✅ client component
import { useEtfList, etfQueryOptions } from "@/domain/etf"

// ✅ server component (page.tsx)
import { etfPrefetch } from "@/domain/etf/server"
```

`export *` 금지, deep import 금지 — 크로스 도메인이든 같은 도메인 내부든 항상 `index.ts`/`server.ts` 진입점을 통해서만 접근한다.

---

## 2. Query Keys (STRICT)

- Query key는 배열이어야 한다.
- Stable & serializable만 담는다.
- 인라인 query key 금지.
- 파라미터는 하나의 단일 객체로 묶는다.

```ts
// etf.query-keys.ts
export const etfQueryKeys = {
    all: ['etf'] as const,
    list: (params: ListKeyParams) => ['etf', 'list', params] as const,
    filterOptions: ['etf', 'filterOptions'] as const,
}
```

금지:
```ts
useQuery(['etf', filters]) // filters가 검증 안 된 객체
```

항상:
```ts
useQuery(etfQueryOptions.list(normalizedFilters))
```

파라미터는 직렬화 안전해야 하고, `undefined` 필드는 제거하며, URL에서 파생된 값은 정렬해 넣는다.

---

## 3. Query Options (MANDATORY)

모든 쿼리는 공유 query option 팩토리를 써야 한다. 인라인 `useQuery({...})`/`useSuspenseQuery({...})` 금지.

### useQuery vs useSuspenseQuery

**`useSuspenseQuery`가 기본이다.** `useQuery`는 Suspense 경계를 둘 수 없거나 `isLoading`을 직접 제어해야 할 때만 예외적으로 쓴다(→ `nextjs-guide` 2절). 이 프로젝트의 `useEtfList`/`useEtfFilterOptions`(`domain/etf/hooks/etf.hooks.ts`)는 모두 `useSuspenseQuery`다 — `data`가 항상 정의되어 있으므로 `isLoading` 분기가 없다.

```ts
// query-options
export const etfQueryOptions = {
    list: (params: ListParams) => ({
        queryKey: etfQueryKeys.list(params),
        queryFn: () => fetchEtfList({ ...params, pageSize: 20 }),
    }),
    filterOptions: () => ({
        queryKey: etfQueryKeys.filterOptions,
        queryFn: fetchEtfFilterOptions,
        staleTime: 24 * 60 * 60_000,   // 필터 옵션처럼 자주 안 바뀌는 데이터는 staleTime을 길게
        gcTime: 24 * 60 * 60_000,
    }),
}

// hooks — data는 항상 정의됨
export function useEtfList(params: ListParams) {
    return useSuspenseQuery(etfQueryOptions.list(params))
}
```

캐시 설정 override 기준: 실시간성 데이터는 짧은 staleTime, 정적 데이터(필터 옵션 등)는 긴 staleTime. 일반적인 목록/상세는 override하지 않고 전역 기본값(`lib/react-query/query-client.ts`: `staleTime: 60_000`, `gcTime: 5 * 60_000`)을 쓴다.

### useInfiniteQuery 예외

`useInfiniteQuery`는 `getNextPageParam` 등 클라이언트 전용 옵션이 필요해 `queryOptions` 팩토리로 공유하지 않고 hooks 파일에 직접 정의한다. queryKey는 반드시 `queryKeys` 팩토리를 재사용한다. (현재 이 프로젝트는 무한 스크롤 대신 페이지네이션을 쓰므로 아직 해당 없음 — 도입 시 이 규칙을 적용한다.)

---

## 4. Prefetch 전략

### 언제 prefetch 하는가

**반드시**: 목록 페이지(SEO, LCP 목적), 내부 네비게이션으로 도달하는 상세 페이지, 주 라우트 데이터.
**선택**: 보조 탭, 비핵심 관련 데이터.
**금지**: 무한 스크롤 2페이지 이후, 휘발성이 큰 데이터, 모달 전용 데이터.

`runPrefetch`가 QueryClient 생성 + dehydrate를 캡슐화한다 — 페이지는 QueryClient를 직접 다루지 않는다.

```ts
// lib/react-query/prefetch.ts
export async function runPrefetch(...prefetchers: Array<(qc: QueryClient) => Promise<void>>) {
    const qc = getQueryClient()
    await Promise.all(prefetchers.map(fn => fn(qc)))
    return dehydrate(qc)
}
```

Prefetch 함수는 **curried 형태**로 작성한다 — `(params?) => (queryClient) => Promise<void>`, `runPrefetch`와 자연스럽게 조합된다.

```ts
// etf.prefetch.ts
import "server-only"
export const etfPrefetch = {
    list(params: ListParams) {
        return async (queryClient: QueryClient) => {
            await queryClient.prefetchQuery(etfQueryOptions.list(params))
        }
    },
}
```

`queryOptions`를 그대로 재사용해야 prefetch의 `queryKey`와 클라이언트 `useQuery`의 `queryKey`가 항상 동일하게 유지되어 dehydration이 올바르게 매칭된다.

```ts
// app/page.tsx — 복수 prefetch는 병렬 실행
const state = await runPrefetch(
    etfPrefetch.filterOptions(),
    etfPrefetch.list({ page, search, assetClass, market, leverage }),
)
```

---

## 5. 캐시 레이어

| 레이어 | 역할 |
|--------|------|
| Next.js fetch cache (L0) | ISR/revalidateTag용 — 클라이언트 freshness 용도 아님 |
| React `cache()` (L1) | 단일 RSC 렌더 내 중복 fetch 제거 (`lib/react-query/query-client.ts`의 `getQueryClient`가 이미 적용) |
| React Query cache (L2) | UI 상태의 단일 출처. 모든 UI는 여기서만 읽는다 |

서버 데이터는 React Query hydration 이후에만 fresh하다고 간주한다.

---

## 6. URL 상태 (nuqs)

이 프로젝트는 `nuqs`를 실제로 쓴다(`domain/etf/params.ts`) — 목록 필터·검색·페이지는 `useState`가 아니라 `useQueryStates`로 URL에 둔다.

```ts
// domain/etf/params.ts
export const etfSearchParams = {
    page: parseAsInteger.withDefault(1),
    search: parseAsString.withDefault(''),
    assetClass: parseAsString,
    market: parseAsString,
    leverage: parseAsStringLiteral(LEVERAGE_VALUES),
}

// 클라이언트 컴포넌트
const [{ page, search, assetClass, market, leverage }, setParams] = useQueryStates(etfSearchParams)
```

규칙:
- `null`은 쿼리 파라미터를 제거한다 (`setParams({ assetClass: null })`처럼 "전체"를 표현할 때 사용, `etf-filters.tsx` 참고).
- enum 기본값은 명시적으로 정의한다(`parseAsStringLiteral`).
- 쿼리 파라미터는 query key와 1:1로 매핑되어야 한다 — `etfQueryKeys.list()`가 `nuqs` 값을 그대로 params로 받는 구조를 유지한다.
- **필터가 바뀌면 페이지를 1로 리셋**한다(`etf-filters.tsx`의 `setParams({ assetClass: v, page: null })`처럼 필터 변경 시 `page: null`을 함께 넘긴다).
- Server Component는 `searchParams`로 초기값을 읽어 prefetch에 반영하고, 클라이언트는 `nuqs`로 이어받는다(`nextjs-guide` 1절).

캐시 규칙: 필터 변경 = 새 캐시, 페이지 변경 = 같은 캐시 그룹.

---

## 7. Mutation & Invalidation (아직 미사용 — 도입 시 규칙)

이 프로젝트는 현재 조회 전용이라 mutation이 없다. 향후 사용자 상호작용 기능(즐겨찾기 등)이 추가되면 아래 규칙을 적용한다:

- Mutation은 외부 API를 직접 호출한다.
- Mutation 성공 후 UI 상태를 수동으로 바꾸지 않는다 — 항상 query key로 `invalidateQueries`한다.
- `router.refresh()`를 주 갱신 수단으로 쓰지 않는다.

```ts
export function useCreateFavorite() {
    const queryClient = useQueryClient()
    return useMutation({
        mutationFn: (etfShortCode: string) => createFavorite(etfShortCode),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: etfQueryKeys.all })
        },
    })
}
```

---

## 8. 페이지네이션

- Page index는 query key의 일부여야 한다(`etfQueryKeys.list(params)`의 `params`에 `page` 포함).
- 필터 변경 = 새 캐시, 페이지 변경 = 같은 캐시 그룹 (6절과 동일 원칙).
- 이 프로젝트는 무한 스크롤이 아니라 이전/다음 버튼 페이지네이션을 쓴다(`components/etf/etf-list.tsx`) — 페이지 전환은 Suspense를 트리거하지 않고 같은 캐시 그룹 내 전환이므로 `nextjs-guide` 2절의 "페이지네이션 로딩에 Suspense 쓰지 않음" 규칙과 일치한다.
