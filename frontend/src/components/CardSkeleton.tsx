/**
 * CardSkeleton Component
 * Loading skeleton for dashboard cards
 */
import { Skeleton } from '@/components/ui/skeleton';

export const CardSkeleton = () => {
  return (
    <div className="rounded-lg border bg-card p-6 shadow-sm">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Skeleton className="h-5 w-5 rounded" />
          <Skeleton className="h-4 w-24" />
        </div>
        <Skeleton className="h-3 w-12" />
      </div>
      <div className="mt-2">
        <Skeleton className="h-8 w-20" />
      </div>
    </div>
  );
};

