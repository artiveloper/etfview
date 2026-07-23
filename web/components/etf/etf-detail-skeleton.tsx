import { Skeleton } from '@/components/ui/skeleton'
import { Card, CardContent } from '@/components/ui/card'

export function EtfDetailSkeleton() {
    return (
        <Card className="gap-0 rounded-lg border py-0 shadow-none ring-0">
            <CardContent className="p-4">
                <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 space-y-2">
                        <Skeleton className="h-5 w-3/4" />
                        <Skeleton className="h-3 w-1/2" />
                    </div>
                    <Skeleton className="h-5 w-12 rounded-full" />
                </div>
                <div className="mt-4 space-y-3">
                    {Array.from({ length: 6 }).map((_, i) => (
                        <Skeleton key={i} className="h-4 w-full" />
                    ))}
                </div>
            </CardContent>
        </Card>
    )
}

export function EtfQuotePanelSkeleton() {
    return (
        <Card className="gap-0 rounded-lg border py-0 shadow-none ring-0">
            <CardContent className="p-4">
                <Skeleton className="h-8 w-40" />
                <div className="mt-4 space-y-3">
                    {Array.from({ length: 6 }).map((_, i) => (
                        <Skeleton key={i} className="h-4 w-full" />
                    ))}
                </div>
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
