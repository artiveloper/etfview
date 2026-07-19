import { Suspense } from 'react'
import { HydrationBoundary } from '@tanstack/react-query'
import { runPrefetch } from '@/lib/react-query/prefetch'
import { etfPrefetch } from '@/domain/etf/server'
import { EtfList } from '@/components/etf/etf-list'
import { EtfSearch } from '@/components/etf/etf-search'
import { EtfFilters } from '@/components/etf/etf-filters'
import { EtfListSkeleton, EtfFiltersSkeleton } from '@/components/etf/etf-list-skeleton'

type SearchParams = {
    page?: string
    search?: string
    assetClass?: string
    market?: string
    leverage?: string
}

type Props = {
    searchParams: Promise<SearchParams>
}

function parseLeverage(value: string | undefined) {
    if (value === 'normal' || value === 'leveraged' || value === 'inverse') return value
    return null
}

export default async function EtfPage({ searchParams }: Props) {
    const params = await searchParams
    const page = params.page ? Math.max(1, Number(params.page)) : 1
    const search = params.search ?? ''
    const assetClass = params.assetClass ?? null
    const market = params.market ?? null
    const leverage = parseLeverage(params.leverage)

    const state = await runPrefetch(
        etfPrefetch.filterOptions(),
        etfPrefetch.list({ page, search, assetClass, market, leverage }),
    )

    return (
        <HydrationBoundary state={state}>
            <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
                <div className="mb-6">
                    <h1 className="text-xl font-bold tracking-tight sm:text-2xl">ETF 목록</h1>
                    <p className="mt-1 text-sm text-muted-foreground">국내 상장 ETF를 검색하고 조회합니다</p>
                </div>

                <div className="mb-3">
                    <EtfSearch />
                </div>

                <div className="mb-4">
                    <Suspense fallback={<EtfFiltersSkeleton />}>
                        <EtfFilters />
                    </Suspense>
                </div>

                <Suspense fallback={<EtfListSkeleton />}>
                    <EtfList />
                </Suspense>
            </main>
        </HydrationBoundary>
    )
}
