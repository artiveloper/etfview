import { infiniteQueryOptions } from '@tanstack/react-query'
import { etfQueryKeys } from '../query-keys/etf.query-keys'
import {
    fetchEtfList,
    fetchEtfFilterOptions,
    fetchEtfDetail,
    fetchEtfQuote,
    fetchEtfConstituents,
    DEFAULT_PAGE_SIZE,
} from '../apis/etf.api'
import type { EtfListParams, EtfListResult } from '../types'

type ListParams = Pick<
    EtfListParams,
    'search' | 'assetClass' | 'market' | 'leverage' | 'manager' | 'replicationMethod' | 'taxType'
>

// infiniteQueryOptions()가 queryOptions()의 infinite 전용 버전이다 —
// pageParam/getNextPageParam까지 타입 추론되고, hooks(client)·prefetch(server)가 그대로 공유한다.
export function etfInfiniteListQuery(params: ListParams) {
    return infiniteQueryOptions({
        queryKey: etfQueryKeys.list(params),
        queryFn: ({ pageParam }) => fetchEtfList({ ...params, page: pageParam, pageSize: DEFAULT_PAGE_SIZE }),
        initialPageParam: 1,
        getNextPageParam: (lastPage: EtfListResult) =>
            lastPage.page < lastPage.totalPages ? lastPage.page + 1 : undefined,
    })
}

export const etfQueryOptions = {
    filterOptions: () => ({
        queryKey: etfQueryKeys.filterOptions,
        queryFn: fetchEtfFilterOptions,
        staleTime: 24 * 60 * 60_000,
        gcTime: 24 * 60 * 60_000,
    }),

    detail: (shortCode: string) => ({
        queryKey: etfQueryKeys.detail(shortCode),
        queryFn: () => fetchEtfDetail(shortCode),
    }),

    quote: (shortCode: string) => ({
        queryKey: etfQueryKeys.quote(shortCode),
        queryFn: () => fetchEtfQuote(shortCode),
    }),

    constituents: (shortCode: string) => ({
        queryKey: etfQueryKeys.constituents(shortCode),
        queryFn: () => fetchEtfConstituents(shortCode),
    }),
}
