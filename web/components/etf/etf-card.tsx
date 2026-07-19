import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import type { EtfInfo } from '@/domain/etf'

type Props = {
    etf: EtfInfo
}

export function EtfCard({ etf }: Props) {
    return (
        <Card className="gap-0 rounded-lg border py-0 shadow-none ring-0 transition-colors hover:bg-accent/50">
            <CardContent className="p-4">
                <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0 flex-1">
                        <p className="truncate font-semibold leading-tight">
                            {etf.name ?? etf.abbrName ?? '-'}
                        </p>
                        <p className="mt-0.5 text-sm text-muted-foreground">{etf.shortCode}</p>
                    </div>
                    {etf.totalFee !== null && (
                        <Badge variant="secondary" className="shrink-0">
                            {etf.totalFee.toFixed(4)}%
                        </Badge>
                    )}
                </div>

                <div className="mt-3 flex flex-wrap items-center gap-x-2 gap-y-1 text-xs text-muted-foreground">
                    {etf.manager && <span>{etf.manager}</span>}
                    {etf.baseAssetClass && (
                        <>
                            <span aria-hidden>·</span>
                            <span>{etf.baseAssetClass}</span>
                        </>
                    )}
                    {etf.baseMarketClass && (
                        <>
                            <span aria-hidden>·</span>
                            <span>{etf.baseMarketClass}</span>
                        </>
                    )}
                    {etf.trackingMultiplier && etf.trackingMultiplier !== '1배' && (
                        <>
                            <span aria-hidden>·</span>
                            <span>{etf.trackingMultiplier}</span>
                        </>
                    )}
                </div>

                {etf.listedDate && (
                    <p className="mt-2 text-xs text-muted-foreground">상장일 {etf.listedDate}</p>
                )}
            </CardContent>
        </Card>
    )
}
