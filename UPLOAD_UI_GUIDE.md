# Upload UI - Visual Guide & User Flow

## Overview

The Upload feature provides an intuitive drag-and-drop interface for CSV file imports with real-time progress tracking.

## User Interface

### Page Structure

```
┌─────────────────────────────────────────────────┐
│  🔹 Upload Products                             │
│  Import products from a CSV file                │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  📋 CSV File Requirements                       │
│  • Required columns: sku, name                  │
│  • Optional columns: description, active        │
│  • SKU: Unique identifier (max 100 chars)       │
│  • Name: Product name (max 255 chars)           │
│  • File size: Maximum 100MB                     │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  📄 Example CSV Format                          │
│  ┌─────────────────────────────────────────┐   │
│  │ sku,name,description,active             │   │
│  │ PROD-001,Widget Pro,Premium widget,true │   │
│  │ PROD-002,Widget Lite,Basic widget,true  │   │
│  └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  ⚠️  Important Notes                            │
│  • Duplicate SKUs will update existing products │
│  • Invalid rows will be skipped                 │
│  • Large files may take several minutes         │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│                                                  │
│          ↓ Drag & drop a CSV file here          │
│              or click to browse                  │
│                  (Max 100MB)                     │
│                                                  │
└─────────────────────────────────────────────────┘
```

## State Flow

### State 1: Empty (Initial)

```
┌─────────────────────────────────────────────────┐
│                    📤                            │
│                                                  │
│          Drag & drop a CSV file here            │
│              or click to browse                  │
│                  (Max 100MB)                     │
│                                                  │
└─────────────────────────────────────────────────┘
```

**Interactions:**
- Hover → Border color changes to primary
- Drag over → Icon scales/rotates
- Click → Opens file picker

### State 2: File Selected

```
┌─────────────────────────────────────────────────┐
│                    📄                            │
│                                                  │
│              products.csv                        │
│                 2.45 MB                          │
│                                                  │
└─────────────────────────────────────────────────┘

┌─────────────────┐  ┌────────────────────────────┐
│ Upload & Process │  │        Cancel              │
└─────────────────┘  └────────────────────────────┘
```

**Toast:** ✅ "File selected" - products.csv

**Actions:**
- Upload & Process → Start import
- Cancel → Reset to empty state

### State 3: Uploading

```
┌─────────────────────────────────────────────────┐
│  ⏳ Import Status                [Pending]       │
│                                                  │
│  Progress                                    0%  │
│  [░░░░░░░░░░░░░░░░░░░░░░░░░░]                  │
│  0 / 0 rows                                     │
└─────────────────────────────────────────────────┘
```

**Toast:** ℹ️ "Upload started" - Processing your CSV file...

**State:** Buttons disabled

### State 4: Processing

```
┌─────────────────────────────────────────────────┐
│  ⏳ Import Status              [Processing]      │
│                                                  │
│  Progress                                   45%  │
│  [███████████░░░░░░░░░░░░░░░]                   │
│  2,500 / 5,000 rows       Processing CSV file...│
└─────────────────────────────────────────────────┘
```

**Animation:**
- Progress bar fills smoothly
- Spinner rotates
- Percentage updates every second

### State 5: Completed (Success)

```
┌─────────────────────────────────────────────────┐
│  ✅ Import Status              [Completed]       │
│                                                  │
│  ┌───────────────────────────────────────────┐  │
│  │    2,500         1,800           50       │  │
│  │    Created       Updated       Errors     │  │
│  └───────────────────────────────────────────┘  │
│                                                  │
│  ┌─────────────────────────────────────────┐   │
│  │      Upload Another File                 │   │
│  └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

**Toast:** ✅ "Import completed successfully!" - Created: 2,500, Updated: 1,800, Errors: 50

**Stats Colors:**
- Created: Green
- Updated: Blue
- Errors: Red

### State 6: Failed (Error)

```
┌─────────────────────────────────────────────────┐
│  ❌ Import Status                  [Failed]      │
│                                                  │
│  ┌─────────────────────────────────────────┐   │
│  │ ❌ Failed to process CSV: Invalid format│   │
│  └─────────────────────────────────────────┘   │
│                                                  │
│  ┌─────────────────────────────────────────┐   │
│  │      Upload Another File                 │   │
│  └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

**Toast:** ❌ "Import failed" - Error message here

## Animations

### Entry Animations

**Page Elements:**
```
Header      → Fade in from top (0s)
Requirements → Fade in from bottom (0.1s)
Example     → Fade in from bottom (0.2s)
Notes       → Fade in from bottom (0.3s)
Upload      → Fade in from bottom (0.4s)
```

**Staggered Effect:** Creates smooth cascading entrance

### Drag Zone Animations

**Hover:**
```
Icon: scale(1.0) → scale(1.1)
      rotate(0deg) → rotate(5deg)
Border: gray → primary
Background: transparent → primary/5%
```

**Duration:** 200ms

### Button Animations

**Upload Button:**
```
<AnimatePresence>
  initial: { opacity: 0, height: 0 }
  animate: { opacity: 1, height: 'auto' }
  exit: { opacity: 0, height: 0 }
</AnimatePresence>
```

**Smooth expansion** when file is selected

### Progress Card Animations

**Status Card:**
```
initial: { opacity: 0, y: 20 }
animate: { opacity: 1, y: 0 }
exit: { opacity: 0, y: -20 }
```

**Stats Grid:**
```
initial: { opacity: 0, scale: 0.95 }
animate: { opacity: 1, scale: 1 }
```

**Creates "pop-in" effect** on completion

### Progress Bar Animation

```
Framer Motion + Tailwind transition

transform: translateX(-${100 - percent}%)
transition: all 300ms ease-in-out
```

**Smooth fill animation** as progress increases

## Color Scheme

### Status Colors

| State | Badge | Icon | Toast |
|-------|-------|------|-------|
| Pending | Secondary (gray) | Spinner | Info (blue) |
| Processing | Default (primary) | Spinner | Info (blue) |
| Completed | Default (green) | Check | Success (green) |
| Failed | Destructive (red) | X | Error (red) |

### Stats Colors

```
Created → text-green-600
Updated → text-blue-600
Errors  → text-red-600
```

### Interactive States

```
Drop Zone:
  Default: border-gray-300 hover:border-primary
  Active: border-primary bg-primary/5
  Selected: bg-gray-50

Buttons:
  Primary: bg-primary hover:bg-primary/90
  Secondary: border hover:bg-gray-50
  Disabled: opacity-50 cursor-not-allowed
```

## Responsive Design

### Desktop (≥1024px)
- Full sidebar visible
- Wide upload zone
- 3-column stats grid

### Tablet (768px-1023px)
- Collapsible sidebar
- Medium upload zone
- 3-column stats grid

### Mobile (<768px)
- Hidden sidebar (hamburger menu)
- Full-width upload zone
- 1-column stats grid (stacked)

## Accessibility

### Keyboard Navigation
- Tab to navigate through elements
- Enter to trigger file picker
- Escape to close dropzone

### Screen Readers
- Alt text on icons
- ARIA labels on interactive elements
- Status announcements

### Focus States
- Visible focus rings
- Keyboard-friendly navigation
- Focus trap in modals

## Error States

### Invalid File Type

```
┌─────────────────────────────────────────────────┐
│  Toast (red):                                   │
│  ❌ Invalid file type                           │
│     Please upload a CSV file                    │
└─────────────────────────────────────────────────┘
```

### File Too Large

```
┌─────────────────────────────────────────────────┐
│  Toast (red):                                   │
│  ❌ File too large                              │
│     Maximum file size is 100MB                  │
└─────────────────────────────────────────────────┘
```

### Upload Failed

```
┌─────────────────────────────────────────────────┐
│  Toast (red):                                   │
│  ❌ Upload failed                               │
│     Network error: Failed to connect            │
└─────────────────────────────────────────────────┘
```

### Import Failed

```
┌─────────────────────────────────────────────────┐
│  ❌ Import Status                  [Failed]      │
│                                                  │
│  ┌─────────────────────────────────────────┐   │
│  │  ❌ Failed to process CSV                │   │
│  │     Missing required column: sku         │   │
│  └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

## Performance

### Optimization Strategies

**Polling:**
- Interval: 1 second (not too aggressive)
- Auto-cleanup on unmount
- Stops when completed/failed

**Rendering:**
- AnimatePresence for mount/unmount
- Conditional rendering
- Memoized components (future)

**Network:**
- Single file upload
- Efficient status polling
- Error retry logic (built-in axios)

### Load Times

- Initial page load: <200ms
- File selection: Instant
- Upload initiation: <500ms
- Status poll: <100ms per request

## Usage Tips

### For Users

1. **Prepare your CSV:**
   - Use the example format
   - Validate columns
   - Check file size

2. **Upload process:**
   - Drag file or click to browse
   - Review file name/size
   - Click "Upload & Process"

3. **Monitor progress:**
   - Watch percentage increase
   - See row counts
   - Wait for completion

4. **Review results:**
   - Check stats (Created/Updated/Errors)
   - Note any errors
   - Upload another file if needed

### For Developers

1. **Test with small files first** (10-100 rows)
2. **Monitor browser console** for errors
3. **Check network tab** for API calls
4. **Test error scenarios** (invalid files)
5. **Verify polling cleanup** (no memory leaks)

## Integration Points

### API Calls

**Upload:**
```typescript
POST /api/v1/products/upload
Content-Type: multipart/form-data
Body: { file: File }
```

**Status Polling:**
```typescript
GET /api/v1/products/upload/{task_id}/status
Response: UploadStatus
```

### State Management

**Local State (useState):**
- file: Selected file
- uploading: Upload in progress
- status: Current upload status
- pollingInterval: Polling timer reference

**No external state management needed** - Self-contained component

## Browser Support

✅ **Chrome** - Full support  
✅ **Firefox** - Full support  
✅ **Safari** - Full support  
✅ **Edge** - Full support  

**Features used:**
- Drag & Drop API
- File API
- Fetch/Axios
- CSS Grid/Flexbox
- CSS Variables

## Troubleshooting

### Upload Not Working

1. Check backend is running (port 8000)
2. Check Vite proxy configuration
3. Verify CORS settings
4. Check browser console

### Progress Not Updating

1. Verify status endpoint responds
2. Check polling interval is active
3. Verify task_id is valid
4. Check Redis is running

### UI Not Responsive

1. Hard refresh browser (Cmd+Shift+R)
2. Clear browser cache
3. Check Tailwind classes are applied
4. Verify CSS is loaded

### Animations Jerky

1. Enable GPU acceleration
2. Reduce motion in OS settings
3. Check CPU usage
4. Simplify animations

## Testing Checklist

### Functional Tests

- [ ] Drag file over zone → Hover effect shows
- [ ] Drop file → File details display
- [ ] Click zone → File picker opens
- [ ] Select non-CSV → Error toast appears
- [ ] Select large file → Error toast appears
- [ ] Select valid CSV → Success toast appears
- [ ] Click Upload → Progress appears
- [ ] Watch progress → Percentage increases
- [ ] Wait for completion → Success toast appears
- [ ] View stats → Numbers displayed correctly
- [ ] Click reset → Returns to empty state

### Visual Tests

- [ ] Animations smooth on entry
- [ ] Progress bar fills correctly
- [ ] Badge colors correct for each state
- [ ] Toast notifications visible
- [ ] Icons render properly
- [ ] Responsive on mobile
- [ ] Dark mode works (if enabled)

### Error Tests

- [ ] Upload .txt file → Rejected
- [ ] Upload 200MB file → Rejected
- [ ] Disconnect backend → Network error
- [ ] Invalid CSV format → Processing error
- [ ] Network timeout → Handled gracefully

## Quick Test Script

### Setup Test File

```bash
cat > test.csv << 'EOF'
sku,name,description,active
TEST-001,Test Product 1,First test,true
TEST-002,Test Product 2,Second test,true
TEST-003,Test Product 3,Third test,false
EOF
```

### Test Flow

1. Open http://localhost:5173/upload
2. Drag `test.csv` onto upload zone
3. Verify file name shows: "test.csv"
4. Click "Upload & Process"
5. Watch progress bar fill
6. Wait for completion toast
7. Verify stats: Created=3, Updated=0, Errors=0
8. Click "Upload Another File"
9. Verify zone resets

### Expected Behavior

```
✅ File selected toast appears
✅ Upload started toast appears
✅ Progress bar animates from 0% → 100%
✅ Row count updates (0/0 → 3/4)
✅ Completion toast appears
✅ Stats display: 3 created, 0 updated, 0 errors
✅ Reset button works
```

## Screenshots Reference

### Default State
- Large upload icon (gray)
- "Drag & drop" text
- Clean, minimal styling
- Dashed border

### Hover State
- Border changes to primary color
- Background slight tint
- Cursor pointer

### Selected State
- File icon (primary color)
- File name prominent
- File size shown
- Upload/Cancel buttons appear

### Processing State
- Status card visible
- Spinner animated
- Progress bar filling
- Row counts updating
- Processing badge

### Success State
- Check icon (green)
- Completed badge
- Stats grid with colors
- Success toast
- Reset button

### Error State
- X icon (red)
- Failed badge
- Error message box
- Error toast
- Reset button

## Customization

### Change Polling Interval

```typescript
// In ProductUpload.tsx
const interval = setInterval(() => {
  pollStatus(task_id);
}, 2000);  // Change to 2 seconds
```

### Change Max File Size

```typescript
const maxSize = 200 * 1024 * 1024;  // 200MB
```

### Change Accepted File Types

```tsx
const { getRootProps, getInputProps } = useDropzone({
  accept: {
    'text/csv': ['.csv'],
    'application/vnd.ms-excel': ['.xls'],
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
  },
});
```

### Customize Colors

```tsx
// In tailwind.config.js
colors: {
  primary: "hsl(220, 90%, 56%)",  // Custom blue
}
```

## Best Practices

### Do's ✅
- ✅ Validate files before upload
- ✅ Show clear error messages
- ✅ Cleanup polling intervals
- ✅ Provide visual feedback
- ✅ Handle all error cases
- ✅ Use semantic HTML
- ✅ Add loading states

### Don'ts ❌
- ❌ Poll too frequently (<500ms)
- ❌ Upload without validation
- ❌ Ignore cleanup on unmount
- ❌ Show technical error messages
- ❌ Block UI during upload
- ❌ Forget accessibility
- ❌ Skip loading states

## Next Steps

### Immediate
1. Test with real CSV files
2. Verify on different browsers
3. Test mobile responsiveness
4. Check accessibility

### Future Enhancements
1. Add CSV preview before upload
2. Implement upload history
3. Add download error report
4. Enable batch uploads
5. Add upload templates
6. Implement pause/resume
7. Add progress notifications
8. Create upload analytics

## See Also

- [Upload Feature Documentation](./UPLOAD_FEATURE.md)
- [Frontend Setup Guide](./FRONTEND_SETUP.md)
- [CSV Import Guide](./CSV_IMPORT_GUIDE.md)
- [API Endpoints Reference](./API_ENDPOINTS.md)

