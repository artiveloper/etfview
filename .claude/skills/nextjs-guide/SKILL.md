---
name: nextjs-guide
description: >
  etfy Next.js App Router 메커니즘 SSoT.
  Server vs Client Component 경계, Suspense 스트리밍, TypeScript 규칙, 코드 포맷팅(4-space),
  Lighthouse ≥ 90 성능 가드레일.
  Next.js, App Router, Server Component, Client Component, 'use client', Suspense,
  RSC, 스트리밍, 타입스크립트, any, non-null assertion, 포맷팅, Lighthouse, 성능 관련
  작업 시 반드시 참조.
---

# Next.js — App Router 메커니즘

> 대상: `web/` 서브프로젝트. 경로 언급은 `web/` 기준 상대경로다.
> UI 스타일링(모바일 퍼스트·shadcn 컴포넌트·스켈레톤) → `shadcn-ui` 스킬 참조
> 데이터 레이어(React Query·query options·prefetch·mutation) → `react-query-guide` 스킬 참조

목표: Lighthouse 점수 ≥ 90. 클라이언트 JS 최소화, 예측 가능한 데이터 흐름, 도메인 주도 구조.

---

## 1. Server Component vs Client Component

기본은 **Server Component**. `'use client'`는 아래가 필요할 때만 붙인다.
- 브라우저 상호작용/이벤트 핸들러, `useState` 등 훅
- React Query 훅(`useSuspenseQuery`/`useQuery`) 소비, `nuqs`의 `useQueryStates` 소비

경계 규칙:
- **데이터 fetch는 Server Component에서 prefetch** → `HydrationBoundary`로 Client에 전달 (→ `react-query-guide`).
- **UI 상호작용·RQ 훅 소비는 Client Component**가 담당.
- UI 컴포넌트에서 `fetch`/`useEffect`로 직접 패칭 금지 → domain hooks 사용.

```tsx
// app/page.tsx — Server Component
export default async function EtfPage({ searchParams }: Props) {
    const params = await searchParams
    const state = await runPrefetch(
        etfPrefetch.filterOptions(),
        etfPrefetch.list({ page, search, assetClass, market, leverage }),
    )

    return (
        <HydrationBoundary state={state}>
            <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
                <EtfSearch />
                <Suspense fallback={<EtfFiltersSkeleton />}>
                    <EtfFilters />
                </Suspense>
                <Suspense fallback={<EtfListSkeleton />}>
                    <EtfList />
                </Suspense>
            </main>
        </HydrationBoundary>
    )
}
```

`searchParams`는 Next.js 15부터 `Promise`이므로 `await searchParams`로 풀어 쓴다. URL 파라미터의 초기값을 서버에서 읽어 prefetch에 그대로 전달하고, 클라이언트에서는 `nuqs`(→ `react-query-guide` URL 상태 절)가 이어받는다.

---

## 2. Suspense 스트리밍 (route 전체가 아니라 섹션 단위)

이 프로젝트는 라우트가 아직 단순해 GamePot 스타일의 `loading.tsx`(라우트 레벨 자동 Suspense)를 쓰지 않는다 — 대신 **`page.tsx` 안에서 섹션별로 `<Suspense>` 경계를 직접 감싼다** (`EtfFilters`, `EtfList` 각각 독립 경계). 이렇게 하면 필터 옵션과 목록이 서로 기다리지 않고 준비되는 대로 스트리밍된다.

`useSuspenseQuery`를 사용하는 컴포넌트는 반드시 `<Suspense fallback={...}>` 경계 안에 위치해야 한다 — 이 프로젝트의 데이터 조회는 기본적으로 `useSuspenseQuery`다(`domain/etf/hooks/etf.hooks.ts`).

Use Suspense: `useSuspenseQuery`를 사용하는 컴포넌트의 부모, 메인 콘텐츠 블록.
Do NOT use Suspense: `useQuery`를 쓰는 컴포넌트(직접 `isLoading` 처리), 사용자 트리거 refetch, 페이지네이션 로딩(페이지네이션은 같은 캐시 그룹 내 전환이라 전체 리로딩이 아니다 — → `react-query-guide` 9절).

새 라우트가 여러 개 생겨 라우트 전환 자체의 로딩이 필요해지면(현재는 단일 페이지) 그때 `loading.tsx` 도입을 검토한다 — 아직 없는 요구를 미리 만들지 않는다.

---

## 3. TypeScript 규칙 (MANDATORY)

- `any` 금지
- non-null assertion(`!`) 금지
- `interface`보다 `type` 선호
- 타입은 가능한 한 이른 지점에서 좁힌다(narrow types early) — 예: 외부 응답을 parser 레이어에서 도메인 타입으로 즉시 변환(`domain/etf/parser/etf.parser.ts`)하고, 그 이후 레이어는 넓은 타입을 다시 좁히지 않는다.

---

## 4. 코드 포맷팅 (MANDATORY)

- 모든 코드는 **4-space 들여쓰기**를 쓴다. 탭·2-space 금지.
- 적용 대상: TypeScript, JavaScript, JSON, Tailwind 클래스 포맷팅, React/JSX/TSX 전체.

```ts
function example() {
    if (true) {
        console.log('4 spaces only')
    }
}
```

---

## 5. 성능 가드레일 (Lighthouse ≥ 90)

**금지:**
- Client Component 안에서 `useEffect`로 데이터 페칭
- 자주 렌더링되는 컴포넌트 내부에서 dynamic import
- 큰 객체를 props로 그대로 전달(경계를 넘어서)
- 메모이제이션 없는 배열/객체를 Client Component에 props로 전달

**필수:**
- Server Component를 기본으로 우선한다
- 직렬화되는 데이터는 최소한만 (hydration payload를 작게 유지)
- 불필요한 client provider를 늘리지 않는다(`app/providers.tsx`에 이미 있는 것 외 추가 시 반드시 필요성 확인)

---

## 6. 에러 처리 (조회/변경 구분)

- **조회(Query)**: 에러를 throw → React Query가 error state로 처리한다. try/catch로 삼키지 않는다.
- **변경(Mutation)**: `useMutation`의 `onError` 또는 `mutateAsync` try/catch로 처리한다(→ `react-query-guide`, 이 프로젝트는 아직 mutation이 없다).
- 원본 `Error` 객체를 UI에 그대로 노출하지 않는다 — 사용자 친화 메시지로 변환한다.
- 빈 상태는 에러가 아니다 — "검색 결과가 없습니다"처럼 왜 비어있는지 설명한다(`components/etf/etf-list.tsx`의 빈 상태 카드 참고).
