import 'server-only'
import type { QueryClient } from '@tanstack/react-query'
import { etfQueryOptions } from '../query-options/etf.query-options'
import type { EtfListParams } from '../types'

type ListParams = Pick<EtfListParams, 'page' | 'search' | 'assetClass' | 'market' | 'leverage'>

export const etfPrefetch = {
    list(params: ListParams) {
        return async (queryClient: QueryClient) => {
            await queryClient.prefetchQuery(etfQueryOptions.list(params))
        }
    },

    filterOptions() {
        return async (queryClient: QueryClient) => {
            await queryClient.prefetchQuery(etfQueryOptions.filterOptions())
        }
    },
}
