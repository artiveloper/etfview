'use client'

import { useQueryStates } from 'nuqs'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { useEtfList } from '@/domain/etf'
import { etfSearchParams } from '@/domain/etf/params'
import { EtfCard } from './etf-card'

export function EtfList() {
    const [{ page, search, assetClass, market, leverage }, setParams] = useQueryStates(etfSearchParams)
    const { data } = useEtfList({ page, search, assetClass, market, leverage })

    const handlePrev = () => setParams({ page: page - 1 })
    const handleNext = () => setParams({ page: page + 1 })

    return (
        <div className="space-y-4">
            <p className="text-sm text-muted-foreground">
                총 <span className="font-medium text-foreground">{data.total.toLocaleString()}</span>개
            </p>

            {data.items.length === 0 ? (
                <Card className="gap-0 rounded-lg border py-0 shadow-none ring-0">
                    <CardContent className="flex min-h-48 flex-col items-center justify-center p-16 text-center">
                        <p className="text-base font-medium">검색 결과가 없습니다</p>
                        <p className="mt-1 text-sm text-muted-foreground">
                            검색어 또는 필터 조건을 변경해보세요
                        </p>
                    </CardContent>
                </Card>
            ) : (
                <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
                    {data.items.map((etf) => (
                        <EtfCard key={etf.shortCode} etf={etf} />
                    ))}
                </div>
            )}

            {data.totalPages > 1 && (
                <div className="flex items-center justify-center gap-4 pt-2">
                    <Button
                        variant="outline"
                        size="icon-lg"
                        onClick={handlePrev}
                        disabled={page <= 1}
                        aria-label="이전 페이지"
                        className="size-11"
                    >
                        <ChevronLeft className="size-5" />
                    </Button>

                    <span className="min-w-20 text-center text-sm">
                        <span className="font-medium">{page}</span>
                        <span className="text-muted-foreground"> / {data.totalPages}</span>
                    </span>

                    <Button
                        variant="outline"
                        size="icon-lg"
                        onClick={handleNext}
                        disabled={page >= data.totalPages}
                        aria-label="다음 페이지"
                        className="size-11"
                    >
                        <ChevronRight className="size-5" />
                    </Button>
                </div>
            )}
        </div>
    )
}
