/**
 * Webhooks Page
 * Main page for webhook management
 */
import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Plus, Webhook as WebhookIcon } from 'lucide-react';
import { WebhooksDataTable } from '@/components/WebhooksDataTable';
import { CreateWebhookDialog } from '@/components/CreateWebhookDialog';
import { EditWebhookDialog } from '@/components/EditWebhookDialog';
import type { Webhook } from '@/types/webhook';

export const Webhooks: React.FC = () => {
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [selectedWebhook, setSelectedWebhook] = useState<Webhook | null>(null);

  const handleEdit = (webhook: Webhook) => {
    setSelectedWebhook(webhook);
    setIsEditDialogOpen(true);
  };

  const handleEditDialogClose = () => {
    setIsEditDialogOpen(false);
    setSelectedWebhook(null);
  };

  return (
    <div className="flex-1 space-y-4 p-8 pt-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="flex items-center justify-between space-y-2"
      >
        <div>
          <h2 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <WebhookIcon className="h-8 w-8" />
            Webhooks
          </h2>
          <p className="text-muted-foreground mt-2">
            Manage webhook integrations for external systems. Get notified when products are created, updated, or deleted.
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button onClick={() => setIsCreateDialogOpen(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Create Webhook
          </Button>
        </div>
      </motion.div>

      {/* Info Cards */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="grid gap-4 md:grid-cols-4"
      >
        <div className="border rounded-lg p-4">
          <div className="flex items-center justify-between">
            <p className="text-sm font-medium text-muted-foreground">Available Events</p>
          </div>
          <p className="text-2xl font-bold mt-2">6</p>
          <p className="text-xs text-muted-foreground mt-1">
            Product & Import events
          </p>
        </div>
        <div className="border rounded-lg p-4">
          <div className="flex items-center justify-between">
            <p className="text-sm font-medium text-muted-foreground">Features</p>
          </div>
          <p className="text-2xl font-bold mt-2">✓</p>
          <p className="text-xs text-muted-foreground mt-1">
            HMAC, Retry, Logs
          </p>
        </div>
        <div className="border rounded-lg p-4">
          <div className="flex items-center justify-between">
            <p className="text-sm font-medium text-muted-foreground">Test Endpoint</p>
          </div>
          <p className="text-2xl font-bold mt-2">🧪</p>
          <p className="text-xs text-muted-foreground mt-1">
            Test with dummy payload
          </p>
        </div>
        <div className="border rounded-lg p-4">
          <div className="flex items-center justify-between">
            <p className="text-sm font-medium text-muted-foreground">Monitoring</p>
          </div>
          <p className="text-2xl font-bold mt-2">📊</p>
          <p className="text-xs text-muted-foreground mt-1">
            Execution logs & stats
          </p>
        </div>
      </motion.div>

      {/* Quick Start Guide */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="border rounded-lg p-4 bg-muted/30"
      >
        <h3 className="font-semibold mb-2">Quick Start Guide</h3>
        <div className="grid md:grid-cols-3 gap-4 text-sm">
          <div>
            <p className="font-medium mb-1">1. Create Webhook</p>
            <p className="text-muted-foreground text-xs">
              Click "Create Webhook" and configure your target URL and events
            </p>
          </div>
          <div>
            <p className="font-medium mb-1">2. Test It</p>
            <p className="text-muted-foreground text-xs">
              Use the test button (🧪) to send a dummy payload and verify connectivity
            </p>
          </div>
          <div>
            <p className="font-medium mb-1">3. Monitor</p>
            <p className="text-muted-foreground text-xs">
              Check execution logs and success/failure statistics for each webhook
            </p>
          </div>
        </div>
      </motion.div>

      {/* Data Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.3 }}
      >
        <WebhooksDataTable onEdit={handleEdit} />
      </motion.div>

      {/* Dialogs */}
      <CreateWebhookDialog
        isOpen={isCreateDialogOpen}
        onOpenChange={setIsCreateDialogOpen}
      />
      <EditWebhookDialog
        webhook={selectedWebhook}
        isOpen={isEditDialogOpen}
        onOpenChange={handleEditDialogClose}
      />
    </div>
  );
};

export default Webhooks;

