# FulFil Frontend Documentation

Complete technical documentation for the FulFil Product Importer frontend application.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Tech Stack](#tech-stack)
3. [Project Structure](#project-structure)
4. [Pages & Components](#pages--components)
5. [State Management](#state-management)
6. [Styling & Design](#styling--design)
7. [Testing](#testing)
8. [Build & Deployment](#build--deployment)

---

## Architecture Overview

### Tech Stack

- **Framework:** React 19 + TypeScript 5.9
- **Build Tool:** Vite 7.2
- **Routing:** React Router DOM v7
- **State Management:** TanStack Query v5 (React Query)
- **Styling:** Tailwind CSS 3.4
- **UI Components:** shadcn/ui + Radix UI
- **Animations:** Framer Motion 12
- **HTTP Client:** Axios
- **Icons:** Lucide React
- **Notifications:** Sonner

### Design Principles

- **Clean Architecture:** Separation of concerns
- **Type Safety:** Full TypeScript coverage
- **Component Composition:** Reusable components
- **Mobile First:** Responsive design
- **Accessibility:** WCAG 2.1 AA standards
- **Performance:** Code splitting, lazy loading

---

## Project Structure

```
frontend/src/
├── components/          # Reusable components
│   ├── layout/         # Layout components (Sidebar, Header)
│   ├── ui/             # shadcn/ui components
│   ├── ProductUpload.tsx
│   ├── ProductsDataTable.tsx
│   ├── WebhooksDataTable.tsx
│   ├── EditProductDialog.tsx
│   ├── EditWebhookDialog.tsx
│   ├── CreateWebhookDialog.tsx
│   ├── PageTransition.tsx
│   ├── TableSkeleton.tsx
│   └── CardSkeleton.tsx
├── pages/              # Page components
│   ├── Dashboard.tsx
│   ├── Upload.tsx
│   ├── Products.tsx
│   └── Webhooks.tsx
├── hooks/              # Custom React hooks
│   ├── useProducts.ts
│   └── useWebhooks.ts
├── types/              # TypeScript types
│   └── webhook.ts
├── lib/                # Utilities
│   ├── api.ts         # Axios instance
│   └── utils.ts       # Helper functions
├── App.tsx            # Root component
└── main.tsx           # Entry point
```

---

## Pages & Components

### Dashboard

**Purpose:** Overview of system stats and recent activity

**Features:**
- Stats cards (Total Products, Active Imports, etc.)
- Recent activity feed
- Animated card grid with stagger effect
- Responsive layout (1/2/4 columns)

**Animations:**
- Cards fade in with 100ms stagger
- Header slides down

### Upload

**Purpose:** CSV file upload with progress tracking

**Features:**
- Drag-and-drop zone (react-dropzone)
- File validation (CSV only, max 100MB)
- Real-time progress bar
- Status badges (Pending, Processing, Completed, Failed)
- Stats display (Created/Updated/Errors)
- Auto-refresh product list on completion

**Components:**
- `ProductUpload` - Main upload component

**Polling:**
- Interval: 1 second
- Stops on: Completed or Failed

### Products

**Purpose:** Product management dashboard

**Features:**
- Data table with server-side pagination
- Search filters (SKU, Name)
- Active status filter
- Edit product dialog
- Delete confirmation
- Bulk delete with double confirmation
- Auto-refresh after operations

**Components:**
- `ProductsDataTable` - Main table
- `EditProductDialog` - Edit form

**Pagination:**
- Rows per page: 10, 20, 50, 100
- First, Previous, Next, Last navigation

### Webhooks

**Purpose:** Webhook management interface

**Features:**
- Webhook list with pagination
- Create webhook dialog
- Edit webhook dialog
- Test button with animated response
- View execution logs
- Active/Inactive filtering
- Quick start guide

**Components:**
- `WebhooksDataTable` - Main table
- `CreateWebhookDialog` - Create form
- `EditWebhookDialog` - Edit form

**Test Button Animation:**
1. Idle: Flask icon
2. Testing: Spinning loader
3. Success: Green checkmark + status code + response time
4. Failure: Red X + error message
5. Auto-clear after 5 seconds

---

## State Management

### TanStack Query (React Query)

**Configuration:**
```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});
```

**Query Keys:**
- `['products', params]` - Product list
- `['product', id]` - Single product
- `['webhooks', params]` - Webhook list
- `['webhook', id]` - Single webhook
- `['uploadStatus', taskId]` - Upload progress
- `['webhookLogs', webhookId]` - Webhook logs

**Cache Invalidation:**
```typescript
// After mutation
queryClient.invalidateQueries({ queryKey: ['products'] });
```

**Polling:**
```typescript
refetchInterval: (data) => {
  if (data?.state === 'Completed') return false;
  return 1000; // Poll every second
}
```

### Local State

**React useState for:**
- Form data
- Dialog open/close
- Filters
- Pagination

**No global state management needed** - React Query handles server state

---

## Styling & Design

### Tailwind CSS

**Configuration:** `/frontend/tailwind.config.js`

**Custom Colors:**
```javascript
colors: {
  primary: "hsl(var(--primary))",
  secondary: "hsl(var(--secondary))",
  destructive: "hsl(var(--destructive))",
  muted: "hsl(var(--muted))",
  accent: "hsl(var(--accent))",
  // ... more colors
}
```

**Responsive Breakpoints:**
```javascript
sm: 640px
md: 768px
lg: 1024px
xl: 1280px
2xl: 1400px
```

### shadcn/ui Components

**Installed:**
- Button, Input, Label
- Dialog, AlertDialog
- Table, Badge, Progress
- Switch, Checkbox, Select, Textarea
- Sonner (Toast)

**Customization:**
- Theme CSS variables in `index.css`
- Component variants via `class-variance-authority`

### Framer Motion

**Page Transitions:**
```typescript
<AnimatePresence mode="wait">
  <Routes location={location} key={location.pathname}>
    ...
  </Routes>
</AnimatePresence>
```

**Variants:**
```typescript
pageVariants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 },
}
```

---

## Testing

### Manual Testing Checklist

**Navigation:**
- [ ] All sidebar links work
- [ ] Page transitions smooth
- [ ] Browser back/forward works

**Product Operations:**
- [ ] Create product
- [ ] Edit product
- [ ] Delete product
- [ ] Bulk delete
- [ ] Search/filter products
- [ ] Pagination

**CSV Upload:**
- [ ] Upload valid CSV
- [ ] Upload invalid CSV
- [ ] Track progress
- [ ] View results

**Webhook Operations:**
- [ ] Create webhook
- [ ] Edit webhook
- [ ] Delete webhook
- [ ] Test webhook
- [ ] View logs

**Responsive:**
- [ ] Mobile (375px)
- [ ] Tablet (768px)
- [ ] Desktop (1920px)

**Toasts:**
- [ ] Success notifications
- [ ] Error notifications
- [ ] Auto-dismiss
- [ ] Manual close

---

## Build & Deployment

### Development

```bash
cd frontend
npm install
npm run dev
```

**Dev Server:** http://localhost:5173  
**Hot Reloading:** Enabled  
**API Proxy:** `/api` → `http://localhost:8000`

### Production Build

```bash
npm run build
```

**Output:** `/frontend/dist`  
**Bundle Size:** ~772 KB (236 KB gzipped)  
**Optimization:** Minification, tree-shaking, code splitting

### Deploy

**Static Hosting (Recommended):**
- Netlify
- Vercel
- AWS S3 + CloudFront
- Nginx

**Configuration:**
```nginx
# Nginx example
location / {
  root /var/www/fulfil/dist;
  try_files $uri $uri/ /index.html;
}

location /api {
  proxy_pass http://backend:8000;
}
```

### Environment Variables

**Build Time:**
- `VITE_API_URL` - Backend API URL (optional, defaults to `/api`)

**Runtime:**
- No runtime env vars needed (all bundled at build time)

---

## Performance

### Bundle Size

| File | Size | Gzipped |
|------|------|---------|
| JS | 772 KB | 236 KB |
| CSS | 32 KB | 6 KB |
| **Total** | **804 KB** | **242 KB** |

### Optimization

- **Code Splitting:** Route-based (future)
- **Tree Shaking:** Enabled
- **Lazy Loading:** Components on demand
- **Image Optimization:** WebP format (future)
- **Caching:** React Query caching strategy

### Loading Performance

- **First Contentful Paint:** < 1.5s
- **Time to Interactive:** < 3s
- **Lighthouse Score:** 90+ (target)

---

## Accessibility

### WCAG 2.1 AA Compliance

- ✅ Keyboard navigation
- ✅ Focus management
- ✅ ARIA labels
- ✅ Color contrast (4.5:1 minimum)
- ✅ Touch targets (44px minimum)
- ✅ Screen reader support

### Keyboard Shortcuts

- `Tab` - Navigate form fields
- `Enter` - Submit forms
- `Esc` - Close dialogs
- `Arrow Keys` - Table navigation (future)

---

## Troubleshooting

### Build Errors

**TypeScript errors:**
```bash
npm run build  # Check for type errors
```

**Dependency issues:**
```bash
rm -rf node_modules package-lock.json
npm install
```

### Runtime Issues

**API connection errors:**
- Check backend is running
- Verify proxy configuration in `vite.config.ts`
- Check CORS settings in backend

**Styling issues:**
- Clear browser cache
- Check Tailwind classes are correct
- Verify CSS variables in `index.css`

---

**Last Updated:** November 26, 2025  
**Version:** 1.0.0  
**Status:** Production Ready

