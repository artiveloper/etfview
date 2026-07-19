import { dehydrate, type QueryClient } from '@tanstack/react-query'
import { getQueryClient } from './query-client'

export async function runPrefetch(
    ...prefetchers: Array<(qc: QueryClient) => Promise<void>>
) {
    const qc = getQueryClient()
    await Promise.all(prefetchers.map((fn) => fn(qc)))
    return dehydrate(qc)
}
