import { Skeleton } from '@/components/ui/skeleton'
import { Card, CardContent } from '@/components/ui/card'

export function EtfFiltersSkeleton() {
    return (
        <div className="space-y-4 rounded-lg border bg-card p-4">
            {[1, 2, 3].map((i) => (
                <div key={i} className="flex flex-col gap-2 sm:flex-row sm:items-center sm:gap-x-3">
                    <Skeleton className="h-4 w-14" />
                    <div className="flex flex-wrap gap-1.5">
                        <Skeleton className="h-11 w-12 rounded-full" />
                        <Skeleton className="h-11 w-20 rounded-full" />
                        <Skeleton className="h-11 w-16 rounded-full" />
                        <Skeleton className="h-11 w-18 rounded-full" />
                    </div>
                </div>
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
