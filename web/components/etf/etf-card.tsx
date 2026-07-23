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

export function EtfCard({ etf }: Props) {
    const { quote } = etf
    const isDown = quote?.priceChange !== null && quote?.priceChange !== undefined && quote.priceChange < 0
    const isUp = quote?.priceChange !== null && quote?.priceChange !== undefined && quote.priceChange > 0
    const changeColor = isDown ? 'text-blue-600' : isUp ? 'text-red-600' : 'text-muted-foreground'

    return (
        <Link href={`/etf/${etf.shortCode}`}>
            <Card className="gap-0 rounded-lg border py-0 shadow-none ring-0 transition-colors hover:bg-accent/50">
                <CardContent className="p-4">
                    <div className="flex min-h-10 items-start justify-between gap-3">
                        <p className="font-semibold leading-tight">{etf.abbreviatedName ?? etf.name ?? '-'}</p>
                        {etf.totalFee !== null && (
                            <Badge variant="secondary" className="shrink-0">
                                총보수 {etf.totalFee.toFixed(4)}%
                            </Badge>
                        )}
                    </div>

                    {quote && quote.currentPrice !== null && (
                        <div className="mt-2 flex items-baseline gap-1.5">
                            <span className="text-sm font-bold">{formatNumber(quote.currentPrice)}원</span>
                            {quote.priceChangeRate !== null && (
                                <span className={`text-sm font-medium ${changeColor}`}>
                                    {quote.priceChangeRate > 0 ? '+' : ''}
                                    {quote.priceChangeRate.toFixed(2)}%
                                </span>
                            )}
                        </div>
                    )}

                    <div className="mt-3 flex flex-wrap items-center gap-x-2 gap-y-1 text-xs text-muted-foreground">
                        {etf.manager && <span>{etf.manager}</span>}
                        {etf.baseAssetClass && (
                            <>
                                <span aria-hidden>·</span>
                                <span>{etf.baseAssetClass}</span>
                            </>
                        )}
                        {etf.baseMarketClass && (
                            <>
                                <span aria-hidden>·</span>
                                <span>{etf.baseMarketClass}</span>
                            </>
                        )}
                        {etf.trackingMultiplier && etf.trackingMultiplier !== '1배' && (
                            <>
                                <span aria-hidden>·</span>
                                <span>{etf.trackingMultiplier}</span>
                            </>
                        )}
                    </div>

                    {(quote?.netAssetTotal || etf.listedDate) && (
                        <p className="mt-2 text-xs text-muted-foreground">
                            {quote?.netAssetTotal != null && <>순자산 {formatNumber(quote.netAssetTotal)}억원</>}
                            {quote?.netAssetTotal != null && etf.listedDate && <> · </>}
                            {etf.listedDate && <>상장일 {etf.listedDate}</>}
                        </p>
                    )}
                </CardContent>
            </Card>
        </Link>
    )
}
