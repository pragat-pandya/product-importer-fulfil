import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from '@/components/ui/sonner';
import { Layout } from './components/layout/Layout';
import { Dashboard } from './pages/Dashboard';
import { Upload } from './pages/Upload';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/upload" element={<Upload />} />
            <Route path="/products" element={<div>Products Page - Coming Soon</div>} />
            <Route path="/tasks" element={<div>Tasks Page - Coming Soon</div>} />
            <Route path="/settings" element={<div>Settings Page - Coming Soon</div>} />
          </Routes>
        </Layout>
        <Toaster />
      </Router>
    </QueryClientProvider>
  );
}

export default App;
