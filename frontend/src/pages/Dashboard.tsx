import { motion } from 'framer-motion';
import { Activity, Upload, Package, TrendingUp, Loader2 } from 'lucide-react';
import { PageTransition } from '@/components/PageTransition';
import { useDashboardStats } from '@/hooks/useDashboard';

function formatNumber(num: number): string {
  return new Intl.NumberFormat('en-US').format(num);
}

export function Dashboard() {
  const { data: stats, isLoading, error } = useDashboardStats();

  const statsCards = [
    {
      name: 'Total Products',
      value: stats ? formatNumber(stats.totalProducts) : '0',
      icon: Package,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50 dark:bg-blue-950',
    },
    {
      name: 'Active Products',
      value: stats ? formatNumber(stats.activeProducts) : '0',
      icon: Upload,
      color: 'text-green-600',
      bgColor: 'bg-green-50 dark:bg-green-950',
    },
    {
      name: 'Tasks Running',
      value: stats ? formatNumber(stats.activeTasks) : '0',
      icon: Activity,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50 dark:bg-purple-950',
    },
    {
      name: 'Active Rate',
      value: stats ? `${stats.successRate}%` : '0%',
      icon: TrendingUp,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50 dark:bg-orange-950',
    },
  ];

  return (
    <PageTransition>
    <div className="space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome to FulFil Product Importer
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {statsCards.map((stat, index) => (
          <motion.div
            key={stat.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="rounded-lg border bg-card p-6 shadow-sm"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className={`rounded-lg p-2 ${stat.bgColor}`}>
                  <stat.icon className={`h-5 w-5 ${stat.color}`} />
                </div>
                <p className="text-sm font-medium text-muted-foreground">
                  {stat.name}
                </p>
              </div>
              {isLoading && (
                <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
              )}
            </div>
            <div className="mt-4">
              {isLoading ? (
                <div className="h-8 w-24 animate-pulse rounded bg-muted" />
              ) : error ? (
                <p className="text-2xl font-bold text-destructive">Error</p>
              ) : (
                <p className="text-2xl font-bold">{stat.value}</p>
              )}
            </div>
          </motion.div>
        ))}
      </div>

      {/* Additional Stats */}
      {stats && (
        <div className="grid gap-4 md:grid-cols-2">
          <div className="rounded-lg border bg-card p-6 shadow-sm">
            <h2 className="text-lg font-semibold mb-4">Product Status</h2>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Active Products</span>
                <span className="text-lg font-semibold text-green-600">
                  {formatNumber(stats.activeProducts)}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Inactive Products</span>
                <span className="text-lg font-semibold text-muted-foreground">
                  {formatNumber(stats.inactiveProducts)}
                </span>
              </div>
              <div className="pt-2 border-t">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Total</span>
                  <span className="text-lg font-bold">
                    {formatNumber(stats.totalProducts)}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div className="rounded-lg border bg-card p-6 shadow-sm">
            <h2 className="text-lg font-semibold mb-4">System Status</h2>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Active Tasks</span>
                <span className="text-lg font-semibold text-purple-600">
                  {formatNumber(stats.activeTasks)}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Active Rate</span>
                <span className="text-lg font-semibold text-orange-600">
                  {stats.successRate}%
                </span>
              </div>
              <div className="pt-2">
                <div className="w-full bg-muted rounded-full h-2">
                  <div
                    className="bg-orange-600 h-2 rounded-full transition-all"
                    style={{ width: `${Math.min(stats.successRate, 100)}%` }}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
    </PageTransition>
  );
}

