import { Skeleton } from '@/components/ui/skeleton'
import { Card, CardContent } from '@/components/ui/card'

export function EtfFiltersSkeleton() {
    return (
        <div className="flex gap-2 overflow-x-auto">
            {[1, 2, 3, 4, 5, 6].map((i) => (
                <Skeleton key={i} className="h-9 w-40 shrink-0" />
            ))}
        </div>
    )
}

export function EtfListSkeleton() {
    return (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 12 }).map((_, i) => (
                <Card key={i} className="gap-0 rounded-lg border py-0 shadow-none ring-0">
                    <CardContent className="p-4">
                        <div className="flex items-start justify-between gap-3">
                            <div className="flex-1 space-y-2">
                                <Skeleton className="h-4 w-3/4" />
                                <Skeleton className="h-3 w-1/4" />
                            </div>
                            <Skeleton className="h-5 w-12 rounded-full" />
                        </div>
                        <div className="mt-3 flex gap-2">
                            <Skeleton className="h-3 w-16" />
                            <Skeleton className="h-3 w-10" />
                            <Skeleton className="h-3 w-10" />
                        </div>
                        <Skeleton className="mt-2 h-3 w-24" />
                    </CardContent>
                </Card>
            ))}
        </div>
    )
}
