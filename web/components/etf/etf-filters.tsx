'use client'

import { useQueryStates } from 'nuqs'
import { X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
    Select,
    SelectGroup,
    SelectLabel,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select'
import { useEtfFilterOptions } from '@/domain/etf'
import { etfSearchParams, LEVERAGE_VALUES } from '@/domain/etf/params'
import type { LeverageType } from '@/domain/etf/params'

const LEVERAGE_LABELS: Record<LeverageType, string> = {
    normal: '일반',
    leveraged: '레버리지',
    inverse: '인버스',
}

function FilterRow({
    label,
    value,
    onChange,
    options,
}: {
    label: string
    value: string | null
    onChange: (value: string | null) => void
    options: { value: string; label: string }[]
}) {
    const items = [{ value: null, label }, ...options]

    return (

    <div className="flex shrink-0 items-center gap-0.5">
      <Select items={items} value={value} onValueChange={onChange}>
        <SelectTrigger className="shrink-0">
          <SelectValue />
        </SelectTrigger>
        <SelectContent className="w-max min-w-(--anchor-width) max-w-72">
          <SelectGroup>
            <SelectLabel>{label}</SelectLabel>
            {items.map((item) => (
              <SelectItem key={item.value ?? 'all'} value={item.value}>
                  {item.label}
              </SelectItem>
          ))}
          </SelectGroup>
        </SelectContent>
      </Select>
      {value !== null && (
        <Button
          type="button"
          variant="ghost"
          size="icon-xs"
          aria-label={`${label} 필터 해제`}
          onClick={() => onChange(null)}
        >
          <X />
        </Button>
      )}
    </div>
    )
}

export function EtfFilters() {
    const { data: filterOptions } = useEtfFilterOptions()
    const [{ assetClass, market, leverage, manager, replicationMethod, taxType }, setParams] =
        useQueryStates(etfSearchParams)

    const hasActiveFilter =
        assetClass !== null ||
        market !== null ||
        leverage !== null ||
        manager !== null ||
        replicationMethod !== null ||
        taxType !== null

    return (
        <div className="flex items-center gap-2 overflow-x-auto">
            <FilterRow
                label="기초자산"
                value={assetClass}
                onChange={(v) => setParams({ assetClass: v })}
                options={filterOptions.assetClasses.map((cls) => ({ value: cls, label: cls }))}
            />
            <FilterRow
                label="시장"
                value={market}
                onChange={(v) => setParams({ market: v })}
                options={filterOptions.markets.map((m) => ({ value: m, label: m }))}
            />
            <FilterRow
                label="유형"
                value={leverage}
                onChange={(v) => setParams({ leverage: v as LeverageType | null })}
                options={LEVERAGE_VALUES.map((v) => ({ value: v, label: LEVERAGE_LABELS[v] }))}
            />
            <FilterRow
                label="운용사"
                value={manager}
                onChange={(v) => setParams({ manager: v })}
                options={filterOptions.managers.map((m) => ({ value: m, label: m }))}
            />
            <FilterRow
                label="복제방법"
                value={replicationMethod}
                onChange={(v) => setParams({ replicationMethod: v })}
                options={filterOptions.replicationMethods.map((m) => ({ value: m, label: m }))}
            />
            <FilterRow
                label="과세유형"
                value={taxType}
                onChange={(v) => setParams({ taxType: v })}
                options={filterOptions.taxTypes.map((t) => ({ value: t, label: t }))}
            />
            {hasActiveFilter && (
                <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="shrink-0"
                    onClick={() =>
                        setParams({
                            assetClass: null,
                            market: null,
                            leverage: null,
                            manager: null,
                            replicationMethod: null,
                            taxType: null,
                        })
                    }
                >
                    초기화
                </Button>
            )}
        </div>
    )
}
