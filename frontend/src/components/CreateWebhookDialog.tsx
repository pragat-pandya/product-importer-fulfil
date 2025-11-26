/**
 * CreateWebhookDialog Component
 * Form dialog for creating new webhooks
 */
import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Textarea } from '@/components/ui/textarea';
import type { WebhookCreate } from '@/types/webhook';
import { WEBHOOK_EVENTS } from '@/types/webhook';
import { useCreateWebhook } from '@/hooks/useWebhooks';
import { Checkbox } from '@/components/ui/checkbox';

interface CreateWebhookDialogProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
}

export const CreateWebhookDialog: React.FC<CreateWebhookDialogProps> = ({
  isOpen,
  onOpenChange,
}) => {
  const [formData, setFormData] = useState<WebhookCreate>({
    url: '',
    events: [],
    is_active: true,
    secret: '',
    description: '',
    headers: null,
    retry_count: 3,
    timeout_seconds: 30,
  });

  const createWebhookMutation = useCreateWebhook();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { id, value } = e.target;
    setFormData((prev) => ({
...prev,
      [id]: id === 'retry_count' || id === 'timeout_seconds' ? parseInt(value) || 0 : value,
    }));
  };

  const handleSwitchChange = (checked: boolean) => {
    setFormData((prev) => ({ ...prev, is_active: checked }));
  };

  const handleEventToggle = (eventValue: string, checked: boolean) => {
    setFormData((prev) => ({
      ...prev,
      events: checked
        ? [...prev.events, eventValue]
        : prev.events.filter((e) => e !== eventValue),
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.url || formData.events.length === 0) {
      return;
    }

    // Clean up empty fields
    const cleanedData: WebhookCreate = {
      url: formData.url,
      events: formData.events,
      is_active: formData.is_active,
      retry_count: formData.retry_count,
      timeout_seconds: formData.timeout_seconds,
    };

    if (formData.secret) cleanedData.secret = formData.secret;
    if (formData.description) cleanedData.description = formData.description;

    try {
      await createWebhookMutation.mutateAsync(cleanedData);
      onOpenChange(false);
      // Reset form
      setFormData({
        url: '',
        events: [],
        is_active: true,
        secret: '',
        description: '',
        headers: null,
        retry_count: 3,
        timeout_seconds: 30,
      });
    } catch (error) {
      // Error handled by mutation
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Create New Webhook</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="grid gap-4 py-4">
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
            <p className="text-xs text-muted-foreground">
              Target URL for webhook delivery (must start with http:// or https://)
            </p>
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
            <p className="text-xs text-muted-foreground">
              Select one or more events to subscribe to
            </p>
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
            <Label htmlFor="secret">Secret Key (Optional)</Label>
            <Input
              id="secret"
              type="password"
              placeholder="Your secret key for HMAC signature"
              value={formData.secret || ''}
              onChange={handleChange}
            />
            <p className="text-xs text-muted-foreground">
              Used for HMAC SHA256 signature verification (X-Webhook-Signature header)
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
              <p className="text-xs text-muted-foreground">0-10 retries</p>
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
              <p className="text-xs text-muted-foreground">1-300 seconds</p>
            </div>
          </div>

          {/* Active Switch */}
          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="is_active">Active</Label>
              <p className="text-xs text-muted-foreground">
                Enable webhook immediately after creation
              </p>
            </div>
            <Switch
              id="is_active"
              checked={formData.is_active}
              onCheckedChange={handleSwitchChange}
            />
          </div>

          <DialogFooter>
            <Button 
              variant="outline" 
              onClick={() => onOpenChange(false)} 
              type="button"
              disabled={createWebhookMutation.isPending}
            >
              Cancel
            </Button>
            <Button 
              type="submit" 
              disabled={createWebhookMutation.isPending || !formData.url || formData.events.length === 0}
            >
              {createWebhookMutation.isPending ? 'Creating...' : 'Create Webhook'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

