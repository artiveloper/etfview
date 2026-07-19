import type { EtfListParams } from '../types'

type ListKeyParams = Pick<EtfListParams, 'page' | 'search' | 'assetClass' | 'market' | 'leverage'>

export const etfQueryKeys = {
    all: ['etf'] as const,

    list: (params: ListKeyParams) =>
        ['etf', 'list', params] as const,

    filterOptions: ['etf', 'filterOptions'] as const,
}
