import type { EtfInfo, EtfQuote, EtfConstituent, EtfListItem, EtfListResult, EtfFilterOptions } from '../types'

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

type RawEtfListRow = RawEtfRow & {
    etf_quote: {
        current_price: number | null
        price_change: number | null
        price_change_rate: number | null
        net_asset_total: number | null
    } | null
}

type RawFilterOptionsRow = {
    asset_classes: string[] | null
    markets: string[] | null
    managers: string[] | null
    replication_methods: string[] | null
    tax_types: string[] | null
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
    nav_change_sign: string | null
    nav_change_rate: number | null
    tracking_error_rate: number | null
    disparity_rate: number | null
    net_asset_total: number | null
    constituent_count: number | null
    circulating_shares: number | null
    foreign_holding_qty: number | null
    foreign_holding_rate: number | null
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

function parseEtfListItem(raw: RawEtfListRow): EtfListItem {
    return {
        ...parseEtfInfo(raw),
        quote: raw.etf_quote && {
            currentPrice: raw.etf_quote.current_price,
            priceChange: raw.etf_quote.price_change,
            priceChangeRate: raw.etf_quote.price_change_rate,
            netAssetTotal: raw.etf_quote.net_asset_total,
        },
    }
}

export function parseEtfList(
    rows: RawEtfListRow[],
    total: number,
    page: number,
    pageSize: number,
): EtfListResult {
    return {
        items: rows.map(parseEtfListItem),
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
        navChangeSign: raw.nav_change_sign,
        navChangeRate: raw.nav_change_rate,
        trackingErrorRate: raw.tracking_error_rate,
        disparityRate: raw.disparity_rate,
        netAssetTotal: raw.net_asset_total,
        constituentCount: raw.constituent_count,
        circulatingShares: raw.circulating_shares,
        foreignHoldingQty: raw.foreign_holding_qty,
        foreignHoldingRate: raw.foreign_holding_rate,
        updatedAt: raw.updated_at,
    }
}

type RawEtfConstituentRow = {
    etf_short_code: string
    constituent_short_code: string
    constituent_name: string | null
    weight_percentage: number | null
    market_value_amount: number | null
}

export function parseEtfConstituent(raw: RawEtfConstituentRow): EtfConstituent {
    return {
        etfShortCode: raw.etf_short_code,
        constituentShortCode: raw.constituent_short_code,
        constituentName: raw.constituent_name,
        weightPercentage: raw.weight_percentage,
        marketValueAmount: raw.market_value_amount,
    }
}

export function parseEtfFilterOptions(raw: RawFilterOptionsRow): EtfFilterOptions {
    return {
        assetClasses: raw.asset_classes ?? [],
        markets: raw.markets ?? [],
        managers: raw.managers ?? [],
        replicationMethods: raw.replication_methods ?? [],
        taxTypes: raw.tax_types ?? [],
    }
}
