'use client'

import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { useEtfDetail } from '@/domain/etf'

type Props = {
    shortCode: string
}

function InfoRow({ label, value }: { label: string; value: string | null }) {
    if (!value) return null
    return (
        <div className="flex items-center justify-between border-b py-2 text-sm last:border-b-0">
            <span className="text-muted-foreground">{label}</span>
            <span className="font-medium">{value}</span>
        </div>
    )
}

export function EtfDetail({ shortCode }: Props) {
    const { data: etf } = useEtfDetail(shortCode)

    return (
        <Card className="gap-0 rounded-lg border py-0 shadow-none ring-0">
            <CardContent className="p-4">
                <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0 flex-1">
                        <p className="truncate text-lg font-semibold leading-tight">
                            {etf.name ?? etf.abbreviatedName ?? '-'}
                        </p>
                        <p className="mt-0.5 text-sm text-muted-foreground">
                            {etf.shortCode} · {etf.standardCode}
                        </p>
                    </div>
                    {etf.totalFee !== null && (
                        <Badge variant="secondary" className="shrink-0">
                            {etf.totalFee.toFixed(4)}%
                        </Badge>
                    )}
                </div>

                <div className="mt-4">
                    <InfoRow label="영문명" value={etf.englishName} />
                    <InfoRow label="운용사" value={etf.manager} />
                    <InfoRow label="기초지수" value={etf.baseIndexName} />
                    <InfoRow label="지수산출기관" value={etf.indexProvider} />
                    <InfoRow label="자산 분류" value={etf.baseAssetClass} />
                    <InfoRow label="시장 분류" value={etf.baseMarketClass} />
                    <InfoRow label="추적배수" value={etf.trackingMultiplier} />
                    <InfoRow label="복제방법" value={etf.replicationMethod} />
                    <InfoRow label="과세유형" value={etf.taxType} />
                    <InfoRow
                        label="상장좌수"
                        value={etf.listedShares !== null ? etf.listedShares.toLocaleString('ko-KR') : null}
                    />
                    <InfoRow
                        label="CU 수량"
                        value={
                            etf.creationUnitQuantity !== null
                                ? etf.creationUnitQuantity.toLocaleString('ko-KR')
                                : null
                        }
                    />
                    <InfoRow label="상장일" value={etf.listedDate} />
                </div>
            </CardContent>
        </Card>
    )
}
