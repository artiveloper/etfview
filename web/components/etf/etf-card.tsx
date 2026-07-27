import Link from 'next/link'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import type { EtfListItem } from '@/domain/etf'

type Props = {
    etf: EtfListItem
}

function formatNumber(value: number | null) {
    if (value === null) return '-'
    return value.toLocaleString('ko-KR')
}

// 순자산총액은 억원 단위로 저장됨 — 1조(=10,000억) 이상은 조 단위로 말아올린다.
function formatAssetTotal(value: number) {
    if (value >= 10000) {
        return `${(value / 10000).toLocaleString('ko-KR', { maximumFractionDigits: 1 })}조원`
    }
    return `${value.toLocaleString('ko-KR')}억원`
}

export function EtfCard({ etf }: Props) {
    const { quote } = etf
    const isDown = quote?.priceChange !== null && quote?.priceChange !== undefined && quote.priceChange < 0
    const isUp = quote?.priceChange !== null && quote?.priceChange !== undefined && quote.priceChange > 0
    const changeColor = isDown ? 'text-blue-600' : isUp ? 'text-red-600' : 'text-muted-foreground'

    const metrics = [
        etf.totalFee !== null ? `총보수 ${etf.totalFee.toFixed(4)}%` : null,
        quote?.netAssetTotal != null ? `순자산 ${formatAssetTotal(quote.netAssetTotal)}` : null,
    ].filter((v): v is string => Boolean(v))

    const categories = [
        etf.baseAssetClass,
        etf.trackingMultiplier && etf.trackingMultiplier !== '1배' ? etf.trackingMultiplier : null,
    ].filter((v): v is string => Boolean(v))

    return (
        <Link href={`/etf/${etf.shortCode}`}>
            <Card className="gap-0 rounded-lg border py-0 shadow-none ring-0 transition-colors hover:bg-accent/50">
                <CardContent className="p-4">
                    <div className="flex items-start justify-between gap-3">
                        <div className="min-w-0">
                            <p className="font-semibold leading-tight break-keep">
                                {etf.abbreviatedName ?? etf.name ?? '-'}
                            </p>
                            <p className="mt-0.5 truncate text-xs text-muted-foreground">
                                {etf.shortCode}
                                {etf.manager && ` · ${etf.manager}`}
                            </p>
                        </div>
                        {quote && quote.currentPrice !== null && (
                            <div className="flex shrink-0 items-baseline gap-1.5">
                                <span className="text-sm font-bold">
                                    {formatNumber(quote.currentPrice)}원
                                </span>
                                {quote.priceChangeRate !== null && (
                                    <span className={`text-sm font-medium ${changeColor}`}>
                                        {quote.priceChangeRate > 0 ? '+' : ''}
                                        {quote.priceChangeRate.toFixed(2)}%
                                    </span>
                                )}
                            </div>
                        )}
                    </div>

                    {metrics.length > 0 && (
                        <p className="mt-4 text-xs text-muted-foreground">{metrics.join(' · ')}</p>
                    )}

                    {categories.length > 0 && (
                        <div className="mt-2 flex flex-wrap items-center gap-1.5">
                            {categories.map((tag, i) => (
                                <Badge key={i} variant="secondary" className="font-normal">
                                    {tag}
                                </Badge>
                            ))}
                        </div>
                    )}

                </CardContent>
            </Card>
        </Link>
    )
}
