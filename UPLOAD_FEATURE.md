# Upload Feature Documentation

## Overview

The Upload feature provides a drag-and-drop interface for importing products from CSV files with real-time progress tracking and smooth animations.

## Features

✅ **Drag & Drop Upload** - Using react-dropzone  
✅ **Real-time Progress** - 1-second polling intervals  
✅ **Animated Progress Bar** - Framer Motion animations  
✅ **Status Badges** - Visual state indicators  
✅ **Toast Notifications** - Success/error messages using Sonner  
✅ **File Validation** - Type and size checks  
✅ **Detailed Stats** - Created/Updated/Errors breakdown  

## Components

### ProductUpload Component

**Location:** `src/components/ProductUpload.tsx`

**Features:**
- Drag-and-drop zone with hover effects
- File validation (CSV only, max 100MB)
- Upload to `/api/v1/products/upload`
- Status polling every 1 second
- Animated progress bar with percentage
- Stats display on completion
- Reset functionality

**State Management:**
```typescript
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
```

**Polling Logic:**
```typescript
// Start polling every 1 second
const interval = setInterval(() => {
  pollStatus(task_id);
}, 1000);

// Stop when Completed or Failed
if (status.state === 'Completed' || status.state === 'Failed') {
  clearInterval(interval);
}
```

### Upload Page

**Location:** `src/pages/Upload.tsx`

**Sections:**
1. **Header** - Title and description
2. **Requirements Card** - CSV format requirements
3. **Example CSV** - Code sample
4. **Important Notes** - Warnings and information
5. **Upload Component** - ProductUpload integration

## User Flow

### 1. Select File

**Methods:**
- Drag & drop CSV file
- Click to browse

**Validation:**
- ✅ File type must be `.csv`
- ✅ File size ≤ 100MB
- ❌ Invalid files show error toast

**Visual Feedback:**
- Hover effect on drag area
- File icon animation
- File name and size display

### 2. Upload File

**Action:** Click "Upload & Process" button

**Process:**
1. Create FormData with file
2. POST to `/api/v1/products/upload`
3. Receive `task_id` in response
4. Show info toast: "Upload started"
5. Start polling status endpoint

**API Call:**
```typescript
const formData = new FormData();
formData.append('file', file);
const response = await api.post('/products/upload', formData);
const { task_id } = response.data;
```

### 3. Track Progress

**Polling:** Every 1 second

**Status Endpoint:** `GET /api/v1/products/upload/{task_id}/status`

**States:**
- **Pending** → Gray badge, "Waiting to start"
- **Processing** → Blue badge, Progress bar, Row count
- **Completed** → Green badge, Stats display
- **Failed** → Red badge, Error message

**Progress Display:**
```
[=====>            ] 45%
2,500 / 5,000 rows
```

### 4. View Results

**On Success (Completed):**
- ✅ Success toast with stats
- 📊 Stats grid:
  - **Created** (green)
  - **Updated** (blue)
  - **Errors** (red)
- 🔄 "Upload Another File" button

**On Failure (Failed):**
- ❌ Error toast with message
- 📝 Error details display
- 🔄 "Upload Another File" button

## Animations

### Framer Motion

**Drop Zone:**
```typescript
<motion.div
  animate={{
    scale: isDragActive ? 1.1 : 1,
    rotate: isDragActive ? 5 : 0,
  }}
>
  <Upload icon />
</motion.div>
```

**Progress Bar:**
```typescript
<motion.div
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
>
  <Progress value={percent} />
</motion.div>
```

**Stats Display:**
```typescript
<motion.div
  initial={{ opacity: 0, scale: 0.95 }}
  animate={{ opacity: 1, scale: 1 }}
>
  Stats grid
</motion.div>
```

**Component Mounting:**
```typescript
<AnimatePresence>
  {condition && (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
    >
      Content
    </motion.div>
  )}
</AnimatePresence>
```

## shadcn/ui Components

### Progress

**Usage:**
```tsx
import { Progress } from '@/components/ui/progress';

<Progress value={75} className="h-2" />
```

**Features:**
- Radix UI primitive
- Smooth transitions
- Customizable height
- Percentage-based

### Badge

**Usage:**
```tsx
import { Badge } from '@/components/ui/badge';

<Badge variant="default">Completed</Badge>
<Badge variant="destructive">Failed</Badge>
<Badge variant="secondary">Pending</Badge>
```

**Variants:**
- `default` - Primary color
- `secondary` - Muted color
- `destructive` - Error/danger color
- `outline` - Outlined style

### Sonner (Toast)

**Usage:**
```tsx
import { toast } from 'sonner';

// Success
toast.success('Upload complete!', {
  description: 'Created: 100, Updated: 50',
});

// Error
toast.error('Upload failed', {
  description: 'Error message here',
});

// Info
toast.info('Processing...', {
  description: 'This may take a few minutes',
});
```

**Setup in App.tsx:**
```tsx
import { Toaster } from '@/components/ui/sonner';

<App>
  {/* routes */}
  <Toaster />
</App>
```

## CSV Format

### Required Columns
- `sku` - Unique identifier (max 100 chars)
- `name` - Product name (max 255 chars)

### Optional Columns
- `description` - Product description (text)
- `active` - Boolean (true/false, 1/0, yes/no)

### Example CSV

```csv
sku,name,description,active
PROD-001,Widget Pro,Premium widget,true
PROD-002,Widget Lite,Basic widget,true
PROD-003,Widget Max,Max widget,false
```

## Error Handling

### File Validation Errors

**Invalid File Type:**
```
❌ "Invalid file type"
   "Please upload a CSV file"
```

**File Too Large:**
```
❌ "File too large"
   "Maximum file size is 100MB"
```

### Upload Errors

**Network Error:**
```typescript
catch (error: any) {
  toast.error('Upload failed', {
    description: error.response?.data?.detail || error.message,
  });
}
```

**API Error:**
- 400: Invalid file or format
- 500: Server error
- 503: Service unavailable

### Status Errors

**Polling Error:**
```typescript
// Silent failure - continues polling
catch (error) {
  console.error('Error polling status:', error);
}
```

**Task Failed:**
```
❌ "Import failed"
   Error message from API
```

## Performance

### Optimization
- ✅ 1-second polling (not too frequent)
- ✅ Automatic cleanup on unmount
- ✅ Single file upload (no batching overhead)
- ✅ Progress updates reduce unnecessary re-renders

### Memory Management
```typescript
// Cleanup polling interval
if (pollingInterval) {
  clearInterval(pollingInterval);
  setPollingInterval(null);
}
```

### Bundle Size
- react-dropzone: ~15KB
- @radix-ui/react-progress: ~10KB
- sonner: ~12KB
- Total additions: ~37KB (gzipped)

## Dependencies

```json
{
  "react-dropzone": "^14.2.10",
  "@radix-ui/react-progress": "^1.0.3",
  "sonner": "^1.2.0"
}
```

## API Integration

### Upload Endpoint

**POST** `/api/v1/products/upload`

**Request:**
```typescript
Content-Type: multipart/form-data

{
  file: File (CSV)
}
```

**Response:**
```json
{
  "task_id": "uuid",
  "status": "submitted",
  "message": "File uploaded successfully",
  "filename": "products.csv"
}
```

### Status Endpoint

**GET** `/api/v1/products/upload/{task_id}/status`

**Response:**
```json
{
  "task_id": "uuid",
  "state": "Processing",
  "progress_percent": 45,
  "current": 2500,
  "total": 5000,
  "created": 1200,
  "updated": 1300,
  "errors": 0,
  "message": "Processing CSV file..."
}
```

## Testing

### Manual Testing

1. **Navigate to Upload page:**
   - http://localhost:5173/upload

2. **Test drag & drop:**
   - Drag CSV file over zone
   - Verify hover effect
   - Drop file
   - Verify file name displayed

3. **Test file validation:**
   - Try non-CSV file → Error toast
   - Try large file (>100MB) → Error toast
   - Try valid CSV → Success toast

4. **Test upload:**
   - Click "Upload & Process"
   - Verify info toast appears
   - Watch progress bar animate
   - Verify percentage updates
   - Wait for completion

5. **Test completion:**
   - Verify success toast
   - Check stats display
   - Click "Upload Another File"
   - Verify reset

### Test CSV

```csv
sku,name,description,active
TEST-001,Test Product 1,First test,true
TEST-002,Test Product 2,Second test,true
TEST-003,Test Product 3,Third test,false
```

## Troubleshooting

### Progress Not Updating

**Issue:** Progress bar stuck at 0%

**Solutions:**
1. Check backend is running
2. Verify proxy configuration
3. Check browser console for errors
4. Verify task_id is valid

### Polling Not Stopping

**Issue:** Continues polling after completion

**Solutions:**
1. Check status.state condition
2. Verify interval cleanup
3. Check for memory leaks

### File Not Uploading

**Issue:** Upload button does nothing

**Solutions:**
1. Check file is selected
2. Verify API endpoint
3. Check browser network tab
4. Verify backend is reachable

### Toast Not Showing

**Issue:** No notifications appear

**Solutions:**
1. Verify `<Toaster />` in App.tsx
2. Check sonner import
3. Verify toast function calls
4. Check browser console

## Future Enhancements

### Planned Features
- [ ] Multiple file upload (batch)
- [ ] Upload history
- [ ] Download error report
- [ ] Pause/Resume upload
- [ ] CSV preview before upload
- [ ] Template download
- [ ] Drag & drop reordering
- [ ] Upload queue management

### UX Improvements
- [ ] Estimated time remaining
- [ ] Speed indicator (rows/sec)
- [ ] Detailed progress (validation, processing, saving)
- [ ] Upload tips/guidance
- [ ] Keyboard shortcuts
- [ ] Dark mode specific styles

### Performance
- [ ] Worker thread for large files
- [ ] Streaming upload
- [ ] Compression before upload
- [ ] Smart polling (exponential backoff)

## Code Examples

### Basic Usage

```tsx
import { ProductUpload } from '@/components/ProductUpload';

function MyPage() {
  return (
    <div>
      <h1>Upload Products</h1>
      <ProductUpload />
    </div>
  );
}
```

### Custom Styling

```tsx
<ProductUpload />

// In your CSS/Tailwind:
.dropzone {
  @apply border-2 border-dashed rounded-lg;
}
```

### Event Handling

```tsx
// Component handles all events internally:
// - onDrop: File selection
// - handleUpload: Upload initiation
// - pollStatus: Status updates
// - handleReset: State reset
```

## Resources

- [react-dropzone Documentation](https://react-dropzone.js.org/)
- [Radix UI Progress](https://www.radix-ui.com/primitives/docs/components/progress)
- [Sonner Toast](https://sonner.emilkowal.ski/)
- [Framer Motion](https://www.framer.com/motion/)
- [shadcn/ui](https://ui.shadcn.com/)

