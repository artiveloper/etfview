'use client'

import { useQueryStates } from 'nuqs'
import { Search } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { etfSearchParams } from '@/domain/etf/params'

export function EtfSearch() {
    const [{ search }, setParams] = useQueryStates(etfSearchParams)

    return (
        <div className="relative">
            <Search
                className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground"
                aria-hidden
            />
            <Input
                type="search"
                value={search}
                onChange={(e) => setParams({ search: e.target.value || null, page: null })}
                placeholder="ETF 이름으로 검색"
                className="h-11 pl-9"
            />
        </div>
    )
}
