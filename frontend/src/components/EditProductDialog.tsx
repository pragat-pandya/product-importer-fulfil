/**
 * Edit Product Dialog Component
 * Modal dialog for editing product details
 */
import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { useUpdateProduct } from '@/hooks/useProducts';
import type { Product, ProductUpdate } from '@/hooks/useProducts';

interface EditProductDialogProps {
  product: Product | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const EditProductDialog: React.FC<EditProductDialogProps> = ({
  product,
  open,
  onOpenChange,
}) => {
  const updateProduct = useUpdateProduct();
  
  const [formData, setFormData] = useState<ProductUpdate>({
    sku: '',
    name: '',
    description: '',
    active: true,
  });

  // Update form when product changes
  useEffect(() => {
    if (product) {
      setFormData({
        sku: product.sku,
        name: product.name,
        description: product.description || '',
        active: product.active,
      });
    }
  }, [product]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!product) return;

    // Only send fields that changed
    const updates: ProductUpdate = {};
    if (formData.sku !== product.sku) updates.sku = formData.sku;
    if (formData.name !== product.name) updates.name = formData.name;
    if (formData.description !== product.description) {
      updates.description = formData.description || null;
    }
    if (formData.active !== product.active) updates.active = formData.active;

    // If no changes, just close
    if (Object.keys(updates).length === 0) {
      onOpenChange(false);
      return;
    }

    try {
      await updateProduct.mutateAsync({
        id: product.id,
        data: updates,
      });
      onOpenChange(false);
    } catch (error) {
      // Error is handled by the hook
      console.error('Failed to update product:', error);
    }
  };

  const handleChange = (field: keyof ProductUpdate, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  if (!product) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>Edit Product</DialogTitle>
          <DialogDescription>
            Update product details. Only modified fields will be saved.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6 py-4">
          <div className="grid gap-4">
            {/* SKU */}
            <div className="grid gap-2">
              <Label htmlFor="sku">
                SKU <span className="text-destructive">*</span>
              </Label>
              <Input
                id="sku"
                value={formData.sku}
                onChange={(e) => handleChange('sku', e.target.value)}
                placeholder="e.g., WIDGET-001"
                required
                maxLength={100}
                className="font-mono"
              />
              <p className="text-xs text-muted-foreground">
                Stock Keeping Unit (1-100 characters, must be unique)
              </p>
            </div>

            {/* Name */}
            <div className="grid gap-2">
              <Label htmlFor="name">
                Name <span className="text-destructive">*</span>
              </Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => handleChange('name', e.target.value)}
                placeholder="e.g., Premium Widget"
                required
                maxLength={255}
              />
              <p className="text-xs text-muted-foreground">
                Product name (1-255 characters)
              </p>
            </div>

            {/* Description */}
            <div className="grid gap-2">
              <Label htmlFor="description">Description</Label>
              <textarea
                id="description"
                value={formData.description || ''}
                onChange={(e) => handleChange('description', e.target.value)}
                placeholder="Product description (optional)"
                className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                rows={3}
              />
            </div>

            {/* Active Status */}
            <div className="flex items-center justify-between rounded-lg border p-4">
              <div className="space-y-0.5">
                <Label>Status</Label>
                <p className="text-sm text-muted-foreground">
                  Set product as active or inactive
                </p>
              </div>
              <button
                type="button"
                role="switch"
                aria-checked={formData.active}
                onClick={() => handleChange('active', !formData.active)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 ${
                  formData.active ? 'bg-primary' : 'bg-input'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-background transition-transform ${
                    formData.active ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
              <Badge variant={formData.active ? 'default' : 'secondary'}>
                {formData.active ? 'Active' : 'Inactive'}
              </Badge>
            </div>

            {/* Metadata */}
            <div className="rounded-lg bg-muted p-4 space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Product ID:</span>
                <span className="font-mono">{product.id.split('-')[0]}...</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Created:</span>
                <span>{new Date(product.created_at).toLocaleString()}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Last Updated:</span>
                <span>{new Date(product.updated_at).toLocaleString()}</span>
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={updateProduct.isPending}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={updateProduct.isPending}>
              {updateProduct.isPending ? (
                <>
                  <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-primary-foreground border-t-transparent" />
                  Updating...
                </>
              ) : (
                'Save Changes'
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default EditProductDialog;

