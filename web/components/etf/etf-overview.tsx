'use client'
// ETF 개요 — 운용사·총보수·기초지수 등 핵심 정보를 한 카드에 표시하는 컴포넌트

import { Card, CardContent } from '@/components/ui/card'
import { useEtfDetail, useEtfQuote } from '@/domain/etf'

type Props = {
    shortCode: string
}

function InfoRow({ label, value }: { label: string; value: string }) {
    return (
        <div className="flex items-center justify-between border-b py-2 text-sm last:border-b-0">
            <span className="text-muted-foreground">{label}</span>
            <span className="text-right font-medium">{value}</span>
        </div>
    )
}

function num(value: number | null | undefined) {
    return value !== null && value !== undefined ? value.toLocaleString('ko-KR') : '-'
}

function pct(value: number | null | undefined) {
    return value !== null && value !== undefined ? `${value.toFixed(2)}%` : '-'
}

export function EtfOverview({ shortCode }: Props) {
    const { data: etf } = useEtfDetail(shortCode)
    const { data: quote } = useEtfQuote(shortCode)

    return (
        <Card className="gap-0 rounded-lg border py-0 shadow-none ring-0">
            <CardContent className="p-4">
                <h2 className="mb-2 text-sm font-semibold">개요</h2>
                <InfoRow label="운용사" value={etf.manager ?? '-'} />
                <InfoRow label="총보수" value={etf.totalFee !== null ? `${etf.totalFee.toFixed(4)}%` : '-'} />
                <InfoRow label="기초지수" value={etf.baseIndexName ?? '-'} />
                <InfoRow label="지수산출기관" value={etf.indexProvider ?? '-'} />
                <InfoRow label="NAV" value={num(quote?.nav)} />
                <InfoRow label="순자산" value={num(quote?.netAssetTotal)} />
                <InfoRow label="상장일" value={etf.listedDate ?? '-'} />
                <InfoRow label="구성종목수" value={num(quote?.constituentCount)} />
                <InfoRow label="괴리율" value={pct(quote?.disparityRate)} />
                <InfoRow label="추적오차율" value={pct(quote?.trackingErrorRate)} />
                <InfoRow label="외국인 보유비중" value={pct(quote?.foreignHoldingRate)} />
            </CardContent>
        </Card>
    )
}
