/**
 * WebhooksDataTable Component
 * Displays webhooks in a data table with Test button and animations
 */
import React, { useState, useMemo } from 'react';
import type {
  ColumnDef,
  PaginationState,
} from '@tanstack/react-table';
import {
  flexRender,
  getCoreRowModel,
  useReactTable,
} from '@tanstack/react-table';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Edit, 
  Trash2, 
  ChevronLeft, 
  ChevronRight, 
  ChevronsLeft, 
  ChevronsRight,
  FlaskConical,
  Loader2,
  CheckCircle2,
  XCircle,
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import type { Webhook, WebhookTestResponse } from '@/types/webhook';
import { useDeleteWebhook, useWebhooks, useTestWebhook } from '@/hooks/useWebhooks';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from '@/components/ui/alert-dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { cn } from '@/lib/utils';
import { TableSkeleton } from '@/components/TableSkeleton';

interface WebhooksDataTableProps {
  initialLimit?: number;
  onEdit: (webhook: Webhook) => void;
}

interface TestResult {
  webhookId: string;
  result: WebhookTestResponse;
  timestamp: number;
}

export const WebhooksDataTable: React.FC<WebhooksDataTableProps> = ({ 
  initialLimit = 10,
  onEdit,
}) => {
  const [pagination, setPagination] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: initialLimit,
  });
  const [activeFilter, setActiveFilter] = useState<boolean | undefined>(undefined);
  const [testResults, setTestResults] = useState<Map<string, TestResult>>(new Map());

  const { data, isLoading, isError, error } = useWebhooks({
    limit: pagination.pageSize,
    offset: pagination.pageIndex * pagination.pageSize,
    is_active: activeFilter,
  });

  const deleteWebhookMutation = useDeleteWebhook();
  const testWebhookMutation = useTestWebhook();

  const webhooks = data?.items || [];
  const totalWebhooks = data?.total || 0;
  const pageCount = data ? Math.ceil(data.total / pagination.pageSize) : 0;

  const handleDelete = async (webhookId: string) => {
    await deleteWebhookMutation.mutateAsync(webhookId);
  };

  const handleTest = async (webhook: Webhook) => {
    const result = await testWebhookMutation.mutateAsync({
      id: webhook.id,
      request: {
        event: webhook.events[0] || 'product.created',
        payload: {
          test: true,
          message: 'This is a test webhook delivery',
          timestamp: new Date().toISOString(),
        },
      },
    });

    // Store test result with timestamp
    setTestResults(prev => new Map(prev).set(webhook.id, {
      webhookId: webhook.id,
      result,
      timestamp: Date.now(),
    }));

    // Auto-clear result after 5 seconds
    setTimeout(() => {
      setTestResults(prev => {
        const next = new Map(prev);
        next.delete(webhook.id);
        return next;
      });
    }, 5000);
  };

  const TestResultBadge: React.FC<{ result: TestResult }> = ({ result }) => {
    const isSuccess = result.result.success;
    
    return (
      <AnimatePresence>
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.8 }}
          transition={{ duration: 0.3, type: 'spring' }}
          className="flex items-center gap-2"
        >
          {isSuccess ? (
            <motion.div
              initial={{ rotate: 0 }}
              animate={{ rotate: 360 }}
              transition={{ duration: 0.5 }}
            >
              <CheckCircle2 className="h-4 w-4 text-green-500" />
            </motion.div>
          ) : (
            <motion.div
              animate={{ x: [-2, 2, -2, 2, 0] }}
              transition={{ duration: 0.5 }}
            >
              <XCircle className="h-4 w-4 text-red-500" />
            </motion.div>
          )}
          <Badge 
            variant={isSuccess ? 'default' : 'destructive'}
            className={cn("animate-pulse", isSuccess && "bg-green-500 hover:bg-green-600")}
          >
            {result.result.status_code || 'Failed'}
          </Badge>
          {result.result.response_time_ms && (
            <span className="text-xs text-muted-foreground">
              {result.result.response_time_ms}ms
            </span>
          )}
        </motion.div>
      </AnimatePresence>
    );
  };

  const columns: ColumnDef<Webhook>[] = useMemo(
    () => [
      {
        accessorKey: 'url',
        header: 'URL',
        cell: ({ row }) => (
          <div className="max-w-[300px] truncate font-mono text-sm">
            {row.original.url}
          </div>
        ),
      },
      {
        accessorKey: 'events',
        header: 'Events',
        cell: ({ row }) => (
          <div className="flex flex-wrap gap-1">
            {row.original.events.slice(0, 2).map((event) => (
              <Badge key={event} variant="outline" className="text-xs">
                {event}
              </Badge>
            ))}
            {row.original.events.length > 2 && (
              <Badge variant="outline" className="text-xs">
                +{row.original.events.length - 2}
              </Badge>
            )}
          </div>
        ),
      },
      {
        accessorKey: 'is_active',
        header: 'Status',
        cell: ({ row }) => (
          <Badge variant={row.original.is_active ? 'default' : 'secondary'} className={cn(row.original.is_active && "bg-green-500 hover:bg-green-600")}>
            {row.original.is_active ? 'Active' : 'Inactive'}
          </Badge>
        ),
      },
      {
        accessorKey: 'stats',
        header: 'Stats',
        cell: ({ row }) => (
          <div className="flex items-center gap-2 text-sm">
            <span className="text-green-600 font-medium">
              ✓ {row.original.success_count}
            </span>
            <span className="text-red-600 font-medium">
              ✗ {row.original.failure_count}
            </span>
          </div>
        ),
      },
      {
        accessorKey: 'created_at',
        header: 'Created',
        cell: ({ row }) => (
          <span className="text-sm">
            {new Date(row.original.created_at).toLocaleDateString()}
          </span>
        ),
      },
      {
        id: 'actions',
        header: 'Actions',
        cell: ({ row }) => {
          const testResult = testResults.get(row.original.id);
          const isTesting = testWebhookMutation.isPending && 
            testWebhookMutation.variables?.id === row.original.id;

          return (
            <div className="flex items-center space-x-2">
              {/* Test Button */}
              <Button
                variant="outline"
                size="icon"
                onClick={() => handleTest(row.original)}
                disabled={isTesting}
                className={cn(
                  "transition-all",
                  testResult?.result.success && "border-green-500",
                  testResult?.result.success === false && "border-red-500"
                )}
              >
                {isTesting ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <FlaskConical className="h-4 w-4" />
                )}
              </Button>

              {/* Edit Button */}
              <Button 
                variant="outline" 
                size="icon" 
                onClick={() => onEdit(row.original)}
              >
                <Edit className="h-4 w-4" />
              </Button>

              {/* Delete Button */}
              <AlertDialog>
                <AlertDialogTrigger asChild>
                  <Button variant="destructive" size="icon">
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </AlertDialogTrigger>
                <AlertDialogContent>
                  <AlertDialogHeader>
                    <AlertDialogTitle>Delete Webhook?</AlertDialogTitle>
                    <AlertDialogDescription>
                      This will permanently delete the webhook{' '}
                      <span className="font-semibold">{row.original.url}</span>.
                      This action cannot be undone.
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogCancel>Cancel</AlertDialogCancel>
                    <AlertDialogAction onClick={() => handleDelete(row.original.id)}>
                      Delete
                    </AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>

              {/* Test Result Display */}
              {testResult && (
                <div className="ml-2">
                  <TestResultBadge result={testResult} />
                </div>
              )}
            </div>
          );
        },
      },
    ],
    [testResults, testWebhookMutation, onEdit]
  );

  const table = useReactTable({
    data: webhooks,
    columns,
    pageCount: pageCount,
    state: {
      pagination,
    },
    onPaginationChange: setPagination,
    getCoreRowModel: getCoreRowModel(),
    manualPagination: true,
  });

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <div className="h-9 w-[180px] bg-muted animate-pulse rounded-md" />
        </div>
        <TableSkeleton rows={5} columns={6} />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="text-center py-8 text-destructive">
        Error: {error?.message || 'Failed to load webhooks'}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex items-center gap-2">
        <Select
          value={activeFilter === true ? 'active' : activeFilter === false ? 'inactive' : 'all'}
          onValueChange={(value: string) => 
            setActiveFilter(value === 'active' ? true : value === 'inactive' ? false : undefined)
          }
        >
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Filter by Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Webhooks</SelectItem>
            <SelectItem value="active">Active Only</SelectItem>
            <SelectItem value="inactive">Inactive Only</SelectItem>
          </SelectContent>
        </Select>
        {activeFilter !== undefined && (
          <Button 
            variant="outline" 
            onClick={() => {
              setActiveFilter(undefined);
              setPagination((prev) => ({ ...prev, pageIndex: 0 }));
            }}
          >
            Clear Filter
          </Button>
        )}
      </div>

      {/* Table */}
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <TableHead key={header.id}>
                    {header.isPlaceholder
                      ? null
                      : flexRender(header.column.columnDef.header, header.getContext())}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow key={row.id} data-state={row.getIsSelected() && 'selected'}>
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={columns.length} className="h-24 text-center">
                  No webhooks found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-end space-x-2 py-4">
        <div className="flex-1 text-sm text-muted-foreground">
          Showing {Math.min(pagination.pageIndex * pagination.pageSize + 1, totalWebhooks)} to{' '}
          {Math.min((pagination.pageIndex + 1) * pagination.pageSize, totalWebhooks)} of{' '}
          {totalWebhooks} webhooks.
        </div>
        <div className="flex items-center space-x-2">
          <Select
            value={String(pagination.pageSize)}
            onValueChange={(value: string) => {
              table.setPageSize(Number(value));
            }}
          >
            <SelectTrigger className="h-8 w-[70px]">
              <SelectValue placeholder={pagination.pageSize} />
            </SelectTrigger>
            <SelectContent>
              {[10, 20, 50, 100].map((pageSize) => (
                <SelectItem key={pageSize} value={String(pageSize)}>
                  {pageSize}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button
            variant="outline"
            className="h-8 w-8 p-0"
            onClick={() => table.setPageIndex(0)}
            disabled={!table.getCanPreviousPage()}
          >
            <ChevronsLeft className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            className="h-8 w-8 p-0"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            className="h-8 w-8 p-0"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            className="h-8 w-8 p-0"
            onClick={() => table.setPageIndex(table.getPageCount() - 1)}
            disabled={!table.getCanNextPage()}
          >
            <ChevronsRight className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
};

