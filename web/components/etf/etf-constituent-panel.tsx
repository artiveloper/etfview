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

                <div className="mt-3 overflow-x-auto">
                    <table className="w-full min-w-[560px] text-sm">
                        <thead>
                            <tr className="border-b text-xs text-muted-foreground">
                                <th className="py-2 pr-3 text-left font-medium">종목명</th>
                                <th className="px-3 py-2 text-right font-medium">현재가</th>
                                <th className="px-3 py-2 text-right font-medium">등락률</th>
                                <th className="px-3 py-2 text-right font-medium">비중</th>
                                <th className="px-3 py-2 text-right font-medium">평가금액</th>
                                <th className="py-2 pl-3 text-right font-medium">시가총액</th>
                            </tr>
                        </thead>
                        <tbody>
                            {constituents.map((item) => {
                                const rate = item.priceChangeRate
                                const rateColor =
                                    rate !== null && rate < 0
                                        ? 'text-blue-600'
                                        : rate !== null && rate > 0
                                          ? 'text-red-600'
                                          : 'text-muted-foreground'
                                return (
                                    <tr key={item.constituentShortCode} className="border-b last:border-b-0">
                                        <td className="py-2 pr-3">
                                            <span className="block font-medium">
                                                {item.constituentName ?? item.constituentShortCode}
                                            </span>
                                            <span className="text-xs text-muted-foreground">
                                                {item.constituentShortCode}
                                            </span>
                                        </td>
                                        <td className="px-3 py-2 text-right tabular-nums">
                                            {formatNumber(item.currentPrice)}
                                        </td>
                                        <td className={`px-3 py-2 text-right tabular-nums ${rateColor}`}>
                                            {rate !== null ? `${rate > 0 ? '+' : ''}${rate.toFixed(2)}%` : '-'}
                                        </td>
                                        <td className="px-3 py-2 text-right tabular-nums">
                                            {item.weightPercentage !== null
                                                ? `${item.weightPercentage.toFixed(2)}%`
                                                : '-'}
                                        </td>
                                        <td className="px-3 py-2 text-right tabular-nums">
                                            {formatNumber(item.marketValueAmount)}
                                        </td>
                                        <td className="py-2 pl-3 text-right tabular-nums">
                                            {formatNumber(item.marketCap)}
                                        </td>
                                    </tr>
                                )
                            })}
                        </tbody>
                    </table>
                </div>
            </CardContent>
        </Card>
    )
}
