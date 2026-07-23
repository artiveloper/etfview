'use client'
// ETF 개요 — 운용사·총보수·기초지수 등 핵심 정보를 한 카드에 표시하는 컴포넌트

import { CircleHelp } from 'lucide-react'
import type { ReactNode } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { useEtfDetail, useEtfQuote } from '@/domain/etf'

type Props = {
    shortCode: string
}

function InfoRow({ label, value, labelExtra }: { label: string; value: string; labelExtra?: ReactNode }) {
    return (
        <div className="flex items-center justify-between border-b py-2 text-sm last:border-b-0">
            <span className="flex items-center gap-1 text-muted-foreground">
                {label}
                {labelExtra}
            </span>
            <span className="text-right font-medium">{value}</span>
        </div>
    )
}

function NavLabelExtra() {
    return (
        <Popover>
            <PopoverTrigger aria-label="NAV 설명 보기" className="inline-flex size-4 items-center justify-center">
                <CircleHelp className="size-3.5" />
            </PopoverTrigger>
            <PopoverContent className="w-72 text-xs">
                <p className="font-medium text-foreground">NAV(순자산가치)란?</p>
                <p className="mt-1 leading-relaxed text-muted-foreground">
                    ETF가 실제로 보유한 자산의 가치를 좌수로 나눈, ETF 1주의 이론적 적정가치예요. 보유 종목의
                    시가총액에서 운용보수 등 부대비용을 뺀 순자산총액을 상장좌수로 나눠서 계산해요. 거래소에서
                    실시간으로 매겨지는 현재가(시장가격)와 달리 NAV는 실제 자산가치를 반영하므로, 둘 사이의
                    차이(괴리율)가 크면 시장가격이 실제 가치보다 고평가 또는 저평가돼 있다는 뜻이에요.
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

export function EtfOverview({ shortCode }: Props) {
    const { data: etf } = useEtfDetail(shortCode)
    const { data: quote } = useEtfQuote(shortCode)

    return (
        <Card className="gap-0 rounded-lg border py-0 shadow-none ring-0">
            <CardContent className="p-4">
                <h2 className="mb-2 text-sm font-semibold">개요</h2>
                <InfoRow label="운용사" value={etf.manager ?? '-'} />
                <InfoRow label="기초지수" value={etf.baseIndexName ?? '-'} />
                <InfoRow label="지수산출기관" value={etf.indexProvider ?? '-'} />
                <InfoRow
                    label="NAV"
                    value={quote?.nav !== null && quote?.nav !== undefined ? `${num(quote.nav)}원` : '-'}
                    labelExtra={<NavLabelExtra />}
                />
                <InfoRow
                    label="1년 최고/최저"
                    value={
                        quote?.yearHighPrice !== null && quote?.yearHighPrice !== undefined
                            ? `${num(quote.yearHighPrice)}원 / ${num(quote?.yearLowPrice)}원`
                            : '-'
                    }
                />
                <InfoRow label="구성종목수" value={num(quote?.constituentCount)} />
                <InfoRow label="외국인 보유비중" value={pct(quote?.foreignHoldingRate)} />
                <InfoRow label="상장일" value={etf.listedDate ?? '-'} />
            </CardContent>
        </Card>
    )
}
