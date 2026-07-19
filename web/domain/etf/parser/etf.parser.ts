import type { EtfInfo, EtfQuote, EtfListResult, EtfFilterOptions } from '../types'

type RawEtfRow = {
    short_code: string
    standard_code: string
    name: string | null
    abbreviated_name: string | null
    english_name: string | null
    listed_date: string | null
    base_index_name: string | null
    index_provider: string | null
    tracking_multiplier: string | null
    replication_method: string | null
    base_market_class: string | null
    base_asset_class: string | null
    listed_shares: number | null
    manager: string | null
    creation_unit_quantity: number | null
    total_fee: number | null
    tax_type: string | null
    updated_at: string
}

type RawFilterRow = {
    base_asset_class: string | null
    base_market_class: string | null
}

type RawEtfQuoteRow = {
    short_code: string
    current_price: number | null
    price_change: number | null
    price_change_sign: string | null
    price_change_rate: number | null
    volume: number | null
    open_price: number | null
    high_price: number | null
    low_price: number | null
    year_high_price: number | null
    year_high_date: string | null
    year_low_price: number | null
    year_low_date: string | null
    nav: number | null
    nav_change: number | null
    nav_change_rate: number | null
    tracking_error_rate: number | null
    disparity_rate: number | null
    net_asset_total: number | null
    constituent_count: number | null
    updated_at: string
}

export function parseEtfInfo(raw: RawEtfRow): EtfInfo {
    return {
        shortCode: raw.short_code,
        standardCode: raw.standard_code,
        name: raw.name,
        abbreviatedName: raw.abbreviated_name,
        englishName: raw.english_name,
        listedDate: raw.listed_date,
        baseIndexName: raw.base_index_name,
        indexProvider: raw.index_provider,
        trackingMultiplier: raw.tracking_multiplier,
        replicationMethod: raw.replication_method,
        baseMarketClass: raw.base_market_class,
        baseAssetClass: raw.base_asset_class,
        listedShares: raw.listed_shares,
        manager: raw.manager,
        creationUnitQuantity: raw.creation_unit_quantity,
        totalFee: raw.total_fee,
        taxType: raw.tax_type,
        updatedAt: raw.updated_at,
    }
}

export function parseEtfList(
    rows: RawEtfRow[],
    total: number,
    page: number,
    pageSize: number,
): EtfListResult {
    return {
        items: rows.map(parseEtfInfo),
        total,
        page,
        pageSize,
        totalPages: Math.max(1, Math.ceil(total / pageSize)),
    }
}

export function parseEtfQuote(raw: RawEtfQuoteRow): EtfQuote {
    return {
        shortCode: raw.short_code,
        currentPrice: raw.current_price,
        priceChange: raw.price_change,
        priceChangeSign: raw.price_change_sign,
        priceChangeRate: raw.price_change_rate,
        volume: raw.volume,
        openPrice: raw.open_price,
        highPrice: raw.high_price,
        lowPrice: raw.low_price,
        yearHighPrice: raw.year_high_price,
        yearHighDate: raw.year_high_date,
        yearLowPrice: raw.year_low_price,
        yearLowDate: raw.year_low_date,
        nav: raw.nav,
        navChange: raw.nav_change,
        navChangeRate: raw.nav_change_rate,
        trackingErrorRate: raw.tracking_error_rate,
        disparityRate: raw.disparity_rate,
        netAssetTotal: raw.net_asset_total,
        constituentCount: raw.constituent_count,
        updatedAt: raw.updated_at,
    }
}

export function parseEtfFilterOptions(rows: RawFilterRow[]): EtfFilterOptions {
    const assetClasses = [
        ...new Set(rows.map((r) => r.base_asset_class).filter((v): v is string => v !== null)),
    ].sort()
    const markets = [
        ...new Set(rows.map((r) => r.base_market_class).filter((v): v is string => v !== null)),
    ].sort()
    return { assetClasses, markets }
}
