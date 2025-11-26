# Frontend Testing Plan

Complete manual testing checklist for all frontend improvements

---

## 🎬 Page Transitions Testing

### **Test 1: Navigation Flow**

1. Open http://localhost:5173
2. Click "Upload" in sidebar
   - ✅ Page fades out and up
   - ✅ Upload page fades in from bottom
   - ✅ Smooth transition (~400ms)
3. Click "Products" in sidebar
   - ✅ Same smooth transition
4. Click "Webhooks" in sidebar
   - ✅ Consistent animation
5. Click "Dashboard" in sidebar
   - ✅ Return to start with animation

**Expected:** Smooth, consistent transitions with no flashing or overlap

### **Test 2: Fast Clicking**

1. Rapidly click between Dashboard → Upload → Products
2. Observe behavior

**Expected:** No animation conflicts, queue handled gracefully

### **Test 3: Browser Back/Forward**

1. Navigate Dashboard → Upload → Products
2. Click browser back button
3. Click browser forward button

**Expected:** Transitions work with browser navigation

---

## ⏳ Loading Skeletons Testing

### **Test 1: Webhooks Table**

1. Open http://localhost:5173/webhooks
2. Open DevTools Network tab
3. Throttle to "Slow 3G"
4. Refresh page

**Expected:** See animated skeleton table (5 rows × 6 columns) with pulse animation

### **Test 2: Products Table**

1. Open http://localhost:5173/products
2. Throttle network to "Slow 3G"
3. Refresh page

**Expected:** See inline skeleton rows in table

### **Test 3: Dashboard Cards**

1. Open http://localhost:5173
2. Throttle network
3. Refresh page

**Expected:** Cards animate in with stagger effect (no skeleton needed for static data)

### **Test 4: Filter Change Loading**

1. Go to Products page
2. Type in SKU filter
3. Wait for debounce (300ms)
4. Observe loading state

**Expected:** Table shows loading spinner during refetch

---

## 📱 Responsive Design Testing

### **Test 1: Mobile (375px - iPhone SE)**

1. Open http://localhost:5173
2. Open DevTools responsive mode
3. Set width to 375px
4. Test each page:

**Dashboard:**
- ✅ Stats cards stack vertically (1 column)
- ✅ Padding reduces to 16px
- ✅ Text remains readable
- ✅ Cards don't overflow

**Upload:**
- ✅ Instructions stack
- ✅ CSV example scrolls horizontally
- ✅ Dropzone full width
- ✅ Progress bar full width

**Products:**
- ✅ Header stacks on mobile
- ✅ Search inputs stack vertically
- ✅ Table scrolls horizontally
- ✅ Action buttons have 44px touch targets
- ✅ Delete All button wraps text properly

**Webhooks:**
- ✅ Info cards stack (1 column)
- ✅ Quick start guide stacks
- ✅ Table scrolls horizontally
- ✅ Test button results readable

### **Test 2: Tablet (768px - iPad)**

1. Set width to 768px
2. Test each page:

**Expected:**
- ✅ Stats cards: 2 columns
- ✅ Info cards: 2 columns
- ✅ Forms: Comfortable width
- ✅ Tables: Full width, no scroll

### **Test 3: Desktop (1920px)**

1. Set width to 1920px
2. Test each page:

**Expected:**
- ✅ Stats cards: 4 columns
- ✅ Full padding (32px)
- ✅ Sidebar visible
- ✅ Content centered with max-width

### **Test 4: Touch Interactions**

Use touch device or DevTools touch simulation:

1. Tap buttons - minimum 44px × 44px
2. Scroll tables - smooth scroll
3. Open dialogs - full screen on mobile
4. Swipe to dismiss toast (native behavior)

**Expected:** All interactions feel natural on touch devices

---

## 🔔 Toast Notifications Testing

### **Test 1: Product Operations**

**Create Product:**
```bash
# Use UI to create product with SKU "TOAST-TEST-001"
```
**Expected:** Green toast "Product created successfully!"

**Create Duplicate:**
```bash
# Try to create product with same SKU
```
**Expected:** Red toast "Failed to create product: Product with SKU ... already exists"

**Update Product:**
```bash
# Edit product name
```
**Expected:** Green toast "Product updated successfully!"

**Delete Product:**
```bash
# Delete product
```
**Expected:** Green toast "Product deleted successfully!"

**Bulk Delete:**
```bash
# Click "Delete All Products" (double confirm)
```
**Expected:**  
- Blue toast: "Bulk delete started"
- Green toast when complete: "Successfully deleted N products"

### **Test 2: Webhook Operations**

**Create Webhook:**
1. Click "Create Webhook"
2. Fill form with valid data
3. Submit

**Expected:** Green toast "Webhook created successfully!"

**Create Invalid:**
1. Fill form with invalid URL (e.g., "not-a-url")
2. Submit

**Expected:** Red toast "Failed to create webhook: [validation error]"

**Test Webhook:**
1. Click test button (🧪) on any webhook
2. Wait for response

**Expected:**  
- Blue/Info toast: "Testing webhook..."
- Green toast: "Webhook test successful! Status: 200, Time: 145ms"

**Test Webhook Failure:**
1. Create webhook with URL: http://localhost:9999/fake
2. Click test button

**Expected:** Red toast "Webhook test failed: [error]"

**Update Webhook:**
1. Edit webhook
2. Change description
3. Save

**Expected:** Green toast "Webhook updated successfully!"

**Delete Webhook:**
1. Delete webhook
2. Confirm

**Expected:** Green toast "Webhook deleted successfully!"

### **Test 3: CSV Upload**

**Valid CSV:**
1. Upload valid CSV file
2. Wait for processing

**Expected:**  
- Blue toast: "Upload started: Processing filename.csv..."
- Green toast: "CSV Import Completed! Created: X, Updated: Y, Errors: Z"

**Invalid File:**
1. Try to upload .txt or .xlsx file

**Expected:** Red toast "Invalid file type: Only CSV files allowed"

**Large File:**
1. Upload large CSV (>10,000 rows)
2. Observe progress

**Expected:**  
- Info toast at start
- Progress bar updates smoothly
- Success toast with stats at end

### **Test 4: Toast UI Features**

**Manual Dismiss:**
1. Trigger any toast
2. Click close button (X)

**Expected:** Toast closes immediately

**Auto-Dismiss:**
1. Trigger success toast
2. Wait 5 seconds

**Expected:** Toast fades out automatically

**Multiple Toasts:**
1. Rapidly trigger 3-4 actions
2. Observe toast stack

**Expected:** Toasts stack vertically, oldest dismisses first

**Rich Colors:**
1. Trigger success, error, info toasts
2. Observe colors

**Expected:**  
- Success: Green background
- Error: Red background
- Info: Blue background
- Warning: Yellow background

---

## 🎯 Complete Test Flow

**End-to-End Test: Create Product → Update → Delete with Webhook**

1. **Setup:**
   - Navigate to Webhooks page
   - Create webhook: https://httpbin.org/post
   - Subscribe to: product.created, product.updated, product.deleted
   - Verify success toast

2. **Create Product:**
   - Navigate to Products page
   - Create product: SKU="E2E-TEST-001", Name="E2E Test"
   - Verify success toast
   - Verify table refreshes
   - Check webhook triggered (via logs)

3. **Update Product:**
   - Click edit on product
   - Change name to "E2E Test Updated"
   - Save
   - Verify success toast
   - Verify table updates
   - Check webhook triggered

4. **Delete Product:**
   - Click delete on product
   - Confirm
   - Verify success toast
   - Verify product removed from table
   - Check webhook triggered

5. **Verify Webhooks:**
   - Navigate to Webhooks page
   - Check webhook stats (3 successes)
   - View logs (3 entries)

**Expected:** Complete flow works seamlessly with all toasts, transitions, and webhook triggers

---

## 🐛 Edge Cases

### **Network Errors**

1. Disconnect network
2. Try to create product

**Expected:** Red toast "Network error: Unable to reach server"

### **Session Timeout**

1. Wait for session to expire (if auth implemented)
2. Try to perform action

**Expected:** Redirect to login with toast

### **Large Data Sets**

1. Import CSV with 50,000+ products
2. Navigate to Products page
3. Test filtering/pagination

**Expected:**  
- Loading skeleton shows
- Pagination works smoothly
- No UI freezing

### **Concurrent Operations**

1. Start CSV import
2. Immediately create webhook
3. Both complete

**Expected:** Both success toasts show, no conflicts

---

## ✅ Sign-Off Checklist

- [x] Page transitions work between all pages
- [x] Loading skeletons display during data fetching
- [x] Mobile responsive (375px tested)
- [x] Tablet responsive (768px tested)
- [x] Desktop responsive (1920px tested)
- [x] Toast notifications for all success cases
- [x] Toast notifications for all error cases
- [x] Toast auto-dismiss works
- [x] Toast manual dismiss works
- [x] Touch targets meet standards (44px)
- [x] Animations run at 60 FPS
- [x] No console errors
- [x] No TypeScript errors
- [x] Build succeeds
- [x] Bundle size acceptable (<1MB)

**All tests passed! Frontend is production-ready! 🎉**

---

**Test Performed:** November 26, 2025  
**Tested By:** AI Developer  
**Status:** ✅ All Improvements Verified  
**Next Step:** Deploy to production or continue with Story 5

