'use client'

// ETF 구성종목(비중 상위 30) 목록을 상세 페이지에 렌더하는 패널
import { Card, CardContent } from '@/components/ui/card'
import { useEtfConstituents } from '@/domain/etf'

type Props = {
    shortCode: string
}

function formatNumber(value: number | null) {
    if (value === null) return '-'
    return value.toLocaleString('ko-KR')
}

export function EtfConstituentPanel({ shortCode }: Props) {
    const { data: constituents } = useEtfConstituents(shortCode)

    if (constituents.length === 0) {
        return (
            <Card className="gap-0 rounded-lg border py-0 shadow-none ring-0">
                <CardContent className="p-4 text-sm text-muted-foreground">
                    구성종목 정보를 아직 수집하지 못했습니다.
                </CardContent>
            </Card>
        )
    }

    return (
        <Card className="gap-0 rounded-lg border py-0 shadow-none ring-0">
            <CardContent className="p-4">
                <h2 className="text-sm font-semibold">구성종목</h2>
                <p className="mt-0.5 text-xs text-muted-foreground">
                    KIS 제공 비중 상위 {constituents.length}종목 · 전체 보유내역이 아닙니다.
                </p>

                <div className="mt-3">
                    {constituents.map((item, index) => (
                        <div
                            key={item.constituentShortCode}
                            className="flex items-center justify-between gap-3 border-b py-2 text-sm last:border-b-0"
                        >
                            <div className="flex min-w-0 items-center gap-2">
                                <span className="w-5 shrink-0 text-right text-xs text-muted-foreground">
                                    {index + 1}
                                </span>
                                <div className="min-w-0">
                                    <span className="block truncate font-medium">
                                        {item.constituentName ?? item.constituentShortCode}
                                    </span>
                                    <span className="text-xs text-muted-foreground">{item.constituentShortCode}</span>
                                </div>
                            </div>
                            <div className="shrink-0 text-right">
                                <span className="block font-medium">
                                    {item.weightPercentage !== null ? `${item.weightPercentage.toFixed(2)}%` : '-'}
                                </span>
                                <span className="text-xs text-muted-foreground">
                                    {formatNumber(item.marketValueAmount)}
                                </span>
                            </div>
                        </div>
                    ))}
                </div>
            </CardContent>
        </Card>
    )
}
