'use client'

import { Card, CardContent } from '@/components/ui/card'
import { useEtfQuote } from '@/domain/etf'

type Props = {
    shortCode: string
}

function formatNumber(value: number | null) {
    if (value === null) return '-'
    return value.toLocaleString('ko-KR')
}

function QuoteRow({
    label,
    value,
    valueClassName = '',
}: {
    label: string
    value: string
    valueClassName?: string
}) {
    return (
        <div className="flex items-center justify-between border-b py-2 text-sm last:border-b-0">
            <span className="text-muted-foreground">{label}</span>
            <span className={`font-medium ${valueClassName}`}>{value}</span>
        </div>
    )
}

export function EtfQuotePanel({ shortCode }: Props) {
    const { data: quote } = useEtfQuote(shortCode)

    if (!quote) {
        return (
            <Card className="gap-0 rounded-lg border py-0 shadow-none ring-0">
                <CardContent className="p-4 text-sm text-muted-foreground">
                    시세 정보를 아직 수집하지 못했습니다.
                </CardContent>
            </Card>
        )
    }

    const isDown = quote.priceChange !== null && quote.priceChange < 0
    const isUp = quote.priceChange !== null && quote.priceChange > 0
    const changeColor = isDown ? 'text-blue-600' : isUp ? 'text-red-600' : 'text-muted-foreground'

    const isNavDown = quote.navChange !== null && quote.navChange < 0
    const isNavUp = quote.navChange !== null && quote.navChange > 0
    const navChangeColor = isNavDown ? 'text-blue-600' : isNavUp ? 'text-red-600' : 'text-muted-foreground'
    const navValue =
        quote.navChange !== null && quote.navChangeRate !== null
            ? `${formatNumber(quote.nav)} (${quote.navChange > 0 ? '+' : ''}${formatNumber(quote.navChange)}, ${quote.navChangeRate.toFixed(2)}%)`
            : formatNumber(quote.nav)

    return (
        <Card className="gap-0 rounded-lg border py-0 shadow-none ring-0">
            <CardContent className="p-4">
                <div className="flex items-baseline gap-2">
                    <span className="text-2xl font-bold">{formatNumber(quote.currentPrice)}</span>
                    {quote.priceChange !== null && quote.priceChangeRate !== null && (
                        <span className={`text-sm font-medium ${changeColor}`}>
                            {quote.priceChange > 0 ? '+' : ''}
                            {formatNumber(quote.priceChange)} ({quote.priceChangeRate.toFixed(2)}%)
                        </span>
                    )}
                </div>

                <div className="mt-4">
                    <QuoteRow label="거래량" value={formatNumber(quote.volume)} />
                    <QuoteRow
                        label="당일 시가/고가/저가"
                        value={`${formatNumber(quote.openPrice)} / ${formatNumber(quote.highPrice)} / ${formatNumber(quote.lowPrice)}`}
                    />
                    <QuoteRow
                        label="연중 최고가"
                        value={`${formatNumber(quote.yearHighPrice)}${quote.yearHighDate ? ` (${quote.yearHighDate})` : ''}`}
                    />
                    <QuoteRow
                        label="연중 최저가"
                        value={`${formatNumber(quote.yearLowPrice)}${quote.yearLowDate ? ` (${quote.yearLowDate})` : ''}`}
                    />
                    <QuoteRow label="NAV" value={navValue} valueClassName={navChangeColor} />
                    <QuoteRow
                        label="추적오차율"
                        value={quote.trackingErrorRate !== null ? `${quote.trackingErrorRate.toFixed(2)}%` : '-'}
                    />
                    <QuoteRow
                        label="괴리율"
                        value={quote.disparityRate !== null ? `${quote.disparityRate.toFixed(2)}%` : '-'}
                    />
                    <QuoteRow label="순자산총액" value={formatNumber(quote.netAssetTotal)} />
                    <QuoteRow label="구성종목수" value={formatNumber(quote.constituentCount)} />
                    <QuoteRow label="유통좌수" value={formatNumber(quote.circulatingShares)} />
                    <QuoteRow label="외국인 보유수량" value={formatNumber(quote.foreignHoldingQty)} />
                    <QuoteRow
                        label="외국인 보유비중"
                        value={quote.foreignHoldingRate !== null ? `${quote.foreignHoldingRate.toFixed(2)}%` : '-'}
                    />
                </div>
            </CardContent>
        </Card>
    )
}
