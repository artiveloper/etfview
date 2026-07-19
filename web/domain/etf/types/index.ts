export type EtfLeverageType = 'normal' | 'leveraged' | 'inverse'

export type EtfInfo = {
    shortCode: string
    standardCode: string
    name: string | null
    abbrName: string | null
    engName: string | null
    listedDate: string | null
    baseIndexName: string | null
    indexProvider: string | null
    trackingMultiplier: string | null
    replicationMethod: string | null
    baseMarketClass: string | null
    baseAssetClass: string | null
    listedShares: number | null
    manager: string | null
    cuQuantity: number | null
    totalFee: number | null
    taxType: string | null
    updatedAt: string
}

export type EtfListParams = {
    page: number
    search: string
    assetClass: string | null
    market: string | null
    leverage: EtfLeverageType | null
    pageSize?: number
}

export type EtfListResult = {
    items: EtfInfo[]
    total: number
    page: number
    pageSize: number
    totalPages: number
}

export type EtfFilterOptions = {
    assetClasses: string[]
    markets: string[]
}
