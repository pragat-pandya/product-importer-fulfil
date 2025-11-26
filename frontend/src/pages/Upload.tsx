import { motion } from 'framer-motion';
import { Upload as UploadIcon, FileUp, AlertCircle } from 'lucide-react';
import { ProductUpload } from '@/components/ProductUpload';

export function Upload() {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <div className="flex items-center gap-3">
          <div className="p-2 bg-primary/10 rounded-lg">
            <UploadIcon className="h-6 w-6 text-primary" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Upload Products</h1>
            <p className="text-muted-foreground">
              Import products from a CSV file
            </p>
          </div>
        </div>
      </motion.div>

      {/* Instructions Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.1 }}
        className="rounded-lg border bg-card p-6"
      >
        <div className="flex items-start gap-3">
          <FileUp className="h-5 w-5 text-primary mt-0.5" />
          <div className="space-y-2">
            <h2 className="font-semibold">CSV File Requirements</h2>
            <ul className="space-y-1 text-sm text-muted-foreground">
              <li>• <strong>Required columns:</strong> sku, name</li>
              <li>• <strong>Optional columns:</strong> description, active</li>
              <li>• <strong>SKU:</strong> Unique identifier (case-insensitive, max 100 characters)</li>
              <li>• <strong>Name:</strong> Product name (max 255 characters)</li>
              <li>• <strong>Active:</strong> Boolean value (true/false, 1/0, yes/no)</li>
              <li>• <strong>File size:</strong> Maximum 100MB</li>
            </ul>
          </div>
        </div>
      </motion.div>

      {/* Example CSV */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.2 }}
        className="rounded-lg border bg-card p-6"
      >
        <h2 className="font-semibold mb-3">Example CSV Format</h2>
        <div className="bg-gray-50 dark:bg-gray-950 rounded-md p-4 font-mono text-sm overflow-x-auto">
          <pre className="text-muted-foreground">
sku,name,description,active
PROD-001,Widget Pro,Premium widget with advanced features,true
PROD-002,Widget Lite,Basic widget for everyday use,true
PROD-003,Widget Max,Maximum performance widget,false
          </pre>
        </div>
      </motion.div>

      {/* Important Notes */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.3 }}
        className="rounded-lg border border-orange-200 dark:border-orange-900 bg-orange-50 dark:bg-orange-950/20 p-6"
      >
        <div className="flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-orange-600 dark:text-orange-400 mt-0.5" />
          <div className="space-y-2">
            <h2 className="font-semibold text-orange-900 dark:text-orange-100">Important Notes</h2>
            <ul className="space-y-1 text-sm text-orange-800 dark:text-orange-200">
              <li>• Duplicate SKUs (case-insensitive) will update existing products</li>
              <li>• Invalid rows will be skipped with detailed error reporting</li>
              <li>• Large files may take several minutes to process</li>
              <li>• You can track progress in real-time during import</li>
            </ul>
          </div>
        </div>
      </motion.div>

      {/* Upload Component */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.4 }}
      >
        <ProductUpload />
      </motion.div>
    </div>
  );
}

