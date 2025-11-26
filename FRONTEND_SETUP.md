# Frontend Setup Guide

## Overview

The FulFil frontend is a modern React application built with Vite, TypeScript, TailwindCSS, and shadcn/ui. It provides a clean, minimalist interface for managing product imports.

## Technology Stack

### Core
- **React 19** - Latest React with improved performance
- **TypeScript** - Type-safe JavaScript
- **Vite 7** - Lightning-fast dev server and build tool

### Styling
- **TailwindCSS 3.4** - Utility-first CSS framework
- **shadcn/ui** - Beautiful, accessible component library
- **Framer Motion 12** - Smooth animations and transitions

### Data & Routing
- **TanStack Query v5** - Powerful async state management
- **React Router 7** - Declarative routing
- **Axios** - Promise-based HTTP client

### Icons & Utilities
- **Lucide React** - Beautiful, consistent icons
- **clsx** - Conditional className utility
- **tailwind-merge** - Merge Tailwind classes intelligently

## Project Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── components/        # Reusable UI components
│   │   └── layout/       # Layout components
│   │       ├── Layout.tsx    # Main layout wrapper
│   │       ├── Sidebar.tsx   # Navigation sidebar
│   │       └── Header.tsx    # Top header bar
│   ├── pages/            # Page components
│   │   └── Dashboard.tsx # Dashboard page
│   ├── lib/              # Utilities and helpers
│   │   ├── api.ts       # Axios instance
│   │   └── utils.ts     # Utility functions (cn)
│   ├── App.tsx           # Main app component
│   ├── main.tsx          # Entry point
│   └── index.css         # Global styles
├── components.json        # shadcn/ui configuration
├── tailwind.config.js     # Tailwind configuration
├── postcss.config.js      # PostCSS configuration
├── vite.config.ts         # Vite configuration
├── tsconfig.json          # TypeScript configuration
├── tsconfig.app.json      # App-specific TS config
├── package.json           # Dependencies
└── README.md              # Frontend documentation
```

## Getting Started

### Prerequisites
- Node.js 18+ and npm 9+
- Backend API running on http://localhost:8000

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

**Dev Server:** http://localhost:5173

**Features:**
- ⚡️ Hot Module Replacement (HMR)
- 🔄 Fast Refresh
- 🎨 Tailwind JIT compilation
- 🔗 API proxy to backend

### Build

```bash
npm run build
```

**Output:** `dist/` directory with optimized production build

### Preview Production Build

```bash
npm run preview
```

## Configuration

### Path Aliases

TypeScript and Vite are configured to use `@/` as an alias for `src/`:

```typescript
// Instead of:
import { Button } from '../../components/Button'

// Use:
import { Button } from '@/components/Button'
```

**Configuration in:**
- `tsconfig.app.json` - TypeScript paths
- `vite.config.ts` - Vite resolve aliases

### API Proxy

All `/api` requests are automatically proxied to the FastAPI backend:

```typescript
// vite.config.ts
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
}
```

**Usage:**
```typescript
// Automatically proxied to http://localhost:8000/api/v1/products/upload
axios.post('/api/v1/products/upload', formData)
```

### Tailwind CSS

Custom theme using CSS variables for easy theming:

**Colors defined in `src/index.css`:**
- `--background` / `--foreground`
- `--primary` / `--primary-foreground`
- `--secondary` / `--secondary-foreground`
- `--muted` / `--muted-foreground`
- `--accent` / `--accent-foreground`
- `--destructive` / `--destructive-foreground`
- `--border` / `--input` / `--ring`
- `--radius` (border radius)

**Dark mode ready** - Use `.dark` class on `<html>` or `<body>`

## Components

### Layout System

#### Layout Component
Main wrapper that provides sidebar and header:

```tsx
<Layout>
  <YourPageContent />
</Layout>
```

#### Sidebar
- Fixed left sidebar (64 width)
- Navigation links with icons
- Active state highlighting
- User profile section
- Animated entrance

**Navigation Routes:**
- Dashboard (`/`)
- Upload (`/upload`)
- Products (`/products`)
- Tasks (`/tasks`)
- Settings (`/settings`)

#### Header
- Sticky top header
- Search bar
- Notification bell
- Backdrop blur effect

### Adding shadcn/ui Components

shadcn/ui is configured and ready to use. Add components as needed:

```bash
# Add a button component
npx shadcn-ui@latest add button

# Add a card component
npx shadcn-ui@latest add card

# Add a dialog component
npx shadcn-ui@latest add dialog

# Add a form component
npx shadcn-ui@latest add form
```

Components will be added to `src/components/ui/`

## Data Fetching

### Axios Configuration

Pre-configured Axios instance in `src/lib/api.ts`:

```typescript
import api from '@/lib/api';

// GET request
const { data } = await api.get('/products');

// POST request
const { data } = await api.post('/products/upload', formData);
```

### TanStack Query Example

```typescript
import { useQuery, useMutation } from '@tanstack/react-query';
import api from '@/lib/api';

// Fetch data
const { data, isLoading, error } = useQuery({
  queryKey: ['products'],
  queryFn: async () => {
    const response = await api.get('/products');
    return response.data;
  },
});

// Mutate data
const mutation = useMutation({
  mutationFn: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/products/upload', formData);
  },
  onSuccess: () => {
    // Invalidate and refetch
    queryClient.invalidateQueries({ queryKey: ['products'] });
  },
});
```

## Routing

React Router 7 configured in `App.tsx`:

```typescript
<Routes>
  <Route path="/" element={<Dashboard />} />
  <Route path="/upload" element={<Upload />} />
  <Route path="/products" element={<Products />} />
  <Route path="/tasks" element={<Tasks />} />
  <Route path="/settings" element={<Settings />} />
</Routes>
```

## Animations

Framer Motion is installed for smooth animations:

```typescript
import { motion } from 'framer-motion';

<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.3 }}
>
  Content
</motion.div>
```

**Example in Sidebar:**
```typescript
<motion.aside
  initial={{ x: -280 }}
  animate={{ x: 0 }}
>
  Sidebar content
</motion.aside>
```

## Styling Guidelines

### Using Tailwind Classes

```tsx
// Responsive design
<div className="w-full md:w-1/2 lg:w-1/3">

// Dark mode
<div className="bg-white dark:bg-gray-900">

// Hover effects
<button className="hover:bg-gray-100 transition-colors">

// Using theme colors
<div className="bg-primary text-primary-foreground">
```

### Using cn() Utility

Combine conditional classes elegantly:

```tsx
import { cn } from '@/lib/utils';

<div className={cn(
  "base-classes",
  isActive && "active-classes",
  isPrimary ? "primary-classes" : "secondary-classes"
)} />
```

## Environment Variables

Create `.env` file in frontend root:

```env
# API URL (optional - defaults to proxy)
VITE_API_URL=http://localhost:8000

# App title
VITE_APP_TITLE="FulFil Product Importer"
```

**Usage:**
```typescript
const apiUrl = import.meta.env.VITE_API_URL;
```

## Scripts

| Script | Command | Description |
|--------|---------|-------------|
| `dev` | `npm run dev` | Start dev server (HMR) |
| `build` | `npm run build` | Build for production |
| `preview` | `npm run preview` | Preview production build |
| `lint` | `npm run lint` | Run ESLint |

## IDE Setup

### VS Code

Recommended extensions:
- ESLint
- Tailwind CSS IntelliSense
- TypeScript Vue Plugin (Volar)

**Settings:**
```json
{
  "typescript.tsdk": "node_modules/typescript/lib",
  "tailwindCSS.experimental.classRegex": [
    ["cn\\(([^)]*)\\)", "[\"'`]([^\"'`]*).*?[\"'`]"]
  ]
}
```

## Performance Optimization

### Code Splitting

Vite automatically code-splits on dynamic imports:

```typescript
const Dashboard = lazy(() => import('./pages/Dashboard'));
```

### Image Optimization

Use Vite's asset handling:

```typescript
import logo from './assets/logo.png';
<img src={logo} alt="Logo" />
```

### Bundle Analysis

```bash
npm run build -- --mode analyze
```

## Troubleshooting

### Port Already in Use

```bash
# Kill process on port 5173
lsof -ti:5173 | xargs kill -9

# Or use a different port
npm run dev -- --port 3000
```

### Tailwind Classes Not Working

1. Check `tailwind.config.js` content array
2. Ensure `@tailwind` directives in `index.css`
3. Restart dev server

### API Proxy Not Working

1. Check backend is running on port 8000
2. Verify `vite.config.ts` proxy configuration
3. Check browser console for CORS errors

### Type Errors

```bash
# Clear TypeScript cache
rm -rf node_modules/.cache

# Rebuild
npm run build
```

## Deployment

### Production Build

```bash
npm run build
```

### Serve with Static Server

```bash
npm install -g serve
serve -s dist -l 3000
```

### Docker

Create `frontend/Dockerfile`:

```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Best Practices

✅ Use TypeScript strictly - no `any` types  
✅ Keep components small and focused  
✅ Use TanStack Query for server state  
✅ Use React Router for navigation  
✅ Leverage Tailwind utilities over custom CSS  
✅ Use shadcn/ui components for consistency  
✅ Implement proper error boundaries  
✅ Add loading states for async operations  
✅ Use Framer Motion sparingly for key interactions  

## Next Steps

1. **Add more pages:**
   - Upload page with drag-drop
   - Products list with filters
   - Task management with real-time updates
   - Settings page

2. **Add components:**
   - File upload with progress
   - Data tables
   - Charts and visualizations
   - Notifications/toasts

3. **Enhance features:**
   - Dark mode toggle
   - User authentication
   - Real-time updates (WebSockets)
   - Offline support (PWA)

## Resources

- [Vite Documentation](https://vitejs.dev/)
- [React Documentation](https://react.dev/)
- [TailwindCSS Documentation](https://tailwindcss.com/)
- [shadcn/ui Documentation](https://ui.shadcn.com/)
- [TanStack Query Documentation](https://tanstack.com/query/)
- [Framer Motion Documentation](https://www.framer.com/motion/)

