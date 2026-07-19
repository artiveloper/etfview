'use client'

import { useQueryStates } from 'nuqs'
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group'
import { useEtfFilterOptions } from '@/domain/etf'
import { etfSearchParams, LEVERAGE_VALUES } from '@/domain/etf/params'
import type { LeverageType } from '@/domain/etf/params'

const LEVERAGE_LABELS: Record<LeverageType, string> = {
    normal: '일반',
    leveraged: '레버리지',
    inverse: '인버스',
}

const chipClass =
    'h-11 rounded-full px-4 text-sm aria-pressed:bg-foreground aria-pressed:text-background data-[state=on]:bg-foreground data-[state=on]:text-background'

export function EtfFilters() {
    const { data: filterOptions } = useEtfFilterOptions()
    const [{ assetClass, market, leverage }, setParams] = useQueryStates(etfSearchParams)

    return (
        <div className="space-y-4 rounded-lg border bg-card p-4">
            <div className="flex flex-col gap-2 sm:flex-row sm:flex-wrap sm:items-center sm:gap-x-3">
                <span className="text-sm font-medium text-muted-foreground sm:w-14">기초자산</span>
                <ToggleGroup
                    type="single"
                    variant="outline"
                    value={assetClass ?? 'all'}
                    onValueChange={(v) =>
                        setParams({ assetClass: v && v !== 'all' ? v : null, page: null })
                    }
                    className="flex-wrap justify-start gap-1.5"
                >
                    <ToggleGroupItem value="all" className={chipClass}>전체</ToggleGroupItem>
                    {filterOptions.assetClasses.map((cls) => (
                        <ToggleGroupItem key={cls} value={cls} className={chipClass}>
                            {cls}
                        </ToggleGroupItem>
                    ))}
                </ToggleGroup>
            </div>

            <div className="flex flex-col gap-2 sm:flex-row sm:flex-wrap sm:items-center sm:gap-x-3">
                <span className="text-sm font-medium text-muted-foreground sm:w-14">시장</span>
                <ToggleGroup
                    type="single"
                    variant="outline"
                    value={market ?? 'all'}
                    onValueChange={(v) =>
                        setParams({ market: v && v !== 'all' ? v : null, page: null })
                    }
                    className="flex-wrap justify-start gap-1.5"
                >
                    <ToggleGroupItem value="all" className={chipClass}>전체</ToggleGroupItem>
                    {filterOptions.markets.map((m) => (
                        <ToggleGroupItem key={m} value={m} className={chipClass}>
                            {m}
                        </ToggleGroupItem>
                    ))}
                </ToggleGroup>
            </div>

            <div className="flex flex-col gap-2 sm:flex-row sm:flex-wrap sm:items-center sm:gap-x-3">
                <span className="text-sm font-medium text-muted-foreground sm:w-14">유형</span>
                <ToggleGroup
                    type="single"
                    variant="outline"
                    value={leverage ?? 'all'}
                    onValueChange={(v) =>
                        setParams({ leverage: v && v !== 'all' ? (v as LeverageType) : null, page: null })
                    }
                    className="flex-wrap justify-start gap-1.5"
                >
                    <ToggleGroupItem value="all" className={chipClass}>전체</ToggleGroupItem>
                    {LEVERAGE_VALUES.map((v) => (
                        <ToggleGroupItem key={v} value={v} className={chipClass}>
                            {LEVERAGE_LABELS[v]}
                        </ToggleGroupItem>
                    ))}
                </ToggleGroup>
            </div>
        </div>
    )
}
