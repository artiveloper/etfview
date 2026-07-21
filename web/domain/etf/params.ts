'use client'

import { parseAsString, parseAsStringLiteral } from 'nuqs'

export const LEVERAGE_VALUES = ['normal', 'leveraged', 'inverse'] as const
export type LeverageType = (typeof LEVERAGE_VALUES)[number]

export const etfSearchParams = {
    search: parseAsString.withDefault(''),
    assetClass: parseAsString,
    market: parseAsString,
    leverage: parseAsStringLiteral(LEVERAGE_VALUES),
    manager: parseAsString,
    replicationMethod: parseAsString,
    taxType: parseAsString,
}
