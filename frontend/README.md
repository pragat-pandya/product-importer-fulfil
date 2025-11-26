# FulFil Frontend

Modern React application built with Vite, TypeScript, TailwindCSS, and shadcn/ui.

## Tech Stack

- **React 19** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **TailwindCSS** - Utility-first CSS
- **shadcn/ui** - Component library
- **React Router** - Client-side routing
- **TanStack Query v5** - Server state management
- **Framer Motion** - Animations
- **Axios** - HTTP client
- **Lucide React** - Icons

## Getting Started

### Install Dependencies

```bash
npm install
```

### Development Server

```bash
npm run dev
```

The app will be available at http://localhost:5173

**API Proxy:** All `/api` requests are proxied to `http://localhost:8000`

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   └── layout/
│   │       ├── Layout.tsx       # Main layout wrapper
│   │       ├── Sidebar.tsx      # Navigation sidebar
│   │       └── Header.tsx       # Top header bar
│   ├── pages/
│   │   └── Dashboard.tsx        # Dashboard page
│   ├── lib/
│   │   ├── api.ts              # Axios instance
│   │   └── utils.ts            # Utility functions
│   ├── App.tsx                 # Main app component
│   ├── main.tsx                # Entry point
│   └── index.css               # Global styles
├── components.json             # shadcn/ui config
├── tailwind.config.js          # Tailwind config
├── vite.config.ts              # Vite config
└── tsconfig.json               # TypeScript config
```

## Features

### Layout
- **Sidebar Navigation** - Clean, minimalist sidebar with icons
- **Header** - Search bar and notifications
- **Responsive** - Mobile-friendly design
- **Dark Mode Ready** - CSS variables for theming

### Routing
- `/` - Dashboard
- `/upload` - CSV Upload
- `/products` - Products List
- `/tasks` - Task Management
- `/settings` - Settings

### API Integration
- Axios configured with base URL
- TanStack Query for data fetching
- Proxy configured for FastAPI backend

## Configuration

### Path Aliases

```typescript
import { Component } from '@/components/Component'
import { utils } from '@/lib/utils'
```

### API Proxy

Vite proxy configuration in `vite.config.ts`:

```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
}
```

### TailwindCSS

Custom theme variables in `src/index.css` for shadcn/ui compatibility.

## Adding shadcn/ui Components

To add components from shadcn/ui:

```bash
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add dialog
```

## Environment Variables

Create `.env` file for environment-specific configuration:

```env
VITE_API_URL=http://localhost:8000
```

## Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## License

Private Project
