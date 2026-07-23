'use client'
// ETF 비교 핵심 지표 4가지(총보수·순자산총액·추적오차율·괴리율)를 카드로 표시하는 컴포넌트

import { CircleHelp } from 'lucide-react'
import type { ReactNode } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { useEtfDetail, useEtfQuote } from '@/domain/etf'

type Props = {
    shortCode: string
}

function MetricCard({
    label,
    labelExtra,
    value,
    valueColor,
}: {
    label: string
    labelExtra?: ReactNode
    value: string
    valueColor?: string
}) {
    return (
        <Card className="gap-0 rounded-lg border py-0 shadow-none ring-0">
            <CardContent className="p-4">
                <p className="flex items-center gap-1 text-xs text-muted-foreground">
                    {label}
                    {labelExtra}
                </p>
                <p className={`mt-1 text-lg font-semibold ${valueColor ?? ''}`}>{value}</p>
            </CardContent>
        </Card>
    )
}

function DisparityLabelExtra() {
    return (
        <Popover>
            <PopoverTrigger aria-label="괴리율 설명 보기" className="inline-flex size-4 items-center justify-center">
                <CircleHelp className="size-3.5" />
            </PopoverTrigger>
            <PopoverContent className="w-72 text-xs">
                <p className="font-medium text-foreground">괴리율이란?</p>
                <p className="mt-1 leading-relaxed text-muted-foreground">
                    거래소에서 실제 거래되는 현재가(시장가격)가 ETF의 이론적 적정가치인 NAV보다 얼마나 비싸거나 싼지
                    나타내는 지표예요. (현재가 - NAV) ÷ NAV로 계산하며, 양수면 시장가격이 NAV보다 비싸게(고평가)
                    거래되고 있다는 뜻이고 음수면 반대예요. 유동성이 부족하거나 수급이 쏠리면 괴리율이 커질 수 있어요.
                </p>
            </PopoverContent>
        </Popover>
    )
}

function num(value: number | null | undefined) {
    return value !== null && value !== undefined ? value.toLocaleString('ko-KR') : '-'
}

function pct(value: number | null | undefined) {
    return value !== null && value !== undefined ? `${value.toFixed(2)}%` : '-'
}

function signColor(value: number | null | undefined) {
    if (value === null || value === undefined || value === 0) return undefined
    return value > 0 ? 'text-red-600' : 'text-blue-600'
}

export function EtfKeyMetrics({ shortCode }: Props) {
    const { data: etf } = useEtfDetail(shortCode)
    const { data: quote } = useEtfQuote(shortCode)

    return (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            <MetricCard label="총보수" value={etf.totalFee !== null ? `${etf.totalFee.toFixed(4)}%` : '-'} />
            <MetricCard
                label="순자산총액"
                value={
                    quote?.netAssetTotal !== null && quote?.netAssetTotal !== undefined
                        ? `${num(quote.netAssetTotal)}억원`
                        : '-'
                }
            />
            <MetricCard label="추적오차율" value={pct(quote?.trackingErrorRate)} />
            <MetricCard
                label="괴리율"
                labelExtra={<DisparityLabelExtra />}
                value={pct(quote?.disparityRate)}
                valueColor={signColor(quote?.disparityRate)}
            />
        </div>
    )
}
