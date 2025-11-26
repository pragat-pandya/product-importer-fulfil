/**
 * Product API Hooks
 * Custom hooks for product CRUD operations using TanStack Query
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import api from '@/lib/api';

// Types
export interface Product {
  id: string;
  sku: string;
  name: string;
  description: string | null;
  active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ProductListResponse {
  items: Product[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

export interface ProductCreate {
  sku: string;
  name: string;
  description?: string | null;
  active?: boolean;
}

export interface ProductUpdate {
  sku?: string;
  name?: string;
  description?: string | null;
  active?: boolean;
}

export interface ProductFilters {
  limit?: number;
  offset?: number;
  sku?: string;
  name?: string;
  active?: boolean;
}

// Query Keys
export const productKeys = {
  all: ['products'] as const,
  lists: () => [...productKeys.all, 'list'] as const,
  list: (filters: ProductFilters) => [...productKeys.lists(), filters] as const,
  details: () => [...productKeys.all, 'detail'] as const,
  detail: (id: string) => [...productKeys.details(), id] as const,
};

/**
 * Hook to fetch paginated and filtered products
 */
export function useProducts(filters: ProductFilters = {}) {
  return useQuery({
    queryKey: productKeys.list(filters),
    queryFn: async (): Promise<ProductListResponse> => {
      const params = new URLSearchParams();
      
      if (filters.limit !== undefined) params.append('limit', filters.limit.toString());
      if (filters.offset !== undefined) params.append('offset', filters.offset.toString());
      if (filters.sku) params.append('sku', filters.sku);
      if (filters.name) params.append('name', filters.name);
      if (filters.active !== undefined) params.append('active', filters.active.toString());
      
      const response = await api.get<ProductListResponse>(`/products?${params.toString()}`);
      return response.data;
    },
    staleTime: 30000, // 30 seconds
  });
}

/**
 * Hook to fetch a single product by ID
 */
export function useProduct(id: string) {
  return useQuery({
    queryKey: productKeys.detail(id),
    queryFn: async (): Promise<Product> => {
      const response = await api.get<Product>(`/products/${id}`);
      return response.data;
    },
    enabled: !!id,
  });
}

/**
 * Hook to create a new product
 */
export function useCreateProduct() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: ProductCreate): Promise<Product> => {
      const response = await api.post<Product>('/products', data);
      return response.data;
    },
    onSuccess: () => {
      // Invalidate and refetch products list
      queryClient.invalidateQueries({ queryKey: productKeys.lists() });
      toast.success('Product created successfully!');
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Failed to create product';
      toast.error(message);
    },
  });
}

/**
 * Hook to update an existing product
 */
export function useUpdateProduct() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: ProductUpdate }): Promise<Product> => {
      const response = await api.put<Product>(`/products/${id}`, data);
      return response.data;
    },
    onSuccess: (data) => {
      // Invalidate and refetch
      queryClient.invalidateQueries({ queryKey: productKeys.lists() });
      queryClient.invalidateQueries({ queryKey: productKeys.detail(data.id) });
      toast.success('Product updated successfully!');
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Failed to update product';
      toast.error(message);
    },
  });
}

/**
 * Hook to delete a single product
 */
export function useDeleteProduct() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id: string): Promise<void> => {
      await api.delete(`/products/${id}`);
    },
    onSuccess: () => {
      // Invalidate and refetch
      queryClient.invalidateQueries({ queryKey: productKeys.lists() });
      toast.success('Product deleted successfully!');
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Failed to delete product';
      toast.error(message);
    },
  });
}

/**
 * Hook to delete all products (Celery task)
 */
export function useBulkDeleteProducts() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (): Promise<{ task_id: string; status: string; message: string }> => {
      const response = await api.delete('/products/all');
      return response.data;
    },
    onSuccess: (data) => {
      toast.info('Bulk delete initiated', {
        description: `Task ID: ${data.task_id}`,
      });
      
      // Invalidate products list after a short delay to allow task to complete
      setTimeout(() => {
        queryClient.invalidateQueries({ queryKey: productKeys.lists() });
      }, 3000);
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Failed to initiate bulk delete';
      toast.error(message);
    },
  });
}

/**
 * Hook to check bulk delete status
 */
export function useBulkDeleteStatus(taskId: string | null) {
  return useQuery({
    queryKey: ['bulk-delete-status', taskId],
    queryFn: async (): Promise<{
      task_id: string;
      status: string;
      message: string;
      percent: number;
      deleted_count?: number;
    }> => {
      if (!taskId) throw new Error('No task ID provided');
      const response = await api.get(`/products/delete/${taskId}/status`);
      return response.data;
    },
    enabled: !!taskId,
    refetchInterval: (query) => {
      // Stop polling if task is complete or failed
      const data = query.state.data;
      if (data?.status === 'SUCCESS' || data?.status === 'FAILURE') {
        return false;
      }
      return 1000; // Poll every second
    },
  });
}

