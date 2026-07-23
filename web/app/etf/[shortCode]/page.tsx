import { Suspense } from 'react'
import { HydrationBoundary } from '@tanstack/react-query'
import { runPrefetch } from '@/lib/react-query/prefetch'
import { etfPrefetch } from '@/domain/etf/server'
import { EtfDetail } from '@/components/etf/etf-detail'
import { EtfQuotePanel } from '@/components/etf/etf-quote-panel'
import { EtfConstituentPanel } from '@/components/etf/etf-constituent-panel'
import {
    EtfDetailSkeleton,
    EtfQuotePanelSkeleton,
    EtfConstituentPanelSkeleton,
} from '@/components/etf/etf-detail-skeleton'

type Props = {
    params: Promise<{ shortCode: string }>
}

export default async function EtfDetailPage({ params }: Props) {
    const { shortCode } = await params

    const state = await runPrefetch(
        etfPrefetch.detail(shortCode),
        etfPrefetch.quote(shortCode),
        etfPrefetch.constituents(shortCode),
    )

    return (
        <HydrationBoundary state={state}>
            <main className="mx-auto max-w-3xl px-4 py-6 sm:px-6 lg:px-8">
                <div className="mb-6">
                    <h1 className="text-xl font-bold tracking-tight sm:text-2xl">ETF 상세</h1>
                    <p className="mt-1 text-sm text-muted-foreground">{shortCode}</p>
                </div>

                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <Suspense fallback={<EtfDetailSkeleton />}>
                        <EtfDetail shortCode={shortCode} />
                    </Suspense>
                    <Suspense fallback={<EtfQuotePanelSkeleton />}>
                        <EtfQuotePanel shortCode={shortCode} />
                    </Suspense>
                </div>

                <div className="mt-4">
                    <Suspense fallback={<EtfConstituentPanelSkeleton />}>
                        <EtfConstituentPanel shortCode={shortCode} />
                    </Suspense>
                </div>
            </main>
        </HydrationBoundary>
    )
}
