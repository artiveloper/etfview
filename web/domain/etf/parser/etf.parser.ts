import type { EtfInfo, EtfListResult, EtfFilterOptions } from '../types'

type RawEtfRow = {
    short_code: string
    standard_code: string
    name: string | null
    abbr_name: string | null
    eng_name: string | null
    listed_date: string | null
    base_index_name: string | null
    index_provider: string | null
    tracking_multiplier: string | null
    replication_method: string | null
    base_market_class: string | null
    base_asset_class: string | null
    listed_shares: number | null
    manager: string | null
    cu_quantity: number | null
    total_fee: number | null
    tax_type: string | null
    updated_at: string
}

type RawFilterRow = {
    base_asset_class: string | null
    base_market_class: string | null
}

function parseEtfInfo(raw: RawEtfRow): EtfInfo {
    return {
        shortCode: raw.short_code,
        standardCode: raw.standard_code,
        name: raw.name,
        abbrName: raw.abbr_name,
        engName: raw.eng_name,
        listedDate: raw.listed_date,
        baseIndexName: raw.base_index_name,
        indexProvider: raw.index_provider,
        trackingMultiplier: raw.tracking_multiplier,
        replicationMethod: raw.replication_method,
        baseMarketClass: raw.base_market_class,
        baseAssetClass: raw.base_asset_class,
        listedShares: raw.listed_shares,
        manager: raw.manager,
        cuQuantity: raw.cu_quantity,
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

export function parseEtfFilterOptions(rows: RawFilterRow[]): EtfFilterOptions {
    const assetClasses = [
        ...new Set(rows.map((r) => r.base_asset_class).filter((v): v is string => v !== null)),
    ].sort()
    const markets = [
        ...new Set(rows.map((r) => r.base_market_class).filter((v): v is string => v !== null)),
    ].sort()
    return { assetClasses, markets }
}
