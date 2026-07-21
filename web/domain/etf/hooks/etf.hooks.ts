import { useSuspenseQuery, useSuspenseInfiniteQuery } from '@tanstack/react-query'
import { etfQueryOptions, etfInfiniteListQuery } from '../query-options/etf.query-options'
import type { EtfListParams } from '../types'

type ListParams = Pick<
    EtfListParams,
    'search' | 'assetClass' | 'market' | 'leverage' | 'manager' | 'replicationMethod' | 'taxType'
>

export function useEtfList(params: ListParams) {
    return useSuspenseInfiniteQuery(etfInfiniteListQuery(params))
}

export function useEtfFilterOptions() {
    return useSuspenseQuery(etfQueryOptions.filterOptions())
}

export function useEtfDetail(shortCode: string) {
    return useSuspenseQuery(etfQueryOptions.detail(shortCode))
}

export function useEtfQuote(shortCode: string) {
    return useSuspenseQuery(etfQueryOptions.quote(shortCode))
}
