import { Skeleton } from '@/components/ui/skeleton'
import { Card, CardContent } from '@/components/ui/card'

export function EtfDetailHeaderSkeleton() {
    return (
        <div>
            <Skeleton className="h-7 w-56 sm:h-8" />
            <Skeleton className="mt-2 h-8 w-40 sm:h-9" />
        </div>
    )
}

export function EtfKeyMetricsSkeleton() {
    return (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            {Array.from({ length: 4 }).map((_, i) => (
                <Card key={i} className="gap-0 rounded-lg border py-0 shadow-none ring-0">
                    <CardContent className="p-4">
                        <Skeleton className="h-3 w-14" />
                        <Skeleton className="mt-2 h-6 w-20" />
                    </CardContent>
                </Card>
            ))}
        </div>
    )
}

export function EtfOverviewSkeleton() {
    return (
        <Card className="gap-0 rounded-lg border py-0 shadow-none ring-0">
            <CardContent className="p-4">
                <Skeleton className="h-4 w-16" />
                <div className="mt-4 space-y-3">
                    {Array.from({ length: 8 }).map((_, i) => (
                        <Skeleton key={i} className="h-4 w-full" />
                    ))}
                </div>
            </CardContent>
        </Card>
    )
}

export function EtfConstituentChartSkeleton() {
    return (
        <Card className="gap-0 rounded-lg border py-0 shadow-none ring-0">
            <CardContent className="p-4">
                <Skeleton className="h-4 w-32" />
                <Skeleton className="mt-2 h-3 w-48" />
                <Skeleton className="mx-auto mt-4 aspect-square max-h-[320px] w-full rounded-full" />
            </CardContent>
        </Card>
    )
}

export function EtfConstituentPanelSkeleton() {
    return (
        <Card className="gap-0 rounded-lg border py-0 shadow-none ring-0">
            <CardContent className="p-4">
                <Skeleton className="h-4 w-24" />
                <Skeleton className="mt-2 h-3 w-56" />
                <div className="mt-4 space-y-3">
                    {Array.from({ length: 8 }).map((_, i) => (
                        <Skeleton key={i} className="h-4 w-full" />
                    ))}
                </div>
            </CardContent>
        </Card>
    )
}
