/**
 * EditWebhookDialog Component
 * Form dialog for editing existing webhooks
 */
import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Textarea } from '@/components/ui/textarea';
import type { Webhook, WebhookUpdate } from '@/types/webhook';
import { WEBHOOK_EVENTS } from '@/types/webhook';
import { useUpdateWebhook } from '@/hooks/useWebhooks';
import { Checkbox } from '@/components/ui/checkbox';

interface EditWebhookDialogProps {
  webhook: Webhook | null;
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
}

export const EditWebhookDialog: React.FC<EditWebhookDialogProps> = ({
  webhook,
  isOpen,
  onOpenChange,
}) => {
  const [formData, setFormData] = useState<Webhook | null>(null);

  const updateWebhookMutation = useUpdateWebhook();

  useEffect(() => {
    if (webhook) {
      setFormData(webhook);
    }
  }, [webhook]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { id, value } = e.target;
    setFormData((prev) => {
      if (!prev) return prev;
      return {
        ...prev,
        [id]: id === 'retry_count' || id === 'timeout_seconds' ? parseInt(value) || 0 : value,
      };
    });
  };

  const handleSwitchChange = (checked: boolean) => {
    setFormData((prev) => (prev ? { ...prev, is_active: checked } : prev));
  };

  const handleEventToggle = (eventValue: string, checked: boolean) => {
    setFormData((prev) => {
      if (!prev) return prev;
      return {
        ...prev,
        events: checked
          ? [...prev.events, eventValue]
          : prev.events.filter((e) => e !== eventValue),
      };
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData || !webhook) return;

    // Build update payload with only changed fields
    const updateData: WebhookUpdate = {};

    if (formData.url !== webhook.url) updateData.url = formData.url;
    if (JSON.stringify(formData.events) !== JSON.stringify(webhook.events)) {
      updateData.events = formData.events;
    }
    if (formData.is_active !== webhook.is_active) updateData.is_active = formData.is_active;
    if (formData.secret !== webhook.secret) updateData.secret = formData.secret || null;
    if (formData.description !== webhook.description) {
      updateData.description = formData.description || null;
    }
    if (formData.retry_count !== webhook.retry_count) updateData.retry_count = formData.retry_count;
    if (formData.timeout_seconds !== webhook.timeout_seconds) {
      updateData.timeout_seconds = formData.timeout_seconds;
    }

    if (Object.keys(updateData).length === 0) {
      onOpenChange(false);
      return;
    }

    try {
      await updateWebhookMutation.mutateAsync({
        id: webhook.id,
        data: updateData,
      });
      onOpenChange(false);
    } catch (error) {
      // Error handled by mutation
    }
  };

  if (!formData) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Edit Webhook</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="grid gap-4 py-4">
          {/* Webhook ID (readonly) */}
          <div className="grid gap-2">
            <Label>Webhook ID</Label>
            <Input value={formData.id} disabled className="font-mono text-xs" />
          </div>

          {/* URL */}
          <div className="grid gap-2">
            <Label htmlFor="url">
              URL <span className="text-red-500">*</span>
            </Label>
            <Input
              id="url"
              type="url"
              placeholder="https://example.com/webhook"
              value={formData.url}
              onChange={handleChange}
              required
            />
          </div>

          {/* Events */}
          <div className="grid gap-2">
            <Label>
              Events <span className="text-red-500">*</span>
            </Label>
            <div className="grid grid-cols-2 gap-3 p-4 border rounded-md">
              {WEBHOOK_EVENTS.map((event) => (
                <div key={event.value} className="flex items-center space-x-2">
                  <Checkbox
                    id={event.value}
                    checked={formData.events.includes(event.value)}
                    onCheckedChange={(checked: boolean) =>
                      handleEventToggle(event.value, checked)
                    }
                  />
                  <label
                    htmlFor={event.value}
                    className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer"
                  >
                    {event.label}
                  </label>
                </div>
              ))}
            </div>
          </div>

          {/* Description */}
          <div className="grid gap-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              placeholder="What is this webhook for?"
              value={formData.description || ''}
              onChange={handleChange}
              rows={3}
            />
          </div>

          {/* Secret */}
          <div className="grid gap-2">
            <Label htmlFor="secret">Secret Key</Label>
            <Input
              id="secret"
              type="password"
              placeholder="Leave blank to keep current secret"
              value={formData.secret || ''}
              onChange={handleChange}
            />
            <p className="text-xs text-muted-foreground">
              Update secret key (leave blank to keep current)
            </p>
          </div>

          {/* Configuration Section */}
          <div className="grid grid-cols-2 gap-4">
            <div className="grid gap-2">
              <Label htmlFor="retry_count">Retry Count</Label>
              <Input
                id="retry_count"
                type="number"
                min="0"
                max="10"
                value={formData.retry_count}
                onChange={handleChange}
              />
            </div>

            <div className="grid gap-2">
              <Label htmlFor="timeout_seconds">Timeout (seconds)</Label>
              <Input
                id="timeout_seconds"
                type="number"
                min="1"
                max="300"
                value={formData.timeout_seconds}
                onChange={handleChange}
              />
            </div>
          </div>

          {/* Statistics (readonly) */}
          <div className="grid grid-cols-3 gap-4 p-4 bg-muted rounded-md">
            <div>
              <Label className="text-xs text-muted-foreground">Success Count</Label>
              <p className="text-lg font-semibold text-green-600">{formData.success_count}</p>
            </div>
            <div>
              <Label className="text-xs text-muted-foreground">Failure Count</Label>
              <p className="text-lg font-semibold text-red-600">{formData.failure_count}</p>
            </div>
            <div>
              <Label className="text-xs text-muted-foreground">Last Triggered</Label>
              <p className="text-xs">
                {formData.last_triggered_at
                  ? new Date(formData.last_triggered_at).toLocaleString()
                  : 'Never'}
              </p>
            </div>
          </div>

          {/* Last Error */}
          {formData.last_error && (
            <div className="grid gap-2">
              <Label className="text-destructive">Last Error</Label>
              <Textarea
                value={formData.last_error}
                disabled
                rows={2}
                className="text-xs font-mono"
              />
            </div>
          )}

          {/* Active Switch */}
          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="is_active">Active</Label>
              <p className="text-xs text-muted-foreground">
                Enable or disable this webhook
              </p>
            </div>
            <Switch
              id="is_active"
              checked={formData.is_active}
              onCheckedChange={handleSwitchChange}
            />
          </div>

          {/* Timestamps (readonly) */}
          <div className="grid grid-cols-2 gap-4 text-xs text-muted-foreground">
            <div>
              <Label className="text-xs">Created</Label>
              <p>{new Date(formData.created_at).toLocaleString()}</p>
            </div>
            <div>
              <Label className="text-xs">Updated</Label>
              <p>{new Date(formData.updated_at).toLocaleString()}</p>
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => onOpenChange(false)}
              type="button"
              disabled={updateWebhookMutation.isPending}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={updateWebhookMutation.isPending || formData.events.length === 0}
            >
              {updateWebhookMutation.isPending ? 'Saving...' : 'Save Changes'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

