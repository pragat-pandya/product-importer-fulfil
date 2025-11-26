import { motion } from 'framer-motion';
import { Activity, Upload, Package, TrendingUp } from 'lucide-react';
import { PageTransition } from '@/components/PageTransition';

const stats = [
  {
    name: 'Total Products',
    value: '12,345',
    change: '+12.5%',
    icon: Package,
    color: 'text-blue-600',
  },
  {
    name: 'Active Imports',
    value: '3',
    change: '+2',
    icon: Upload,
    color: 'text-green-600',
  },
  {
    name: 'Tasks Running',
    value: '5',
    change: '-1',
    icon: Activity,
    color: 'text-purple-600',
  },
  {
    name: 'Success Rate',
    value: '98.5%',
    change: '+0.3%',
    icon: TrendingUp,
    color: 'text-orange-600',
  },
];

export function Dashboard() {
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
        {stats.map((stat, index) => (
          <motion.div
            key={stat.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="rounded-lg border bg-card p-6 shadow-sm"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <stat.icon className={`h-5 w-5 ${stat.color}`} />
                <p className="text-sm font-medium text-muted-foreground">
                  {stat.name}
                </p>
              </div>
              <span className="text-xs text-green-600">{stat.change}</span>
            </div>
            <div className="mt-2">
              <p className="text-2xl font-bold">{stat.value}</p>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Recent Activity */}
      <div className="rounded-lg border bg-card p-6 shadow-sm">
        <h2 className="text-lg font-semibold mb-4">Recent Activity</h2>
        <div className="space-y-4">
          {[1, 2, 3].map((item) => (
            <div key={item} className="flex items-center gap-4">
              <div className="h-2 w-2 rounded-full bg-green-500" />
              <div className="flex-1">
                <p className="text-sm font-medium">
                  CSV import completed
                </p>
                <p className="text-xs text-muted-foreground">
                  2 minutes ago
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
    </PageTransition>
  );
}

