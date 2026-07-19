import { etfQueryKeys } from '../query-keys/etf.query-keys'
import { fetchEtfList, fetchEtfFilterOptions } from '../apis/etf.api'
import type { EtfListParams } from '../types'

type ListParams = Pick<EtfListParams, 'page' | 'search' | 'assetClass' | 'market' | 'leverage'>

export const etfQueryOptions = {
    list: (params: ListParams) => ({
        queryKey: etfQueryKeys.list(params),
        queryFn: () => fetchEtfList({ ...params, pageSize: 20 }),
    }),

    filterOptions: () => ({
        queryKey: etfQueryKeys.filterOptions,
        queryFn: fetchEtfFilterOptions,
        staleTime: 24 * 60 * 60_000,
        gcTime: 24 * 60 * 60_000,
    }),
}
