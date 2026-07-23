import { Suspense } from 'react'
import { HydrationBoundary } from '@tanstack/react-query'
import { runPrefetch } from '@/lib/react-query/prefetch'
import { etfPrefetch } from '@/domain/etf/server'
import { EtfDetailHeader } from '@/components/etf/etf-detail-header'
import { EtfOverview } from '@/components/etf/etf-overview'
import { EtfConstituentChart } from '@/components/etf/etf-constituent-chart'
import { EtfConstituentPanel } from '@/components/etf/etf-constituent-panel'
import {
    EtfDetailHeaderSkeleton,
    EtfOverviewSkeleton,
    EtfConstituentChartSkeleton,
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
            <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
                <div className="mb-6">
                    <Suspense fallback={<EtfDetailHeaderSkeleton />}>
                        <EtfDetailHeader shortCode={shortCode} />
                    </Suspense>
                </div>

                <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
                    <Suspense fallback={<EtfOverviewSkeleton />}>
                        <EtfOverview shortCode={shortCode} />
                    </Suspense>
                    <Suspense fallback={<EtfConstituentChartSkeleton />}>
                        <EtfConstituentChart shortCode={shortCode} />
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
