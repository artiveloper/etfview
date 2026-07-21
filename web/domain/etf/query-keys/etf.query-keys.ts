import type { EtfListParams } from '../types'

type ListKeyParams = Pick<
    EtfListParams,
    'search' | 'assetClass' | 'market' | 'leverage' | 'manager' | 'replicationMethod' | 'taxType'
>

export const etfQueryKeys = {
    all: ['etf'] as const,

    list: (params: ListKeyParams) =>
        ['etf', 'list', params] as const,

    filterOptions: ['etf', 'filterOptions'] as const,

    detail: (shortCode: string) => ['etf', 'detail', shortCode] as const,

    quote: (shortCode: string) => ['etf', 'quote', shortCode] as const,
}
