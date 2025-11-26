/**
 * Webhook TypeScript Types
 */

export interface Webhook {
  id: string;
  url: string;
  events: string[];
  is_active: boolean;
  secret: string | null;
  description: string | null;
  headers: Record<string, string> | null;
  retry_count: number;
  timeout_seconds: number;
  last_triggered_at: string | null;
  last_error: string | null;
  success_count: number;
  failure_count: number;
  created_at: string;
  updated_at: string;
}

export interface WebhookCreate {
  url: string;
  events: string[];
  is_active?: boolean;
  secret?: string | null;
  description?: string | null;
  headers?: Record<string, string> | null;
  retry_count?: number;
  timeout_seconds?: number;
}

export interface WebhookUpdate {
  url?: string;
  events?: string[];
  is_active?: boolean;
  secret?: string | null;
  description?: string | null;
  headers?: Record<string, string> | null;
  retry_count?: number;
  timeout_seconds?: number;
}

export interface WebhookListResponse {
  items: Webhook[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

export interface WebhookTestRequest {
  event: string;
  payload?: Record<string, any>;
}

export interface WebhookTestResponse {
  success: boolean;
  status_code: number | null;
  response_time_ms: number | null;
  response_body: string | null;
  error: string | null;
}

export interface WebhookLog {
  id: string;
  webhook_id: string;
  event: string;
  payload: Record<string, any>;
  status_code: number | null;
  response_body: string | null;
  response_time_ms: number | null;
  error: string | null;
  created_at: string;
}

export const WEBHOOK_EVENTS = [
  { value: 'product.created', label: 'Product Created' },
  { value: 'product.updated', label: 'Product Updated' },
  { value: 'product.deleted', label: 'Product Deleted' },
  { value: 'import.started', label: 'Import Started' },
  { value: 'import.completed', label: 'Import Completed' },
  { value: 'import.failed', label: 'Import Failed' },
] as const;

export type WebhookEventType = typeof WEBHOOK_EVENTS[number]['value'];

