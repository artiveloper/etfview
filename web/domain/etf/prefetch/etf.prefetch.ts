import 'server-only'
import { unstable_cache } from 'next/cache'
import type { QueryClient } from '@tanstack/react-query'
import { etfQueryKeys } from '../query-keys/etf.query-keys'
import { etfQueryOptions, etfInfiniteListQuery } from '../query-options/etf.query-options'
import { fetchEtfFilterOptions } from '../apis/etf.api'
import type { EtfListParams } from '../types'

type ListParams = Pick<
    EtfListParams,
    'search' | 'assetClass' | 'market' | 'leverage' | 'manager' | 'replicationMethod' | 'taxType'
>

// React Query의 QueryClient는 요청마다 새로 생성돼(query-client.ts의 cache() 스코프)
// staleTime이 SSR 단계에서는 요청 간에 유지되지 않는다 — Next.js Data Cache로 실제 요청 간 공유되게 한다.
const getCachedFilterOptions = unstable_cache(fetchEtfFilterOptions, ['etf-filter-options'], {
    revalidate: 24 * 60 * 60,
})

export const etfPrefetch = {
    list(params: ListParams) {
        return async (queryClient: QueryClient) => {
            await queryClient.prefetchInfiniteQuery(etfInfiniteListQuery(params))
        }
    },

    filterOptions() {
        return async (queryClient: QueryClient) => {
            await queryClient.prefetchQuery({
                queryKey: etfQueryKeys.filterOptions,
                queryFn: getCachedFilterOptions,
                staleTime: 24 * 60 * 60_000,
                gcTime: 24 * 60 * 60_000,
            })
        }
    },

    detail(shortCode: string) {
        return async (queryClient: QueryClient) => {
            await queryClient.prefetchQuery(etfQueryOptions.detail(shortCode))
        }
    },

    quote(shortCode: string) {
        return async (queryClient: QueryClient) => {
            await queryClient.prefetchQuery(etfQueryOptions.quote(shortCode))
        }
    },
}
