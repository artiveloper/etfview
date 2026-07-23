'use client'

// ETF 구성종목(비중 상위 30) 목록을 상세 페이지에 렌더하는 패널
import { Badge } from '@/components/ui/badge'
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

    const rows = constituents.map((item) => {
        const rate = item.priceChangeRate
        const rateColor =
            rate !== null && rate < 0
                ? 'text-blue-600'
                : rate !== null && rate > 0
                  ? 'text-red-600'
                  : 'text-muted-foreground'
        const priceText = `${formatNumber(item.currentPrice)} (${rate !== null ? `${rate > 0 ? '+' : ''}${rate.toFixed(2)}%` : '-'})`
        const weightText = item.weightPercentage !== null ? `${item.weightPercentage.toFixed(2)}%` : '-'
        return { item, rateColor, priceText, weightText }
    })

    return (
        <Card className="gap-0 rounded-lg border py-0 shadow-none ring-0">
            <CardContent className="p-4">
                <h2 className="text-sm font-semibold">구성종목 TOP30</h2>
                <p className="mt-0.5 text-xs text-muted-foreground">비중 상위 30개 종목 · 전체 보유내역이 아닙니다.</p>

                <div className="mt-3 divide-y sm:hidden">
                    {rows.map(({ item, rateColor, priceText, weightText }) => (
                        <div key={item.constituentShortCode} className="flex items-center justify-between py-2">
                            <div className="whitespace-nowrap">
                                <span className="font-medium">{item.constituentName ?? '-'}</span>{' '}
                                <Badge variant="outline">{item.constituentShortCode}</Badge>
                            </div>
                            <div className="text-right">
                                <div className="tabular-nums">{weightText}</div>
                                <div className={`mt-0.5 text-xs tabular-nums ${rateColor}`}>{priceText}</div>
                            </div>
                        </div>
                    ))}
                </div>

                <div className="mt-3 hidden overflow-x-auto sm:block">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b text-xs text-muted-foreground">
                                <th className="py-2 pr-3 text-left font-medium">종목명</th>
                                <th className="px-3 py-2 text-right font-medium">현재가</th>
                                <th className="py-2 pl-3 text-right font-medium">비중</th>
                            </tr>
                        </thead>
                        <tbody>
                            {rows.map(({ item, rateColor, priceText, weightText }) => (
                                <tr key={item.constituentShortCode} className="border-b last:border-b-0">
                                    <td className="py-2 pr-3 whitespace-nowrap">
                                        <span className="font-medium">{item.constituentName ?? '-'}</span>{' '}
                                        <Badge variant="outline">{item.constituentShortCode}</Badge>
                                    </td>
                                    <td className={`px-3 py-2 text-right tabular-nums ${rateColor}`}>{priceText}</td>
                                    <td className="py-2 pl-3 text-right tabular-nums">{weightText}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </CardContent>
        </Card>
    )
}
