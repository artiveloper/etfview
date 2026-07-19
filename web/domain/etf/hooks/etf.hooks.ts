import { useSuspenseQuery } from '@tanstack/react-query'
import { etfQueryOptions } from '../query-options/etf.query-options'
import type { EtfListParams } from '../types'

type ListParams = Pick<EtfListParams, 'page' | 'search' | 'assetClass' | 'market' | 'leverage'>

export function useEtfList(params: ListParams) {
    return useSuspenseQuery(etfQueryOptions.list(params))
}

export function useEtfFilterOptions() {
    return useSuspenseQuery(etfQueryOptions.filterOptions())
}
