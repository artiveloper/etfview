---
name: shadcn-ui
description: >
  etfy Tailwind/shadcn UI 구현 패턴 SSoT.
  모바일 퍼스트 className 규칙(44px 터치 타겟), Card/Badge/ToggleGroup 컴포넌트 패턴,
  피처 콜로케이션 스켈레톤 컴포넌트, 빈 상태 카드.
  Next.js App Router 메커니즘은 nextjs-guide, 데이터 레이어는 react-query-guide 참조.
  Tailwind, shadcn, className, Card, Badge, ToggleGroup, Skeleton, 반응형, 터치 타겟,
  UI 컴포넌트 작업 시 참조.
---

# shadcn/Tailwind — UI 구현 패턴

> 대상: `web/` 서브프로젝트. 경로 언급은 `web/` 기준 상대경로다.
> Next.js App Router 메커니즘(Server/Client 경계·Suspense) → `nextjs-guide` 스킬 참조
> 데이터 레이어(React Query·nuqs) → `react-query-guide` 스킬 참조
> 라이브러리 불문 UI 원칙(모바일 퍼스트·터치 타겟·로딩/빈/에러 상태·접근성) → `design-system` 스킬 참조. 이 스킬은 그 원칙들의 **Tailwind/shadcn 구현**만 다룬다.

이 프로젝트는 `components.json` 기준 `style: radix-luma`, `baseColor: neutral`, `iconLibrary: lucide`, `cssVariables: true`로 설정되어 있다. 새 shadcn 컴포넌트는 `npx shadcn add <component>`로 추가한다(수동 복붙 금지 — 버전/스타일 일관성이 깨진다).

---

## 0. UI 1원칙: 모바일 퍼스트

> 원칙 자체(왜·판단 기준)는 `design-system` 스킬 참조. 이 섹션은 그 원칙의 Tailwind 구현만 다루며, 아래 모든 섹션에 우선한다. **MANDATORY** — 모든 신규 UI에 예외 없이 적용한다.

### Tailwind 사용 규칙

```tsx
// ✅ 모바일 기본, 데스크탑 확장 (app/page.tsx, etf-list.tsx 실제 패턴)
<main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
<div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">

// ❌ 데스크탑 기준으로 먼저 설계
<div className="grid grid-cols-3 gap-6">
```

레이아웃은 GamePot류 대시보드(Sidebar)가 아니라 **단순 페이지 셸**이다 — `<main>` 하나에 콘텐츠를 순서대로 쌓는다. Sidebar/오프캔버스 메뉴가 필요해지면(다중 라우트로 확장될 때) 그때 도입을 검토한다.

### 터치 타겟 (44px)

```tsx
// ✅ 충분한 터치 타겟 — etf-list.tsx 페이지네이션 버튼 실제 패턴
<Button variant="outline" size="icon-lg" className="size-11" aria-label="다음 페이지">
    <ChevronRight className="size-5" />
</Button>

// ✅ 필터 칩도 h-11로 44px 확보 — etf-filters.tsx
const chipClass = 'h-11 rounded-full px-4 text-sm ...'
```

인터랙티브 요소(버튼, 토글, 링크)는 시각적 크기가 작아 보여도 터치 영역은 항상 최소 44px을 유지한다.

---

## 1. 컴포넌트 패턴

### 카드 목록 (Card/CardContent)

```tsx
// components/etf/etf-card.tsx
export function EtfCard({ etf }: { etf: EtfInfo }) {
    return (
        <Card className="gap-0 rounded-lg border py-0 shadow-none ring-0 transition-colors hover:bg-accent/50">
            <CardContent className="p-4">
                <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0 flex-1">
                        <p className="truncate font-semibold leading-tight">{etf.name ?? etf.abbrName ?? '-'}</p>
                        <p className="mt-0.5 text-sm text-muted-foreground">{etf.shortCode}</p>
                    </div>
                    {etf.totalFee !== null && <Badge variant="secondary">{etf.totalFee.toFixed(4)}%</Badge>}
                </div>
            </CardContent>
        </Card>
    )
}
```

- `min-w-0 flex-1` + `truncate`로 긴 종목명이 카드 레이아웃을 깨지 않게 한다.
- 값이 `null`일 수 있는 필드는 조건부 렌더링하거나(`etf.totalFee !== null && <Badge>`) fallback을 명시한다(`etf.name ?? etf.abbrName ?? '-'`) — 원본 데이터가 부분적으로만 채워질 수 있다는 전제(→ `eft-collector`가 마스터파일 기준 필드만 우선 채움)를 UI가 흡수한다.

### 필터 칩 (ToggleGroup)

```tsx
// components/etf/etf-filters.tsx
<ToggleGroup
    type="single"
    variant="outline"
    value={assetClass ?? 'all'}
    onValueChange={(v) => setParams({ assetClass: v && v !== 'all' ? v : null, page: null })}
    className="flex-wrap justify-start gap-1.5"
>
    <ToggleGroupItem value="all" className={chipClass}>전체</ToggleGroupItem>
    {filterOptions.assetClasses.map((cls) => (
        <ToggleGroupItem key={cls} value={cls} className={chipClass}>{cls}</ToggleGroupItem>
    ))}
</ToggleGroup>
```

- "전체" 옵션은 항상 명시적 항목(`value="all"`)으로 두고, 선택 시 `null`로 변환해 URL에서 파라미터를 제거한다(→ `react-query-guide` 6절).
- 필터 변경 시 반드시 `page: null`을 함께 넘겨 페이지를 리셋한다.
- 선택 상태 표현은 `aria-pressed`/`data-state` 속성 기반 클래스(`aria-pressed:bg-foreground data-[state=on]:bg-foreground`)로 하며, 색상만으로 구분하지 않는다(`ToggleGroupItem`은 텍스트 라벨을 함께 가지므로 접근성 요건을 만족한다 — → `design-system`).

### 빈 상태

```tsx
// components/etf/etf-list.tsx
{data.items.length === 0 ? (
    <Card className="gap-0 rounded-lg border py-0 shadow-none ring-0">
        <CardContent className="flex min-h-48 flex-col items-center justify-center p-16 text-center">
            <p className="text-base font-medium">검색 결과가 없습니다</p>
            <p className="mt-1 text-sm text-muted-foreground">검색어 또는 필터 조건을 변경해보세요</p>
        </CardContent>
    </Card>
) : ( /* 목록 그리드 */ )}
```

빈 상태는 "왜 비어있고 무엇을 해야 하는지"를 함께 안내한다 — 단순히 "결과 없음"만 보여주지 않는다.

---

## 2. 스켈레톤 컴포넌트 (피처 콜로케이션)

로딩 UI는 `components/{feature}/{feature}-list-skeleton.tsx`처럼 **기능 디렉토리에 콜로케이션**한다 — GamePot처럼 여러 대시보드 화면이 공유하는 `components/ui/skeletons.tsx` 같은 전역 위치를 이 프로젝트는 아직 쓰지 않는다(현재 도메인이 `etf` 하나뿐이기 때문). 두 번째 feature가 추가되어 스켈레톤 형태가 실제로 겹치기 시작하면 그때 공용 위치로 추출을 검토한다 — 미리 추상화하지 않는다.

```tsx
// components/etf/etf-list-skeleton.tsx
export function EtfListSkeleton() {
    return (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 12 }).map((_, i) => (
                <Card key={i} className="gap-0 rounded-lg border py-0 shadow-none ring-0">
                    <CardContent className="p-4">
                        <Skeleton className="h-4 w-3/4" />
                        <Skeleton className="h-3 w-1/4" />
                    </CardContent>
                </Card>
            ))}
        </div>
    )
}
```

스켈레톤은 실제 카드와 **동일한 그리드 클래스**(`grid-cols-1 sm:grid-cols-2 lg:grid-cols-3`)와 개수 감각(12개)을 맞춰 레이아웃 시프트(CLS)를 방지한다 — `EtfListSkeleton`이 `EtfCard`의 실제 grid와 다른 컬럼 수를 쓰면 데이터 도착 시 화면이 튄다. "불러오는 중..." 텍스트로 대체하지 않는다.

---

## 3. 리스트 Client Component (Suspense 소비)

```tsx
// components/etf/etf-list.tsx — 'use client'
export function EtfList() {
    const [{ page, ...filters }, setParams] = useQueryStates(etfSearchParams)
    const { data } = useEtfList({ page, ...filters })   // useSuspenseQuery — data는 항상 정의됨

    return ( /* 빈 상태 분기 또는 목록 렌더 — isLoading 분기 없음 */ )
}
```

`useSuspenseQuery` 기반이므로 컴포넌트 안에 `isLoading` 분기가 없다 — 로딩 UI는 부모의 `<Suspense fallback={<EtfListSkeleton />}>`(→ `nextjs-guide` 2절)가 전담한다. `useQuery`를 쓰는 예외적 컴포넌트만 `isLoading`/`error` 분기를 컴포넌트 내부에 둔다.
