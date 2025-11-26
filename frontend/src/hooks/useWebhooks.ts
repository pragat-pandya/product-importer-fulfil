/**
 * Custom React Query hooks for Webhook API interactions
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import api from '@/lib/api';
import type {
  Webhook,
  WebhookCreate,
  WebhookUpdate,
  WebhookListResponse,
  WebhookTestRequest,
  WebhookTestResponse,
  WebhookLog,
} from '@/types/webhook';

interface WebhooksQueryParams {
  limit?: number;
  offset?: number;
  is_active?: boolean;
}

export const useWebhooks = (params: WebhooksQueryParams = {}) => {
  return useQuery<WebhookListResponse, Error>({
    queryKey: ['webhooks', params],
    queryFn: async () => {
      const { data } = await api.get<WebhookListResponse>('/webhooks', { params });
      return data;
    },
    placeholderData: (previousData) => previousData,
  });
};

export const useWebhook = (id: string) => {
  return useQuery<Webhook, Error>({
    queryKey: ['webhook', id],
    queryFn: async () => {
      const { data } = await api.get<Webhook>(`/webhooks/${id}`);
      return data;
    },
    enabled: !!id,
  });
};

export const useCreateWebhook = () => {
  const queryClient = useQueryClient();
  
  return useMutation<Webhook, Error, WebhookCreate>({
    mutationFn: async (newWebhook) => {
      const { data } = await api.post<Webhook>('/webhooks', newWebhook);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['webhooks'] });
      toast.success('Webhook created successfully!');
    },
    onError: (error: any) => {
      toast.error('Failed to create webhook', {
        description: error.response?.data?.detail || error.message,
      });
    },
  });
};

export const useUpdateWebhook = () => {
  const queryClient = useQueryClient();
  
  return useMutation<Webhook, Error, { id: string; data: WebhookUpdate }>({
    mutationFn: async ({ id, data }) => {
      const { data: updatedWebhook } = await api.put<Webhook>(`/webhooks/${id}`, data);
      return updatedWebhook;
    },
    onSuccess: (updatedWebhook) => {
      queryClient.invalidateQueries({ queryKey: ['webhooks'] });
      queryClient.invalidateQueries({ queryKey: ['webhook', updatedWebhook.id] });
      toast.success('Webhook updated successfully!');
    },
    onError: (error: any) => {
      toast.error('Failed to update webhook', {
        description: error.response?.data?.detail || error.message,
      });
    },
  });
};

export const useDeleteWebhook = () => {
  const queryClient = useQueryClient();
  
  return useMutation<void, Error, string>({
    mutationFn: async (id) => {
      await api.delete(`/webhooks/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['webhooks'] });
      toast.success('Webhook deleted successfully!');
    },
    onError: (error: any) => {
      toast.error('Failed to delete webhook', {
        description: error.response?.data?.detail || error.message,
      });
    },
  });
};

export const useTestWebhook = () => {
  return useMutation<WebhookTestResponse, Error, { id: string; request: WebhookTestRequest }>({
    mutationFn: async ({ id, request }) => {
      const { data } = await api.post<WebhookTestResponse>(`/webhooks/${id}/test`, request);
      return data;
    },
    onSuccess: (result) => {
      if (result.success) {
        toast.success('Webhook test successful!', {
          description: `Status: ${result.status_code}, Time: ${result.response_time_ms}ms`,
        });
      } else {
        toast.error('Webhook test failed', {
          description: result.error || 'Unknown error',
        });
      }
    },
    onError: (error: any) => {
      toast.error('Failed to test webhook', {
        description: error.response?.data?.detail || error.message,
      });
    },
  });
};

export const useWebhookLogs = (webhookId: string, limit: number = 50, offset: number = 0) => {
  return useQuery<WebhookLog[], Error>({
    queryKey: ['webhookLogs', webhookId, limit, offset],
    queryFn: async () => {
      const { data } = await api.get<WebhookLog[]>(`/webhooks/${webhookId}/logs`, {
        params: { limit, offset },
      });
      return data;
    },
    enabled: !!webhookId,
  });
};

