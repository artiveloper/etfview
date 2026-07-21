import { supabase } from '@/lib/supabase/client'
import { parseEtfList, parseEtfInfo, parseEtfQuote, parseEtfFilterOptions } from '../parser/etf.parser'
import type { EtfListParams, EtfListResult, EtfFilterOptions, EtfInfo, EtfQuote } from '../types'

const DEFAULT_PAGE_SIZE = 20

export async function fetchEtfList(params: EtfListParams): Promise<EtfListResult> {
    const {
        page,
        search,
        assetClass,
        market,
        leverage,
        manager,
        replicationMethod,
        taxType,
        pageSize = DEFAULT_PAGE_SIZE,
    } = params
    const from = (page - 1) * pageSize
    const to = from + pageSize - 1

    let query = supabase
        .from('etf')
        .select('*, etf_quote(current_price, price_change, price_change_rate, net_asset_total)', {
            count: 'exact',
        })
        .order('short_code', { ascending: true })

    if (search) {
        query = query.ilike('name', `%${search}%`)
    }
    if (assetClass) {
        query = query.eq('base_asset_class', assetClass)
    }
    if (market) {
        query = query.eq('base_market_class', market)
    }
    if (manager) {
        query = query.eq('manager', manager)
    }
    if (replicationMethod) {
        query = query.eq('replication_method', replicationMethod)
    }
    if (taxType) {
        query = query.eq('tax_type', taxType)
    }
    if (leverage === 'inverse') {
        query = query.ilike('tracking_multiplier', '%인버스%')
    }
    if (leverage === 'leveraged') {
        query = query.ilike('tracking_multiplier', '%레버리지%')
    }
    if (leverage === 'normal') {
        query = query
            .not('tracking_multiplier', 'ilike', '%인버스%')
            .not('tracking_multiplier', 'ilike', '%레버리지%')
    }

    const { data, error, count } = await query.range(from, to)

    if (error) throw new Error(error.message)
    if (!data) throw new Error('ETF 데이터를 가져올 수 없습니다.')

    return parseEtfList(data, count ?? 0, page, pageSize)
}

export async function fetchEtfDetail(shortCode: string): Promise<EtfInfo> {
    const { data, error } = await supabase.from('etf').select('*').eq('short_code', shortCode).single()

    if (error) throw new Error(error.message)
    return parseEtfInfo(data)
}

export async function fetchEtfQuote(shortCode: string): Promise<EtfQuote | null> {
    const { data, error } = await supabase
        .from('etf_quote')
        .select('*')
        .eq('short_code', shortCode)
        .maybeSingle()

    if (error) throw new Error(error.message)
    return data ? parseEtfQuote(data) : null
}

export async function fetchEtfFilterOptions(): Promise<EtfFilterOptions> {
    const { data, error } = await supabase
        .from('etf_filter_options')
        .select('asset_classes, markets, managers, replication_methods, tax_types')
        .single()

    if (error) throw new Error(error.message)
    return parseEtfFilterOptions(data)
}
