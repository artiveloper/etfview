export type EtfLeverageType = 'normal' | 'leveraged' | 'inverse'

export type EtfInfo = {
    shortCode: string
    standardCode: string
    name: string | null
    abbreviatedName: string | null
    englishName: string | null
    listedDate: string | null
    baseIndexName: string | null
    indexProvider: string | null
    trackingMultiplier: string | null
    replicationMethod: string | null
    baseMarketClass: string | null
    baseAssetClass: string | null
    listedShares: number | null
    manager: string | null
    creationUnitQuantity: number | null
    totalFee: number | null
    taxType: string | null
    updatedAt: string
}

export type EtfQuote = {
    shortCode: string
    currentPrice: number | null
    priceChange: number | null
    priceChangeSign: string | null
    priceChangeRate: number | null
    volume: number | null
    openPrice: number | null
    highPrice: number | null
    lowPrice: number | null
    yearHighPrice: number | null
    yearHighDate: string | null
    yearLowPrice: number | null
    yearLowDate: string | null
    nav: number | null
    navChange: number | null
    navChangeRate: number | null
    trackingErrorRate: number | null
    disparityRate: number | null
    netAssetTotal: number | null
    constituentCount: number | null
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
