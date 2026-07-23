'use client'
// ETF 구성종목 비중 상위 10종목을 파이차트로 보여주는 컴포넌트 (나머지는 '기타'로 합산)

import { Pie, PieChart } from 'recharts'
import { Card, CardContent } from '@/components/ui/card'
import {
    ChartContainer,
    ChartTooltip,
    ChartTooltipContent,
    ChartLegend,
    ChartLegendContent,
    type ChartConfig,
} from '@/components/ui/chart'
import { useEtfConstituents } from '@/domain/etf'

type Props = {
    shortCode: string
}

const TOP_N = 10

export function EtfConstituentChart({ shortCode }: Props) {
    const { data: constituents } = useEtfConstituents(shortCode)

    const withWeight = constituents.filter((c) => c.weightPercentage !== null)

    if (withWeight.length === 0) {
        return (
            <Card className="gap-0 rounded-lg border py-0 shadow-none ring-0">
                <CardContent className="p-4 text-sm text-muted-foreground">
                    구성종목 비중 정보를 아직 수집하지 못했습니다.
                </CardContent>
            </Card>
        )
    }

    const sorted = [...withWeight].sort((a, b) => (b.weightPercentage ?? 0) - (a.weightPercentage ?? 0))
    const top = sorted.slice(0, TOP_N)
    const restWeight = sorted.slice(TOP_N).reduce((sum, c) => sum + (c.weightPercentage ?? 0), 0)

    const data = top.map((c, i) => ({
        name: c.constituentName ?? c.constituentShortCode,
        weight: Number((c.weightPercentage ?? 0).toFixed(2)),
        fill: `hsl(${(i * 34) % 360} 62% 55%)`,
    }))
    if (restWeight > 0) {
        data.push({ name: '기타', weight: Number(restWeight.toFixed(2)), fill: 'hsl(0 0% 72%)' })
    }

    const chartConfig: ChartConfig = {}
    for (const d of data) {
        chartConfig[d.name] = { label: d.name }
    }

    return (
        <Card className="gap-0 rounded-lg border py-0 shadow-none ring-0">
            <CardContent className="p-4">
                <h2 className="text-sm font-semibold">구성종목 (상위 {TOP_N}종목)</h2>
                <p className="mt-0.5 text-xs text-muted-foreground">비중 상위 {TOP_N}종목 · 나머지는 기타로 합산</p>
                <ChartContainer config={chartConfig} className="mx-auto mt-3 aspect-square max-h-[320px]">
                    <PieChart>
                        <ChartTooltip content={<ChartTooltipContent nameKey="name" hideLabel />} />
                        <Pie data={data} dataKey="weight" nameKey="name" />
                        <ChartLegend content={<ChartLegendContent nameKey="name" />} className="flex-wrap gap-2" />
                    </PieChart>
                </ChartContainer>
            </CardContent>
        </Card>
    )
}
