/**
 * Products Page Component
 * Main dashboard for product management with DataTable, filters, and actions
 */
import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Search, Package, Trash2, AlertTriangle } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';
import ProductsDataTable from '@/components/ProductsDataTable';
import EditProductDialog from '@/components/EditProductDialog';
import {
  useProducts,
  useDeleteProduct,
  useBulkDeleteProducts,
  useBulkDeleteStatus,
} from '@/hooks/useProducts';
import type { Product } from '@/hooks/useProducts';
import { toast } from 'sonner';

const Products: React.FC = () => {
  // State
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(20);
  const [skuFilter, setSkuFilter] = useState('');
  const [nameFilter, setNameFilter] = useState('');
  const [activeFilter, setActiveFilter] = useState<boolean | undefined>(undefined);
  const [editProduct, setEditProduct] = useState<Product | null>(null);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [bulkDeleteConfirmOpen, setbulkDeleteConfirmOpen] = useState(false);
  const [bulkDeleteDoubleConfirmOpen, setBulkDeleteDoubleConfirmOpen] = useState(false);
  const [bulkDeleteTaskId, setBulkDeleteTaskId] = useState<string | null>(null);

  // Debounced filters (for search inputs)
  const [debouncedSkuFilter, setDebouncedSkuFilter] = useState(skuFilter);
  const [debouncedNameFilter, setDebouncedNameFilter] = useState(nameFilter);

  // Debounce search inputs
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSkuFilter(skuFilter);
    }, 300);
    return () => clearTimeout(timer);
  }, [skuFilter]);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedNameFilter(nameFilter);
    }, 300);
    return () => clearTimeout(timer);
  }, [nameFilter]);

  // API Hooks
  const {
    data: productsData,
    isLoading,
    refetch,
  } = useProducts({
    limit: pageSize,
    offset: page * pageSize,
    sku: debouncedSkuFilter || undefined,
    name: debouncedNameFilter || undefined,
    active: activeFilter,
  });

  const deleteProduct = useDeleteProduct();
  const bulkDeleteProducts = useBulkDeleteProducts();

  // Monitor bulk delete status
  const { data: bulkDeleteStatus } = useBulkDeleteStatus(bulkDeleteTaskId);

  // Handle bulk delete status changes
  useEffect(() => {
    if (bulkDeleteStatus) {
      if (bulkDeleteStatus.status === 'SUCCESS') {
        toast.success('Bulk delete completed!', {
          description: `Deleted ${bulkDeleteStatus.deleted_count} products`,
        });
        setBulkDeleteTaskId(null);
        refetch(); // Refresh the product list
      } else if (bulkDeleteStatus.status === 'FAILURE') {
        toast.error('Bulk delete failed');
        setBulkDeleteTaskId(null);
      }
    }
  }, [bulkDeleteStatus, refetch]);

  const handleEdit = (product: Product) => {
    setEditProduct(product);
    setEditDialogOpen(true);
  };

  const handleDelete = (id: string) => {
    deleteProduct.mutate(id);
  };

  const handleBulkDelete = async () => {
    setBulkDeleteDoubleConfirmOpen(false);
    setbulkDeleteConfirmOpen(false);
    
    try {
      const result = await bulkDeleteProducts.mutateAsync();
      setBulkDeleteTaskId(result.task_id);
    } catch (error) {
      // Error handled by hook
    }
  };

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
  };

  const handlePageSizeChange = (newPageSize: number) => {
    setPageSize(newPageSize);
    setPage(0); // Reset to first page
  };

  const handleClearFilters = () => {
    setSkuFilter('');
    setNameFilter('');
    setActiveFilter(undefined);
    setPage(0);
  };

  const hasActiveFilters = skuFilter || nameFilter || activeFilter !== undefined;

  return (
    <div className="flex-1 space-y-6 p-8 pt-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="flex items-center justify-between"
      >
        <div>
          <h2 className="text-3xl font-bold tracking-tight flex items-center gap-2">
            <Package className="h-8 w-8" />
            Products
          </h2>
          <p className="text-muted-foreground mt-1">
            Manage your product catalog with advanced filtering and bulk operations
          </p>
        </div>

        {/* Bulk Delete Button */}
        <AlertDialog
          open={bulkDeleteConfirmOpen}
          onOpenChange={setbulkDeleteConfirmOpen}
        >
          <AlertDialogTrigger asChild>
            <Button
              variant="destructive"
              className="gap-2"
              disabled={!productsData?.total || bulkDeleteTaskId !== null}
            >
              <Trash2 className="h-4 w-4" />
              Delete All Products
            </Button>
          </AlertDialogTrigger>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle className="flex items-center gap-2 text-destructive">
                <AlertTriangle className="h-5 w-5" />
                Bulk Delete Warning
              </AlertDialogTitle>
              <AlertDialogDescription className="space-y-2">
                <p>
                  You are about to delete <strong>ALL {productsData?.total || 0} products</strong> in
                  the database.
                </p>
                <p className="text-destructive font-semibold">
                  This action CANNOT be undone!
                </p>
                <p>Are you absolutely sure you want to proceed?</p>
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Cancel</AlertDialogCancel>
              <AlertDialogAction
                onClick={(e) => {
                  e.preventDefault();
                  setbulkDeleteConfirmOpen(false);
                  setBulkDeleteDoubleConfirmOpen(true);
                }}
                className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              >
                Continue
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>

        {/* Double Confirmation Dialog */}
        <AlertDialog
          open={bulkDeleteDoubleConfirmOpen}
          onOpenChange={setBulkDeleteDoubleConfirmOpen}
        >
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle className="flex items-center gap-2 text-destructive">
                <AlertTriangle className="h-5 w-5" />
                Final Confirmation Required
              </AlertDialogTitle>
              <AlertDialogDescription className="space-y-3">
                <p className="text-lg font-semibold">
                  This is your LAST CHANCE to cancel!
                </p>
                <div className="rounded-lg bg-destructive/10 p-4 space-y-2">
                  <p className="font-medium">You are about to:</p>
                  <ul className="list-disc list-inside space-y-1 text-sm">
                    <li>Delete ALL {productsData?.total || 0} products</li>
                    <li>Remove all product data permanently</li>
                    <li>This process cannot be reversed</li>
                  </ul>
                </div>
                <p className="text-sm">
                  The deletion will run as a background task and may take a few seconds to complete.
                </p>
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Cancel</AlertDialogCancel>
              <AlertDialogAction
                onClick={handleBulkDelete}
                className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              >
                Yes, Delete Everything
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </motion.div>

      {/* Filters */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.1 }}
        className="rounded-lg border bg-card p-4"
      >
        <div className="grid gap-4 md:grid-cols-3 lg:grid-cols-4">
          {/* SKU Filter */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Search by SKU</label>
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="e.g., WIDGET-001"
                value={skuFilter}
                onChange={(e) => setSkuFilter(e.target.value)}
                className="pl-9"
              />
            </div>
          </div>

          {/* Name Filter */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Search by Name</label>
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="e.g., Premium Widget"
                value={nameFilter}
                onChange={(e) => setNameFilter(e.target.value)}
                className="pl-9"
              />
            </div>
          </div>

          {/* Status Filter */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Filter by Status</label>
            <select
              value={activeFilter === undefined ? 'all' : activeFilter ? 'active' : 'inactive'}
              onChange={(e) => {
                const value = e.target.value;
                setActiveFilter(
                  value === 'all' ? undefined : value === 'active' ? true : false
                );
                setPage(0);
              }}
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              <option value="all">All Products</option>
              <option value="active">Active Only</option>
              <option value="inactive">Inactive Only</option>
            </select>
          </div>

          {/* Clear Filters */}
          <div className="flex items-end">
            <Button
              variant="outline"
              onClick={handleClearFilters}
              disabled={!hasActiveFilters}
              className="w-full"
            >
              Clear Filters
            </Button>
          </div>
        </div>

        {/* Active Filters Display */}
        {hasActiveFilters && (
          <div className="mt-4 flex flex-wrap gap-2">
            {skuFilter && (
              <Badge variant="secondary">
                SKU: {skuFilter}
              </Badge>
            )}
            {nameFilter && (
              <Badge variant="secondary">
                Name: {nameFilter}
              </Badge>
            )}
            {activeFilter !== undefined && (
              <Badge variant="secondary">
                Status: {activeFilter ? 'Active' : 'Inactive'}
              </Badge>
            )}
          </div>
        )}
      </motion.div>

      {/* Stats */}
      {productsData && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.2 }}
          className="flex gap-4"
        >
          <div className="rounded-lg border bg-card p-4 flex-1">
            <div className="text-2xl font-bold">{productsData.total}</div>
            <p className="text-xs text-muted-foreground">Total Products</p>
          </div>
          <div className="rounded-lg border bg-card p-4 flex-1">
            <div className="text-2xl font-bold">{productsData.items.length}</div>
            <p className="text-xs text-muted-foreground">Showing on Page</p>
          </div>
        </motion.div>
      )}

      {/* Bulk Delete Status */}
      {bulkDeleteStatus && bulkDeleteStatus.status === 'PROGRESS' && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-lg border bg-destructive/10 p-4"
        >
          <div className="flex items-center gap-3">
            <div className="h-4 w-4 animate-spin rounded-full border-2 border-destructive border-t-transparent" />
            <div className="flex-1">
              <p className="font-medium">Bulk Delete in Progress</p>
              <p className="text-sm text-muted-foreground">{bulkDeleteStatus.message}</p>
            </div>
            <Badge variant="destructive">{bulkDeleteStatus.percent}%</Badge>
          </div>
        </motion.div>
      )}

      {/* Data Table */}
      {productsData && (
        <ProductsDataTable
          products={productsData.items}
          total={productsData.total}
          limit={pageSize}
          offset={page * pageSize}
          onPageChange={handlePageChange}
          onPageSizeChange={handlePageSizeChange}
          onEdit={handleEdit}
          onDelete={handleDelete}
          isLoading={isLoading}
        />
      )}

      {/* Edit Dialog */}
      <EditProductDialog
        product={editProduct}
        open={editDialogOpen}
        onOpenChange={setEditDialogOpen}
      />
    </div>
  );
};

export default Products;

