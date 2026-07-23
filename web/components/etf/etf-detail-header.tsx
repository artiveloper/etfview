'use client'
// ETF 상세 헤더 — 종목명(종목코드)과 현재가·등락금액·등락률을 표시하는 컴포넌트

import { useEtfDetail, useEtfQuote } from '@/domain/etf'

type Props = {
    shortCode: string
}

function formatNumber(value: number | null) {
    if (value === null) return '-'
    return value.toLocaleString('ko-KR')
}

export function EtfDetailHeader({ shortCode }: Props) {
    const { data: etf } = useEtfDetail(shortCode)
    const { data: quote } = useEtfQuote(shortCode)

    const name = etf.abbreviatedName ?? etf.name ?? '-'

    const isDown = quote?.priceChange != null && quote.priceChange < 0
    const isUp = quote?.priceChange != null && quote.priceChange > 0
    const changeColor = isDown ? 'text-blue-600' : isUp ? 'text-red-600' : 'text-muted-foreground'

    return (
        <div>
            <h1 className="text-xl font-bold tracking-tight sm:text-2xl">
                {name}{' '}
                <span className="text-base font-normal text-muted-foreground sm:text-lg">
                    ({etf.shortCode})
                </span>
            </h1>
            {quote && (
                <div className="mt-1 flex items-baseline gap-2">
                    <span className="text-2xl font-bold sm:text-3xl">{formatNumber(quote.currentPrice)}</span>
                    {quote.priceChange !== null && quote.priceChangeRate !== null && (
                        <span className={`text-sm font-medium ${changeColor}`}>
                            {quote.priceChange > 0 ? '+' : ''}
                            {formatNumber(quote.priceChange)} ({quote.priceChangeRate.toFixed(2)}%)
                        </span>
                    )}
                </div>
            )}
        </div>
    )
}
