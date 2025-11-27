/**
 * Dashboard API Hooks
 * Custom hooks for dashboard statistics
 */
import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api';

export interface DashboardStats {
  totalProducts: number;
  activeProducts: number;
  inactiveProducts: number;
  activeTasks: number;
  successRate: number;
}

export interface TaskInfo {
  active: number;
  stats: Record<string, any>;
}

/**
 * Hook to fetch dashboard statistics
 */
export function useDashboardStats() {
  return useQuery({
    queryKey: ['dashboard', 'stats'],
    queryFn: async (): Promise<DashboardStats> => {
      // Fetch total products
      const totalResponse = await api.get('/products?limit=1&offset=0');
      const totalProducts = totalResponse.data.total || 0;

      // Fetch active products
      const activeResponse = await api.get('/products?limit=1&offset=0&active=true');
      const activeProducts = activeResponse.data.total || 0;

      // Fetch inactive products
      const inactiveResponse = await api.get('/products?limit=1&offset=0&active=false');
      const inactiveProducts = inactiveResponse.data.total || 0;

      // Fetch active tasks (Celery workers)
      let activeTasks = 0;
      try {
        const workersResponse = await api.get('/celery/workers');
        const workers = workersResponse.data.workers;
        if (workers?.active) {
          // Count active tasks across all workers
          activeTasks = Object.values(workers.active).reduce(
            (count: number, tasks: any) => count + (Array.isArray(tasks) ? tasks.length : 0),
            0
          );
        }
      } catch (error) {
        console.error('Failed to fetch active tasks:', error);
      }

      // Calculate active rate (percentage of products that are active)
      const successRate = totalProducts > 0 
        ? Math.round((activeProducts / totalProducts) * 100 * 10) / 10 
        : 100;

      return {
        totalProducts,
        activeProducts,
        inactiveProducts,
        activeTasks,
        successRate,
      };
    },
    staleTime: 10000, // 10 seconds
    refetchInterval: 30000, // Refetch every 30 seconds
  });
}

