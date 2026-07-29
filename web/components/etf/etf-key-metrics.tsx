'use client'
// ETF 비교 핵심 지표 4가지(총보수·순자산총액·추적오차율·NAV/괴리율)를 카드로 표시하는 컴포넌트

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
    subValue,
}: {
    label: string
    labelExtra?: ReactNode
    value: string
    valueColor?: string
    subValue?: string
}) {
    return (
        <Card className="gap-0 rounded-lg border py-0 shadow-none ring-0">
            <CardContent className="p-4">
                <p className="flex items-center gap-1 text-xs text-muted-foreground">
                    {label}
                    {labelExtra}
                </p>
                <p className={`mt-1 text-lg font-semibold ${valueColor ?? ''}`}>{value}</p>
                {subValue !== undefined && <p className="mt-0.5 text-xs text-muted-foreground">{subValue}</p>}
            </CardContent>
        </Card>
    )
}

function DisparityLabelExtra() {
    return (
        <Popover>
            <PopoverTrigger
                aria-label="NAV와 괴리율 설명 보기"
                className="inline-flex size-4 items-center justify-center"
            >
                <CircleHelp className="size-3.5" />
            </PopoverTrigger>
            <PopoverContent className="w-72 text-xs">
                <p className="font-medium text-foreground">NAV와 괴리율이란?</p>
                <p className="mt-1 leading-relaxed text-muted-foreground">
                    NAV(순자산가치)는 ETF가 보유한 자산을 상장좌수로 나눈 ETF 1주의 이론적 적정가치예요. 괴리율은
                    거래소에서 실제 거래되는 현재가(시장가격)가 이 NAV보다 얼마나 비싸거나 싼지를 (현재가 - NAV) ÷
                    NAV로 나타낸 값이고, 양수면 시장가격이 고평가, 음수면 저평가된 상태라는 뜻이에요. 유동성이
                    부족하거나 수급이 쏠리면 괴리율이 커질 수 있어요.
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
                label="NAV / 괴리율"
                labelExtra={<DisparityLabelExtra />}
                value={pct(quote?.disparityRate)}
                valueColor={signColor(quote?.disparityRate)}
                subValue={
                    quote?.nav !== null && quote?.nav !== undefined ? `NAV ${num(quote.nav)}원` : 'NAV -'
                }
            />
        </div>
    )
}
