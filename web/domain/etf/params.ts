'use client'

import { parseAsInteger, parseAsString, parseAsStringLiteral } from 'nuqs'

export const LEVERAGE_VALUES = ['normal', 'leveraged', 'inverse'] as const
export type LeverageType = (typeof LEVERAGE_VALUES)[number]

export const etfSearchParams = {
    page: parseAsInteger.withDefault(1),
    search: parseAsString.withDefault(''),
    assetClass: parseAsString,
    market: parseAsString,
    leverage: parseAsStringLiteral(LEVERAGE_VALUES),
}
