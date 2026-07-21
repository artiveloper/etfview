'use client'

import { useEffect, useRef } from 'react'
import { useQueryStates } from 'nuqs'
import { Card, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { useEtfList } from '@/domain/etf'
import { etfSearchParams } from '@/domain/etf/params'
import { EtfCard } from './etf-card'

function useLoadMoreOnVisible(onVisible: () => void, enabled: boolean) {
    const ref = useRef<HTMLDivElement>(null)

    useEffect(() => {
        const el = ref.current
        if (!enabled || !el) return

        const observer = new IntersectionObserver(
            (entries) => {
                if (entries[0]?.isIntersecting) onVisible()
            },
            { rootMargin: '400px' },
        )
        observer.observe(el)
        return () => observer.disconnect()
    }, [onVisible, enabled])

    return ref
}

export function EtfList() {
    const [{ search, assetClass, market, leverage, manager, replicationMethod, taxType }] =
        useQueryStates(etfSearchParams)
    const { data, fetchNextPage, hasNextPage, isFetchingNextPage } = useEtfList({
        search,
        assetClass,
        market,
        leverage,
        manager,
        replicationMethod,
        taxType,
    })

    const items = data.pages.flatMap((p) => p.items)
    const total = data.pages[0].total

    const sentinelRef = useLoadMoreOnVisible(() => {
        if (!isFetchingNextPage) fetchNextPage()
    }, hasNextPage)

    return (
        <div className="space-y-4">
            <p className="text-sm text-muted-foreground">
                총 <span className="font-medium text-foreground">{total.toLocaleString()}</span>개
            </p>

            {items.length === 0 ? (
                <Card className="gap-0 rounded-lg border py-0 shadow-none ring-0">
                    <CardContent className="flex min-h-48 flex-col items-center justify-center p-16 text-center">
                        <p className="text-base font-medium">검색 결과가 없습니다</p>
                        <p className="mt-1 text-sm text-muted-foreground">
                            검색어 또는 필터 조건을 변경해보세요
                        </p>
                    </CardContent>
                </Card>
            ) : (
                <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
                    {items.map((etf) => (
                        <EtfCard key={etf.shortCode} etf={etf} />
                    ))}
                </div>
            )}

            {hasNextPage && (
                <div ref={sentinelRef} className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
                    {isFetchingNextPage &&
                        Array.from({ length: 3 }).map((_, i) => (
                            <Card key={i} className="gap-0 rounded-lg border py-0 shadow-none ring-0">
                                <CardContent className="p-4">
                                    <Skeleton className="h-10 w-3/4" />
                                    <Skeleton className="mt-2 h-5 w-28" />
                                </CardContent>
                            </Card>
                        ))}
                </div>
            )}
        </div>
    )
}
