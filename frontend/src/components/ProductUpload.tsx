import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, FileText, CheckCircle2, XCircle, Loader2 } from 'lucide-react';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import api from '@/lib/api';

interface UploadStatus {
  task_id: string;
  state: 'Pending' | 'Processing' | 'Completed' | 'Failed';
  progress_percent?: number;
  current?: number;
  total?: number;
  created?: number;
  updated?: number;
  errors?: number;
  message?: string;
  error?: string;
}

export function ProductUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [status, setStatus] = useState<UploadStatus | null>(null);
  const [pollingInterval, setPollingInterval] = useState<ReturnType<typeof setInterval> | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const selectedFile = acceptedFiles[0];
    if (selectedFile) {
      // Validate file type
      if (!selectedFile.name.endsWith('.csv')) {
        toast.error('Invalid file type', {
          description: 'Please upload a CSV file',
        });
        return;
      }

      // Validate file size (100MB max)
      const maxSize = 100 * 1024 * 1024;
      if (selectedFile.size > maxSize) {
        toast.error('File too large', {
          description: 'Maximum file size is 100MB',
        });
        return;
      }

      setFile(selectedFile);
      setStatus(null);
      toast.success('File selected', {
        description: selectedFile.name,
      });
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
    },
    multiple: false,
  });

  const pollStatus = async (taskId: string) => {
    try {
      const response = await api.get<UploadStatus>(`/products/upload/${taskId}/status`);
      const newStatus = response.data;
      setStatus(newStatus);

      // Stop polling if completed or failed
      if (newStatus.state === 'Completed' || newStatus.state === 'Failed') {
        if (pollingInterval) {
          clearInterval(pollingInterval);
          setPollingInterval(null);
        }
        setUploading(false);

        if (newStatus.state === 'Completed') {
          toast.success('Import completed successfully!', {
            description: `Created: ${newStatus.created}, Updated: ${newStatus.updated}, Errors: ${newStatus.errors}`,
          });
        } else {
          toast.error('Import failed', {
            description: newStatus.error || 'An error occurred during import',
          });
        }
      }
    } catch (error) {
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setStatus(null);

    try {
      // Upload file
      const formData = new FormData();
      formData.append('file', file);

      const response = await api.post<{
        task_id: string;
        status: string;
        message: string;
        filename: string;
      }>('/products/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const { task_id } = response.data;

      toast.info('Upload started', {
        description: 'Processing your CSV file...',
      });

      // Start polling status every 1 second
      const interval = setInterval(() => {
        pollStatus(task_id);
      }, 1000);

      setPollingInterval(interval);

      // Initial status check
      pollStatus(task_id);
    } catch (error: any) {
      setUploading(false);
      toast.error('Upload failed', {
        description: error.response?.data?.detail || error.message || 'Failed to upload file',
      });
    }
  };

  const handleReset = () => {
    if (pollingInterval) {
      clearInterval(pollingInterval);
      setPollingInterval(null);
    }
    setFile(null);
    setStatus(null);
    setUploading(false);
  };

  const getStatusBadgeVariant = () => {
    if (!status) return 'default';
    switch (status.state) {
      case 'Completed':
        return 'default';
      case 'Failed':
        return 'destructive';
      case 'Processing':
        return 'default';
      case 'Pending':
        return 'secondary';
      default:
        return 'default';
    }
  };

  const getStatusIcon = () => {
    if (!status) return null;
    switch (status.state) {
      case 'Completed':
        return <CheckCircle2 className="h-4 w-4 text-green-600" />;
      case 'Failed':
        return <XCircle className="h-4 w-4 text-red-600" />;
      case 'Processing':
      case 'Pending':
        return <Loader2 className="h-4 w-4 animate-spin" />;
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      {/* Drop Zone */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <div
          {...getRootProps()}
          className={`
            relative border-2 border-dashed rounded-lg p-12 text-center cursor-pointer
            transition-all duration-200
            ${
              isDragActive
                ? 'border-primary bg-primary/5'
                : 'border-gray-300 dark:border-gray-700 hover:border-primary hover:bg-gray-50 dark:hover:bg-gray-900'
            }
            ${file ? 'bg-gray-50 dark:bg-gray-900' : ''}
          `}
        >
          <input {...getInputProps()} />
          
          <div className="flex flex-col items-center gap-4">
            <motion.div
              animate={{
                scale: isDragActive ? 1.1 : 1,
                rotate: isDragActive ? 5 : 0,
              }}
              transition={{ duration: 0.2 }}
            >
              {file ? (
                <FileText className="h-16 w-16 text-primary" />
              ) : (
                <Upload className="h-16 w-16 text-gray-400" />
              )}
            </motion.div>

            <div>
              {file ? (
                <div>
                  <p className="text-lg font-medium">{file.name}</p>
                  <p className="text-sm text-muted-foreground">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              ) : (
                <div>
                  <p className="text-lg font-medium">
                    {isDragActive ? 'Drop the CSV file here' : 'Drag & drop a CSV file here'}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    or click to browse (Max 100MB)
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </motion.div>

      {/* Upload Button */}
      <AnimatePresence>
        {file && !status && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="flex gap-4"
          >
            <button
              onClick={handleUpload}
              disabled={uploading}
              className="flex-1 bg-primary text-primary-foreground px-6 py-3 rounded-lg font-medium hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {uploading ? 'Uploading...' : 'Upload & Process'}
            </button>
            <button
              onClick={handleReset}
              disabled={uploading}
              className="px-6 py-3 rounded-lg font-medium border hover:bg-gray-50 dark:hover:bg-gray-900 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Cancel
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Progress & Status */}
      <AnimatePresence>
        {status && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="rounded-lg border bg-card p-6 space-y-4"
          >
            {/* Status Header */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                {getStatusIcon()}
                <h3 className="font-semibold">Import Status</h3>
              </div>
              <Badge variant={getStatusBadgeVariant()}>{status.state}</Badge>
            </div>

            {/* Progress Bar */}
            {(status.state === 'Processing' || status.state === 'Pending') && (
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Progress</span>
                  <span className="font-medium">{status.progress_percent || 0}%</span>
                </div>
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                >
                  <Progress
                    value={status.progress_percent || 0}
                    className="h-2"
                  />
                </motion.div>
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>
                    {status.current || 0} / {status.total || 0} rows
                  </span>
                  <span>{status.message}</span>
                </div>
              </div>
            )}

            {/* Stats */}
            {status.state === 'Completed' && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="grid grid-cols-3 gap-4 pt-4 border-t"
              >
                <div className="text-center">
                  <p className="text-2xl font-bold text-green-600">{status.created || 0}</p>
                  <p className="text-sm text-muted-foreground">Created</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-blue-600">{status.updated || 0}</p>
                  <p className="text-sm text-muted-foreground">Updated</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-red-600">{status.errors || 0}</p>
                  <p className="text-sm text-muted-foreground">Errors</p>
                </div>
              </motion.div>
            )}

            {/* Error Message */}
            {status.state === 'Failed' && status.error && (
              <div className="p-4 bg-destructive/10 border border-destructive/20 rounded-md">
                <p className="text-sm text-destructive">{status.error}</p>
              </div>
            )}

            {/* Reset Button */}
            {(status.state === 'Completed' || status.state === 'Failed') && (
              <button
                onClick={handleReset}
                className="w-full px-6 py-3 rounded-lg font-medium border hover:bg-gray-50 dark:hover:bg-gray-900 transition-colors"
              >
                Upload Another File
              </button>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

